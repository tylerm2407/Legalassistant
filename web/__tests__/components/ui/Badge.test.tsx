import React from "react";
import { render, screen } from "@testing-library/react";
import Badge from "@/components/ui/Badge";

describe("Badge", () => {
  it("renders children text", () => {
    render(<Badge>open</Badge>);
    expect(screen.getByText("open")).toBeInTheDocument();
  });

  it("applies success variant styling", () => {
    render(<Badge variant="success">resolved</Badge>);
    const badge = screen.getByText("resolved");
    expect(badge.className).toContain("text-green-400");
  });

  it("applies error variant styling", () => {
    render(<Badge variant="error">escalated</Badge>);
    const badge = screen.getByText("escalated");
    expect(badge.className).toContain("text-red-400");
  });

  it("applies warning variant styling", () => {
    render(<Badge variant="warning">watching</Badge>);
    const badge = screen.getByText("watching");
    expect(badge.className).toContain("text-yellow-400");
  });

  it("applies md size styling", () => {
    render(<Badge size="md">large badge</Badge>);
    const badge = screen.getByText("large badge");
    expect(badge.className).toContain("px-2.5");
  });
});
