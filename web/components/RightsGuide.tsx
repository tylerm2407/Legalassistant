"use client";

import React from "react";
import Card from "./ui/Card";

interface Guide {
  id: string;
  domain: string;
  title: string;
  description: string;
  explanation: string;
  your_rights: string[];
  action_steps: string[];
  deadlines: string[];
  common_mistakes: string[];
  when_to_get_a_lawyer: string;
}

interface RightsGuideProps {
  guide: Guide;
}

export default function RightsGuide({ guide }: RightsGuideProps) {
  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <span className="text-xs font-medium text-blue-400 uppercase tracking-wider">
          {guide.domain.replace(/_/g, " ")}
        </span>
        <h1 className="text-2xl font-bold text-white mt-1">{guide.title}</h1>
        <p className="text-gray-400 mt-2">{guide.description}</p>
      </div>

      {/* Explanation */}
      <Card>
        <Card.Header>
          <h2 className="text-sm font-semibold text-white">What You Need to Know</h2>
        </Card.Header>
        <Card.Body>
          <p className="text-sm text-gray-300 leading-relaxed">{guide.explanation}</p>
        </Card.Body>
      </Card>

      {/* Your Rights */}
      <Card>
        <Card.Header>
          <h2 className="text-sm font-semibold text-white">Your Rights</h2>
        </Card.Header>
        <Card.Body>
          <ul className="space-y-2">
            {guide.your_rights.map((right, i) => (
              <li key={i} className="text-sm text-gray-300 flex gap-2">
                <svg className="w-5 h-5 text-green-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {right}
              </li>
            ))}
          </ul>
        </Card.Body>
      </Card>

      {/* Action Steps */}
      <Card>
        <Card.Header>
          <h2 className="text-sm font-semibold text-white">Action Steps</h2>
        </Card.Header>
        <Card.Body>
          <ol className="space-y-3">
            {guide.action_steps.map((step, i) => (
              <li key={i} className="text-sm text-gray-300 flex gap-3">
                <span className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-xs font-bold flex items-center justify-center shrink-0">
                  {i + 1}
                </span>
                {step}
              </li>
            ))}
          </ol>
        </Card.Body>
      </Card>

      {/* Deadlines */}
      {guide.deadlines.length > 0 && (
        <Card>
          <Card.Header>
            <h2 className="text-sm font-semibold text-white">Important Deadlines</h2>
          </Card.Header>
          <Card.Body>
            <ul className="space-y-2">
              {guide.deadlines.map((deadline, i) => (
                <li key={i} className="text-sm text-yellow-400 flex gap-2">
                  <svg className="w-4 h-4 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {deadline}
                </li>
              ))}
            </ul>
          </Card.Body>
        </Card>
      )}

      {/* Common Mistakes */}
      {guide.common_mistakes.length > 0 && (
        <Card>
          <Card.Header>
            <h2 className="text-sm font-semibold text-red-400">Common Mistakes to Avoid</h2>
          </Card.Header>
          <Card.Body>
            <ul className="space-y-2">
              {guide.common_mistakes.map((mistake, i) => (
                <li key={i} className="text-sm text-gray-300 flex gap-2">
                  <svg className="w-4 h-4 text-red-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                  </svg>
                  {mistake}
                </li>
              ))}
            </ul>
          </Card.Body>
        </Card>
      )}

      {/* When to Get a Lawyer */}
      <Card>
        <Card.Header>
          <h2 className="text-sm font-semibold text-white">When to Get a Lawyer</h2>
        </Card.Header>
        <Card.Body>
          <p className="text-sm text-gray-300 leading-relaxed">{guide.when_to_get_a_lawyer}</p>
        </Card.Body>
      </Card>

      {/* Disclaimer */}
      <p className="text-xs text-gray-500 text-center py-4 flex items-center justify-center gap-1.5">
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
        </svg>
        This is legal information, not legal advice. Consult a licensed attorney for your specific situation.
      </p>
    </div>
  );
}
