"""Midwest region state law citations.

States: IA, IL, IN, KS, MI, MN, MO, NE, ND, OH, SD, WI
"""

from __future__ import annotations

MIDWEST_LAWS: dict[str, dict[str, str]] = {
    "IA": {
        "landlord_tenant": (
            "Iowa Uniform Residential Landlord and Tenant Act (Iowa Code § 562A.1 et seq.) governs "
            "tenancies. Security deposits are limited to two months' rent (Iowa Code § 562A.12) and "
            "must be returned within 30 days. Eviction requires a 3-day notice for nonpayment (Iowa "
            "Code § 562A.27). Retaliatory eviction is prohibited under Iowa Code § 562A.36."
        ),
        "employment_rights": (
            "Iowa Civil Rights Act (Iowa Code § 216.1 et seq.) prohibits employment discrimination "
            "for employers with 4+ employees. Iowa minimum wage is set by Iowa Code § 91D.1. The "
            "Wage Payment Collection Act (Iowa Code § 91A.1 et seq.) governs timely payment. "
            "Workers' compensation is under Iowa Code § 85.1 et seq."
        ),
        "consumer_protection": (
            "Iowa Consumer Fraud Act (Iowa Code § 714H.1 et seq.) prohibits deceptive practices "
            "and provides actual damages plus attorney fees. The Lemon Law (Iowa Code § 322G.1 "
            "et seq.) covers new vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Iowa Debt Collection Practices Act (Iowa Code § 537.7101 et seq.) governs collectors. "
            "The statute of limitations on written contracts is 10 years (Iowa Code § 614.1(5)). "
            "Wage garnishment follows Iowa Code § 642.21. Homestead exemption protects up to "
            "one-half acre in a city under Iowa Code § 561.2."
        ),
        "small_claims": (
            "Iowa small claims court handles disputes up to $6,500 under Iowa Code § 631.1. Filing "
            "fees are approximately $95. Cases are heard in the small claims division of District "
            "Court. Appeals go to District Court within 20 days."
        ),
        "contract_disputes": (
            "Iowa follows common law and the UCC (Iowa Code Chapter 554) for goods. The statute of "
            "frauds is at Iowa Code § 622.32. Written contract SOL is 10 years (Iowa Code "
            "§ 614.1(5)); oral is 5 years (Iowa Code § 614.1(4))."
        ),
        "traffic_violations": (
            "Iowa traffic law is in Iowa Code Chapter 321. Speeding is under Iowa Code § 321.285. "
            "OWI is under Iowa Code § 321J.2. Points accumulate under Iowa Code § 321.210. License "
            "suspensions are handled by the DOT."
        ),
        "family_law": (
            "Iowa dissolution of marriage is governed by Iowa Code § 598.1 et seq. Iowa follows "
            "equitable distribution (Iowa Code § 598.21). Custody uses best interests standard "
            "(Iowa Code § 598.41). Child support guidelines are in Iowa Ct. R. 9.1 et seq."
        ),
        "criminal_records": (
            "Iowa allows expungement of acquittals and deferred judgments under Iowa Code § 901C.1 "
            "et seq. Certain misdemeanors and non-violent felonies may be expunged after 8 years. "
            "Iowa does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Iowa enacted SF 2340 requiring law enforcement to cooperate with federal immigration "
            "authorities. Driver's licenses require legal presence under Iowa Code § 321.182. "
            "Iowa does not provide in-state tuition for undocumented students."
        ),
    },
    "IL": {
        "landlord_tenant": (
            "Illinois landlord-tenant law is governed by the Chicago RLTO in Chicago and common law "
            "elsewhere. Security deposit return is governed by 765 ILCS 710/1 (Security Deposit "
            "Return Act) requiring return within 30-45 days. Eviction requires a 5-day notice for "
            "nonpayment under 735 ILCS 5/9-209. The Tenant Utility Payment Disclosure Act is at "
            "765 ILCS 740/1."
        ),
        "employment_rights": (
            "Illinois Human Rights Act (775 ILCS 5/1-101 et seq.) prohibits employment "
            "discrimination. Minimum wage is set by 820 ILCS 105/4. The Illinois Wage Payment and "
            "Collection Act (820 ILCS 115/1 et seq.) governs timely payment. The Illinois Freedom "
            "to Work Act (820 ILCS 90/1) restricts non-compete agreements for low-wage workers."
        ),
        "consumer_protection": (
            "Illinois Consumer Fraud and Deceptive Business Practices Act (815 ILCS 505/1 et seq.) "
            "prohibits fraud and deception with actual damages and attorney fees. The Lemon Law "
            "(815 ILCS 380/1 et seq.) covers new vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Illinois Collection Agency Act (225 ILCS 425/1 et seq.) regulates collectors. The "
            "statute of limitations on written contracts is 10 years (735 ILCS 5/13-206). Wage "
            "garnishment is limited to 15% of gross wages under 735 ILCS 5/12-803. Homestead "
            "exemption protects up to $15,000 under 735 ILCS 5/12-901."
        ),
        "small_claims": (
            "Illinois small claims court handles disputes up to $10,000 under 735 ILCS 5/2-101. "
            "Filing fees range from $50 to $200. Cases are heard in the Circuit Court small claims "
            "division. Appeals go to the Appellate Court within 30 days."
        ),
        "contract_disputes": (
            "Illinois follows common law and the UCC (810 ILCS 5/) for goods. The statute of frauds "
            "is at 740 ILCS 80/1. Written contract SOL is 10 years (735 ILCS 5/13-206); oral is "
            "5 years (735 ILCS 5/13-205)."
        ),
        "traffic_violations": (
            "Illinois Vehicle Code (625 ILCS 5/) governs traffic. Speeding is under 625 ILCS "
            "5/11-601. DUI is under 625 ILCS 5/11-501. Points are not used; instead, three moving "
            "violations in 12 months triggers suspension under 625 ILCS 5/6-206. License suspensions "
            "are handled by the Secretary of State."
        ),
        "family_law": (
            "Illinois Marriage and Dissolution of Marriage Act (750 ILCS 5/101 et seq.) governs "
            "divorce. The state follows equitable distribution (750 ILCS 5/503). Custody uses best "
            "interests standard (750 ILCS 5/602.7). Child support guidelines are in 750 ILCS 5/505. "
            "Maintenance follows statutory formula under 750 ILCS 5/504."
        ),
        "criminal_records": (
            "Illinois allows expungement and sealing under 20 ILCS 2630/5.2. The Criminal "
            "Identification Act governs the process. Cannabis convictions may be automatically "
            "expunged. Illinois's ban-the-box law (820 ILCS 75/15) applies to employers with "
            "15+ employees."
        ),
        "immigration": (
            "Illinois TRUST Act (5 ILCS 805/1) limits law enforcement cooperation with ICE. "
            "Illinois provides driver's licenses to all residents under the Temporary Visitor "
            "Driver's License program (625 ILCS 5/6-105.1). In-state tuition is available for "
            "undocumented students under 110 ILCS 305/7e-5."
        ),
    },
    "IN": {
        "landlord_tenant": (
            "Indiana landlord-tenant law is in Ind. Code § 32-31-1-1 et seq. Security deposits are "
            "limited to one month's rent for most situations. Deposits must be returned within 45 "
            "days (Ind. Code § 32-31-3-12). Eviction requires a 10-day notice for nonpayment "
            "(Ind. Code § 32-31-1-6)."
        ),
        "employment_rights": (
            "Indiana Civil Rights Law (Ind. Code § 22-9-1-1 et seq.) prohibits employment "
            "discrimination for employers with 6+ employees. Indiana follows the federal minimum "
            "wage. The Wage Claims Act (Ind. Code § 22-2-9-1 et seq.) governs timely payment. "
            "Workers' compensation is under Ind. Code § 22-3-2-1 et seq."
        ),
        "consumer_protection": (
            "Indiana Deceptive Consumer Sales Act (Ind. Code § 24-5-0.5-1 et seq.) prohibits "
            "deceptive practices with treble damages for knowing violations. The Lemon Law (Ind. "
            "Code § 24-5-13-1 et seq.) covers new vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Indiana does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 10 years (Ind. Code § 34-11-2-11). Wage "
            "garnishment follows Ind. Code § 24-4.5-5-105 with 25% of disposable earnings limit. "
            "Homestead exemption protects up to $19,300 under Ind. Code § 34-55-10-2(c)(1)."
        ),
        "small_claims": (
            "Indiana small claims court handles disputes up to $10,000 under Ind. Code § 33-34-3-2. "
            "Filing fees are approximately $35-$97. Cases are heard in the small claims division of "
            "the Marion County courts or township courts. Appeals go within 30 days."
        ),
        "contract_disputes": (
            "Indiana follows common law and the UCC (Ind. Code Title 26) for goods. The statute "
            "of frauds is at Ind. Code § 32-21-1-1. Written contract SOL is 10 years (Ind. Code "
            "§ 34-11-2-11); oral is 6 years (Ind. Code § 34-11-2-7)."
        ),
        "traffic_violations": (
            "Indiana traffic law is in Ind. Code Title 9. Speeding is under Ind. Code § 9-21-5-1 "
            "et seq. OWI is under Ind. Code § 9-30-5-1. Points accumulate under Ind. Code "
            "§ 9-24-18-14.5. License suspensions are handled by the BMV."
        ),
        "family_law": (
            "Indiana dissolution of marriage is governed by Ind. Code § 31-15-1-1 et seq. The "
            "state follows equitable distribution with a presumption of equal division (Ind. Code "
            "§ 31-15-7-5). Custody uses best interests standard (Ind. Code § 31-17-2-8). Child "
            "support guidelines are in Indiana Child Support Rules."
        ),
        "criminal_records": (
            "Indiana allows expungement under Ind. Code § 35-38-9-1 et seq. Misdemeanors may be "
            "expunged 5 years after conviction; felonies 8-10 years depending on severity. Indiana's "
            "ban-the-box law (Ind. Code § 22-2-17-3) applies to state and local government."
        ),
        "immigration": (
            "Indiana enacted SEA 590 requiring law enforcement cooperation with federal immigration "
            "authorities. Driver's licenses require legal presence under Ind. Code § 9-24-9-1. "
            "Indiana does not provide in-state tuition for undocumented students."
        ),
    },
    "KS": {
        "landlord_tenant": (
            "Kansas Residential Landlord and Tenant Act (K.S.A. § 58-2540 et seq.) governs "
            "tenancies. Security deposits are limited to one month's rent for unfurnished units "
            "(K.S.A. § 58-2550). Deposits must be returned within 30 days (K.S.A. § 58-2550). "
            "Eviction requires a 3-day notice for nonpayment (K.S.A. § 58-2564)."
        ),
        "employment_rights": (
            "Kansas Act Against Discrimination (K.S.A. § 44-1001 et seq.) prohibits employment "
            "discrimination for employers with 4+ employees. Kansas follows the federal minimum "
            "wage. The Wage Payment Act (K.S.A. § 44-313 et seq.) governs timely payment. Workers' "
            "compensation is under K.S.A. § 44-501 et seq."
        ),
        "consumer_protection": (
            "Kansas Consumer Protection Act (K.S.A. § 50-623 et seq.) prohibits deceptive and "
            "unconscionable practices. The Lemon Law (K.S.A. § 50-645 et seq.) covers new vehicles. "
            "The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Kansas does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 5 years (K.S.A. § 60-511). Wage garnishment "
            "follows K.S.A. § 60-2310 with 25% of disposable earnings limit. Homestead exemption "
            "protects 160 acres outside city limits under K.S.A. § 60-2301."
        ),
        "small_claims": (
            "Kansas small claims court handles disputes up to $4,000 under K.S.A. § 61-2703. "
            "Filing fees are approximately $55-$75. Cases are heard in the Limited Actions division "
            "of District Court. Appeals go within 14 days."
        ),
        "contract_disputes": (
            "Kansas follows common law and the UCC (K.S.A. Chapter 84) for goods. The statute of "
            "frauds is at K.S.A. § 33-106. Written contract SOL is 5 years (K.S.A. § 60-511); "
            "oral is 3 years (K.S.A. § 60-512)."
        ),
        "traffic_violations": (
            "Kansas traffic law is in K.S.A. Chapter 8. Speeding is under K.S.A. § 8-1557. DUI "
            "is under K.S.A. § 8-1567. Points are not used in Kansas; instead, habitual violator "
            "status triggers suspension under K.S.A. § 8-286. License suspensions are handled by "
            "the Division of Vehicles."
        ),
        "family_law": (
            "Kansas divorce is governed by K.S.A. § 23-2701 et seq. The state follows equitable "
            "distribution (K.S.A. § 23-2802). Custody uses best interests standard (K.S.A. "
            "§ 23-3222). Child support guidelines are in K.S.A. § 23-3001 et seq."
        ),
        "criminal_records": (
            "Kansas allows expungement under K.S.A. § 21-6614. Misdemeanors may be expunged 3-5 "
            "years after completion of sentence; certain felonies after 5-10 years. Kansas does "
            "not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Kansas enacted K.S.A. § 75-723 requiring state agencies to verify immigration status. "
            "Driver's licenses require legal presence under K.S.A. § 8-240. Kansas provides "
            "in-state tuition for certain undocumented students under K.S.A. § 76-731a."
        ),
    },
    "MI": {
        "landlord_tenant": (
            "Michigan's Truth in Renting Act (MCL § 554.631 et seq.) and the Summary Proceedings "
            "Act (MCL § 600.5701 et seq.) govern tenancies. Security deposits are limited to 1.5 "
            "months' rent (MCL § 554.602). Deposits must be returned within 30 days (MCL § 554.609). "
            "Eviction requires a 7-day notice for nonpayment (MCL § 554.134)."
        ),
        "employment_rights": (
            "Michigan Elliott-Larsen Civil Rights Act (MCL § 37.2101 et seq.) prohibits employment "
            "discrimination. Michigan minimum wage is set by MCL § 408.384. The Payment of Wages "
            "and Fringe Benefits Act (MCL § 408.471 et seq.) governs timely payment. Workers' "
            "compensation is under MCL § 418.101 et seq."
        ),
        "consumer_protection": (
            "Michigan Consumer Protection Act (MCL § 445.901 et seq.) prohibits unfair or deceptive "
            "practices. The Lemon Law (MCL § 257.1401 et seq.) covers new vehicles. The AG enforces "
            "consumer protection."
        ),
        "debt_collections": (
            "Michigan Collection Practices Act (MCL § 445.251 et seq.) governs collectors. The "
            "statute of limitations on written contracts is 6 years (MCL § 600.5807). Wage "
            "garnishment follows MCL § 600.4012 with 25% of disposable earnings limit. Homestead "
            "exemption protects up to $42,775 under MCL § 600.6023."
        ),
        "small_claims": (
            "Michigan small claims court handles disputes up to $6,500 under MCL § 600.8401. "
            "Filing fees are approximately $30-$70. Cases are heard in District Court. No attorneys "
            "are permitted. Appeals go to Circuit Court within 7 days."
        ),
        "contract_disputes": (
            "Michigan follows common law and the UCC (MCL Chapter 440) for goods. The statute of "
            "frauds is at MCL § 566.132. Written contract SOL is 6 years (MCL § 600.5807); oral "
            "is 6 years."
        ),
        "traffic_violations": (
            "Michigan Vehicle Code (MCL § 257.1 et seq.) governs traffic. Speeding is under MCL "
            "§ 257.627. OWI is under MCL § 257.625. Points accumulate under MCL § 257.320a. "
            "License suspensions are handled by the Secretary of State."
        ),
        "family_law": (
            "Michigan divorce is governed by MCL § 552.1 et seq. The state follows equitable "
            "distribution (MCL § 552.19). Custody uses best interests factors (MCL § 722.23). "
            "Child support guidelines follow the Michigan Child Support Formula."
        ),
        "criminal_records": (
            "Michigan Clean Slate Act allows automatic expungement of certain misdemeanors after "
            "7 years and felonies after 10 years. Traditional expungement is under MCL § 780.621. "
            "Michigan's ban-the-box law applies to public employers."
        ),
        "immigration": (
            "Michigan does not have a statewide sanctuary policy. Driver's licenses require legal "
            "presence under MCL § 257.307. Michigan does not provide in-state tuition for "
            "undocumented students at the state level. Individual universities set their own policies."
        ),
    },
    "MN": {
        "landlord_tenant": (
            "Minnesota landlord-tenant law is in Minn. Stat. § 504B.001 et seq. Security deposits "
            "are limited by Minn. Stat. § 504B.178 and must be returned within 21 days with interest "
            "for deposits held over 12 months. Eviction requires a 14-day notice for nonpayment "
            "(Minn. Stat. § 504B.135). Tenant remedies are in Minn. Stat. § 504B.381."
        ),
        "employment_rights": (
            "Minnesota Human Rights Act (Minn. Stat. § 363A.01 et seq.) prohibits employment "
            "discrimination. Minimum wage is set by Minn. Stat. § 177.24. The Minnesota Wage Theft "
            "Prevention Act (Minn. Stat. § 181.101) governs timely payment. Paid sick and safe leave "
            "is required under Minn. Stat. § 181.9447."
        ),
        "consumer_protection": (
            "Minnesota Consumer Fraud Act (Minn. Stat. § 325F.68 et seq.) prohibits deceptive "
            "practices. The Private Attorney General statute (Minn. Stat. § 8.31) allows private "
            "enforcement. The Lemon Law (Minn. Stat. § 325F.665) covers new vehicles."
        ),
        "debt_collections": (
            "Minnesota Collection Agency Act (Minn. Stat. § 332.31 et seq.) regulates collectors. "
            "The statute of limitations on written contracts is 6 years (Minn. Stat. § 541.05). "
            "Wage garnishment follows Minn. Stat. § 571.55 with 25% of disposable earnings limit. "
            "Homestead exemption protects up to $450,000 under Minn. Stat. § 510.02."
        ),
        "small_claims": (
            "Minnesota conciliation court handles disputes up to $15,000 under Minn. Stat. "
            "§ 491A.01. Filing fees range from $75 to $100. Cases are heard in the conciliation "
            "court division. Appeals go to District Court within 20 days."
        ),
        "contract_disputes": (
            "Minnesota follows common law and the UCC (Minn. Stat. Chapter 336) for goods. The "
            "statute of frauds is at Minn. Stat. § 513.01. Written contract SOL is 6 years "
            "(Minn. Stat. § 541.05); oral is 6 years."
        ),
        "traffic_violations": (
            "Minnesota traffic law is in Minn. Stat. Chapter 169. Speeding is under Minn. Stat. "
            "§ 169.14. DWI is under Minn. Stat. § 169A.20. License revocations are handled by "
            "the Department of Public Safety under Minn. Stat. § 171.18."
        ),
        "family_law": (
            "Minnesota dissolution of marriage is governed by Minn. Stat. § 518.002 et seq. The "
            "state follows equitable distribution (Minn. Stat. § 518.58). Custody uses best "
            "interests factors (Minn. Stat. § 518.17). Child support guidelines are in Minn. "
            "Stat. § 518A.34."
        ),
        "criminal_records": (
            "Minnesota allows expungement under Minn. Stat. § 609A.01 et seq. Petitions can be "
            "filed for dismissed cases, certain misdemeanors, and qualifying felonies. Minnesota "
            "has a ban-the-box law (Minn. Stat. § 364.021) for both public and private employers."
        ),
        "immigration": (
            "Minnesota does not have a statewide sanctuary policy but several cities limit ICE "
            "cooperation. Driver's licenses are available to all residents under Minn. Stat. "
            "§ 171.04. Minnesota provides in-state tuition for undocumented students under the "
            "Minnesota DREAM Act (Minn. Stat. § 135A.043)."
        ),
    },
    "MO": {
        "landlord_tenant": (
            "Missouri landlord-tenant law is in Mo. Rev. Stat. § 441.005 et seq. Security deposits "
            "are limited to two months' rent (Mo. Rev. Stat. § 535.300) and must be returned within "
            "30 days. Eviction requires a rent and possession suit under Mo. Rev. Stat. § 535.010. "
            "No statewide rent control exists."
        ),
        "employment_rights": (
            "Missouri Human Rights Act (Mo. Rev. Stat. § 213.010 et seq.) prohibits employment "
            "discrimination for employers with 6+ employees. Minimum wage is set by Mo. Rev. Stat. "
            "§ 290.502. The Wage Payment Act (Mo. Rev. Stat. § 290.010 et seq.) governs timely "
            "payment. Workers' compensation is under Mo. Rev. Stat. § 287.010 et seq."
        ),
        "consumer_protection": (
            "Missouri Merchandising Practices Act (Mo. Rev. Stat. § 407.010 et seq.) prohibits "
            "unfair practices. The Lemon Law (Mo. Rev. Stat. § 407.560 et seq.) covers new vehicles. "
            "The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Missouri does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 10 years (Mo. Rev. Stat. § 516.110). Wage "
            "garnishment follows Mo. Rev. Stat. § 525.030 with 25% of disposable earnings limit. "
            "Homestead exemption protects up to $15,000 under Mo. Rev. Stat. § 513.475."
        ),
        "small_claims": (
            "Missouri small claims court handles disputes up to $5,000 under Mo. Rev. Stat. "
            "§ 482.300. Filing fees are approximately $25-$50. Cases are heard in the Associate "
            "Circuit division. Appeals go to Circuit Court within 10 days."
        ),
        "contract_disputes": (
            "Missouri follows common law and the UCC (Mo. Rev. Stat. Chapter 400) for goods. The "
            "statute of frauds is at Mo. Rev. Stat. § 432.010. Written contract SOL is 10 years "
            "(Mo. Rev. Stat. § 516.110); oral is 5 years (Mo. Rev. Stat. § 516.120)."
        ),
        "traffic_violations": (
            "Missouri traffic law is in Mo. Rev. Stat. Title 19. Speeding is under Mo. Rev. Stat. "
            "§ 304.010. DWI is under Mo. Rev. Stat. § 577.010. Points accumulate under Mo. Rev. "
            "Stat. § 302.302. License suspensions are handled by the Department of Revenue."
        ),
        "family_law": (
            "Missouri dissolution of marriage is governed by Mo. Rev. Stat. § 452.300 et seq. The "
            "state follows equitable distribution (Mo. Rev. Stat. § 452.330). Custody uses best "
            "interests standard (Mo. Rev. Stat. § 452.375). Child support guidelines are in Mo. "
            "Rev. Stat. § 452.340."
        ),
        "criminal_records": (
            "Missouri allows expungement under Mo. Rev. Stat. § 610.140. Certain misdemeanors may "
            "be expunged after 3 years; felonies after 7 years. Expanded eligibility was enacted in "
            "2018. Missouri does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Missouri enacted Mo. Rev. Stat. § 67.307 prohibiting sanctuary city policies. Driver's "
            "licenses require legal presence under Mo. Rev. Stat. § 302.171. Missouri does not "
            "provide in-state tuition for undocumented students."
        ),
    },
    "NE": {
        "landlord_tenant": (
            "Nebraska Uniform Residential Landlord and Tenant Act (Neb. Rev. Stat. § 76-1401 "
            "et seq.) governs tenancies. Security deposits are limited to one month's rent for "
            "no-pets units (Neb. Rev. Stat. § 76-1416). Deposits must be returned within 14 days "
            "(Neb. Rev. Stat. § 76-1416). Eviction requires a 3-day notice for nonpayment "
            "(Neb. Rev. Stat. § 76-1431)."
        ),
        "employment_rights": (
            "Nebraska Fair Employment Practice Act (Neb. Rev. Stat. § 48-1101 et seq.) prohibits "
            "employment discrimination for employers with 15+ employees. Minimum wage is set by "
            "Neb. Rev. Stat. § 48-1203. The Wage Payment and Collection Act (Neb. Rev. Stat. "
            "§ 48-1228 et seq.) governs timely payment."
        ),
        "consumer_protection": (
            "Nebraska Consumer Protection Act (Neb. Rev. Stat. § 59-1601 et seq.) prohibits unfair "
            "or deceptive practices. The Lemon Law (Neb. Rev. Stat. § 60-2701 et seq.) covers new "
            "vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Nebraska Collection Agency Act (Neb. Rev. Stat. § 45-601 et seq.) regulates collectors. "
            "The statute of limitations on written contracts is 5 years (Neb. Rev. Stat. § 25-205). "
            "Wage garnishment follows Neb. Rev. Stat. § 25-1558 with 25% of disposable earnings "
            "limit. Homestead exemption protects up to $60,000 under Neb. Rev. Stat. § 40-101."
        ),
        "small_claims": (
            "Nebraska small claims court handles disputes up to $3,900 under Neb. Rev. Stat. "
            "§ 25-2802. Filing fees are approximately $26-$47. Cases are heard in County Court. "
            "No attorneys are permitted. Appeals go to District Court within 30 days."
        ),
        "contract_disputes": (
            "Nebraska follows common law and the UCC (Neb. Rev. Stat. Chapter 2) for goods. The "
            "statute of frauds is at Neb. Rev. Stat. § 36-202. Written contract SOL is 5 years "
            "(Neb. Rev. Stat. § 25-205); oral is 4 years (Neb. Rev. Stat. § 25-206)."
        ),
        "traffic_violations": (
            "Nebraska traffic law is in Neb. Rev. Stat. Chapter 60. Speeding is under Neb. Rev. "
            "Stat. § 60-6,186. DUI is under Neb. Rev. Stat. § 60-6,196. Points accumulate under "
            "Neb. Rev. Stat. § 60-4,182. License suspensions are handled by the DMV."
        ),
        "family_law": (
            "Nebraska dissolution of marriage is governed by Neb. Rev. Stat. § 42-347 et seq. The "
            "state follows equitable distribution (Neb. Rev. Stat. § 42-365). Custody uses best "
            "interests standard (Neb. Rev. Stat. § 42-364). Child support guidelines are in "
            "Neb. Ct. R. § 4-200."
        ),
        "criminal_records": (
            "Nebraska allows set-aside of convictions under Neb. Rev. Stat. § 29-2264. Pardons are "
            "handled by the Board of Pardons under Neb. Const. Art. IV, § 13. Nebraska does not "
            "have a comprehensive expungement statute or a statewide ban-the-box law."
        ),
        "immigration": (
            "Nebraska does not have sanctuary state policies. Driver's licenses require legal "
            "presence under Neb. Rev. Stat. § 60-484.04. Nebraska does not provide in-state tuition "
            "for undocumented students. State law enforcement cooperates with federal immigration "
            "authorities."
        ),
    },
    "ND": {
        "landlord_tenant": (
            "North Dakota landlord-tenant law is in N.D.C.C. § 47-16-01 et seq. Security deposits "
            "are limited to one month's rent plus a pet deposit (N.D.C.C. § 47-16-07.1). Deposits "
            "must be returned within 30 days (N.D.C.C. § 47-16-07.1). Eviction requires a 3-day "
            "notice for nonpayment under N.D.C.C. § 33-06-01."
        ),
        "employment_rights": (
            "North Dakota Human Rights Act (N.D.C.C. § 14-02.4-01 et seq.) prohibits employment "
            "discrimination. Minimum wage is set by N.D.C.C. § 34-06-22. The Wage and Hour "
            "statutes (N.D.C.C. Chapter 34-06) govern timely payment. Workers' compensation is "
            "under N.D.C.C. § 65-01-01 et seq."
        ),
        "consumer_protection": (
            "North Dakota Consumer Fraud Act (N.D.C.C. § 51-15-01 et seq.) prohibits deceptive "
            "practices. The Lemon Law (N.D.C.C. § 51-07-16 et seq.) covers new vehicles. The AG "
            "enforces consumer protection."
        ),
        "debt_collections": (
            "North Dakota Collection Agency Act (N.D.C.C. § 13-05-01 et seq.) regulates collectors. "
            "The statute of limitations on written contracts is 6 years (N.D.C.C. § 28-01-16). "
            "Wage garnishment follows N.D.C.C. § 32-09.1-03 with 25% of disposable earnings limit. "
            "Homestead exemption protects up to $150,000 under N.D.C.C. § 47-18-01."
        ),
        "small_claims": (
            "North Dakota small claims court handles disputes up to $15,000 under N.D.C.C. "
            "§ 27-08.1-01. Filing fees are approximately $20-$50. Cases are heard in the small "
            "claims division of District Court. No attorneys are permitted."
        ),
        "contract_disputes": (
            "North Dakota follows common law and the UCC (N.D.C.C. Title 41) for goods. The statute "
            "of frauds is at N.D.C.C. § 9-06-04. Written contract SOL is 6 years (N.D.C.C. "
            "§ 28-01-16); oral is 6 years."
        ),
        "traffic_violations": (
            "North Dakota traffic law is in N.D.C.C. Chapter 39. Speeding is under N.D.C.C. "
            "§ 39-09-02. DUI is under N.D.C.C. § 39-08-01. Points accumulate under N.D.C.C. "
            "§ 39-06.1-10. License suspensions are handled by the DOT."
        ),
        "family_law": (
            "North Dakota divorce is governed by N.D.C.C. § 14-05-01 et seq. The state follows "
            "equitable distribution (N.D.C.C. § 14-05-24). Custody uses best interests standard "
            "(N.D.C.C. § 14-09-06.2). Child support guidelines are in N.D. Admin. Code § 75-02-04.1."
        ),
        "criminal_records": (
            "North Dakota allows expungement under N.D.C.C. § 12-32-07.1. Certain non-violent "
            "offenses may be sealed after waiting periods. North Dakota does not have a statewide "
            "ban-the-box law."
        ),
        "immigration": (
            "North Dakota does not have sanctuary state policies. Driver's licenses require legal "
            "presence under N.D.C.C. § 39-06-01. North Dakota does not provide in-state tuition "
            "for undocumented students. State law enforcement cooperates with federal immigration "
            "authorities."
        ),
    },
    "OH": {
        "landlord_tenant": (
            "Ohio Landlord-Tenant Act (Ohio Rev. Code § 5321.01 et seq.) governs tenancies. There "
            "is no statutory limit on security deposits. Deposits must be returned within 30 days "
            "(Ohio Rev. Code § 5321.16). Eviction requires a 3-day notice for nonpayment (Ohio Rev. "
            "Code § 1923.04). Tenant remedies include rent escrow under Ohio Rev. Code § 5321.07."
        ),
        "employment_rights": (
            "Ohio Civil Rights Act (Ohio Rev. Code § 4112.01 et seq.) prohibits employment "
            "discrimination for employers with 4+ employees. Minimum wage is set by Ohio Const. "
            "Art. II, § 34a. The Prompt Pay Act (Ohio Rev. Code § 4113.15) governs timely payment. "
            "Workers' compensation is under Ohio Rev. Code § 4123.01 et seq."
        ),
        "consumer_protection": (
            "Ohio Consumer Sales Practices Act (Ohio Rev. Code § 1345.01 et seq.) prohibits unfair "
            "or deceptive practices with treble damages for knowing violations. The Lemon Law (Ohio "
            "Rev. Code § 1345.71 et seq.) covers new vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Ohio does not have a separate state debt collection statute. The statute of limitations "
            "on written contracts is 8 years (Ohio Rev. Code § 2305.06). Wage garnishment follows "
            "Ohio Rev. Code § 2329.66 with 25% of disposable earnings limit. Homestead exemption "
            "protects up to $145,425 under Ohio Rev. Code § 2329.66(A)(1)."
        ),
        "small_claims": (
            "Ohio small claims court handles disputes up to $6,000 under Ohio Rev. Code § 1925.02. "
            "Filing fees range from $30 to $65. Cases are heard in the small claims division of "
            "municipal courts. No appeals are allowed from small claims judgments."
        ),
        "contract_disputes": (
            "Ohio follows common law and the UCC (Ohio Rev. Code Chapter 1302) for goods. The "
            "statute of frauds is at Ohio Rev. Code § 1335.05. Written contract SOL is 8 years "
            "(Ohio Rev. Code § 2305.06); oral is 6 years (Ohio Rev. Code § 2305.07)."
        ),
        "traffic_violations": (
            "Ohio traffic law is in Ohio Rev. Code Title 45. Speeding is under Ohio Rev. Code "
            "§ 4511.21. OVI is under Ohio Rev. Code § 4511.19. Points accumulate under Ohio Rev. "
            "Code § 4510.036. License suspensions are handled by the BMV."
        ),
        "family_law": (
            "Ohio divorce is governed by Ohio Rev. Code § 3105.01 et seq. The state follows "
            "equitable distribution (Ohio Rev. Code § 3105.171). Custody uses best interests "
            "standard (Ohio Rev. Code § 3109.04). Child support guidelines are in Ohio Rev. Code "
            "§ 3119.01 et seq."
        ),
        "criminal_records": (
            "Ohio allows expungement/sealing under Ohio Rev. Code § 2953.31 et seq. Eligible "
            "offenses include certain misdemeanors and non-violent felonies after waiting periods. "
            "Ohio does not have a statewide ban-the-box law, though some cities have ordinances."
        ),
        "immigration": (
            "Ohio does not have sanctuary state policies. Driver's licenses require legal presence "
            "under Ohio Rev. Code § 4507.08. Ohio does not provide in-state tuition for undocumented "
            "students. State law enforcement cooperates with federal immigration authorities."
        ),
    },
    "SD": {
        "landlord_tenant": (
            "South Dakota landlord-tenant law is in SDCL § 43-32-1 et seq. Security deposits are "
            "limited to one month's rent (SDCL § 43-32-6.1). Deposits must be returned within "
            "14 days for lease termination or 45 days for eviction (SDCL § 43-32-24). Eviction "
            "requires a 3-day notice for nonpayment (SDCL § 21-16-1)."
        ),
        "employment_rights": (
            "South Dakota Human Relations Act (SDCL § 20-13-1 et seq.) prohibits employment "
            "discrimination. South Dakota follows the federal minimum wage. The Wage Payment Act "
            "(SDCL § 60-11-1 et seq.) governs timely payment. Workers' compensation is under "
            "SDCL § 62-1-1 et seq."
        ),
        "consumer_protection": (
            "South Dakota Deceptive Trade Practices Act (SDCL § 37-24-1 et seq.) prohibits "
            "deceptive practices. The Lemon Law (SDCL § 32-6D-1 et seq.) covers new vehicles. "
            "The AG enforces consumer protection."
        ),
        "debt_collections": (
            "South Dakota does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 6 years (SDCL § 15-2-13). Wage garnishment "
            "follows SDCL § 21-18-51 with 20% of disposable earnings limit. Homestead exemption "
            "has unlimited acreage (up to 1 acre in town) under SDCL § 43-31-1."
        ),
        "small_claims": (
            "South Dakota small claims court handles disputes up to $12,000 under SDCL § 15-39-45.1. "
            "Filing fees are approximately $40-$60. Cases are heard in the small claims division of "
            "Circuit Court. Appeals go to Circuit Court within 10 days."
        ),
        "contract_disputes": (
            "South Dakota follows common law and the UCC (SDCL Title 57A) for goods. The statute "
            "of frauds is at SDCL § 53-8-2. Written contract SOL is 6 years (SDCL § 15-2-13); "
            "oral is 6 years."
        ),
        "traffic_violations": (
            "South Dakota traffic law is in SDCL Title 32. Speeding is under SDCL § 32-25-1.1. "
            "DUI is under SDCL § 32-23-1. Points accumulate under SDCL § 32-12-49.1. License "
            "suspensions are handled by the Department of Public Safety."
        ),
        "family_law": (
            "South Dakota divorce is governed by SDCL § 25-4-1 et seq. The state follows equitable "
            "distribution (SDCL § 25-4-44). Custody uses best interests standard (SDCL § 25-4-45). "
            "Child support guidelines are in SDCL § 25-7-6.1 et seq."
        ),
        "criminal_records": (
            "South Dakota allows expungement under SDCL § 23A-3-27 for arrests not leading to "
            "conviction. Conviction expungement is very limited. Pardons are handled by the Board "
            "of Pardons and Paroles under SDCL § 24-14-1. South Dakota does not have a ban-the-box "
            "law."
        ),
        "immigration": (
            "South Dakota does not have sanctuary state policies. Driver's licenses require legal "
            "presence under SDCL § 32-12-17.2. South Dakota does not provide in-state tuition for "
            "undocumented students. State law enforcement cooperates with federal immigration "
            "authorities."
        ),
    },
    "WI": {
        "landlord_tenant": (
            "Wisconsin Residential Landlord-Tenant Code (Wis. Stat. Chapter 704 and ATCP 134) "
            "governs tenancies. Security deposits have no statutory limit but ATCP 134.06 governs "
            "handling. Deposits must be returned within 21 days (ATCP 134.06(2)). Eviction requires "
            "a 5-day notice for nonpayment (Wis. Stat. § 704.17(1)(b))."
        ),
        "employment_rights": (
            "Wisconsin Fair Employment Act (Wis. Stat. § 111.31 et seq.) prohibits employment "
            "discrimination. Minimum wage is set by Wis. Stat. § 104.01. The Wage Payment and "
            "Collection Act (Wis. Stat. § 109.01 et seq.) governs timely payment. Workers' "
            "compensation is under Wis. Stat. § 102.01 et seq."
        ),
        "consumer_protection": (
            "Wisconsin Deceptive Trade Practices Act (Wis. Stat. § 100.18 et seq.) prohibits "
            "fraudulent representations with pecuniary loss damages. The Lemon Law (Wis. Stat. "
            "§ 218.0171) covers new vehicles. The Department of Agriculture, Trade and Consumer "
            "Protection (DATCP) enforces consumer protections."
        ),
        "debt_collections": (
            "Wisconsin Consumer Act (Wis. Stat. § 427.101 et seq.) governs debt collection and "
            "provides stronger protections than the FDCPA. The statute of limitations on written "
            "contracts is 6 years (Wis. Stat. § 893.43). Wage garnishment follows Wis. Stat. "
            "§ 812.34 with 20% of disposable earnings limit. Homestead exemption protects up to "
            "$75,000 under Wis. Stat. § 815.20."
        ),
        "small_claims": (
            "Wisconsin small claims court handles disputes up to $10,000 under Wis. Stat. § 799.01. "
            "Filing fees are approximately $55-$95. Cases are heard in the small claims division of "
            "Circuit Court. Appeals go to Circuit Court within 15 days."
        ),
        "contract_disputes": (
            "Wisconsin follows common law and the UCC (Wis. Stat. Chapter 402) for goods. The "
            "statute of frauds is at Wis. Stat. § 241.02. Written contract SOL is 6 years (Wis. "
            "Stat. § 893.43); oral is 6 years."
        ),
        "traffic_violations": (
            "Wisconsin traffic law is in Wis. Stat. Chapter 346. Speeding is under Wis. Stat. "
            "§ 346.57. OWI is under Wis. Stat. § 346.63. Demerit points accumulate under Wis. Stat. "
            "§ 343.32. License suspensions are handled by the DOT. First offense OWI is a civil "
            "violation rather than criminal."
        ),
        "family_law": (
            "Wisconsin is a community property state (Wis. Stat. § 766.001 et seq.). Divorce is "
            "governed by Wis. Stat. § 767.001 et seq. Custody uses best interests standard (Wis. "
            "Stat. § 767.41). Child support guidelines are in Wis. Admin. Code DCF 150."
        ),
        "criminal_records": (
            "Wisconsin does not have a comprehensive expungement statute. Limited expungement is "
            "available under Wis. Stat. § 973.015 for certain offenses committed before age 25. "
            "Wisconsin does not have a statewide ban-the-box law, though Milwaukee and Madison have "
            "local ordinances."
        ),
        "immigration": (
            "Wisconsin does not have a statewide sanctuary policy, though some cities limit ICE "
            "cooperation. Driver's licenses require legal presence under Wis. Stat. § 343.14. "
            "Wisconsin does not provide in-state tuition for undocumented students at the state "
            "level."
        ),
    },
}
