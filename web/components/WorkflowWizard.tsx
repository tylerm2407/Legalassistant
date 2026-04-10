"use client";

import React, { useState } from "react";
import Button from "./ui/Button";
import { useTranslation } from "@/lib/i18n";
import { api } from "@/lib/api";
import {
  FileText,
  Clock,
  CheckCircle,
  Lightbulb,
} from "@phosphor-icons/react";

/**
 * A single step within a guided legal workflow.
 *
 * @property id - Unique step identifier
 * @property title - Display title for the step (e.g., "Gather Evidence")
 * @property explanation - Detailed instructions for completing this step
 * @property required_documents - List of documents needed for this step
 * @property tips - Helpful tips for completing the step successfully
 * @property deadlines - Time-sensitive deadlines associated with this step
 * @property status - Current completion status of the step
 */
interface WorkflowStep {
  id: string;
  title: string;
  explanation: string;
  required_documents: string[];
  tips: string[];
  deadlines: string[];
  status: string;
}

/**
 * Props for the WorkflowWizard component.
 *
 * @property workflowId - Unique identifier for this workflow instance
 * @property title - Display title for the workflow (e.g., "Security Deposit Recovery")
 * @property steps - Array of workflow steps with instructions, documents, tips, and deadlines
 * @property initialStep - Zero-based index of the step to display initially
 * @property onStepComplete - Callback fired when a step is marked complete
 */
interface WorkflowWizardProps {
  workflowId: string;
  title: string;
  steps: WorkflowStep[];
  initialStep: number;
  onStepComplete?: (workflowId: string, stepIndex: number) => void;
}

/**
 * Step-by-step guided workflow wizard for common legal processes.
 *
 * Walks users through multi-step legal procedures (e.g., filing small claims,
 * recovering a security deposit) with detailed instructions, required documents,
 * tips, and deadlines for each step. Progress is persisted via the onStepComplete
 * callback which writes to localStorage.
 *
 * @param props - Component props
 * @param props.workflowId - Workflow instance ID
 * @param props.title - Workflow title displayed at the top
 * @param props.steps - Ordered array of workflow steps
 * @param props.initialStep - Step index to start from (supports resuming)
 * @param props.onStepComplete - Callback to persist step completion
 */
export default function WorkflowWizard({
  workflowId,
  title,
  steps,
  initialStep,
  onStepComplete,
}: WorkflowWizardProps) {
  const [currentStep, setCurrentStep] = useState(initialStep);
  const [stepStatuses, setStepStatuses] = useState<string[]>(
    steps.map((s: WorkflowStep) => s.status)
  );
  const { t } = useTranslation();

  const step = steps[currentStep];
  const allComplete = stepStatuses.every((s) => s === "completed");

  function completeStep() {
    const newStatuses = [...stepStatuses];
    newStatuses[currentStep] = "completed";
    if (currentStep + 1 < steps.length) {
      newStatuses[currentStep + 1] = "in_progress";
    }
    setStepStatuses(newStatuses);
    api.updateWorkflowStep(workflowId, currentStep, "completed");
    if (onStepComplete) {
      onStepComplete(workflowId, currentStep);
    }
    if (currentStep + 1 < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Title */}
      <header className="space-y-3">
        <h1 className="font-serif font-medium tracking-tight leading-tight text-3xl md:text-4xl text-ink-primary">
          {title}
        </h1>
        <p className="text-sm font-sans text-ink-tertiary">
          {t("step")} {currentStep + 1} {t("of")} {steps.length}
        </p>
      </header>

      {/* Step progress */}
      <div className="flex items-center gap-2">
        {steps.map((s: WorkflowStep, i: number) => (
          <button
            key={s.id}
            onClick={() => setCurrentStep(i)}
            className={`flex-1 h-1 rounded-sm transition-colors ${
              stepStatuses[i] === "completed"
                ? "bg-accent"
                : i === currentStep
                ? "bg-accent"
                : "bg-border"
            }`}
            aria-label={`${t("step")} ${i + 1}`}
          />
        ))}
      </div>

      {/* All complete banner */}
      {allComplete && (
        <div className="bg-accent-subtle border border-accent/30 rounded-lg p-6 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-accent shrink-0 mt-0.5" weight="regular" />
          <p className="font-sans text-sm text-ink-primary">
            You&apos;ve finished every step. You can revisit any step by clicking the progress bar above.
          </p>
        </div>
      )}

      {/* Current step */}
      <section className="bg-white border border-border rounded-lg p-8">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-serif font-medium tracking-tight text-2xl text-ink-primary">
            {step.title}
          </h2>
          {stepStatuses[currentStep] === "completed" && (
            <span className="inline-flex items-center gap-1.5 text-xs font-sans font-medium text-accent bg-accent-subtle border border-accent/20 px-2.5 py-1 rounded-md">
              <CheckCircle className="w-3.5 h-3.5" weight="regular" />
              {t("completed")}
            </span>
          )}
        </div>

        <div className="space-y-8">
          <p className="font-sans text-base text-ink-secondary leading-relaxed max-w-[65ch]">
            {step.explanation}
          </p>

          {step.required_documents.length > 0 && (
            <div>
              <h3 className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-3">
                {t("requiredDocuments")}
              </h3>
              <ul className="space-y-2">
                {step.required_documents.map((doc: string, i: number) => (
                  <li
                    key={i}
                    className="font-sans text-sm text-ink-secondary flex gap-2"
                  >
                    <FileText
                      className="w-4 h-4 text-ink-tertiary shrink-0 mt-0.5"
                      weight="regular"
                    />
                    {doc}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {step.tips.length > 0 && (
            <div>
              <h3 className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-3">
                {t("tips")}
              </h3>
              <ul className="space-y-2">
                {step.tips.map((tip: string, i: number) => (
                  <li
                    key={i}
                    className="font-sans text-sm text-ink-secondary flex gap-2"
                  >
                    <Lightbulb
                      className="w-4 h-4 text-accent shrink-0 mt-0.5"
                      weight="regular"
                    />
                    {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {step.deadlines.length > 0 && (
            <div className="bg-warning-subtle border border-warning/30 rounded-md p-4">
              <h3 className="text-xs font-sans font-medium text-warning uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" weight="regular" />
                {t("deadlines")}
              </h3>
              <ul className="space-y-2">
                {step.deadlines.map((deadline: string, i: number) => (
                  <li
                    key={i}
                    className="font-sans text-sm text-warning flex gap-2"
                  >
                    <span className="shrink-0">•</span>
                    {deadline}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
          disabled={currentStep === 0}
        >
          {t("previous")}
        </Button>
        <div className="flex gap-2">
          {stepStatuses[currentStep] !== "completed" && (
            <Button size="sm" onClick={completeStep}>
              {t("markCompleteBtn")}
            </Button>
          )}
          {currentStep < steps.length - 1 && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setCurrentStep(currentStep + 1)}
            >
              {t("next")}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
