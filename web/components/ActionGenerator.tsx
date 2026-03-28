"use client";

import React, { useState } from "react";
import Button from "./ui/Button";
import Card from "./ui/Card";
import { api } from "@/lib/api";
import type { DemandLetter, RightsSummary, Checklist } from "@/lib/types";

type ActionType = "letter" | "rights" | "checklist";
type ActionResult = DemandLetter | RightsSummary | Checklist;

interface ActionGeneratorProps {
  userId: string;
}

export default function ActionGenerator({ userId }: ActionGeneratorProps) {
  const [activeAction, setActiveAction] = useState<ActionType | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ActionResult | null>(null);
  const [resultType, setResultType] = useState<ActionType | null>(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  async function handleGenerate(action: ActionType) {
    setLoading(true);
    setActiveAction(action);
    setResult(null);
    setResultType(null);
    setError("");

    try {
      let data: ActionResult;
      switch (action) {
        case "letter":
          data = await api.generateLetter(userId);
          break;
        case "rights":
          data = await api.generateRights(userId);
          break;
        case "checklist":
          data = await api.generateChecklist(userId);
          break;
      }
      setResult(data);
      setResultType(action);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate. Try again."
      );
    } finally {
      setLoading(false);
      setActiveAction(null);
    }
  }

  function getTextContent(): string {
    if (!result || !resultType) return "";
    switch (resultType) {
      case "letter":
        return (result as DemandLetter).letter_text;
      case "rights":
        return (result as RightsSummary).summary_text;
      case "checklist":
        return (result as Checklist).items.join("\n");
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(getTextContent());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback: ignored
    }
  }

  function renderResult() {
    if (!result || !resultType) return null;

    switch (resultType) {
      case "letter": {
        const letter = result as DemandLetter;
        return (
          <Card>
            <Card.Header>
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900">
                  Demand Letter
                </h3>
                <Button variant="ghost" size="sm" onClick={handleCopy}>
                  {copied ? "Copied!" : "Copy"}
                </Button>
              </div>
            </Card.Header>
            <Card.Body>
              <pre className="text-sm text-gray-800 whitespace-pre-wrap font-sans leading-relaxed">
                {letter.letter_text}
              </pre>
              {letter.legal_citations.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                    Legal Citations
                  </p>
                  <ul className="space-y-1">
                    {letter.legal_citations.map((cite, i) => (
                      <li key={i} className="text-xs text-gray-600">
                        {cite}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </Card.Body>
          </Card>
        );
      }

      case "rights": {
        const rights = result as RightsSummary;
        return (
          <Card>
            <Card.Header>
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900">
                  Rights Summary
                </h3>
                <Button variant="ghost" size="sm" onClick={handleCopy}>
                  {copied ? "Copied!" : "Copy"}
                </Button>
              </div>
            </Card.Header>
            <Card.Body>
              <p className="text-sm text-gray-800 leading-relaxed mb-4">
                {rights.summary_text}
              </p>
              {rights.key_rights.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                    Key Rights
                  </p>
                  <ul className="space-y-1.5">
                    {rights.key_rights.map((right, i) => (
                      <li
                        key={i}
                        className="text-sm text-gray-700 flex gap-2"
                      >
                        <span className="text-green-500 shrink-0">&#10003;</span>
                        {right}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </Card.Body>
          </Card>
        );
      }

      case "checklist": {
        const checklist = result as Checklist;
        return (
          <Card>
            <Card.Header>
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900">
                  Legal Checklist
                </h3>
                <Button variant="ghost" size="sm" onClick={handleCopy}>
                  {copied ? "Copied!" : "Copy"}
                </Button>
              </div>
            </Card.Header>
            <Card.Body>
              <ul className="space-y-2">
                {checklist.items.map((item, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm">
                    <input
                      type="checkbox"
                      className="mt-0.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <div>
                      <span className="text-gray-800">{item}</span>
                      {checklist.deadlines[i] && (
                        <span className="block text-xs text-red-500 mt-0.5">
                          Deadline: {checklist.deadlines[i]}
                        </span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </Card.Body>
          </Card>
        );
      }
    }
  }

  return (
    <div className="bg-gray-50 border-t border-gray-200 px-6 py-3 shrink-0">
      {/* Action buttons */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs text-gray-500 mr-1">Actions:</span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleGenerate("letter")}
          disabled={loading}
        >
          {loading && activeAction === "letter" ? (
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin" />
              Generating...
            </span>
          ) : (
            "Generate Letter"
          )}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleGenerate("rights")}
          disabled={loading}
        >
          {loading && activeAction === "rights" ? (
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin" />
              Generating...
            </span>
          ) : (
            "Rights Summary"
          )}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleGenerate("checklist")}
          disabled={loading}
        >
          {loading && activeAction === "checklist" ? (
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin" />
              Generating...
            </span>
          ) : (
            "Checklist"
          )}
        </Button>
      </div>

      {error && (
        <p className="text-xs text-red-600 bg-red-50 rounded-lg p-2 mb-2">
          {error}
        </p>
      )}

      {result && <div className="max-h-64 overflow-y-auto">{renderResult()}</div>}
    </div>
  );
}
