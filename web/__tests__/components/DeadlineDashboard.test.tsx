import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import DeadlineDashboard from "@/components/DeadlineDashboard";

// Mock api
const mockGetDeadlines = jest.fn();
const mockCreateDeadline = jest.fn();
const mockUpdateDeadline = jest.fn();

jest.mock("@/lib/api", () => ({
  api: {
    getDeadlines: () => mockGetDeadlines(),
    createDeadline: (...args: unknown[]) => mockCreateDeadline(...args),
    updateDeadline: (...args: unknown[]) => mockUpdateDeadline(...args),
  },
}));

const futureDate = new Date();
futureDate.setDate(futureDate.getDate() + 10);
const futureDateStr = futureDate.toISOString().split("T")[0];

const pastDate = new Date();
pastDate.setDate(pastDate.getDate() - 5);
const pastDateStr = pastDate.toISOString().split("T")[0];

const mockDeadlines = [
  {
    id: "dl-1",
    title: "File small claims court form",
    date: futureDateStr,
    legal_area: "landlord_tenant",
    status: "active",
    notes: "Courthouse closes at 4pm",
  },
  {
    id: "dl-2",
    title: "Old deadline",
    date: pastDateStr,
    legal_area: null,
    status: "completed",
    notes: "",
  },
];

describe("DeadlineDashboard", () => {
  beforeEach(() => {
    mockGetDeadlines.mockReset();
    mockCreateDeadline.mockReset();
    mockUpdateDeadline.mockReset();
  });

  it("shows loading spinner initially", () => {
    mockGetDeadlines.mockReturnValueOnce(new Promise(() => {}));
    render(<DeadlineDashboard />);
    // Spinner should be visible (no empty state text yet)
    expect(screen.queryByText("No active deadlines")).not.toBeInTheDocument();
  });

  it("shows empty state when no deadlines", async () => {
    mockGetDeadlines.mockResolvedValueOnce([]);
    render(<DeadlineDashboard />);
    await waitFor(() => {
      expect(screen.getByText("No active deadlines")).toBeInTheDocument();
    });
  });

  it("renders active deadlines", async () => {
    mockGetDeadlines.mockResolvedValueOnce(mockDeadlines);
    render(<DeadlineDashboard />);
    await waitFor(() => {
      expect(screen.getByText("File small claims court form")).toBeInTheDocument();
    });
  });

  it("shows days remaining for active deadlines", async () => {
    mockGetDeadlines.mockResolvedValueOnce(mockDeadlines);
    render(<DeadlineDashboard />);
    await waitFor(() => {
      expect(screen.getByText(/days remaining/)).toBeInTheDocument();
    });
  });

  it("renders past/completed deadlines in separate section", async () => {
    mockGetDeadlines.mockResolvedValueOnce(mockDeadlines);
    render(<DeadlineDashboard />);
    await waitFor(() => {
      expect(screen.getByText("Past Deadlines")).toBeInTheDocument();
      expect(screen.getByText("Old deadline")).toBeInTheDocument();
    });
  });

  it("shows Add Deadline button", async () => {
    mockGetDeadlines.mockResolvedValueOnce([]);
    render(<DeadlineDashboard />);
    await waitFor(() => {
      expect(screen.getByText("+ Add Deadline")).toBeInTheDocument();
    });
  });

  it("toggles add deadline form", async () => {
    mockGetDeadlines.mockResolvedValueOnce([]);
    const user = userEvent.setup();
    render(<DeadlineDashboard />);
    await waitFor(() => {
      expect(screen.getByText("+ Add Deadline")).toBeInTheDocument();
    });
    await user.click(screen.getByText("+ Add Deadline"));
    expect(screen.getByPlaceholderText("Deadline title...")).toBeInTheDocument();
    expect(screen.getByText("Cancel")).toBeInTheDocument();
  });

  it("shows notes for deadlines that have them", async () => {
    mockGetDeadlines.mockResolvedValueOnce(mockDeadlines);
    render(<DeadlineDashboard />);
    await waitFor(() => {
      expect(screen.getByText("Courthouse closes at 4pm")).toBeInTheDocument();
    });
  });
});
