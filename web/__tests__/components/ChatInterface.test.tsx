import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ChatInterface from "@/components/ChatInterface";
import type { LegalProfile } from "@/lib/types";

// Mock child components to isolate ChatInterface
jest.mock("@/components/LegalProfileSidebar", () => {
  return function MockSidebar({ profile }: { profile: { display_name: string } }) {
    return <div data-testid="profile-sidebar">{profile.display_name}</div>;
  };
});

jest.mock("@/components/ConversationHistory", () => {
  return function MockHistory() {
    return <div data-testid="conversation-history">History</div>;
  };
});

jest.mock("@/components/ActionGenerator", () => {
  return function MockActions() {
    return <div data-testid="action-generator">Actions</div>;
  };
});

// Mock the api module
const mockChat = jest.fn();
jest.mock("@/lib/api", () => ({
  api: {
    chat: (...args: unknown[]) => mockChat(...args),
    getConversation: jest.fn(),
  },
}));

const mockProfile: LegalProfile = {
  user_id: "user-123",
  display_name: "Sarah Chen",
  state: "Massachusetts",
  housing_situation: "Renter",
  employment_type: "W-2 Employee",
  family_status: "Single",
  active_issues: [],
  legal_facts: [],
  documents: [],
  member_since: "2026-01-15T00:00:00Z",
  conversation_count: 5,
};

describe("ChatInterface", () => {
  beforeEach(() => {
    mockChat.mockReset();
  });

  it("renders the welcome message with user name and state", () => {
    render(<ChatInterface profile={mockProfile} />);
    expect(screen.getByText(/Hi Sarah Chen/)).toBeInTheDocument();
    expect(screen.getByText(/Massachusetts/)).toBeInTheDocument();
  });

  it("renders the CaseMate header", () => {
    render(<ChatInterface profile={mockProfile} />);
    expect(screen.getByText("CaseMate")).toBeInTheDocument();
    expect(screen.getByText("AI Legal Assistant")).toBeInTheDocument();
  });

  it("renders the message input textarea", () => {
    render(<ChatInterface profile={mockProfile} />);
    expect(screen.getByPlaceholderText("Describe your legal question...")).toBeInTheDocument();
  });

  it("renders the Send button", () => {
    render(<ChatInterface profile={mockProfile} />);
    expect(screen.getByRole("button", { name: "Send" })).toBeInTheDocument();
  });

  it("disables Send button when input is empty", () => {
    render(<ChatInterface profile={mockProfile} />);
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
  });

  it("enables Send button when input has text", async () => {
    const user = userEvent.setup();
    render(<ChatInterface profile={mockProfile} />);
    await user.type(screen.getByPlaceholderText("Describe your legal question..."), "My landlord");
    expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
  });

  it("renders the profile sidebar", () => {
    render(<ChatInterface profile={mockProfile} />);
    expect(screen.getByTestId("profile-sidebar")).toBeInTheDocument();
  });

  it("renders conversation history panel", () => {
    render(<ChatInterface profile={mockProfile} />);
    expect(screen.getByTestId("conversation-history")).toBeInTheDocument();
  });

  it("renders navigation links", () => {
    render(<ChatInterface profile={mockProfile} />);
    expect(screen.getByText("Rights")).toBeInTheDocument();
    expect(screen.getByText("Workflows")).toBeInTheDocument();
    expect(screen.getByText("Deadlines")).toBeInTheDocument();
    expect(screen.getByText("Attorneys")).toBeInTheDocument();
  });

  it("shows disclaimer text", () => {
    render(<ChatInterface profile={mockProfile} />);
    expect(screen.getByText(/AI assistant — not legal advice/)).toBeInTheDocument();
  });
});
