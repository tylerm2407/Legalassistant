export interface RightsGuide {
  id: string;
  domain: string;
  title: string;
  description: string;
  explanation: string;
  your_rights: string[];
  action_steps: string[];
  deadlines: string[];
  common_mistakes: string[];
  when_to_get_a_lawyer: string;
}

export interface RightsDomain {
  domain: string;
  label: string;
  guide_count: number;
}
