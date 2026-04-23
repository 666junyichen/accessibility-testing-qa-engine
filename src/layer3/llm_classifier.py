"""Bedrock-backed Layer 3 LLM classifier.

This module wraps single-request Bedrock invocation and validates 5.1-A/B
outputs against the canonical Pydantic schemas. Batch execution, checkpointing,
and cost tracking are intentionally left to Step 5.2 Task 2.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Literal, Optional, Union

import boto3
from botocore.exceptions import ClientError
from json_repair import loads as repair_json_loads
from pydantic import ValidationError

from layer3 import prompts_a, prompts_b
from layer3.schemas_a import FindingsOutput
from layer3.schemas_b import VideoAssessment


DEFAULT_MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
DEFAULT_REGION = "us-east-1"
DEFAULT_PROFILE = "smp-cs20"
ANTHROPIC_VERSION = "bedrock-2023-05-31"
RETRYABLE_ERROR_CODES = {
    "ThrottlingException",
    "TooManyRequestsException",
    "ServiceUnavailableException",
    "InternalServerException",
    "ModelTimeoutException",
}

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    output: Optional[Union[FindingsOutput, VideoAssessment]]
    flag: Literal["ok", "json_parse_error", "schema_violation", "api_error"]
    raw_text: str
    usage: dict
    error: Optional[str]
    latency_ms: int
    findings_dropped: int = 0


def _to_anthropic_payload(messages: list[dict], max_tokens: int) -> dict:
    system_parts: list[str] = []
    anthropic_messages: list[dict] = []

    for message in messages:
        role = message.get("role")
        content = message.get("content", "")
        if role == "system":
            system_parts.append(str(content))
        elif role in {"user", "assistant"}:
            anthropic_messages.append({"role": role, "content": str(content)})
        else:
            raise ValueError(f"unsupported message role: {role!r}")

    payload = {
        "anthropic_version": ANTHROPIC_VERSION,
        "max_tokens": max_tokens,
        "messages": anthropic_messages,
    }
    if system_parts:
        payload["system"] = "\n\n".join(system_parts)
    return payload


def _read_bedrock_body(response: dict) -> dict:
    body = response.get("body")
    if hasattr(body, "read"):
        body = body.read()
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    if isinstance(body, str):
        return json.loads(body)
    if isinstance(body, dict):
        return body
    raise TypeError(f"unsupported Bedrock body type: {type(body)!r}")


def _is_retryable_exception(exc: Exception) -> bool:
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return True
    if isinstance(exc, ClientError):
        code = exc.response.get("Error", {}).get("Code", "")
        return code in RETRYABLE_ERROR_CODES
    return False


def invoke_bedrock(
    messages: list[dict],
    model_id: str = DEFAULT_MODEL_ID,
    max_tokens: int = 2000,
    region: str = DEFAULT_REGION,
    profile: str = DEFAULT_PROFILE,
    max_retries: int = 3,
) -> dict:
    """Invoke Bedrock runtime and return the raw Anthropic response dict."""

    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client("bedrock-runtime", region_name=region)
    payload = _to_anthropic_payload(messages, max_tokens=max_tokens)

    attempt = 0
    while True:
        try:
            response = client.invoke_model(
                modelId=model_id,
                body=json.dumps(payload),
                contentType="application/json",
                accept="application/json",
            )
            return _read_bedrock_body(response)
        except Exception as exc:
            if not _is_retryable_exception(exc) or attempt >= max_retries - 1:
                logger.exception("Bedrock invoke failed")
                raise
            sleep_seconds = 2**attempt
            logger.warning(
                "Retryable Bedrock error on attempt %s/%s; sleeping %ss",
                attempt + 1,
                max_retries,
                sleep_seconds,
            )
            time.sleep(sleep_seconds)
            attempt += 1


def _extract_raw_text(raw: dict) -> str:
    content = raw.get("content", [])
    if not content:
        return ""
    first = content[0]
    if isinstance(first, dict):
        return str(first.get("text", ""))
    return str(first)


def _extract_json_text(raw_text: str) -> str:
    fence = re.search(r"```(?:json)?\s*(.*?)```", raw_text, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()

    start = raw_text.find("{")
    if start == -1:
        raise ValueError("no JSON object found in model text")

    depth = 0
    in_string = False
    escaped = False
    for idx in range(start, len(raw_text)):
        char = raw_text[idx]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return raw_text[start : idx + 1].strip()

    raise ValueError("unterminated JSON object in model text")


def _parse_json_object(raw_text: str) -> dict:
    json_text = _extract_json_text(raw_text)
    try:
        obj = json.loads(json_text)
    except json.JSONDecodeError:
        obj = repair_json_loads(json_text)
    if not isinstance(obj, dict):
        raise ValueError("model output JSON root must be an object")
    return obj


def _classify_with_schema(
    messages: list[dict],
    schema_cls,
    model_id: str,
) -> ClassificationResult:
    start = time.monotonic()
    raw: dict = {}
    raw_text = ""
    usage: dict = {}

    try:
        raw = invoke_bedrock(messages, model_id=model_id)
        raw_text = _extract_raw_text(raw)
        usage = raw.get("usage", {}) or {}
        obj = _parse_json_object(raw_text)
        output = schema_cls.model_validate(obj)
        output, findings_dropped = _drop_null_enum_findings(output)
        return ClassificationResult(
            output=output,
            flag="ok",
            raw_text=raw_text,
            usage=usage,
            error=None,
            latency_ms=int((time.monotonic() - start) * 1000),
            findings_dropped=findings_dropped,
        )
    except ValidationError as exc:
        return ClassificationResult(
            output=None,
            flag="schema_violation",
            raw_text=raw_text,
            usage=usage,
            error=str(exc),
            latency_ms=int((time.monotonic() - start) * 1000),
        )
    except (json.JSONDecodeError, ValueError) as exc:
        return ClassificationResult(
            output=None,
            flag="json_parse_error",
            raw_text=raw_text,
            usage=usage,
            error=str(exc),
            latency_ms=int((time.monotonic() - start) * 1000),
        )
    except Exception as exc:
        usage = raw.get("usage", {}) if isinstance(raw, dict) else {}
        return ClassificationResult(
            output=None,
            flag="api_error",
            raw_text=raw_text,
            usage=usage,
            error=str(exc),
            latency_ms=int((time.monotonic() - start) * 1000),
        )


def _drop_null_enum_findings(output):
    if not isinstance(output, FindingsOutput):
        return output, 0

    kept = [
        finding
        for finding in output.findings
        if finding.friction_type is not None
        and finding.severity_s is not None
        and finding.calibrator_score_l is not None
    ]
    dropped = len(output.findings) - len(kept)
    if dropped == 0:
        return output, 0
    return FindingsOutput(findings=kept), dropped


def classify_finding_level(
    window_id: str,
    project: str,
    video_id: str,
    window_text: str,
    task_title: str,
    task_instructions: str,
    model_id: str = DEFAULT_MODEL_ID,
) -> ClassificationResult:
    messages = prompts_a.build_messages(
        window_id=window_id,
        project=project,
        video_id=video_id,
        window_text=window_text,
        task_title=task_title,
        task_instructions=task_instructions,
    )
    return _classify_with_schema(messages, FindingsOutput, model_id=model_id)


def classify_video_level(
    video_id: str,
    project: str,
    task_title: str,
    aggregated_transcript: str,
    model_id: str = DEFAULT_MODEL_ID,
) -> ClassificationResult:
    messages = prompts_b.build_messages(
        video_id=video_id,
        project=project,
        transcript=aggregated_transcript,
        task_title=task_title,
        task_instructions="No task instructions provided.",
    )
    return _classify_with_schema(messages, VideoAssessment, model_id=model_id)


@dataclass
class WindowInput:
    window_id: str
    project: str
    video_id: str
    window_text: str
    task_title: str
    task_instructions: str


@dataclass
class VideoInput:
    video_id: str
    project: str
    task_title: str
    aggregated_transcript: str


@dataclass
class BatchSummary:
    total: int
    succeeded: int
    schema_violation: int
    json_parse_error: int
    api_error: int
    total_input_tokens: int
    total_output_tokens: int
    estimated_cost_usd: float
    elapsed_seconds: float
    findings_dropped: int


_CHECKPOINT_FLAGS = {"ok", "schema_violation", "json_parse_error"}
_OUTPUT_FIELDS = [
    "window_id",
    "flag",
    "output_json",
    "input_tokens",
    "output_tokens",
    "latency_ms",
    "error",
    "findings_dropped",
    "timestamp_utc",
]
_CHECKPOINT_FIELDS = ["window_id", "flag", "timestamp_utc"]


def _timestamp_utc() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _ensure_parent(path: str) -> None:
    from pathlib import Path

    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _read_done_ids(checkpoint_csv: str) -> set[str]:
    import csv
    from pathlib import Path

    path = Path(checkpoint_csv)
    if not path.exists():
        return set()

    with path.open(newline="", encoding="utf-8") as handle:
        return {
            row["window_id"]
            for row in csv.DictReader(handle)
            if row.get("flag") in _CHECKPOINT_FLAGS
        }


def _append_csv_row(path: str, fieldnames: list[str], row: dict) -> None:
    import csv
    from pathlib import Path

    _ensure_parent(path)
    csv_path = Path(path)
    write_header = not csv_path.exists() or csv_path.stat().st_size == 0
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def _result_output_json(result: ClassificationResult) -> str:
    if result.output is None:
        return result.raw_text
    return result.output.model_dump_json()


def _mock_finding_result() -> ClassificationResult:
    output = FindingsOutput(findings=[])
    return ClassificationResult(
        output=output,
        flag="ok",
        raw_text=output.model_dump_json(),
        usage={"input_tokens": 0, "output_tokens": 0},
        error=None,
        latency_ms=0,
        findings_dropped=0,
    )


def _mock_video_result() -> ClassificationResult:
    output = VideoAssessment(
        narration_quality="adequate",
        recording_quality="good",
        coaching_evidence="none",
    )
    return ClassificationResult(
        output=output,
        flag="ok",
        raw_text=output.model_dump_json(),
        usage={"input_tokens": 0, "output_tokens": 0},
        error=None,
        latency_ms=0,
        findings_dropped=0,
    )


def _summarize_batch(
    total: int,
    results: list[ClassificationResult],
    elapsed_seconds: float,
    cost_per_1m_input: float,
    cost_per_1m_output: float,
) -> BatchSummary:
    total_input_tokens = sum(int(result.usage.get("input_tokens", 0)) for result in results)
    total_output_tokens = sum(
        int(result.usage.get("output_tokens", 0)) for result in results
    )
    estimated_cost = (
        total_input_tokens * cost_per_1m_input / 1_000_000
        + total_output_tokens * cost_per_1m_output / 1_000_000
    )
    return BatchSummary(
        total=total,
        succeeded=sum(result.flag == "ok" for result in results),
        schema_violation=sum(result.flag == "schema_violation" for result in results),
        json_parse_error=sum(result.flag == "json_parse_error" for result in results),
        api_error=sum(result.flag == "api_error" for result in results),
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        estimated_cost_usd=estimated_cost,
        elapsed_seconds=elapsed_seconds,
        findings_dropped=sum(result.findings_dropped for result in results),
    )


def _record_batch_result(
    item_id: str,
    result: ClassificationResult,
    output_csv: str,
    checkpoint_csv: str,
) -> None:
    timestamp = _timestamp_utc()
    _append_csv_row(
        output_csv,
        _OUTPUT_FIELDS,
        {
            "window_id": item_id,
            "flag": result.flag,
            "output_json": _result_output_json(result),
            "input_tokens": int(result.usage.get("input_tokens", 0)),
            "output_tokens": int(result.usage.get("output_tokens", 0)),
            "latency_ms": result.latency_ms,
            "error": result.error or "",
            "findings_dropped": result.findings_dropped,
            "timestamp_utc": timestamp,
        },
    )
    if result.flag in _CHECKPOINT_FLAGS:
        _append_csv_row(
            checkpoint_csv,
            _CHECKPOINT_FIELDS,
            {"window_id": item_id, "flag": result.flag, "timestamp_utc": timestamp},
        )


def batch_classify_windows(
    windows: list[WindowInput],
    output_csv: str,
    checkpoint_csv: str,
    model_id: str = DEFAULT_MODEL_ID,
    max_concurrency: int = 4,
    dry_run: bool = False,
    cost_per_1m_input: float = 0.25,
    cost_per_1m_output: float = 1.25,
) -> BatchSummary:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    started = time.monotonic()
    done_ids = _read_done_ids(checkpoint_csv)
    pending = [window for window in windows if window.window_id not in done_ids]
    results: list[ClassificationResult] = []

    logger.info("Starting 5.1-A batch: total=%s pending=%s", len(windows), len(pending))
    if not pending:
        return _summarize_batch(
            total=0,
            results=[],
            elapsed_seconds=time.monotonic() - started,
            cost_per_1m_input=cost_per_1m_input,
            cost_per_1m_output=cost_per_1m_output,
        )

    def run_one(window: WindowInput) -> tuple[str, ClassificationResult]:
        if dry_run:
            return window.window_id, _mock_finding_result()
        return (
            window.window_id,
            classify_finding_level(
                window_id=window.window_id,
                project=window.project,
                video_id=window.video_id,
                window_text=window.window_text,
                task_title=window.task_title,
                task_instructions=window.task_instructions,
                model_id=model_id,
            ),
        )

    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        futures = [executor.submit(run_one, window) for window in pending]
        for index, future in enumerate(as_completed(futures), start=1):
            item_id, result = future.result()
            results.append(result)
            _record_batch_result(item_id, result, output_csv, checkpoint_csv)
            if index % 20 == 0 or index == len(futures):
                summary = _summarize_batch(
                    total=len(results),
                    results=results,
                    elapsed_seconds=time.monotonic() - started,
                    cost_per_1m_input=cost_per_1m_input,
                    cost_per_1m_output=cost_per_1m_output,
                )
                logger.info("5.1-A progress: %s/%s %s", index, len(futures), summary)

    return _summarize_batch(
        total=len(pending),
        results=results,
        elapsed_seconds=time.monotonic() - started,
        cost_per_1m_input=cost_per_1m_input,
        cost_per_1m_output=cost_per_1m_output,
    )


def batch_classify_videos(
    videos: list[VideoInput],
    output_csv: str,
    checkpoint_csv: str,
    model_id: str = DEFAULT_MODEL_ID,
    max_concurrency: int = 2,
    dry_run: bool = False,
    cost_per_1m_input: float = 0.25,
    cost_per_1m_output: float = 1.25,
) -> BatchSummary:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    started = time.monotonic()
    done_ids = _read_done_ids(checkpoint_csv)
    pending = [video for video in videos if video.video_id not in done_ids]
    results: list[ClassificationResult] = []

    logger.info("Starting 5.1-B batch: total=%s pending=%s", len(videos), len(pending))
    if not pending:
        return _summarize_batch(
            total=0,
            results=[],
            elapsed_seconds=time.monotonic() - started,
            cost_per_1m_input=cost_per_1m_input,
            cost_per_1m_output=cost_per_1m_output,
        )

    def run_one(video: VideoInput) -> tuple[str, ClassificationResult]:
        if dry_run:
            return video.video_id, _mock_video_result()
        return (
            video.video_id,
            classify_video_level(
                video_id=video.video_id,
                project=video.project,
                task_title=video.task_title,
                aggregated_transcript=video.aggregated_transcript,
                model_id=model_id,
            ),
        )

    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        futures = [executor.submit(run_one, video) for video in pending]
        for index, future in enumerate(as_completed(futures), start=1):
            item_id, result = future.result()
            results.append(result)
            _record_batch_result(item_id, result, output_csv, checkpoint_csv)
            if index % 20 == 0 or index == len(futures):
                summary = _summarize_batch(
                    total=len(results),
                    results=results,
                    elapsed_seconds=time.monotonic() - started,
                    cost_per_1m_input=cost_per_1m_input,
                    cost_per_1m_output=cost_per_1m_output,
                )
                logger.info("5.1-B progress: %s/%s %s", index, len(futures), summary)

    return _summarize_batch(
        total=len(pending),
        results=results,
        elapsed_seconds=time.monotonic() - started,
        cost_per_1m_input=cost_per_1m_input,
        cost_per_1m_output=cost_per_1m_output,
    )
