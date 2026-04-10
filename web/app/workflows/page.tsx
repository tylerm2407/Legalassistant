"use client";

import React, { useEffect, useState, useCallback } from "react";
import WorkflowWizard from "@/components/WorkflowWizard";
import { WORKFLOW_TEMPLATES } from "@/lib/workflow-templates";
import { useTranslation } from "@/lib/i18n";
import type { WorkflowStep } from "@/lib/shared-types/workflows";
import { ArrowLeft, X, CheckCircle, ArrowRight } from "@phosphor-icons/react";

/** Persisted workflow instance stored in localStorage. */
interface SavedWorkflow {
  id: string;
  template_id: string;
  title: string;
  domain: string;
  steps: WorkflowStep[];
  current_step: number;
  status: string;
  started_at: string;
  updated_at: string;
}

const STORAGE_KEY = "casemate_workflows";

/** Load saved workflows from localStorage. */
function loadWorkflows(): SavedWorkflow[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

/** Save workflows to localStorage. */
function saveWorkflows(workflows: SavedWorkflow[]): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(workflows));
}

/**
 * Guided legal workflows page with template browsing and active workflow management.
 *
 * Templates are embedded client-side so the feature works without a backend.
 * User progress is persisted to localStorage and restored on return visits.
 */
export default function WorkflowsPage() {
  const { t } = useTranslation();
  const [activeWorkflows, setActiveWorkflows] = useState<SavedWorkflow[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<SavedWorkflow | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setActiveWorkflows(loadWorkflows());
    setLoaded(true);
  }, []);

  /** Start a new workflow from a template. */
  const handleStartWorkflow = useCallback((templateId: string) => {
    const template = WORKFLOW_TEMPLATES.find((t) => t.id === templateId);
    if (!template) return;

    const now = new Date().toISOString();
    const newWorkflow: SavedWorkflow = {
      id: `${templateId}_${Date.now()}`,
      template_id: templateId,
      title: template.title,
      domain: template.domain,
      steps: template.steps.map((s, i) => ({
        ...s,
        status: i === 0 ? "in_progress" : "not_started",
      })),
      current_step: 0,
      status: "in_progress",
      started_at: now,
      updated_at: now,
    };

    const updated = [newWorkflow, ...loadWorkflows()];
    saveWorkflows(updated);
    setActiveWorkflows(updated);
    setSelectedWorkflow(newWorkflow);
  }, []);

  /** Resume an existing workflow. */
  const handleLoadWorkflow = useCallback((workflowId: string) => {
    const workflows = loadWorkflows();
    const found = workflows.find((w) => w.id === workflowId);
    if (found) setSelectedWorkflow(found);
  }, []);

  /** Called by the wizard when a step is completed. Updates localStorage. */
  const handleStepComplete = useCallback((workflowId: string, stepIndex: number) => {
    const workflows = loadWorkflows();
    const wf = workflows.find((w) => w.id === workflowId);
    if (!wf) return;

    wf.steps[stepIndex].status = "completed";
    if (stepIndex + 1 < wf.steps.length) {
      wf.steps[stepIndex + 1].status = "in_progress";
      wf.current_step = stepIndex + 1;
    } else {
      wf.status = "completed";
    }
    wf.updated_at = new Date().toISOString();

    saveWorkflows(workflows);
    setActiveWorkflows([...workflows]);
    setSelectedWorkflow({ ...wf });
  }, []);

  /** Delete a workflow from localStorage. */
  const handleDeleteWorkflow = useCallback((workflowId: string) => {
    const workflows = loadWorkflows().filter((w) => w.id !== workflowId);
    saveWorkflows(workflows);
    setActiveWorkflows(workflows);
  }, []);

  if (!loaded) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <p className="font-sans text-ink-secondary">Loading…</p>
      </div>
    );
  }

  if (selectedWorkflow) {
    return (
      <div className="min-h-screen bg-bg">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <button
            onClick={() => setSelectedWorkflow(null)}
            className="font-sans text-sm text-ink-secondary hover:text-ink-primary mb-8 flex items-center gap-2 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" weight="regular" />
            {t("backToWorkflows")}
          </button>
          <WorkflowWizard
            workflowId={selectedWorkflow.id}
            title={selectedWorkflow.title}
            steps={selectedWorkflow.steps}
            initialStep={selectedWorkflow.current_step}
            onStepComplete={handleStepComplete}
          />
        </div>
      </div>
    );
  }

  const inProgressWorkflows = activeWorkflows.filter((w) => w.status === "in_progress");
  const completedWorkflows = activeWorkflows.filter((w) => w.status === "completed");

  return (
    <div className="min-h-screen bg-bg">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-12 max-w-[65ch]">
          <h1 className="font-serif text-5xl md:text-6xl font-medium tracking-tight leading-tight text-ink-primary">
            Step by step
          </h1>
          <p className="font-sans text-base text-ink-secondary mt-4">
            Pick a situation and we'll walk you through exactly what to do,
            one step at a time. No legalese. No guessing.
          </p>
        </div>

        {/* Active Workflows */}
        {inProgressWorkflows.length > 0 && (
          <div className="mb-12">
            <h2 className="font-sans text-sm font-medium text-ink-tertiary uppercase tracking-wider mb-4">
              In progress
            </h2>
            <div className="space-y-3">
              {inProgressWorkflows.map((w) => {
                const completedSteps = w.steps.filter((s) => s.status === "completed").length;
                return (
                  <div
                    key={w.id}
                    className="flex items-center gap-4 bg-white border border-border rounded-lg p-6 hover:border-border-strong transition-colors"
                  >
                    <button
                      onClick={() => handleLoadWorkflow(w.id)}
                      className="flex-1 text-left"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-serif text-2xl font-medium tracking-tight text-ink-primary">
                          {w.title}
                        </h3>
                        <span className="font-sans text-sm text-ink-secondary shrink-0 ml-4">
                          Step {w.current_step + 1} of {w.steps.length}
                        </span>
                      </div>
                      <div className="w-full bg-bg-hover rounded-md h-1.5 overflow-hidden">
                        <div
                          className="bg-accent h-1.5 transition-all"
                          style={{ width: `${(completedSteps / w.steps.length) * 100}%` }}
                        />
                      </div>
                    </button>
                    <button
                      onClick={() => handleDeleteWorkflow(w.id)}
                      className="text-ink-tertiary hover:text-warning transition-colors p-2"
                      title="Remove"
                    >
                      <X className="w-4 h-4" weight="regular" />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Completed Workflows */}
        {completedWorkflows.length > 0 && (
          <div className="mb-12">
            <h2 className="font-sans text-sm font-medium text-ink-tertiary uppercase tracking-wider mb-4">
              Completed
            </h2>
            <div className="space-y-3">
              {completedWorkflows.map((w) => (
                <div
                  key={w.id}
                  className="flex items-center gap-4 bg-white border border-border rounded-lg p-6"
                >
                  <button
                    onClick={() => handleLoadWorkflow(w.id)}
                    className="flex-1 text-left flex items-center gap-3"
                  >
                    <CheckCircle className="w-5 h-5 text-accent shrink-0" weight="regular" />
                    <h3 className="font-serif text-xl font-medium tracking-tight text-ink-primary">
                      {w.title}
                    </h3>
                  </button>
                  <button
                    onClick={() => handleDeleteWorkflow(w.id)}
                    className="text-ink-tertiary hover:text-warning transition-colors p-2"
                    title="Remove"
                  >
                    <X className="w-4 h-4" weight="regular" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Available Templates */}
        <h2 className="font-sans text-sm font-medium text-ink-tertiary uppercase tracking-wider mb-4">
          Available guides
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {WORKFLOW_TEMPLATES.map((tmpl) => (
            <div
              key={tmpl.id}
              className="bg-white border border-border rounded-lg p-6 hover:border-border-strong transition-colors flex flex-col"
            >
              <span className="font-sans text-xs font-medium text-accent uppercase tracking-wider mb-2">
                {tmpl.domain.replace(/_/g, " ")}
              </span>
              <h3 className="font-serif text-2xl font-medium tracking-tight text-ink-primary mb-2">
                {tmpl.title}
              </h3>
              <p className="font-sans text-base text-ink-secondary mb-6 flex-1 max-w-[65ch]">
                {tmpl.description}
              </p>
              <div className="flex items-center justify-between pt-4 border-t border-border">
                <span className="font-sans text-sm text-ink-tertiary">
                  {tmpl.steps.length} steps · {tmpl.estimated_time}
                </span>
                <button
                  onClick={() => handleStartWorkflow(tmpl.id)}
                  className="font-sans text-sm font-medium text-accent hover:text-accent-hover transition-colors flex items-center gap-1.5"
                >
                  Start
                  <ArrowRight className="w-4 h-4" weight="regular" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
