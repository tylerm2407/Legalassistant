"""Federal default statute citations applicable across all states.

Provides baseline federal law references for each legal domain.
State-specific entries override these defaults when available.
"""

from __future__ import annotations

FEDERAL_DEFAULTS: dict[str, dict[str, str]] = {
    "federal_defaults": {
        "landlord_tenant": (
            "The Fair Housing Act (42 U.S.C. § 3601 et seq.) prohibits discrimination in housing. "
            "The Servicemembers Civil Relief Act (50 U.S.C. § 3951) protects military tenants. "
            "HUD regulations at 24 CFR Part 100 implement fair housing enforcement. Section 8 "
            "housing vouchers are governed by 42 U.S.C. § 1437f."
        ),
        "employment_rights": (
            "Title VII of the Civil Rights Act (42 U.S.C. § 2000e) prohibits employment "
            "discrimination. The FLSA (29 U.S.C. § 201 et seq.) sets minimum wage and overtime "
            "rules. The ADA (42 U.S.C. § 12101) requires reasonable accommodation. FMLA (29 "
            "U.S.C. § 2601) provides 12 weeks unpaid leave. OSHA (29 U.S.C. § 654) mandates "
            "safe workplaces."
        ),
        "consumer_protection": (
            "The FTC Act (15 U.S.C. § 45) prohibits unfair or deceptive acts. The Magnuson-Moss "
            "Warranty Act (15 U.S.C. § 2301) governs consumer product warranties. The CFPB "
            "enforces the Consumer Financial Protection Act (12 U.S.C. § 5531). The CAN-SPAM "
            "Act (15 U.S.C. § 7701) regulates commercial email."
        ),
        "debt_collections": (
            "The Fair Debt Collection Practices Act (15 U.S.C. § 1692) regulates third-party "
            "debt collectors. The Fair Credit Reporting Act (15 U.S.C. § 1681) governs credit "
            "reporting. The Truth in Lending Act (15 U.S.C. § 1601) requires disclosure. "
            "Regulation F (12 CFR Part 1006) implements FDCPA with modern communication rules."
        ),
        "small_claims": (
            "Federal courts do not have a small claims procedure for general disputes. Diversity "
            "jurisdiction requires over $75,000 (28 U.S.C. § 1332). Federal question "
            "jurisdiction is under 28 U.S.C. § 1331. Most small claims are exclusively state "
            "court matters. The Federal Arbitration Act (9 U.S.C. § 1) may apply if arbitration "
            "clauses exist."
        ),
        "contract_disputes": (
            "The Uniform Commercial Code (UCC) Articles 1-2 govern sale of goods contracts in "
            "all states. The Federal Arbitration Act (9 U.S.C. § 1-16) supports enforcement of "
            "arbitration agreements. The Electronic Signatures in Global and National Commerce "
            "Act (15 U.S.C. § 7001) validates electronic contracts. Federal preemption applies "
            "in regulated industries."
        ),
        "traffic_violations": (
            "Federal traffic law is limited. The National Highway Traffic Safety Administration "
            "(NHTSA) sets vehicle safety standards under 49 U.S.C. § 30101. Federal Motor "
            "Carrier Safety Regulations (49 CFR Parts 390-399) govern commercial vehicles. "
            "The National Driver Register (49 U.S.C. § 30302) tracks license revocations across "
            "states."
        ),
        "family_law": (
            "Family law is primarily state-governed. Federal involvement includes the Uniform "
            "Child Custody Jurisdiction and Enforcement Act (UCCJEA). The Child Support "
            "Enforcement Act (42 U.S.C. § 651) provides federal enforcement. DOMA was struck "
            "down; Obergefell v. Hodges (2015) requires marriage equality. The Hague Convention "
            "governs international child abduction cases."
        ),
        "criminal_records": (
            "Federal expungement is extremely limited; there is no general federal expungement "
            "statute. 18 U.S.C. § 3607 allows first-time drug possession dismissal. The Fair "
            "Chance to Compete for Jobs Act (Ban the Box) applies to federal contractors. The "
            "EEOC provides guidance on using criminal records in employment decisions under "
            "Title VII."
        ),
        "immigration": (
            "The Immigration and Nationality Act (8 U.S.C. § 1101 et seq.) is the primary "
            "federal immigration statute. USCIS processes applications under 8 CFR. DACA was "
            "established by executive action in 2012. Asylum is governed by 8 U.S.C. § 1158. "
            "Removal proceedings are under 8 U.S.C. § 1229a before immigration judges."
        ),
    },
}
