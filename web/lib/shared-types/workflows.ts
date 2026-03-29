/**
 * A single step within a guided legal workflow.
 *
 * @property id - Unique step identifier
 * @property title - Display title for the step
 * @property explanation - Detailed instructions for completing this step
 * @property required_documents - Documents needed for this step
 * @property tips - Helpful tips for successful completion
 * @property deadlines - Time-sensitive deadlines for this step
 * @property status - Completion status: not_started, in_progress, completed, or skipped
 */
export interface WorkflowStep {
  id: string;
  title: string;
  explanation: string;
  required_documents: string[];
  tips: string[];
  deadlines: string[];
  status: "not_started" | "in_progress" | "completed" | "skipped";
}

/**
 * A reusable workflow template defining a multi-step legal process.
 *
 * @property id - Unique template identifier
 * @property title - Display title (e.g., "Security Deposit Recovery")
 * @property description - Brief description of what the workflow covers
 * @property domain - Legal domain category
 * @property estimated_time - Human-readable time estimate (e.g., "2-3 weeks")
 * @property steps - Ordered array of workflow steps
 */
export interface WorkflowTemplate {
  id: string;
  title: string;
  description: string;
  domain: string;
  estimated_time: string;
  steps: WorkflowStep[];
}

/**
 * An active workflow instance created from a template, with user-specific progress.
 *
 * @property id - Unique instance identifier
 * @property user_id - The user who started this workflow
 * @property template_id - The template this instance was created from
 * @property title - Workflow title (copied from template)
 * @property domain - Legal domain category
 * @property steps - Array of steps with user-specific status updates
 * @property current_step - Zero-based index of the current active step
 * @property status - Overall workflow status
 * @property started_at - ISO timestamp of when the user started this workflow
 * @property updated_at - ISO timestamp of last activity
 */
export interface WorkflowInstance {
  id: string;
  user_id: string;
  template_id: string;
  title: string;
  domain: string;
  steps: WorkflowStep[];
  current_step: number;
  status: string;
  started_at: string;
  updated_at: string;
}

/**
 * Abbreviated workflow data for display in the active workflows list.
 *
 * @property id - Unique instance identifier
 * @property template_id - Source template ID
 * @property title - Workflow title
 * @property domain - Legal domain category
 * @property current_step - Current step index
 * @property total_steps - Total number of steps in the workflow
 * @property completed_steps - Number of steps marked as completed
 * @property status - Overall workflow status
 * @property started_at - ISO timestamp of workflow start
 * @property updated_at - ISO timestamp of last activity
 */
export interface WorkflowSummary {
  id: string;
  template_id: string;
  title: string;
  domain: string;
  current_step: number;
  total_steps: number;
  completed_steps: number;
  status: string;
  started_at: string;
  updated_at: string;
}
