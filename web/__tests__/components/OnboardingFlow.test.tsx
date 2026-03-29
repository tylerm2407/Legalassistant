import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";
import OnboardingFlow from "@/components/OnboardingFlow";

// Mock next/navigation
const mockPush = jest.fn();
jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

// Mock auth
jest.mock("@/lib/auth", () => ({
  useAuth: () => ({ user: { id: "user-123" } }),
}));

// Mock api
const mockCreateProfile = jest.fn();
jest.mock("@/lib/api", () => ({
  api: {
    createProfile: (...args: unknown[]) => mockCreateProfile(...args),
  },
}));

describe("OnboardingFlow", () => {
  beforeEach(() => {
    mockPush.mockReset();
    mockCreateProfile.mockReset();
    mockCreateProfile.mockResolvedValue({});
  });

  it("renders step 1 with name and state fields", () => {
    render(<OnboardingFlow />);
    expect(screen.getByText("Let's get to know you")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("e.g. Sarah Chen")).toBeInTheDocument();
    expect(screen.getByText("Select your state")).toBeInTheDocument();
  });

  it("shows step progress indicator", () => {
    render(<OnboardingFlow />);
    expect(screen.getByText("Step 1 of 5")).toBeInTheDocument();
    expect(screen.getByText("20%")).toBeInTheDocument();
  });

  it("disables Next button when required fields are empty", () => {
    render(<OnboardingFlow />);
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  });

  it("enables Next button after filling name and state", async () => {
    const user = userEvent.setup();
    render(<OnboardingFlow />);
    await user.type(screen.getByPlaceholderText("e.g. Sarah Chen"), "Sarah");
    await user.selectOptions(screen.getByRole("combobox"), "Massachusetts");
    expect(screen.getByRole("button", { name: "Next" })).not.toBeDisabled();
  });

  it("advances to step 2 when Next is clicked", async () => {
    const user = userEvent.setup();
    render(<OnboardingFlow />);
    await user.type(screen.getByPlaceholderText("e.g. Sarah Chen"), "Sarah");
    await user.selectOptions(screen.getByRole("combobox"), "Massachusetts");
    await user.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByText("Housing Situation")).toBeInTheDocument();
    expect(screen.getByText("Step 2 of 5")).toBeInTheDocument();
  });

  it("allows going back to previous step", async () => {
    const user = userEvent.setup();
    render(<OnboardingFlow />);
    await user.type(screen.getByPlaceholderText("e.g. Sarah Chen"), "Sarah");
    await user.selectOptions(screen.getByRole("combobox"), "Massachusetts");
    await user.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByText("Housing Situation")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Back" }));
    expect(screen.getByText("Let's get to know you")).toBeInTheDocument();
  });

  it("disables Back button on step 1", () => {
    render(<OnboardingFlow />);
    expect(screen.getByRole("button", { name: "Back" })).toBeDisabled();
  });

  it("renders step 2 housing options", async () => {
    const user = userEvent.setup();
    render(<OnboardingFlow />);
    await user.type(screen.getByPlaceholderText("e.g. Sarah Chen"), "Sarah");
    await user.selectOptions(screen.getByRole("combobox"), "Massachusetts");
    await user.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByText("Renter")).toBeInTheDocument();
    expect(screen.getByText("Homeowner")).toBeInTheDocument();
    expect(screen.getByText("Other")).toBeInTheDocument();
  });

  it("has no accessibility violations", async () => {
    const { container } = render(<OnboardingFlow />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
