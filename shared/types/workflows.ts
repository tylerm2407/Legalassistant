export interface WorkflowStep {
  id: string;
  title: string;
  explanation: string;
  required_documents: string[];
  tips: string[];
  deadlines: string[];
  status: "not_started" | "in_progress" | "completed" | "skipped";
}

export interface WorkflowTemplate {
  id: string;
  title: string;
  description: string;
  domain: string;
  estimated_time: string;
  steps: WorkflowStep[];
}

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
