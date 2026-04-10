"use client";

import React from "react";
import { useTranslation } from "@/lib/i18n";
import {
  CheckCircle,
  Clock,
  Warning,
  Scales,
  ShieldCheck,
} from "@phosphor-icons/react";

/**
 * Complete rights guide data from the CaseMate knowledge base.
 *
 * @property id - Unique guide identifier
 * @property domain - Legal domain category (e.g., "landlord_tenant", "employment_rights")
 * @property title - Display title for the guide
 * @property description - Brief summary shown in guide listings
 * @property explanation - Detailed plain-language legal explanation
 * @property your_rights - List of specific rights the user has under this area of law
 * @property action_steps - Ordered list of concrete steps the user should take
 * @property deadlines - Time-sensitive deadlines or statutes of limitations
 * @property common_mistakes - Mistakes to avoid that could weaken the user's position
 * @property when_to_get_a_lawyer - Guidance on when professional legal help is necessary
 */
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

/**
 * Props for the RightsGuide component.
 *
 * @property guide - Complete rights guide data to render
 */
interface RightsGuideProps {
  guide: Guide;
}

/**
 * Detailed rights guide display for the "Know Your Rights" library.
 *
 * Renders a comprehensive legal rights guide with sections for explanation,
 * enumerated rights, ordered action steps, important deadlines, common mistakes
 * to avoid, and guidance on when to hire a lawyer. Uses editorial typography
 * (serif headlines, generous whitespace, readable measure) so the page reads
 * like a well-designed magazine article.
 *
 * @param props - Component props
 * @param props.guide - The complete rights guide data to display
 */
export default function RightsGuide({ guide }: RightsGuideProps) {
  const { t } = useTranslation();

  return (
    <article className="max-w-[72ch] mx-auto">
      {/* Article header */}
      <header className="pb-10 mb-10 border-b border-border">
        <span className="text-xs font-sans font-medium text-accent uppercase tracking-wider">
          {guide.domain.replace(/_/g, " ")}
        </span>
        <h1 className="font-serif font-medium tracking-tight leading-tight text-4xl md:text-5xl text-ink-primary mt-4">
          {guide.title}
        </h1>
        <p className="font-sans text-lg text-ink-secondary leading-relaxed mt-5 max-w-[65ch]">
          {guide.description}
        </p>
      </header>

      {/* Explanation */}
      <section className="mb-12">
        <h2 className="font-serif font-medium tracking-tight text-2xl text-ink-primary mb-4">
          {t("whatYouNeedToKnow")}
        </h2>
        <p className="font-sans text-base text-ink-secondary leading-relaxed max-w-[65ch]">
          {guide.explanation}
        </p>
      </section>

      {/* Your Rights */}
      <section className="mb-12">
        <h2 className="font-serif font-medium tracking-tight text-2xl text-ink-primary mb-5">
          {t("yourRights")}
        </h2>
        <ul className="space-y-4 max-w-[65ch]">
          {guide.your_rights.map((right: string, i: number) => (
            <li key={i} className="flex gap-3 font-sans text-base text-ink-secondary leading-relaxed">
              <CheckCircle
                className="w-5 h-5 text-accent shrink-0 mt-1"
                weight="regular"
              />
              <span>{right}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Pull quote — a single rights line used as an editorial break */}
      {guide.your_rights.length > 0 && (
        <blockquote className="font-serif text-3xl italic leading-snug py-12 max-w-[40ch] text-ink-primary border-l-2 border-accent pl-6 my-12">
          &ldquo;{guide.your_rights[0]}&rdquo;
        </blockquote>
      )}

      {/* Action Steps */}
      <section className="mb-12">
        <h2 className="font-serif font-medium tracking-tight text-2xl text-ink-primary mb-5">
          {t("actionSteps")}
        </h2>
        <ol className="space-y-5 max-w-[65ch]">
          {guide.action_steps.map((step: string, i: number) => (
            <li key={i} className="flex gap-4">
              <span className="w-8 h-8 rounded-md bg-accent-subtle text-accent border border-accent/20 font-sans font-medium text-sm flex items-center justify-center shrink-0">
                {i + 1}
              </span>
              <p className="font-sans text-base text-ink-secondary leading-relaxed pt-1">
                {step}
              </p>
            </li>
          ))}
        </ol>
      </section>

      {/* Deadlines */}
      {guide.deadlines.length > 0 && (
        <section className="mb-12 bg-warning-subtle border border-warning/30 rounded-lg p-8">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-warning" weight="regular" />
            <h2 className="font-serif font-medium tracking-tight text-2xl text-ink-primary">
              {t("importantDeadlines")}
            </h2>
          </div>
          <ul className="space-y-3">
            {guide.deadlines.map((deadline: string, i: number) => (
              <li
                key={i}
                className="font-sans text-base text-warning leading-relaxed flex gap-2"
              >
                <span className="text-warning shrink-0">•</span>
                <span>{deadline}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Common Mistakes */}
      {guide.common_mistakes.length > 0 && (
        <section className="mb-12">
          <div className="flex items-center gap-2 mb-5">
            <Warning className="w-5 h-5 text-warning" weight="regular" />
            <h2 className="font-serif font-medium tracking-tight text-2xl text-ink-primary">
              {t("commonMistakes")}
            </h2>
          </div>
          <ul className="space-y-4 max-w-[65ch]">
            {guide.common_mistakes.map((mistake: string, i: number) => (
              <li
                key={i}
                className="font-sans text-base text-ink-secondary leading-relaxed flex gap-3"
              >
                <span className="text-warning shrink-0 mt-1">—</span>
                <span>{mistake}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* When to Get a Lawyer */}
      <section className="mb-12 bg-white border border-border rounded-lg p-8">
        <div className="flex items-center gap-2 mb-4">
          <Scales className="w-5 h-5 text-ink-secondary" weight="regular" />
          <h2 className="font-serif font-medium tracking-tight text-2xl text-ink-primary">
            {t("whenToGetLawyer")}
          </h2>
        </div>
        <p className="font-sans text-base text-ink-secondary leading-relaxed max-w-[65ch]">
          {guide.when_to_get_a_lawyer}
        </p>
      </section>

      {/* Disclaimer */}
      <div className="border-t border-border pt-8 mt-12">
        <p className="text-xs font-sans text-ink-tertiary text-center flex items-center justify-center gap-2">
          <ShieldCheck className="w-4 h-4" weight="regular" />
          {t("rightsDisclaimer")}
        </p>
      </div>
    </article>
  );
}
