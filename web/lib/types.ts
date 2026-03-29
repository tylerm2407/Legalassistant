/**
 * Central type barrel file for the CaseMate frontend.
 *
 * Re-exports all shared types from domain-specific modules. Import types
 * from "@/lib/types" rather than from individual shared-types files.
 */

export type {
  LegalProfile,
  LegalIssue,
  IssueStatus,
} from "./shared-types/legal-profile";

export type { Message, ChatResponse, ConversationSummary, ConversationDetail } from "./shared-types/conversation";

export type {
  DemandLetter,
  RightsSummary,
  Checklist,
} from "./shared-types/actions";

export type { Deadline, DeadlineCreateRequest, DeadlineUpdateRequest } from "./shared-types/deadlines";

export type { RightsGuide, RightsDomain } from "./shared-types/rights";

export type { WorkflowStep, WorkflowTemplate, WorkflowInstance, WorkflowSummary } from "./shared-types/workflows";

export type { Attorney, ReferralSuggestion } from "./shared-types/referrals";
