const restrictedPatterns = [
  /the university of queensland/gi,
  /\buq\b/gi,
];

export function sanitizePublicLabel(value) {
  let output = value;
  for (const pattern of restrictedPatterns) {
    output = output.replace(pattern, "Junyi Chen");
  }
  return output.replace(/\s+/g, " ").trim();
}

export function containsRestrictedSchoolName(value) {
  return restrictedPatterns.some((pattern) => {
    pattern.lastIndex = 0;
    return pattern.test(value);
  });
}
