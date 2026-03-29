import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import WaitlistForm from "@/components/WaitlistForm";

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe("WaitlistForm", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("renders the email input and submit button", () => {
    render(<WaitlistForm />);
    expect(screen.getByPlaceholderText("Enter your email")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Join Waitlist" })).toBeInTheDocument();
  });

  it("allows typing in the email field", async () => {
    const user = userEvent.setup();
    render(<WaitlistForm />);
    const input = screen.getByPlaceholderText("Enter your email");
    await user.type(input, "sarah@example.com");
    expect(input).toHaveValue("sarah@example.com");
  });

  it("shows success message on successful submission", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const user = userEvent.setup();
    render(<WaitlistForm />);
    await user.type(screen.getByPlaceholderText("Enter your email"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Join Waitlist" }));

    await waitFor(() => {
      expect(screen.getByText(/You're on the list/)).toBeInTheDocument();
    });
  });

  it("shows error message on API error response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: "Email already registered" }),
    });

    const user = userEvent.setup();
    render(<WaitlistForm />);
    await user.type(screen.getByPlaceholderText("Enter your email"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Join Waitlist" }));

    await waitFor(() => {
      expect(screen.getByText("Email already registered")).toBeInTheDocument();
    });
  });

  it("shows generic error message on network failure", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network error"));

    const user = userEvent.setup();
    render(<WaitlistForm />);
    await user.type(screen.getByPlaceholderText("Enter your email"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Join Waitlist" }));

    await waitFor(() => {
      expect(screen.getByText("Something went wrong. Please try again.")).toBeInTheDocument();
    });
  });

  it("shows Joining... text while submitting", async () => {
    let resolvePromise: (value: unknown) => void;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    mockFetch.mockReturnValueOnce(pendingPromise);

    const user = userEvent.setup();
    render(<WaitlistForm />);
    await user.type(screen.getByPlaceholderText("Enter your email"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Join Waitlist" }));

    expect(screen.getByRole("button", { name: "Joining..." })).toBeDisabled();

    // Clean up
    resolvePromise!({ ok: true, json: () => Promise.resolve({ success: true }) });
  });
});
