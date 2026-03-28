"""South Central region state law citations.

States: OK, TX
"""

from __future__ import annotations

SOUTH_CENTRAL_LAWS: dict[str, dict[str, str]] = {
    "OK": {
        "landlord_tenant": (
            "Oklahoma Residential Landlord and Tenant Act (15 Okla. Stat. § 321 et seq.) governs "
            "tenancies. There is no statutory limit on security deposits. Deposits must be returned "
            "within 45 days (15 Okla. Stat. § 115). Eviction requires a 5-day notice for nonpayment "
            "(12 Okla. Stat. § 1148.7). Oklahoma allows landlord liens under 41 Okla. Stat. § 23."
        ),
        "employment_rights": (
            "Oklahoma Anti-Discrimination Act (25 Okla. Stat. § 1101 et seq.) prohibits employment "
            "discrimination for employers with 15+ employees. Oklahoma follows the federal minimum "
            "wage. The Oklahoma Protection of Labor Act (40 Okla. Stat. § 165.1 et seq.) governs "
            "timely payment. Workers' compensation is under 85A Okla. Stat. § 1 et seq."
        ),
        "consumer_protection": (
            "Oklahoma Consumer Protection Act (15 Okla. Stat. § 751 et seq.) prohibits unfair or "
            "deceptive practices. The Lemon Law (15 Okla. Stat. § 901 et seq.) covers new vehicles. "
            "The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Oklahoma does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 5 years (12 Okla. Stat. § 95). Wage garnishment "
            "follows 12 Okla. Stat. § 1171.2 with 25% of disposable earnings limit. Homestead "
            "exemption is unlimited in acreage (up to 1 acre in city) under Okla. Const. Art. 12, "
            "§ 1."
        ),
        "small_claims": (
            "Oklahoma small claims court handles disputes up to $10,000 under 12 Okla. Stat. "
            "§ 1751. Filing fees are approximately $58-$72. Cases are heard in the small claims "
            "division of District Court. Appeals go within 30 days."
        ),
        "contract_disputes": (
            "Oklahoma follows common law and the UCC (12A Okla. Stat.) for goods. The statute of "
            "frauds is at 15 Okla. Stat. § 136. Written contract SOL is 5 years (12 Okla. Stat. "
            "§ 95); oral is 3 years (12 Okla. Stat. § 95(2))."
        ),
        "traffic_violations": (
            "Oklahoma traffic law is in 47 Okla. Stat. Speeding is under 47 Okla. Stat. § 11-801. "
            "DUI is under 47 Okla. Stat. § 11-902. Points accumulate under 47 Okla. Stat. § 6-205.1. "
            "License suspensions are handled by the Department of Public Safety."
        ),
        "family_law": (
            "Oklahoma divorce is governed by 43 Okla. Stat. § 101 et seq. The state follows "
            "equitable distribution (43 Okla. Stat. § 121). Custody uses best interests standard "
            "(43 Okla. Stat. § 113). Child support guidelines are in 43 Okla. Stat. § 118."
        ),
        "criminal_records": (
            "Oklahoma allows expungement under 22 Okla. Stat. § 18 et seq. Non-violent "
            "misdemeanors may be expunged 5 years after completion. Non-violent felonies after "
            "5-10 years. Oklahoma does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Oklahoma Taxpayer and Citizen Protection Act (25 Okla. Stat. § 1312 et seq.) requires "
            "E-Verify for public employers and contractors. Driver's licenses require legal presence "
            "under 47 Okla. Stat. § 6-105.3. Oklahoma does not provide in-state tuition for "
            "undocumented students."
        ),
    },
    "TX": {
        "landlord_tenant": (
            "Texas Property Code Chapter 92 governs residential tenancies. Security deposits "
            "must be returned within 30 days (Tex. Prop. Code § 92.103) with an itemized list "
            "of deductions. There is no statewide rent control (Tex. Prop. Code § 214.902 "
            "preempts local rent control). Eviction requires a 3-day notice to vacate under "
            "Tex. Prop. Code § 24.005. Landlord lien rights are in § 54.041."
        ),
        "employment_rights": (
            "Texas follows employment at-will doctrine with narrow exceptions. The Texas "
            "Commission on Human Rights Act (Tex. Lab. Code Chapter 21) mirrors federal Title "
            "VII protections. Texas Payday Law (Tex. Lab. Code Chapter 61) governs wage payment "
            "timing. Texas does not have a state minimum wage above the federal level. Workers' "
            "compensation is optional under Tex. Lab. Code § 406.002."
        ),
        "consumer_protection": (
            "Texas Deceptive Trade Practices Act (Tex. Bus. & Com. Code § 17.41 et seq.) "
            "provides treble damages for knowing violations. The Texas Lemon Law (Tex. Occ. Code "
            "Chapter 2301) covers new motor vehicles. The AG Consumer Protection Division "
            "enforces DTPA. Filing a DTPA claim requires a 60-day demand letter under § 17.505."
        ),
        "debt_collections": (
            "Texas Finance Code Chapter 392 (Texas Debt Collection Act) governs collector "
            "behavior. The statute of limitations on written contracts is 4 years (Tex. Civ. "
            "Prac. & Rem. Code § 16.004). Texas has strong homestead exemption (Tex. Prop. Code "
            "§ 41.001) protecting homes from most creditors. Current wages are generally exempt "
            "from garnishment under Tex. Prop. Code § 42.001."
        ),
        "small_claims": (
            "Texas justice courts handle small claims up to $20,000 under Tex. Gov. Code "
            "§ 27.031. Filing fees are typically $50-$100. Either party may appeal to county "
            "court for a trial de novo. Service of process follows Tex. R. Civ. P. Rules 501-507. "
            "Mediation is encouraged but not required."
        ),
        "contract_disputes": (
            "Texas contract law follows common law and the UCC for goods (Tex. Bus. & Com. Code). "
            "The statute of frauds is at Tex. Bus. & Com. Code § 26.01. Written contract SOL is "
            "4 years (Tex. Civ. Prac. & Rem. Code § 16.004). Non-compete agreements must meet "
            "reasonableness requirements under Tex. Bus. & Com. Code § 15.50."
        ),
        "traffic_violations": (
            "Texas Transportation Code governs traffic offenses. Speeding is under Transp. Code "
            "§ 545.351. DWI is under Tex. Penal Code § 49.04. License suspensions are handled "
            "by DPS under Transp. Code Chapter 521. Defensive driving can dismiss tickets under "
            "Code Crim. Proc. Art. 45.0511. Texas uses a surcharge/points system for repeat "
            "offenders."
        ),
        "family_law": (
            "Texas is a community property state (Tex. Fam. Code § 3.002). Divorce requires a "
            "60-day waiting period (Tex. Fam. Code § 6.702). Child custody uses the best "
            "interests standard (Tex. Fam. Code § 153.002). Child support guidelines follow "
            "Tex. Fam. Code § 154.125. Spousal maintenance is limited under Tex. Fam. Code "
            "§ 8.051."
        ),
        "criminal_records": (
            "Texas Government Code Chapter 411, Subchapter F governs expunction (complete "
            "erasure) of criminal records. Nondisclosure orders under Tex. Gov. Code § 411.071 "
            "seal records from public access. Deferred adjudication may qualify for nondisclosure "
            "after waiting periods. Texas does not have a statewide ban-the-box law, though some "
            "cities do."
        ),
        "immigration": (
            "Texas has enacted SB 4 (Tex. Code Crim. Proc. Art. 2.251) requiring local law "
            "enforcement cooperation with ICE. Texas does not provide driver's licenses to "
            "undocumented immigrants. Tex. Penal Code § 20.05 addresses human smuggling. Texas "
            "allows in-state tuition for certain undocumented students under Tex. Educ. Code "
            "§ 54.052(j)."
        ),
    },
}
