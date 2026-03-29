# ADR 027: WorkflowWizard Improvements

## Status
Accepted

## Context
The WorkflowWizard component required `onStepComplete` as a mandatory callback prop, which forced parent pages to provide a handler even when no side-effect was needed. Additionally, there was no visual indication when a user completed all steps in a workflow.

## Decision
- Make `onStepComplete` optional (default no-op) so the wizard can be used standalone.
- Add an all-steps-complete banner that shows when every step in the workflow is marked done, giving users clear confirmation they finished the process.

## Consequences
- **Positive:** Simpler integration — parent pages don't need boilerplate callback handlers.
- **Positive:** Better UX with completion feedback.
- **Negative:** None significant.
