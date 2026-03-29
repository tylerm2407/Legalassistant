import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import WorkflowWizard from "@/components/WorkflowWizard";

// Mock api
const mockUpdateWorkflowStep = jest.fn();

jest.mock("@/lib/api", () => ({
  api: {
    updateWorkflowStep: (...args: unknown[]) => mockUpdateWorkflowStep(...args),
  },
}));

const mockSteps = [
  {
    id: "step-1",
    title: "Gather Documentation",
    explanation: "Collect all relevant documents for your case.",
    required_documents: ["Lease agreement", "Move-in photos"],
    tips: ["Take photos of all damage"],
    deadlines: ["30 days after move-out"],
    status: "in_progress",
  },
  {
    id: "step-2",
    title: "Send Demand Letter",
    explanation: "Send a formal demand to your landlord.",
    required_documents: [],
    tips: ["Send via certified mail"],
    deadlines: [],
    status: "pending",
  },
  {
    id: "step-3",
    title: "File in Court",
    explanation: "If no response, file in small claims court.",
    required_documents: ["Filed demand letter copy"],
    tips: [],
    deadlines: ["6 months from move-out"],
    status: "pending",
  },
];

describe("WorkflowWizard", () => {
  beforeEach(() => {
    mockUpdateWorkflowStep.mockReset();
    mockUpdateWorkflowStep.mockResolvedValue({});
  });

  it("renders the workflow title", () => {
    render(<WorkflowWizard workflowId="wf-1" title="Recover Security Deposit" steps={mockSteps} initialStep={0} />);
    expect(screen.getByText("Recover Security Deposit")).toBeInTheDocument();
  });

  it("shows current step number", () => {
    render(<WorkflowWizard workflowId="wf-1" title="Test" steps={mockSteps} initialStep={0} />);
    expect(screen.getByText("Step 1 of 3")).toBeInTheDocument();
  });

  it("renders the current step title and explanation", () => {
    render(<WorkflowWizard workflowId="wf-1" title="Test" steps={mockSteps} initialStep={0} />);
    expect(screen.getByText("Gather Documentation")).toBeInTheDocument();
    expect(screen.getByText("Collect all relevant documents for your case.")).toBeInTheDocument();
  });

  it("renders required documents list", () => {
    render(<WorkflowWizard workflowId="wf-1" title="Test" steps={mockSteps} initialStep={0} />);
    expect(screen.getByText("Lease agreement")).toBeInTheDocument();
    expect(screen.getByText("Move-in photos")).toBeInTheDocument();
  });

  it("renders tips", () => {
    render(<WorkflowWizard workflowId="wf-1" title="Test" steps={mockSteps} initialStep={0} />);
    expect(screen.getByText("Take photos of all damage")).toBeInTheDocument();
  });

  it("renders deadlines", () => {
    render(<WorkflowWizard workflowId="wf-1" title="Test" steps={mockSteps} initialStep={0} />);
    expect(screen.getByText("30 days after move-out")).toBeInTheDocument();
  });

  it("navigates to next step", async () => {
    const user = userEvent.setup();
    render(<WorkflowWizard workflowId="wf-1" title="Test" steps={mockSteps} initialStep={0} />);
    await user.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByText("Send Demand Letter")).toBeInTheDocument();
    expect(screen.getByText("Step 2 of 3")).toBeInTheDocument();
  });

  it("navigates to previous step", async () => {
    const user = userEvent.setup();
    render(<WorkflowWizard workflowId="wf-1" title="Test" steps={mockSteps} initialStep={1} />);
    await user.click(screen.getByRole("button", { name: "Previous" }));
    expect(screen.getByText("Gather Documentation")).toBeInTheDocument();
  });

  it("disables Previous button on first step", () => {
    render(<WorkflowWizard workflowId="wf-1" title="Test" steps={mockSteps} initialStep={0} />);
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
  });

  it("hides Next button on last step", () => {
    render(<WorkflowWizard workflowId="wf-1" title="Test" steps={mockSteps} initialStep={2} />);
    expect(screen.queryByRole("button", { name: "Next" })).not.toBeInTheDocument();
  });

  it("calls API when Mark Complete is clicked", async () => {
    const user = userEvent.setup();
    render(<WorkflowWizard workflowId="wf-1" title="Test" steps={mockSteps} initialStep={0} />);
    await user.click(screen.getByRole("button", { name: "Mark Complete" }));
    await waitFor(() => {
      expect(mockUpdateWorkflowStep).toHaveBeenCalledWith("wf-1", 0, "completed");
    });
  });
});
