"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import WorkflowWizard from "@/components/WorkflowWizard";

interface WorkflowTemplate {
  id: string;
  title: string;
  description: string;
  domain: string;
  estimated_time: string;
  steps: WorkflowStep[];
}

interface WorkflowStep {
  id: string;
  title: string;
  explanation: string;
  required_documents: string[];
  tips: string[];
  deadlines: string[];
  status: string;
}

interface ActiveWorkflow {
  id: string;
  template_id: string;
  title: string;
  domain: string;
  current_step: number;
  total_steps: number;
  completed_steps: number;
  status: string;
}

/**
 * Guided legal workflows page with template browsing and active workflow management.
 *
 * Displays available workflow templates (e.g., "Recover Security Deposit") and
 * the user's active workflows with progress bars. Starting a workflow or clicking
 * an active one opens the WorkflowWizard for step-by-step guidance.
 */
export default function WorkflowsPage() {
  const { user, loading: authLoading } = useAuth();
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [activeWorkflows, setActiveWorkflows] = useState<ActiveWorkflow[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<{ id: string; steps: WorkflowStep[]; title: string; currentStep: number } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading || !user) return;
    async function load() {
      try {
        const [t, a] = await Promise.all([
          api.getWorkflowTemplates(),
          api.getActiveWorkflows(),
        ]);
        setTemplates(t);
        setActiveWorkflows(a);
      } catch {
        // silent
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [user, authLoading]);

  async function handleStartWorkflow(templateId: string) {
    setLoading(true);
    try {
      const instance = await api.startWorkflow(templateId);
      setSelectedWorkflow({
        id: instance.id,
        steps: instance.steps,
        title: instance.title,
        currentStep: instance.current_step,
      });
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }

  async function handleLoadWorkflow(workflowId: string) {
    setLoading(true);
    try {
      const instance = await api.getWorkflow(workflowId);
      setSelectedWorkflow({
        id: instance.id,
        steps: instance.steps,
        title: instance.title,
        currentStep: instance.current_step,
      });
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }

  if (authLoading || loading) {
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
            Back to workflows
          </button>
          <WorkflowWizard
            workflowId={selectedWorkflow.id}
            title={selectedWorkflow.title}
            steps={selectedWorkflow.steps}
            initialStep={selectedWorkflow.currentStep}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-2">Guided Workflows</h1>
        <p className="text-gray-400 mb-8">Step-by-step guides for common legal processes</p>

        {/* Active Workflows */}
        {activeWorkflows.length > 0 && (
          <div className="mb-10">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Your Active Workflows</h2>
            <div className="space-y-3">
              {activeWorkflows.map((w: ActiveWorkflow) => (
                <button
                  key={w.id}
                  onClick={() => handleLoadWorkflow(w.id)}
                  className="w-full text-left p-4 bg-white/[0.03] backdrop-blur-xl rounded-xl border border-blue-500/20 hover:border-blue-500/40 transition-all"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-semibold text-white">{w.title}</h3>
                    <span className="text-xs text-blue-400">
                      Step {w.current_step + 1} of {w.total_steps}
                    </span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-1.5">
                    <div
                      className="bg-gradient-to-r from-blue-600 to-violet-500 h-1.5 rounded-full transition-all"
                      style={{ width: `${(w.completed_steps / w.total_steps) * 100}%` }}
                    />
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Available Templates */}
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Available Workflows</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {templates.map((t: WorkflowTemplate) => (
            <div
              key={t.id}
              className="p-5 bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 hover:border-blue-500/30 transition-all"
            >
              <span className="text-xs text-blue-400 font-medium">
                {t.domain.replace(/_/g, " ")}
              </span>
              <h3 className="text-base font-semibold text-white mt-1 mb-1">{t.title}</h3>
              <p className="text-sm text-gray-400 mb-3">{t.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">{t.steps.length} steps · {t.estimated_time}</span>
                <button
                  onClick={() => handleStartWorkflow(t.id)}
                  className="text-xs font-medium text-blue-400 hover:text-blue-300 transition-colors"
                >
                  Start workflow →
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
