"use client";

import React, { useEffect, useState, useCallback } from "react";
import WorkflowWizard from "@/components/WorkflowWizard";
import { WORKFLOW_TEMPLATES } from "@/lib/workflow-templates";
import { useTranslation } from "@/lib/i18n";
import type { WorkflowStep } from "@/lib/shared-types/workflows";

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
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (selectedWorkflow) {
    return (
      <div className="min-h-screen bg-[#050505] p-6">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => setSelectedWorkflow(null)}
            className="text-sm text-gray-400 hover:text-white mb-6 flex items-center gap-1.5 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
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
    <div className="min-h-screen bg-[#050505] p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-2">{t("guidedWorkflows")}</h1>
        <p className="text-gray-400 mb-8">{t("workflowsDescription")}</p>

        {/* Active Workflows */}
        {inProgressWorkflows.length > 0 && (
          <div className="mb-10">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
              {t("yourActiveWorkflows")}
            </h2>
            <div className="space-y-3">
              {inProgressWorkflows.map((w) => {
                const completedSteps = w.steps.filter((s) => s.status === "completed").length;
                return (
                  <div
                    key={w.id}
                    className="flex items-center gap-3 p-4 bg-white/[0.03] backdrop-blur-xl rounded-xl border border-blue-500/20 hover:border-blue-500/40 transition-all"
                  >
                    <button
                      onClick={() => handleLoadWorkflow(w.id)}
                      className="flex-1 text-left"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-semibold text-white">{w.title}</h3>
                        <span className="text-xs text-blue-400">
                          {t("step")} {w.current_step + 1} {t("of")} {w.steps.length}
                        </span>
                      </div>
                      <div className="w-full bg-white/10 rounded-full h-1.5">
                        <div
                          className="bg-gradient-to-r from-blue-600 to-violet-500 h-1.5 rounded-full transition-all"
                          style={{ width: `${(completedSteps / w.steps.length) * 100}%` }}
                        />
                      </div>
                    </button>
                    <button
                      onClick={() => handleDeleteWorkflow(w.id)}
                      className="text-gray-600 hover:text-red-400 transition-colors p-1"
                      title="Delete workflow"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Completed Workflows */}
        {completedWorkflows.length > 0 && (
          <div className="mb-10">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
              {t("completed")}
            </h2>
            <div className="space-y-3">
              {completedWorkflows.map((w) => (
                <div
                  key={w.id}
                  className="flex items-center gap-3 p-4 bg-white/[0.03] backdrop-blur-xl rounded-xl border border-green-500/20"
                >
                  <button
                    onClick={() => handleLoadWorkflow(w.id)}
                    className="flex-1 text-left"
                  >
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-white">{w.title}</h3>
                      <span className="text-xs text-green-400 bg-green-500/10 px-2 py-0.5 rounded-full">
                        {t("completed")}
                      </span>
                    </div>
                  </button>
                  <button
                    onClick={() => handleDeleteWorkflow(w.id)}
                    className="text-gray-600 hover:text-red-400 transition-colors p-1"
                    title="Delete workflow"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Available Templates */}
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
          {t("availableWorkflows")}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {WORKFLOW_TEMPLATES.map((tmpl) => (
            <div
              key={tmpl.id}
              className="p-5 bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 hover:border-blue-500/30 transition-all"
            >
              <span className="text-xs text-blue-400 font-medium">
                {tmpl.domain.replace(/_/g, " ")}
              </span>
              <h3 className="text-base font-semibold text-white mt-1 mb-1">{tmpl.title}</h3>
              <p className="text-sm text-gray-400 mb-3">{tmpl.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {tmpl.steps.length} {t("steps")} · {tmpl.estimated_time}
                </span>
                <button
                  onClick={() => handleStartWorkflow(tmpl.id)}
                  className="text-xs font-medium text-blue-400 hover:text-blue-300 transition-colors"
                >
                  {t("startWorkflow")}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
