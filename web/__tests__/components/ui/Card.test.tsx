import React from "react";
import { render, screen } from "@testing-library/react";
import Card from "@/components/ui/Card";

describe("Card", () => {
  it("renders children content", () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText("Card content")).toBeInTheDocument();
  });

  it("renders Card.Header", () => {
    render(
      <Card>
        <Card.Header>Header text</Card.Header>
      </Card>
    );
    expect(screen.getByText("Header text")).toBeInTheDocument();
  });

  it("renders Card.Body", () => {
    render(
      <Card>
        <Card.Body>Body text</Card.Body>
      </Card>
    );
    expect(screen.getByText("Body text")).toBeInTheDocument();
  });

  it("renders Card.Footer", () => {
    render(
      <Card>
        <Card.Footer>Footer text</Card.Footer>
      </Card>
    );
    expect(screen.getByText("Footer text")).toBeInTheDocument();
  });

  it("renders all sub-components together", () => {
    render(
      <Card>
        <Card.Header>Title</Card.Header>
        <Card.Body>Content</Card.Body>
        <Card.Footer>Actions</Card.Footer>
      </Card>
    );
    expect(screen.getByText("Title")).toBeInTheDocument();
    expect(screen.getByText("Content")).toBeInTheDocument();
    expect(screen.getByText("Actions")).toBeInTheDocument();
  });
});
