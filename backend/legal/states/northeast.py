"""Northeast region state law citations.

States: CT, ME, MA, NH, NJ, NY, PA, RI, VT
"""

from __future__ import annotations

NORTHEAST_LAWS: dict[str, dict[str, str]] = {
    "CT": {
        "landlord_tenant": (
            "Connecticut General Statutes § 47a-1 through § 47a-74 govern residential tenancies. "
            "Security deposits are limited to two months' rent (C.G.S. § 47a-21) and must be returned "
            "within 30 days. Eviction requires a court process under C.G.S. § 47a-23. Rent increases "
            "require proper notice under C.G.S. § 47a-15."
        ),
        "employment_rights": (
            "The Connecticut Fair Employment Practices Act (C.G.S. § 46a-60) prohibits discrimination "
            "in employment. Minimum wage is set by C.G.S. § 31-58. The Connecticut Wage Payment Act "
            "(C.G.S. § 31-71a et seq.) governs timely payment. Paid sick leave is required under "
            "C.G.S. § 31-57s for employers with 50+ employees."
        ),
        "consumer_protection": (
            "The Connecticut Unfair Trade Practices Act (C.G.S. § 42-110a et seq.) prohibits unfair "
            "or deceptive acts and provides for punitive damages. The Lemon Law (C.G.S. § 42-179) "
            "covers new motor vehicles. The AG enforces consumer protection through C.G.S. § 42-110d."
        ),
        "debt_collections": (
            "Connecticut debt collection is governed by C.G.S. § 36a-645 et seq. The statute of "
            "limitations on written contracts is 6 years (C.G.S. § 52-576). Wage garnishment is "
            "limited to 25% of disposable earnings under C.G.S. § 52-361a. Homestead exemption "
            "protects up to $75,000 under C.G.S. § 52-352b(t)."
        ),
        "small_claims": (
            "Connecticut small claims court handles disputes up to $5,000 under C.G.S. § 51-15. "
            "Filing fees range from $50 to $100. Cases are heard in the Superior Court small claims "
            "session. Either party may transfer to the regular docket."
        ),
        "contract_disputes": (
            "Connecticut follows common law contract principles. The statute of frauds is at C.G.S. "
            "§ 52-550. Written contract SOL is 6 years (C.G.S. § 52-576); oral contracts also 6 years. "
            "The UCC governs sales of goods under C.G.S. Title 42a."
        ),
        "traffic_violations": (
            "Connecticut General Statutes Title 14 governs motor vehicles and traffic. Speeding "
            "penalties are under C.G.S. § 14-219. DUI is under C.G.S. § 14-227a. License suspensions "
            "are handled by the DMV under C.G.S. § 14-111. An online traffic school option may be "
            "available for eligible violations."
        ),
        "family_law": (
            "Connecticut dissolution of marriage is governed by C.G.S. § 46b-40 et seq. The state "
            "follows equitable distribution (C.G.S. § 46b-81). Child custody uses best interests "
            "standard (C.G.S. § 46b-56). Child support guidelines are in C.G.S. § 46b-215a. Alimony "
            "factors are in C.G.S. § 46b-82."
        ),
        "criminal_records": (
            "Connecticut allows erasure of criminal records under C.G.S. § 54-142a for dismissed "
            "cases and pardoned convictions. The Clean Slate Act (Public Act 21-32) provides automatic "
            "erasure for certain misdemeanors. Ban-the-box applies to employers under C.G.S. § 31-51i."
        ),
        "immigration": (
            "Connecticut's TRUST Act (C.G.S. § 54-192h) limits cooperation with ICE detainers. "
            "C.G.S. § 10a-29 provides in-state tuition for undocumented students who attended "
            "Connecticut high schools. Driver's licenses are available to all residents under "
            "C.G.S. § 14-36a regardless of immigration status."
        ),
    },
    "ME": {
        "landlord_tenant": (
            "Maine's landlord-tenant law is in 14 M.R.S.A. §§ 6001-6046. Security deposits are "
            "limited to two months' rent (14 M.R.S.A. § 6032) and must be returned within 30 days. "
            "Eviction requires a 7-day notice for nonpayment (14 M.R.S.A. § 6002). Rent increase "
            "requires 45 days' notice (14 M.R.S.A. § 6015)."
        ),
        "employment_rights": (
            "The Maine Human Rights Act (5 M.R.S.A. § 4571 et seq.) prohibits employment "
            "discrimination. Minimum wage is set by 26 M.R.S.A. § 664. Maine requires earned paid "
            "leave under 26 M.R.S.A. § 637. Whistleblower protection is under 26 M.R.S.A. § 833."
        ),
        "consumer_protection": (
            "Maine's Unfair Trade Practices Act (5 M.R.S.A. § 207) prohibits unfair or deceptive "
            "practices. The Lemon Law (10 M.R.S.A. § 1161 et seq.) covers new vehicles. The AG "
            "enforces consumer protection. Maine's Used Car Lemon Law is at 10 M.R.S.A. § 1475."
        ),
        "debt_collections": (
            "Maine Fair Debt Collection Practices Act (32 M.R.S.A. § 11001 et seq.) governs "
            "collectors. The statute of limitations on written contracts is 6 years (14 M.R.S.A. "
            "§ 752). Wage garnishment follows 14 M.R.S.A. § 3127. Homestead exemption protects "
            "up to $80,000 under 14 M.R.S.A. § 4422(1)."
        ),
        "small_claims": (
            "Maine small claims court handles disputes up to $6,000 under 14 M.R.S.A. § 7481. "
            "Filing fees are approximately $50-$80. Cases are heard in District Court. Appeals go "
            "to Superior Court within 30 days."
        ),
        "contract_disputes": (
            "Maine follows common law contract principles and the UCC (11 M.R.S.A.) for goods. "
            "The statute of frauds is at 33 M.R.S.A. § 51. Written contract SOL is 6 years "
            "(14 M.R.S.A. § 752); oral is also 6 years."
        ),
        "traffic_violations": (
            "Maine traffic law is in 29-A M.R.S.A. Speeding penalties are under 29-A M.R.S.A. "
            "§ 2074. OUI is under 29-A M.R.S.A. § 2411. License suspensions are handled by the "
            "Secretary of State under 29-A M.R.S.A. § 2451."
        ),
        "family_law": (
            "Maine divorce is governed by 19-A M.R.S.A. § 901 et seq. The state follows equitable "
            "distribution (19-A M.R.S.A. § 953). Parental rights use best interests standard "
            "(19-A M.R.S.A. § 1653). Child support guidelines are in 19-A M.R.S.A. § 2001."
        ),
        "criminal_records": (
            "Maine allows expungement of certain records under 15 M.R.S.A. § 2169. Criminal "
            "history record information is governed by 16 M.R.S.A. § 703. Maine does not have a "
            "comprehensive ban-the-box law, though some municipalities have adopted ordinances."
        ),
        "immigration": (
            "Maine does not have sanctuary state policies. Driver's licenses require legal presence "
            "documentation. 20-A M.R.S.A. § 12542 governs in-state tuition eligibility. Maine "
            "provides some state-funded assistance to asylum seekers through general assistance "
            "programs under 22 M.R.S.A. § 4301."
        ),
    },
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
    "NH": {
        "landlord_tenant": (
            "New Hampshire RSA 540 governs landlord-tenant relations. Security deposits are limited "
            "to one month's rent or $100, whichever is greater (RSA 540-A:6). Deposits must be "
            "returned within 30 days (RSA 540-A:7). Eviction requires a 7-day notice for nonpayment "
            "(RSA 540:3). Retaliation by landlords is prohibited under RSA 540:13-a."
        ),
        "employment_rights": (
            "New Hampshire RSA 354-A (Law Against Discrimination) prohibits employment discrimination. "
            "Minimum wage follows the federal rate; RSA 279:21 governs wage payment. RSA 275:43 "
            "requires timely payment of wages on termination. Whistleblower protection is under "
            "RSA 275-E."
        ),
        "consumer_protection": (
            "New Hampshire Consumer Protection Act (RSA 358-A) prohibits unfair or deceptive practices "
            "and provides treble damages. The Lemon Law (RSA 357-D) covers new motor vehicles. The AG "
            "enforces consumer protection under RSA 358-A:4."
        ),
        "debt_collections": (
            "New Hampshire RSA 358-C governs debt collection. The statute of limitations on written "
            "contracts is 3 years (RSA 508:4). Wage garnishment follows RSA 512:21. Homestead "
            "exemption protects up to $120,000 under RSA 480:1."
        ),
        "small_claims": (
            "New Hampshire small claims court handles disputes up to $10,000 under RSA 503:1. Filing "
            "fees are approximately $45-$80. Cases are heard in District Court. Appeals go to Superior "
            "Court for trial de novo."
        ),
        "contract_disputes": (
            "New Hampshire follows common law contract principles. The statute of frauds is at "
            "RSA 506:2. Written contract SOL is 3 years (RSA 508:4). The UCC governs sales of goods "
            "under RSA Title 27."
        ),
        "traffic_violations": (
            "New Hampshire traffic law is in RSA Title XXI. Speeding is under RSA 265:60. DUI is "
            "under RSA 265-A:2. License suspensions are handled by the DMV under RSA 263. New "
            "Hampshire does not require mandatory auto insurance but has financial responsibility "
            "requirements under RSA 264."
        ),
        "family_law": (
            "New Hampshire divorce is governed by RSA 458. The state follows equitable distribution "
            "(RSA 458:16-a). Child custody uses best interests standard (RSA 461-A:6). Child support "
            "guidelines are in RSA 458-C. Alimony factors are in RSA 458:19."
        ),
        "criminal_records": (
            "New Hampshire allows annulment (expungement) of criminal records under RSA 651:5. "
            "Waiting periods vary by offense severity. RSA 651:5(X) governs the annulment process. "
            "New Hampshire does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "New Hampshire does not have sanctuary state policies. RSA 263:1 requires legal presence "
            "for driver's licenses. New Hampshire does not provide in-state tuition benefits based "
            "on immigration status. State law enforcement generally cooperates with federal "
            "immigration authorities."
        ),
    },
    "NJ": {
        "landlord_tenant": (
            "New Jersey's Anti-Eviction Act (N.J.S.A. 2A:18-61.1) provides strong tenant protections "
            "requiring good cause for eviction. Security deposits are limited to 1.5 months' rent "
            "(N.J.S.A. 46:8-21.2) and must be held in an interest-bearing account. The Truth in "
            "Renting Act (N.J.S.A. 46:8-43 et seq.) requires disclosure of tenant rights."
        ),
        "employment_rights": (
            "The New Jersey Law Against Discrimination (N.J.S.A. 10:5-1 et seq.) provides broad "
            "employment protections. Minimum wage is set by N.J.S.A. 34:11-56a4. The NJ WARN Act "
            "(N.J.S.A. 34:21-1) requires 90 days' notice for mass layoffs. Earned sick leave is "
            "mandated under N.J.S.A. 34:11D-1. Non-competes are restricted under N.J.S.A. 34:6A-18."
        ),
        "consumer_protection": (
            "New Jersey Consumer Fraud Act (N.J.S.A. 56:8-1 et seq.) provides treble damages and "
            "attorney fees for unconscionable practices. The Lemon Law (N.J.S.A. 56:12-29 et seq.) "
            "covers new vehicles. The Division of Consumer Affairs enforces protections."
        ),
        "debt_collections": (
            "New Jersey debt collection is regulated under N.J.S.A. 45:18-1 et seq. The statute of "
            "limitations on written contracts is 6 years (N.J.S.A. 2A:14-1). Wage garnishment is "
            "limited to 10% of gross income under N.J.S.A. 2A:17-56. Homestead exemption is not "
            "available in New Jersey, but personal property exemptions exist."
        ),
        "small_claims": (
            "New Jersey small claims court handles disputes up to $5,000 ($3,000 for landlord "
            "security deposit cases) under N.J.S.A. 2A:6-43. Filing fees range from $15 to $50. "
            "Cases are heard in the Special Civil Part of Superior Court. Mediation is available."
        ),
        "contract_disputes": (
            "New Jersey follows common law and the UCC (N.J.S.A. 12A:2-101 et seq.) for goods. The "
            "statute of frauds is at N.J.S.A. 25:1-5. Written contract SOL is 6 years (N.J.S.A. "
            "2A:14-1). The Contractual Liability Act (N.J.S.A. 2A:58C-1) limits product liability."
        ),
        "traffic_violations": (
            "New Jersey Title 39 governs motor vehicles and traffic. Speeding is under N.J.S.A. "
            "39:4-98. DUI is under N.J.S.A. 39:4-50. Points are assigned under N.J.A.C. 13:19-10.1. "
            "Defensive driving courses can reduce points. Municipal courts handle traffic cases."
        ),
        "family_law": (
            "New Jersey divorce is governed by N.J.S.A. 2A:34-2 (no-fault available). The state "
            "follows equitable distribution (N.J.S.A. 2A:34-23.1). Custody uses best interests "
            "standard (N.J.S.A. 9:2-4). Child support guidelines are in N.J.C.S.A. Rules Appendix "
            "IX-A. Alimony was reformed under N.J.S.A. 2A:34-23."
        ),
        "criminal_records": (
            "New Jersey's Clean Slate Law (N.J.S.A. 2C:52-5.3) provides automatic expungement of "
            "certain convictions after 10 years. Traditional expungement is under N.J.S.A. 2C:52-1 "
            "et seq. The Opportunity to Compete Act (N.J.S.A. 34:6B-11) is a ban-the-box law."
        ),
        "immigration": (
            "New Jersey's Immigrant Trust Directive (AG Directive 2018-6) limits law enforcement "
            "cooperation with ICE. N.J.S.A. 39:3-10 provides driver's licenses regardless of "
            "immigration status. N.J.S.A. 18A:62-4.4 allows in-state tuition for undocumented "
            "students who attended NJ high schools."
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
    "PA": {
        "landlord_tenant": (
            "Pennsylvania's Landlord and Tenant Act (68 Pa.C.S. § 250.101 et seq.) governs "
            "residential tenancies. Security deposits are limited to two months' rent in the first "
            "year and one month thereafter (68 Pa.C.S. § 250.511a). Deposits must be returned within "
            "30 days. Eviction requires a 10-day notice for nonpayment (68 Pa.C.S. § 250.501)."
        ),
        "employment_rights": (
            "The Pennsylvania Human Relations Act (43 P.S. § 951 et seq.) prohibits employment "
            "discrimination. Pennsylvania Minimum Wage Act (43 P.S. § 333.101 et seq.) sets minimum "
            "wage. The Wage Payment and Collection Law (43 P.S. § 260.1 et seq.) governs timely "
            "payment. Whistleblower protection is under 43 P.S. § 1421 et seq."
        ),
        "consumer_protection": (
            "Pennsylvania's Unfair Trade Practices and Consumer Protection Law (73 P.S. § 201-1 "
            "et seq.) prohibits deceptive practices and provides treble damages. The Automobile "
            "Lemon Law (73 P.S. § 1951 et seq.) covers new vehicles. The AG enforces through the "
            "Bureau of Consumer Protection."
        ),
        "debt_collections": (
            "Pennsylvania Fair Credit Extension Uniformity Act (73 P.S. § 2270.1 et seq.) governs "
            "debt collection. The statute of limitations on written contracts is 4 years (42 Pa.C.S. "
            "§ 5525). Pennsylvania does not allow wage garnishment for most consumer debts. Homestead "
            "exemption is not available, but personal property exemptions exist under 42 Pa.C.S. § 8123."
        ),
        "small_claims": (
            "Pennsylvania magistrate courts handle small claims up to $12,000 under 42 Pa.C.S. "
            "§ 1515. Filing fees range from $45 to $125. Cases can be appealed to the Court of "
            "Common Pleas for trial de novo within 30 days."
        ),
        "contract_disputes": (
            "Pennsylvania follows common law and the UCC (13 Pa.C.S.) for goods. The statute of "
            "frauds is at 33 P.S. § 3. Written contract SOL is 4 years (42 Pa.C.S. § 5525). "
            "Non-compete agreements are enforceable if reasonable in scope and duration."
        ),
        "traffic_violations": (
            "Pennsylvania Vehicle Code (75 Pa.C.S.) governs traffic. Speeding is under 75 Pa.C.S. "
            "§ 3362. DUI is under 75 Pa.C.S. § 3802. Points accumulate under 75 Pa.C.S. § 1535. "
            "License suspensions are handled by PennDOT. Accelerated Rehabilitative Disposition "
            "(ARD) is available for first-time DUI offenders."
        ),
        "family_law": (
            "Pennsylvania divorce is governed by 23 Pa.C.S. § 3301 et seq. The state follows "
            "equitable distribution (23 Pa.C.S. § 3502). Custody uses best interests standard "
            "(23 Pa.C.S. § 5328). Child support guidelines are in Pa.R.C.P. 1910.16. Alimony "
            "factors are in 23 Pa.C.S. § 3701."
        ),
        "criminal_records": (
            "Pennsylvania's Clean Slate Law (18 Pa.C.S. § 9122.2) provides automatic sealing of "
            "certain non-conviction records and minor offenses. Expungement is available under "
            "18 Pa.C.S. § 9122. Ban-the-box applies to state and local government employers under "
            "Executive Order 2018-04."
        ),
        "immigration": (
            "Pennsylvania does not have a statewide sanctuary policy, though Philadelphia has a "
            "sanctuary city policy. Driver's licenses require proof of legal presence under "
            "75 Pa.C.S. § 1510. Pennsylvania does not provide in-state tuition specifically for "
            "undocumented students at the state level."
        ),
    },
    "RI": {
        "landlord_tenant": (
            "Rhode Island Residential Landlord and Tenant Act (R.I. Gen. Laws § 34-18-1 et seq.) "
            "governs tenancies. Security deposits are limited to one month's rent (R.I. Gen. Laws "
            "§ 34-18-19) and must be returned within 20 days. Eviction requires a 5-day notice for "
            "nonpayment (R.I. Gen. Laws § 34-18-35)."
        ),
        "employment_rights": (
            "Rhode Island Fair Employment Practices Act (R.I. Gen. Laws § 28-5-1 et seq.) prohibits "
            "discrimination. Minimum wage is set by R.I. Gen. Laws § 28-12-3. The Payment of Wages "
            "Act (R.I. Gen. Laws § 28-14-1 et seq.) governs timely payment. Paid sick leave is "
            "required under R.I. Gen. Laws § 28-57-1."
        ),
        "consumer_protection": (
            "Rhode Island Deceptive Trade Practices Act (R.I. Gen. Laws § 6-13.1-1 et seq.) "
            "prohibits unfair practices. The Lemon Law (R.I. Gen. Laws § 31-5.2-1 et seq.) covers "
            "new vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Rhode Island debt collection is governed by R.I. Gen. Laws § 19-14.9-1 et seq. The "
            "statute of limitations on written contracts is 10 years (R.I. Gen. Laws § 9-1-13). "
            "Wage garnishment follows R.I. Gen. Laws § 9-26-4. Homestead exemption protects up to "
            "$500,000 under R.I. Gen. Laws § 9-26-4.1."
        ),
        "small_claims": (
            "Rhode Island small claims court handles disputes up to $5,000 under R.I. Gen. Laws "
            "§ 10-16-1. Filing fees are approximately $30-$50. Cases are heard in District Court. "
            "Appeals go to Superior Court within 2 days."
        ),
        "contract_disputes": (
            "Rhode Island follows common law and the UCC (R.I. Gen. Laws Title 6A) for goods. The "
            "statute of frauds is at R.I. Gen. Laws § 9-1-4. Written contract SOL is 10 years "
            "(R.I. Gen. Laws § 9-1-13); oral is 10 years."
        ),
        "traffic_violations": (
            "Rhode Island traffic law is in R.I. Gen. Laws Title 31. Speeding is under R.I. Gen. "
            "Laws § 31-14-2. DUI is under R.I. Gen. Laws § 31-27-2. License suspensions are handled "
            "by the DMV. Traffic Tribunal handles contested violations under R.I. Gen. Laws § 31-41.1-1."
        ),
        "family_law": (
            "Rhode Island divorce is governed by R.I. Gen. Laws § 15-5-1 et seq. The state follows "
            "equitable distribution (R.I. Gen. Laws § 15-5-16.1). Custody uses best interests "
            "standard (R.I. Gen. Laws § 15-5-16). Child support guidelines are in R.I. Family "
            "Court Administrative Order 2012-08."
        ),
        "criminal_records": (
            "Rhode Island allows expungement under R.I. Gen. Laws § 12-1.3-1 et seq. First offender "
            "misdemeanors can be expunged after 5 years; felonies after 10 years. R.I. Gen. Laws "
            "§ 28-5.1-14 limits employer inquiries into sealed records."
        ),
        "immigration": (
            "Rhode Island does not have comprehensive sanctuary state policies. The Trust Act "
            "executive order limits cooperation with ICE in certain circumstances. Driver's licenses "
            "require legal presence. R.I. Gen. Laws § 16-57-4 provides in-state tuition for certain "
            "undocumented students who attended RI high schools."
        ),
    },
    "VT": {
        "landlord_tenant": (
            "Vermont's Residential Rental Agreements Act (9 V.S.A. § 4451 et seq.) governs "
            "tenancies. Security deposits are limited to one month's rent for unfurnished units "
            "(9 V.S.A. § 4461) and must be returned within 14 days. Eviction requires a 14-day "
            "notice for nonpayment (9 V.S.A. § 4467). Landlords must provide notice of lead paint "
            "under 18 V.S.A. § 1759."
        ),
        "employment_rights": (
            "Vermont Fair Employment Practices Act (21 V.S.A. § 495 et seq.) prohibits "
            "discrimination. Minimum wage is set by 21 V.S.A. § 384. Vermont requires earned "
            "sick time under 21 V.S.A. § 481. Parental leave is mandated under 21 V.S.A. § 472."
        ),
        "consumer_protection": (
            "Vermont Consumer Protection Act (9 V.S.A. § 2451 et seq.) prohibits unfair or "
            "deceptive practices. The Lemon Law (9 V.S.A. § 4170 et seq.) covers new motor "
            "vehicles. The AG's Consumer Assistance Program handles complaints."
        ),
        "debt_collections": (
            "Vermont debt collection is regulated under 9 V.S.A. § 2451a. The statute of "
            "limitations on written contracts is 6 years (12 V.S.A. § 511). Wage garnishment "
            "follows 12 V.S.A. § 3170. Homestead exemption protects up to $125,000 under "
            "27 V.S.A. § 101."
        ),
        "small_claims": (
            "Vermont small claims court handles disputes up to $5,000 under 12 V.S.A. § 5531. "
            "Filing fees are approximately $75. Cases are heard in the Civil Division of Superior "
            "Court. Appeals go to the Civil Division within 30 days."
        ),
        "contract_disputes": (
            "Vermont follows common law and the UCC (9A V.S.A.) for goods. The statute of frauds "
            "is at 12 V.S.A. § 181. Written contract SOL is 6 years (12 V.S.A. § 511). Oral "
            "contract SOL is 6 years."
        ),
        "traffic_violations": (
            "Vermont traffic law is in 23 V.S.A. Title 23. Speeding is under 23 V.S.A. § 1081. "
            "DUI is under 23 V.S.A. § 1201. License suspensions are handled by the DMV under "
            "23 V.S.A. § 636. The Judicial Bureau handles traffic violations."
        ),
        "family_law": (
            "Vermont divorce is governed by 15 V.S.A. § 551 et seq. The state follows equitable "
            "distribution (15 V.S.A. § 751). Custody uses best interests standard (15 V.S.A. "
            "§ 665). Child support guidelines are in 15 V.S.A. § 656. Vermont was the first state "
            "to offer civil unions (15 V.S.A. § 1201, now superseded by marriage equality)."
        ),
        "criminal_records": (
            "Vermont allows expungement of certain records under 13 V.S.A. § 7602. Automatic "
            "expungement is available for qualifying misdemeanors. Vermont's ban-the-box law "
            "(21 V.S.A. § 495j) restricts employer inquiries on initial applications."
        ),
        "immigration": (
            "Vermont does not have formal sanctuary state policies. Driver's privilege cards are "
            "available to all residents under 23 V.S.A. § 603(b) regardless of immigration status. "
            "Vermont provides in-state tuition for undocumented students under 16 V.S.A. § 2185."
        ),
    },
}
