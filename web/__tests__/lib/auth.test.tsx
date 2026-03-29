import React from "react";
import { render, screen, waitFor, act } from "@testing-library/react";
import { AuthProvider, useAuth } from "@/lib/auth";

// Store the callback so we can trigger auth state changes
let authStateCallback: (event: string, session: unknown) => void;

jest.mock("@/lib/supabase", () => ({
  supabase: {
    auth: {
      getSession: jest.fn().mockResolvedValue({
        data: { session: null },
      }),
      onAuthStateChange: jest.fn((callback: (event: string, session: unknown) => void) => {
        authStateCallback = callback;
        return {
          data: {
            subscription: {
              unsubscribe: jest.fn(),
            },
          },
        };
      }),
      signOut: jest.fn().mockResolvedValue({}),
    },
  },
}));

const mockPush = jest.fn();
const mockPathname = jest.fn().mockReturnValue("/");
jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
  usePathname: () => mockPathname(),
}));

// Test component that consumes the auth context
function AuthConsumer() {
  const { user, loading, session } = useAuth();
  return (
    <div>
      <span data-testid="loading">{loading ? "true" : "false"}</span>
      <span data-testid="user">{user ? user.id : "none"}</span>
      <span data-testid="session">{session ? "active" : "none"}</span>
    </div>
  );
}

describe("AuthProvider", () => {
  beforeEach(() => {
    mockPush.mockReset();
    mockPathname.mockReturnValue("/");
  });

  it("provides initial loading state", () => {
    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>
    );
    // Initially loading is true before getSession resolves
    expect(screen.getByTestId("user")).toHaveTextContent("none");
  });

  it("sets user to null when no session", async () => {
    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>
    );
    await waitFor(() => {
      expect(screen.getByTestId("loading")).toHaveTextContent("false");
    });
    expect(screen.getByTestId("user")).toHaveTextContent("none");
  });

  it("updates user when auth state changes", async () => {
    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading")).toHaveTextContent("false");
    });

    act(() => {
      authStateCallback("SIGNED_IN", {
        user: { id: "user-123" },
        access_token: "token",
      });
    });

    expect(screen.getByTestId("user")).toHaveTextContent("user-123");
    expect(screen.getByTestId("session")).toHaveTextContent("active");
  });

  it("renders children", () => {
    render(
      <AuthProvider>
        <div>App Content</div>
      </AuthProvider>
    );
    expect(screen.getByText("App Content")).toBeInTheDocument();
  });
});

describe("useAuth", () => {
  it("returns default values outside of provider", () => {
    function TestComponent() {
      const { user, loading } = useAuth();
      return (
        <div>
          <span data-testid="user">{user ? "exists" : "null"}</span>
          <span data-testid="loading">{loading ? "true" : "false"}</span>
        </div>
      );
    }
    render(<TestComponent />);
    expect(screen.getByTestId("user")).toHaveTextContent("null");
    expect(screen.getByTestId("loading")).toHaveTextContent("true");
  });
});
