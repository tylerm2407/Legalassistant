"""Immigration law domain guidance, statutes, and common questions.

This module provides domain-specific prompt fragments, key statute citations,
and common questions for immigration issues. Used by the memory injector
to specialize Claude's responses when the classifier detects an immigration
question.
"""

from __future__ import annotations

DOMAIN_GUIDANCE: str = (
    "You are assisting with an immigration matter. Immigration law is exclusively "
    "federal, though state laws affect daily life for immigrants. Always clarify the "
    "user's current immigration status as it determines available options. For visa "
    "questions, explain the specific visa category requirements, processing times, and "
    "limitations. For green card applications, outline the preference categories and "
    "priority dates. For DACA recipients, explain renewal procedures and current legal "
    "status of the program. For removal/deportation proceedings, this is urgent — explain "
    "the right to counsel (not appointed), bond hearings, and relief options like asylum "
    "or cancellation of removal. ALWAYS recommend consulting an immigration attorney for "
    "complex cases, as mistakes can have severe consequences including deportation. Never "
    "advise someone to make false statements on immigration forms."
)

KEY_STATUTES: dict[str, str] = {
    "INA (8 U.S.C. § 1101 et seq.)": (
        "Immigration and Nationality Act — the primary federal immigration statute "
        "governing visas, green cards, naturalization, and removal."
    ),
    "8 U.S.C. § 1158 (Asylum)": (
        "Asylum provision allowing individuals in the US to apply for protection "
        "based on persecution by race, religion, nationality, political opinion, "
        "or social group."
    ),
    "8 U.S.C. § 1229a (Removal Proceedings)": (
        "Removal proceeding statute governing how the government initiates and "
        "conducts deportation proceedings before immigration judges."
    ),
    "8 U.S.C. § 1427 (Naturalization)": (
        "Naturalization requirements including 5-year residency (3 for spouse of "
        "citizen), good moral character, English, and civics test."
    ),
    "8 U.S.C. § 1255 (Adjustment of Status)": (
        "Adjustment of status provision allowing certain individuals already in the "
        "US to apply for green card without leaving the country."
    ),
    "8 CFR § 214.2(h) (H-1B Visa)": (
        "H-1B specialty occupation visa regulations including employer sponsorship "
        "requirements, annual cap, and 6-year maximum duration."
    ),
    "DACA (Executive Action 2012)": (
        "Deferred Action for Childhood Arrivals providing work authorization and "
        "deferred deportation for qualifying individuals brought to the US as children."
    ),
    "8 U.S.C. § 1182 (Inadmissibility Grounds)": (
        "Grounds of inadmissibility that can prevent entry or status adjustment, "
        "including criminal convictions, health, and public charge."
    ),
}

COMMON_QUESTIONS: list[str] = [
    "What are my options for getting a green card?",
    "How do I renew my DACA work permit?",
    "I received a deportation notice. What should I do immediately?",
    "Can my employer sponsor me for an H-1B visa?",
    "How long does the naturalization process take?",
]
