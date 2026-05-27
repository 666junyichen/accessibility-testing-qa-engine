import { pipelineSteps } from "../lib/demo-data";
import styles from "./pipeline-diagram.module.css";

export function PipelineDiagram() {
  return (
    <div className={styles.grid}>
      {pipelineSteps.map((step, index) => (
        <article key={step.name} className={styles.card}>
          <p className={styles.index}>0{index + 1}</p>
          <h3>{step.name}</h3>
          <p>{step.detail}</p>
        </article>
      ))}
    </div>
  );
}
