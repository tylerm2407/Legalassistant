import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import DocumentUpload from "@/components/DocumentUpload";

// Mock api
const mockUploadDocument = jest.fn();

jest.mock("@/lib/api", () => ({
  api: {
    uploadDocument: (...args: unknown[]) => mockUploadDocument(...args),
  },
}));

function getFileInput(): HTMLInputElement {
  return document.querySelector('input[type="file"]') as HTMLInputElement;
}

function createFile(name: string, type: string, sizeBytes: number = 100): File {
  const content = new Uint8Array(sizeBytes);
  return new File([content], name, { type });
}

function triggerFileSelect(input: HTMLInputElement, file: File) {
  // We need to set files on the input and fire change
  Object.defineProperty(input, "files", {
    value: [file],
    writable: false,
    configurable: true,
  });
  fireEvent.change(input);
}

describe("DocumentUpload", () => {
  beforeEach(() => {
    mockUploadDocument.mockReset();
  });

  it("renders the drop zone with instructions", () => {
    render(<DocumentUpload userId="user-123" />);
    expect(screen.getByText(/Drag and drop a document here/)).toBeInTheDocument();
    expect(screen.getByText("Browse Files")).toBeInTheDocument();
  });

  it("renders accepted file types info", () => {
    render(<DocumentUpload userId="user-123" />);
    expect(screen.getByText(/PDF, images, or text files up to 10MB/)).toBeInTheDocument();
  });

  it("shows error for unsupported file types", () => {
    render(<DocumentUpload userId="user-123" />);
    const input = getFileInput();
    const file = createFile("test.exe", "application/x-msdownload");
    triggerFileSelect(input, file);
    expect(screen.getByText(/Unsupported file type/)).toBeInTheDocument();
  });

  it("shows error for files over 10MB", () => {
    render(<DocumentUpload userId="user-123" />);
    const input = getFileInput();
    const file = createFile("large.pdf", "application/pdf", 11 * 1024 * 1024);
    triggerFileSelect(input, file);
    expect(screen.getByText(/File too large/)).toBeInTheDocument();
  });

  it("displays analysis results after successful upload", async () => {
    mockUploadDocument.mockResolvedValueOnce({
      filename: "lease.pdf",
      key_facts: ["Lease term is 12 months", "Pet deposit required"],
      red_flags: ["No move-in inspection clause"],
      summary: "Standard residential lease agreement",
    });

    render(<DocumentUpload userId="user-123" />);
    const input = getFileInput();
    const file = createFile("lease.pdf", "application/pdf");
    triggerFileSelect(input, file);

    await waitFor(() => {
      expect(screen.getByText("Document Analysis: lease.pdf")).toBeInTheDocument();
      expect(screen.getByText("Standard residential lease agreement")).toBeInTheDocument();
      expect(screen.getByText("Lease term is 12 months")).toBeInTheDocument();
      expect(screen.getByText("No move-in inspection clause")).toBeInTheDocument();
    });
  });

  it("calls onUploadComplete callback after successful upload", async () => {
    mockUploadDocument.mockResolvedValueOnce({
      filename: "doc.pdf",
      key_facts: [],
      red_flags: [],
      summary: "A document",
    });

    const onComplete = jest.fn();
    render(<DocumentUpload userId="user-123" onUploadComplete={onComplete} />);
    const input = getFileInput();
    const file = createFile("doc.pdf", "application/pdf");
    triggerFileSelect(input, file);

    await waitFor(() => {
      expect(onComplete).toHaveBeenCalledTimes(1);
    });
  });

  it("shows error message on upload failure", async () => {
    mockUploadDocument.mockRejectedValueOnce(new Error("Upload failed"));

    render(<DocumentUpload userId="user-123" />);
    const input = getFileInput();
    const file = createFile("lease.pdf", "application/pdf");
    triggerFileSelect(input, file);

    await waitFor(() => {
      expect(screen.getByText("Upload failed")).toBeInTheDocument();
    });
  });
});
