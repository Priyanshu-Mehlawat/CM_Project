# Stage 00 viva notes

- This project studies AKI progression after Stage 1, rather than AKI onset.
- The current deliverable demonstrates software structure and honest availability
  states. It establishes no predictive validity or clinical benefit.
- A healthy API is not a loaded model: `service_alive` and `model_available` differ.
- Cases are invented interface fixtures, not de-identified patient records.
- The frontend does not calculate clinical stage or invent model probabilities.
- Clinical baseline, timing and negative-outcome ascertainment depend on G1.
  Missing follow-up cannot establish a negative outcome.
- External evaluation requires comparable cohort definitions and frozen models.
- Git ignore rules do not remove tracked files; staged/history checks supplement
  human disclosure review and OS-level isolation.
- Demonstrate selecting a synthetic example, switching to Research Console,
  and the unavailable-backend/retry state. No model results should appear.
