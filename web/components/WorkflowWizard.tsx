"use client";

import React, { useState } from "react";
import Card from "./ui/Card";
import Button from "./ui/Button";
import { api } from "@/lib/api";

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
 * @property workflowId - Unique identifier for this workflow instance in Supabase
 * @property title - Display title for the workflow (e.g., "Security Deposit Recovery")
 * @property steps - Array of workflow steps with instructions, documents, tips, and deadlines
 * @property initialStep - Zero-based index of the step to display initially
 */
interface WorkflowWizardProps {
  workflowId: string;
  title: string;
  steps: WorkflowStep[];
  initialStep: number;
}

/**
 * Step-by-step guided workflow wizard for common legal processes.
 *
 * Walks users through multi-step legal procedures (e.g., filing small claims,
 * recovering a security deposit) with detailed instructions, required documents,
 * tips, and deadlines for each step. Progress is persisted to Supabase so users
 * can resume where they left off.
 *
 * @param props - Component props
 * @param props.workflowId - Workflow instance ID for persisting step progress
 * @param props.title - Workflow title displayed at the top
 * @param props.steps - Ordered array of workflow steps
 * @param props.initialStep - Step index to start from (supports resuming)
 */
export default function WorkflowWizard({ workflowId, title, steps, initialStep }: WorkflowWizardProps) {
  const [currentStep, setCurrentStep] = useState(initialStep);
  const [stepStatuses, setStepStatuses] = useState<string[]>(steps.map((s: WorkflowStep) => s.status));
  const [updating, setUpdating] = useState(false);

  const step = steps[currentStep];

  async function completeStep() {
    setUpdating(true);
    try {
      await api.updateWorkflowStep(workflowId, currentStep, "completed");
      const newStatuses = [...stepStatuses];
      newStatuses[currentStep] = "completed";
      if (currentStep + 1 < steps.length) {
        newStatuses[currentStep + 1] = "in_progress";
      }
      setStepStatuses(newStatuses);
      if (currentStep + 1 < steps.length) {
        setCurrentStep(currentStep + 1);
      }
    } catch {
      // silent
    } finally {
      setUpdating(false);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-white">{title}</h1>

      {/* Step progress */}
      <div className="flex items-center gap-1">
        {steps.map((s: WorkflowStep, i: number) => (
          <button
            key={s.id}
            onClick={() => setCurrentStep(i)}
            className={`flex-1 h-2 rounded-full transition-all ${
              stepStatuses[i] === "completed"
                ? "bg-green-500"
                : i === currentStep
                ? "bg-blue-500"
                : "bg-white/10"
            }`}
          />
        ))}
      </div>
      <p className="text-xs text-gray-500">
        Step {currentStep + 1} of {steps.length}
      </p>

      {/* Current step */}
      <Card>
        <Card.Header>
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white">{step.title}</h2>
            {stepStatuses[currentStep] === "completed" && (
              <span className="text-xs text-green-400 bg-green-500/10 px-2 py-0.5 rounded-full">
                Completed
              </span>
            )}
          </div>
        </Card.Header>
        <Card.Body>
          <div className="space-y-5">
            <p className="text-sm text-gray-300 leading-relaxed">{step.explanation}</p>

            {step.required_documents.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Required Documents</h3>
                <ul className="space-y-1">
                  {step.required_documents.map((doc: string, i: number) => (
                    <li key={i} className="text-sm text-gray-300 flex gap-2">
                      <svg className="w-4 h-4 text-gray-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                      </svg>
                      {doc}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {step.tips.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Tips</h3>
                <ul className="space-y-1">
                  {step.tips.map((tip: string, i: number) => (
                    <li key={i} className="text-sm text-blue-300 flex gap-2">
                      <span className="text-blue-400 shrink-0">&#x2022;</span>
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {step.deadlines.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-yellow-400 uppercase tracking-wider mb-2">Deadlines</h3>
                <ul className="space-y-1">
                  {step.deadlines.map((deadline: string, i: number) => (
                    <li key={i} className="text-sm text-yellow-400 flex gap-2">
                      <svg className="w-4 h-4 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {deadline}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Card.Body>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
          disabled={currentStep === 0}
        >
          Previous
        </Button>
        <div className="flex gap-2">
          {stepStatuses[currentStep] !== "completed" && (
            <Button
              size="sm"
              onClick={completeStep}
              disabled={updating}
            >
              {updating ? "Saving..." : "Mark Complete"}
            </Button>
          )}
          {currentStep < steps.length - 1 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentStep(currentStep + 1)}
            >
              Next
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
