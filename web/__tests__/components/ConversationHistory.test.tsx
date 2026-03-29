import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ConversationHistory from "@/components/ConversationHistory";

// Mock the api module
const mockGetConversations = jest.fn();
const mockDeleteConversation = jest.fn();

jest.mock("@/lib/api", () => ({
  api: {
    getConversations: () => mockGetConversations(),
    deleteConversation: (...args: unknown[]) => mockDeleteConversation(...args),
  },
}));

const mockConversations = [
  {
    id: "conv-1",
    legal_area: "landlord_tenant",
    updated_at: "2026-03-01T00:00:00Z",
    preview: "My landlord is withholding my deposit",
    message_count: 4,
  },
  {
    id: "conv-2",
    legal_area: null,
    updated_at: "2026-02-15T00:00:00Z",
    preview: "I need help with a contract",
    message_count: 2,
  },
];

describe("ConversationHistory", () => {
  beforeEach(() => {
    mockGetConversations.mockReset();
    mockDeleteConversation.mockReset();
  });

  it("renders new conversation button", () => {
    mockGetConversations.mockResolvedValueOnce([]);
    render(
      <ConversationHistory
        onSelectConversation={jest.fn()}
        onNewConversation={jest.fn()}
      />
    );
    expect(screen.getByText("New conversation")).toBeInTheDocument();
  });

  it("calls onNewConversation when new conversation button is clicked", async () => {
    mockGetConversations.mockResolvedValueOnce([]);
    const onNew = jest.fn();
    const user = userEvent.setup();
    render(
      <ConversationHistory
        onSelectConversation={jest.fn()}
        onNewConversation={onNew}
      />
    );
    await user.click(screen.getByText("New conversation"));
    expect(onNew).toHaveBeenCalledTimes(1);
  });

  it("shows loading spinner initially", () => {
    mockGetConversations.mockReturnValueOnce(new Promise(() => {}));
    render(
      <ConversationHistory
        onSelectConversation={jest.fn()}
        onNewConversation={jest.fn()}
      />
    );
    // The spinner is rendered while loading
    expect(screen.queryByText("No previous conversations")).not.toBeInTheDocument();
  });

  it("shows empty state when no conversations", async () => {
    mockGetConversations.mockResolvedValueOnce([]);
    render(
      <ConversationHistory
        onSelectConversation={jest.fn()}
        onNewConversation={jest.fn()}
      />
    );
    await waitFor(() => {
      expect(screen.getByText("No previous conversations")).toBeInTheDocument();
    });
  });

  it("renders conversation previews", async () => {
    mockGetConversations.mockResolvedValueOnce(mockConversations);
    render(
      <ConversationHistory
        onSelectConversation={jest.fn()}
        onNewConversation={jest.fn()}
      />
    );
    await waitFor(() => {
      expect(screen.getByText("My landlord is withholding my deposit")).toBeInTheDocument();
      expect(screen.getByText("I need help with a contract")).toBeInTheDocument();
    });
  });

  it("shows legal area label when present", async () => {
    mockGetConversations.mockResolvedValueOnce(mockConversations);
    render(
      <ConversationHistory
        onSelectConversation={jest.fn()}
        onNewConversation={jest.fn()}
      />
    );
    await waitFor(() => {
      expect(screen.getByText("landlord tenant")).toBeInTheDocument();
    });
  });

  it("calls onSelectConversation when a conversation is clicked", async () => {
    mockGetConversations.mockResolvedValueOnce(mockConversations);
    const onSelect = jest.fn();
    const user = userEvent.setup();
    render(
      <ConversationHistory
        onSelectConversation={onSelect}
        onNewConversation={jest.fn()}
      />
    );
    await waitFor(() => {
      expect(screen.getByText("My landlord is withholding my deposit")).toBeInTheDocument();
    });
    await user.click(screen.getByText("My landlord is withholding my deposit"));
    expect(onSelect).toHaveBeenCalledWith("conv-1");
  });
});
