"""Real statute citations organized by state and legal domain.

This module provides the STATE_LAWS dictionary, which maps state codes
and legal domains to concise descriptions of applicable laws with real
statute citations. Used by the memory injector and action generators
to ground Claude's responses in actual law.

States covered: MA, CA, NY, TX, FL, plus federal_defaults.
"""

from __future__ import annotations

STATE_LAWS: dict[str, dict[str, str]] = {
    "MA": {
        "landlord_tenant": (
            "Massachusetts security deposit law (M.G.L. c. 186, § 15B) requires landlords to "
            "return deposits within 30 days with an itemized list of deductions. Landlords must "
            "hold deposits in a separate interest-bearing account and provide annual interest "
            "statements. Failure to comply entitles tenants to triple damages. M.G.L. c. 239 "
            "governs summary eviction proceedings, requiring a 14-day notice for nonpayment."
        ),
        "employment_rights": (
            "Massachusetts Wage Act (M.G.L. c. 149, § 148) requires timely payment of all wages "
            "and provides treble damages for violations. The Massachusetts Fair Employment "
            "Practices Act (M.G.L. c. 151B) prohibits discrimination based on race, gender, "
            "sexual orientation, and other protected classes. Minimum wage is governed by "
            "M.G.L. c. 151, § 1. Non-compete agreements are restricted under M.G.L. c. 149, § 24L."
        ),
        "consumer_protection": (
            "Massachusetts Consumer Protection Act (M.G.L. c. 93A) prohibits unfair or deceptive "
            "acts and provides treble damages plus attorney fees. A demand letter under § 9 must "
            "be sent 30 days before filing suit. The Attorney General enforces c. 93A through the "
            "Consumer Protection Division. Lemon law protections are in M.G.L. c. 90, § 7N½."
        ),
        "debt_collections": (
            "Massachusetts debt collection practices are governed by M.G.L. c. 93, § 49 and the "
            "Attorney General's regulations at 940 CMR 7.00. Collectors may not contact consumers "
            "at unreasonable hours or use deceptive practices. The statute of limitations on "
            "written contracts is 6 years (M.G.L. c. 260, § 2). Wage garnishment is limited to "
            "15% of gross wages under M.G.L. c. 246, § 28."
        ),
        "small_claims": (
            "Massachusetts small claims court handles disputes up to $7,000 under M.G.L. c. 218, "
            "§ 21. Filing fees range from $40 to $150 depending on the amount. Cases are heard in "
            "the district court where the defendant lives or where the claim arose. Appeals go to "
            "the Superior Court for a trial de novo."
        ),
        "contract_disputes": (
            "Massachusetts contract law follows the Restatement (Second) of Contracts. The statute "
            "of frauds (M.G.L. c. 259, § 1) requires certain contracts to be in writing. The "
            "statute of limitations for written contracts is 6 years (M.G.L. c. 260, § 2) and "
            "oral contracts is 6 years (M.G.L. c. 260, § 2). M.G.L. c. 93A applies to contracts "
            "involving unfair business practices."
        ),
        "traffic_violations": (
            "Massachusetts traffic violations are governed by M.G.L. c. 90. Speeding penalties "
            "include fines and surchargeable events under the Safe Driver Insurance Plan (SDIP). "
            "OUI (Operating Under the Influence) is under M.G.L. c. 90, § 24. License "
            "suspensions are handled by the RMV under M.G.L. c. 90, § 22. Traffic court "
            "hearings can be requested through the clerk magistrate."
        ),
        "family_law": (
            "Massachusetts divorce is governed by M.G.L. c. 208. Both fault and no-fault grounds "
            "are available. Child custody follows the best interests standard (M.G.L. c. 208, "
            "§ 31). Child support guidelines are issued by the Trial Court under M.G.L. c. 208, "
            "§ 28. Alimony reform under M.G.L. c. 208, §§ 48-55 establishes durational limits "
            "based on length of marriage."
        ),
        "criminal_records": (
            "Massachusetts expungement law (M.G.L. c. 276, § 100E-100U) allows sealing of "
            "certain records. Misdemeanors can be sealed 3 years after disposition; felonies after "
            "7 years. CORI reform (M.G.L. c. 6, § 172) limits employer access to criminal "
            "records. Ban-the-box law (M.G.L. c. 151B, § 4(9½)) prohibits asking about criminal "
            "history on initial job applications."
        ),
        "immigration": (
            "Massachusetts does not have state-level immigration enforcement beyond federal law. "
            "The Massachusetts Trust Act limits state and local cooperation with ICE detainers. "
            "M.G.L. c. 90, § 8J allows undocumented immigrants to obtain driver's licenses. "
            "The state provides in-state tuition for DACA recipients under M.G.L. c. 15A, § 9."
        ),
    },
    "CA": {
        "landlord_tenant": (
            "California security deposit law (Cal. Civ. Code § 1950.5) limits deposits to two "
            "months' rent for unfurnished units and requires return within 21 days with an "
            "itemized statement. The Tenant Protection Act (AB 1482, Cal. Civ. Code § 1946.2) "
            "caps annual rent increases at 5% plus CPI. Just cause eviction is required under "
            "Cal. Civ. Code § 1946.2(b). Habitability standards are in Cal. Civ. Code § 1941."
        ),
        "employment_rights": (
            "California Labor Code §§ 200-244 govern wage payment requirements including final "
            "pay timing. The FEHA (Cal. Gov. Code § 12940) provides broad employment "
            "discrimination protections. Cal. Labor Code § 1102.5 protects whistleblowers. "
            "Non-compete agreements are generally void under Cal. Bus. & Prof. Code § 16600. "
            "Minimum wage is set by Cal. Labor Code § 1182.12."
        ),
        "consumer_protection": (
            "California Consumers Legal Remedies Act (Cal. Civ. Code § 1750 et seq.) prohibits "
            "deceptive practices and allows class actions. The Song-Beverly Consumer Warranty Act "
            "(Cal. Civ. Code § 1790 et seq.) provides lemon law protections. Cal. Bus. & Prof. "
            "Code § 17200 (UCL) prohibits unfair competition. CCPA (Cal. Civ. Code § 1798.100) "
            "provides data privacy rights."
        ),
        "debt_collections": (
            "California's Rosenthal Fair Debt Collection Practices Act (Cal. Civ. Code § 1788) "
            "extends FDCPA protections to original creditors. The statute of limitations on "
            "written contracts is 4 years (Cal. Code Civ. Proc. § 337). Wage garnishment is "
            "limited to 25% of disposable earnings under Cal. Code Civ. Proc. § 706.050. "
            "Exempt property protections are in Cal. Code Civ. Proc. § 703.140."
        ),
        "small_claims": (
            "California small claims court handles disputes up to $10,000 ($5,000 for "
            "corporations) under Cal. Code Civ. Proc. § 116.220. No attorneys are allowed in "
            "small claims. Filing fees range from $30 to $75. The defendant may appeal to "
            "Superior Court; the plaintiff may not. Cases must be filed where the defendant "
            "resides or the obligation was incurred."
        ),
        "contract_disputes": (
            "California contract law is codified in Cal. Civ. Code §§ 1549-1701. The statute of "
            "frauds is at Cal. Civ. Code § 1624. Written contract SOL is 4 years (Cal. Code "
            "Civ. Proc. § 337); oral is 2 years (§ 339). Unconscionable contracts may be voided "
            "under Cal. Civ. Code § 1670.5. Liquidated damages must be reasonable under § 1671."
        ),
        "traffic_violations": (
            "California Vehicle Code (CVC) governs all traffic violations. Speeding fines are "
            "set by CVC § 22350 (basic speed law) and § 22349 (maximum speed). DUI is under "
            "CVC § 23152. Points are assessed per CVC § 12810. Traffic school eligibility is "
            "under CVC § 42005. The DMV hearing process for license suspensions is separate "
            "from court proceedings."
        ),
        "family_law": (
            "California is a community property state (Cal. Fam. Code § 760). Dissolution is "
            "governed by Cal. Fam. Code § 2310 (no-fault only). Child custody follows the best "
            "interests standard (Cal. Fam. Code § 3011). Child support guidelines are in "
            "Cal. Fam. Code § 4055. Spousal support factors are listed in Cal. Fam. Code § 4320."
        ),
        "criminal_records": (
            "California Penal Code § 1203.4 allows expungement of convictions after probation. "
            "Proposition 47 (Penal Code § 1170.18) reclassified certain felonies as misdemeanors. "
            "Cal. Labor Code § 432.7 limits employer inquiries into arrest records. AB 1008 "
            "(Fair Chance Act) is a ban-the-box law for employers with 5+ employees."
        ),
        "immigration": (
            "California Values Act (SB 54, Cal. Gov. Code § 7284) limits state and local law "
            "enforcement cooperation with federal immigration authorities. AB 60 provides "
            "driver's licenses regardless of immigration status. Cal. Labor Code § 1019 prohibits "
            "employers from retaliating based on immigration status. The TRUST Act limits "
            "immigration holds in county jails."
        ),
    },
    "NY": {
        "landlord_tenant": (
            "New York's Housing Stability and Tenant Protection Act of 2019 reformed rent "
            "regulation statewide. Security deposits are limited to one month's rent under "
            "N.Y. Gen. Oblig. Law § 7-108 and must be returned within 14 days. The HSTPA "
            "eliminated most vacancy decontrol. N.Y. Real Prop. Law § 226-c requires landlords "
            "to give 30-90 days notice of non-renewal depending on tenancy length."
        ),
        "employment_rights": (
            "New York Labor Law § 191 requires timely wage payment. The New York State Human "
            "Rights Law (N.Y. Exec. Law § 296) prohibits employment discrimination. N.Y. Labor "
            "Law § 740 protects whistleblowers with expanded coverage since 2022. Minimum wage "
            "is set by N.Y. Labor Law § 652. Non-compete restrictions are limited by recent "
            "legislation and judicial precedent."
        ),
        "consumer_protection": (
            "New York General Business Law § 349 prohibits deceptive acts and practices, allowing "
            "private right of action with treble damages up to $1,000. GBL § 350 covers false "
            "advertising. The New York Lemon Law (GBL § 198-a) covers new vehicles. N.Y. "
            "Personal Property Law § 302 governs used car warranties. The AG enforces through "
            "GBL Article 22-A."
        ),
        "debt_collections": (
            "New York City has additional protections under the NYC Department of Consumer and "
            "Worker Protection rules. The statute of limitations on written contracts is 6 years "
            "(N.Y. C.P.L.R. § 213). Income execution (garnishment) is limited to 10% of gross "
            "income under N.Y. C.P.L.R. § 5231. N.Y. Gen. Oblig. Law § 17-101 governs "
            "acknowledgment of time-barred debts."
        ),
        "small_claims": (
            "New York small claims court handles disputes up to $10,000 in NYC and $5,000 "
            "elsewhere under N.Y. Uniform City Court Act § 1801. Individuals may appear without "
            "an attorney. Filing fees are $15-$20. Judgments can be appealed within 30 days. "
            "Arbitration is available as an alternative."
        ),
        "contract_disputes": (
            "New York contract law is common law based with statutory supplements. The statute of "
            "frauds is at N.Y. Gen. Oblig. Law § 5-701. Written contract SOL is 6 years (N.Y. "
            "C.P.L.R. § 213). N.Y. Gen. Oblig. Law § 5-1401 allows parties to choose NY law. "
            "Unconscionability doctrine follows UCC § 2-302 for goods."
        ),
        "traffic_violations": (
            "New York Vehicle and Traffic Law (VTL) governs traffic offenses. Speeding is under "
            "VTL § 1180. DWI/DWAI is under VTL § 1192. Points accumulate under VTL § 510; 11 "
            "points in 18 months triggers suspension. The Traffic Violations Bureau handles NYC "
            "cases. Defensive driving courses can reduce up to 4 points."
        ),
        "family_law": (
            "New York is an equitable distribution state (N.Y. Dom. Rel. Law § 236B). No-fault "
            "divorce requires irretrievable breakdown for 6+ months (DRL § 170(7)). Child "
            "custody follows the best interests standard (DRL § 240). Child support follows the "
            "CSSA formula (DRL § 240(1-b)). Maintenance (alimony) guidelines are in DRL § 236B(6)."
        ),
        "criminal_records": (
            "New York Criminal Procedure Law § 160.59 allows sealing of up to two convictions. "
            "CPL § 160.50 provides automatic sealing of favorable dispositions. N.Y. Correction "
            "Law Article 23-A limits employer discrimination based on criminal records. NYC's "
            "Fair Chance Act (Admin. Code § 8-107(11-a)) is a ban-the-box law."
        ),
        "immigration": (
            "New York City's detainer law (Admin. Code § 14-154) limits ICE cooperation. The "
            "Green Light Law (VTL § 502(1)(a)) provides driver's licenses regardless of "
            "immigration status. N.Y. Labor Law § 215 protects workers from retaliation "
            "regardless of immigration status. NYC provides legal representation for detained "
            "immigrants through the New York Immigrant Family Unity Project."
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
    "FL": {
        "landlord_tenant": (
            "Florida Residential Landlord and Tenant Act (Fla. Stat. § 83.40-83.682) governs "
            "rental relationships. Security deposits must be returned within 15-30 days depending "
            "on whether deductions are claimed (Fla. Stat. § 83.49). Landlords must hold deposits "
            "in a Florida banking institution. Eviction requires a 3-day notice for nonpayment "
            "(Fla. Stat. § 83.56(3)). No statewide rent control exists."
        ),
        "employment_rights": (
            "Florida Civil Rights Act (Fla. Stat. § 760.01-760.11) mirrors federal Title VII "
            "protections for employers with 15+ employees. Florida minimum wage is in Fla. Const. "
            "Art. X, § 24. Florida does not have a comprehensive wage theft statute; remedies are "
            "through common law. Workers' compensation is mandatory under Fla. Stat. Chapter 440. "
            "Florida is a strict employment at-will state."
        ),
        "consumer_protection": (
            "Florida Deceptive and Unfair Trade Practices Act (Fla. Stat. § 501.201 et seq.) "
            "provides consumer protections with attorney fees for prevailing plaintiffs. The "
            "Florida Lemon Law (Fla. Stat. § 681.10 et seq.) covers new vehicles. Fla. Stat. "
            "§ 501.160 prohibits price gouging during emergencies. The AG's Office enforces "
            "through the Division of Consumer Services."
        ),
        "debt_collections": (
            "Florida Consumer Collection Practices Act (Fla. Stat. § 559.55-559.785) governs "
            "debt collection. The statute of limitations on written contracts is 5 years (Fla. "
            "Stat. § 95.11(2)(b)). Florida provides strong homestead protection under Fla. "
            "Const. Art. X, § 4. Head of household wages are exempt from garnishment under "
            "Fla. Stat. § 222.11."
        ),
        "small_claims": (
            "Florida small claims court handles disputes up to $8,000 under Fla. Stat. § 34.01. "
            "Filing fees are based on the claim amount (typically $55-$300). Cases follow "
            "Florida Small Claims Rules 7.010-7.350. Pre-trial mediation is mandatory. Either "
            "party may appeal to circuit court within 30 days."
        ),
        "contract_disputes": (
            "Florida contract law follows common law and the UCC (Fla. Stat. Chapter 672) for "
            "goods. The statute of frauds is at Fla. Stat. § 725.01. Written contract SOL is 5 "
            "years (Fla. Stat. § 95.11(2)(b)); oral is 4 years (§ 95.11(3)(k)). Non-compete "
            "agreements are enforceable if reasonable under Fla. Stat. § 542.335."
        ),
        "traffic_violations": (
            "Florida Statutes Chapter 316 (State Uniform Traffic Control) governs traffic "
            "violations. Speeding penalties are in Fla. Stat. § 316.183. DUI is under Fla. "
            "Stat. § 316.193. Points are assigned per Fla. Stat. § 322.27. Traffic school can "
            "withhold points (Fla. Stat. § 318.14(9)). The DHSMV handles license suspensions "
            "under Chapter 322."
        ),
        "family_law": (
            "Florida is an equitable distribution state (Fla. Stat. § 61.075). Dissolution of "
            "marriage requires irretrievable breakdown (Fla. Stat. § 61.052). Parenting plans "
            "are required under Fla. Stat. § 61.13. Child support guidelines follow Fla. Stat. "
            "§ 61.30. Alimony was reformed in 2023, eliminating permanent alimony under "
            "Fla. Stat. § 61.08."
        ),
        "criminal_records": (
            "Florida Statutes § 943.0585 governs expungement and § 943.059 governs sealing of "
            "criminal records. Only one expungement or sealing is allowed per lifetime. A "
            "Certificate of Eligibility from FDLE is required. Fla. Stat. § 112.011 limits "
            "government employer inquiries into sealed records. Some municipalities have adopted "
            "ban-the-box ordinances."
        ),
        "immigration": (
            "Florida enacted SB 1718 requiring employers with 25+ employees to use E-Verify. "
            "Florida does not provide driver's licenses to undocumented immigrants. Fla. Stat. "
            "§ 908.102 requires law enforcement cooperation with federal immigration authorities. "
            "Florida does not offer in-state tuition based solely on attendance at Florida high "
            "schools for undocumented students."
        ),
    },
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
