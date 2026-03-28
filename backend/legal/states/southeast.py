"""Southeast region state law citations.

States: AL, AR, DE, FL, GA, KY, LA, MD, MS, NC, SC, TN, VA, WV
"""

from __future__ import annotations

SOUTHEAST_LAWS: dict[str, dict[str, str]] = {
    "AL": {
        "landlord_tenant": (
            "Alabama Uniform Residential Landlord and Tenant Act (Ala. Code § 35-9A-101 et seq.) "
            "governs tenancies. Security deposits are limited to one month's rent (Ala. Code "
            "§ 35-9A-201) and must be returned within 60 days. Eviction requires a 7-day notice "
            "for nonpayment (Ala. Code § 35-9A-421)."
        ),
        "employment_rights": (
            "Alabama does not have a comprehensive state employment discrimination statute but "
            "relies on federal Title VII. The Alabama Age Discrimination Act (Ala. Code § 25-1-20 "
            "et seq.) covers age discrimination. Alabama follows the federal minimum wage. Workers' "
            "compensation is governed by Ala. Code § 25-5-1 et seq."
        ),
        "consumer_protection": (
            "Alabama Deceptive Trade Practices Act (Ala. Code § 8-19-1 et seq.) prohibits unfair "
            "practices but does not provide a private right of action for consumers. The Lemon Law "
            "(Ala. Code § 8-20A-1 et seq.) covers new motor vehicles. The AG enforces consumer "
            "protection."
        ),
        "debt_collections": (
            "Alabama does not have a separate state debt collection statute beyond the federal "
            "FDCPA. The statute of limitations on written contracts is 6 years (Ala. Code "
            "§ 6-2-34). Wage garnishment follows federal limits under 15 U.S.C. § 1673. Homestead "
            "exemption protects up to $16,450 in value under Ala. Code § 6-10-2."
        ),
        "small_claims": (
            "Alabama small claims court handles disputes up to $6,000 under Ala. Code § 12-12-31. "
            "Filing fees are approximately $50-$100. Cases are heard in District Court. Appeals go "
            "to Circuit Court within 14 days."
        ),
        "contract_disputes": (
            "Alabama follows common law and the UCC (Ala. Code Title 7) for goods. The statute of "
            "frauds is at Ala. Code § 8-9-2. Written contract SOL is 6 years (Ala. Code § 6-2-34); "
            "oral is 6 years (Ala. Code § 6-2-34)."
        ),
        "traffic_violations": (
            "Alabama traffic law is in Ala. Code Title 32. Speeding is under Ala. Code § 32-5A-171. "
            "DUI is under Ala. Code § 32-5A-191. Points accumulate under Ala. Code § 32-5A-195. "
            "License suspensions are handled by the Alabama Law Enforcement Agency."
        ),
        "family_law": (
            "Alabama divorce is governed by Ala. Code § 30-2-1 et seq. The state follows equitable "
            "distribution (Ala. Code § 30-2-51). Custody uses best interests standard (Ala. Code "
            "§ 30-3-152). Child support guidelines are in Ala. R. Jud. Admin. Rule 32."
        ),
        "criminal_records": (
            "Alabama allows expungement of certain records under Ala. Code § 15-27-1 et seq. "
            "Eligible offenses include non-convictions and certain misdemeanors. There is no "
            "statewide ban-the-box law. Pardons are handled by the Board of Pardons and Paroles "
            "under Ala. Code § 15-22-36."
        ),
        "immigration": (
            "Alabama's Beason-Hammon Alabama Taxpayer and Citizen Protection Act (Ala. Code "
            "§ 31-13-1 et seq.) is one of the strictest state immigration laws. It requires law "
            "enforcement to check immigration status during stops. Driver's licenses require legal "
            "presence. No in-state tuition for undocumented students."
        ),
    },
    "AR": {
        "landlord_tenant": (
            "Arkansas landlord-tenant law is in Ark. Code § 18-17-101 et seq. Security deposit "
            "limits are not set by statute but must be returned within 60 days (Ark. Code "
            "§ 18-16-305). Eviction requires a 3-day notice for nonpayment under Ark. Code "
            "§ 18-60-304. Arkansas allows criminal eviction under Ark. Code § 18-16-101."
        ),
        "employment_rights": (
            "Arkansas Civil Rights Act (Ark. Code § 16-123-101 et seq.) prohibits employment "
            "discrimination for employers with 9+ employees. Minimum wage is set by Ark. Code "
            "§ 11-4-210. The Arkansas Minimum Wage Act governs wage payment. Workers' compensation "
            "is under Ark. Code § 11-9-101 et seq."
        ),
        "consumer_protection": (
            "Arkansas Deceptive Trade Practices Act (Ark. Code § 4-88-101 et seq.) prohibits "
            "unfair practices and provides for actual damages and attorney fees. The Lemon Law "
            "(Ark. Code § 4-90-401 et seq.) covers new vehicles. The AG enforces consumer "
            "protection."
        ),
        "debt_collections": (
            "Arkansas does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 5 years (Ark. Code § 16-56-111). Wage garnishment "
            "follows Ark. Code § 16-110-401 et seq. Arkansas has a strong homestead exemption "
            "with no cap on acreage in rural areas under Ark. Const. Art. 9, § 3."
        ),
        "small_claims": (
            "Arkansas small claims court handles disputes up to $5,000 under Ark. Code § 16-17-601 "
            "et seq. Filing fees are approximately $30-$65. Cases are heard in District Court. "
            "Appeals go to Circuit Court within 30 days."
        ),
        "contract_disputes": (
            "Arkansas follows common law and the UCC (Ark. Code Title 4) for goods. The statute of "
            "frauds is at Ark. Code § 4-59-101. Written contract SOL is 5 years (Ark. Code "
            "§ 16-56-111); oral is 5 years."
        ),
        "traffic_violations": (
            "Arkansas traffic law is in Ark. Code Title 27. Speeding is under Ark. Code § 27-51-201. "
            "DUI is under Ark. Code § 5-65-103. Points accumulate under Ark. Code § 27-16-707. "
            "License suspensions are handled by the Office of Driver Services."
        ),
        "family_law": (
            "Arkansas divorce is governed by Ark. Code § 9-12-301 et seq. The state follows "
            "equitable distribution (Ark. Code § 9-12-315). Custody uses best interests standard "
            "(Ark. Code § 9-13-101). Child support guidelines are in Ark. Admin. Order No. 10."
        ),
        "criminal_records": (
            "Arkansas allows sealing of certain records under Ark. Code § 16-90-1401 et seq. "
            "Eligible offenses include non-violent felonies after waiting periods. Arkansas does "
            "not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Arkansas does not have sanctuary state policies. Ark. Code § 27-16-801 requires "
            "legal presence for driver's licenses. Arkansas does not provide in-state tuition "
            "for undocumented students. State law enforcement cooperates with federal immigration "
            "authorities."
        ),
    },
    "DE": {
        "landlord_tenant": (
            "Delaware Residential Landlord-Tenant Code (25 Del. C. § 5101 et seq.) governs "
            "tenancies. Security deposits are limited to one month's rent (25 Del. C. § 5514) "
            "and must be returned within 20 days. Eviction requires a 5-day notice for nonpayment "
            "(25 Del. C. § 5502). Summary possession is under 25 Del. C. § 5702."
        ),
        "employment_rights": (
            "Delaware Discrimination in Employment Act (19 Del. C. § 710 et seq.) prohibits "
            "employment discrimination. Minimum wage is set by 19 Del. C. § 902. The Wage Payment "
            "and Collection Act (19 Del. C. § 1101 et seq.) governs timely payment. Delaware "
            "requires earned sick leave under 19 Del. C. § 1101A."
        ),
        "consumer_protection": (
            "Delaware Consumer Fraud Act (6 Del. C. § 2511 et seq.) prohibits deceptive practices "
            "and provides for treble damages. The Lemon Law (6 Del. C. § 5001 et seq.) covers new "
            "vehicles. The AG's Consumer Protection Unit enforces the statute."
        ),
        "debt_collections": (
            "Delaware does not have a comprehensive state debt collection statute. The statute of "
            "limitations on written contracts is 3 years (10 Del. C. § 8106). Wage garnishment "
            "follows 10 Del. C. § 4913. Delaware does not have a homestead exemption."
        ),
        "small_claims": (
            "Delaware Justice of the Peace Court handles small claims up to $25,000 under "
            "10 Del. C. § 9301. Filing fees range from $35 to $50. Appeals go to the Court of "
            "Common Pleas within 15 days."
        ),
        "contract_disputes": (
            "Delaware follows common law and the UCC (6 Del. C.) for goods. The statute of frauds "
            "is at 6 Del. C. § 2714. Written contract SOL is 3 years (10 Del. C. § 8106). "
            "Delaware is a favored state for corporate law under Del. Gen. Corp. Law Title 8."
        ),
        "traffic_violations": (
            "Delaware traffic law is in 21 Del. C. Speeding is under 21 Del. C. § 4168. DUI is "
            "under 21 Del. C. § 4177. Points accumulate under 21 Del. C. § 2812. License "
            "suspensions are handled by the Division of Motor Vehicles."
        ),
        "family_law": (
            "Delaware divorce is governed by 13 Del. C. § 1501 et seq. The state follows equitable "
            "distribution (13 Del. C. § 1513). Custody uses best interests standard (13 Del. C. "
            "§ 722). Child support guidelines are in Del. Fam. Ct. C.P.R. Rule 52(c)."
        ),
        "criminal_records": (
            "Delaware allows expungement under 11 Del. C. § 4372 et seq. Mandatory expungement "
            "applies to acquittals and dismissed charges. Adult conviction expungement requires a "
            "petition. Delaware's ban-the-box law (19 Del. C. § 711(g)) restricts employer inquiries."
        ),
        "immigration": (
            "Delaware does not have a sanctuary state policy. Driver's licenses require legal "
            "presence under 21 Del. C. § 2710. Delaware provides in-state tuition for DACA "
            "recipients. State law enforcement generally cooperates with federal immigration "
            "authorities."
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
    "GA": {
        "landlord_tenant": (
            "Georgia landlord-tenant law is in O.C.G.A. § 44-7-1 et seq. There is no statutory "
            "limit on security deposits. Deposits must be returned within 30 days (O.C.G.A. "
            "§ 44-7-34). Landlords must provide a move-in inspection list. Eviction requires a "
            "demand for possession under O.C.G.A. § 44-7-50."
        ),
        "employment_rights": (
            "Georgia Fair Employment Practices Act (O.C.G.A. § 45-19-20 et seq.) applies to "
            "state employees. Private sector employees rely on federal Title VII. Georgia follows "
            "the federal minimum wage. Workers' compensation is governed by O.C.G.A. § 34-9-1 "
            "et seq. Georgia is a strict at-will employment state."
        ),
        "consumer_protection": (
            "Georgia Fair Business Practices Act (O.C.G.A. § 10-1-390 et seq.) prohibits unfair "
            "or deceptive practices. The Lemon Law (O.C.G.A. § 10-1-780 et seq.) covers new "
            "vehicles. The Governor's Office of Consumer Protection enforces the statute."
        ),
        "debt_collections": (
            "Georgia Fair Business Practices Act applies to debt collection. The statute of "
            "limitations on written contracts is 6 years (O.C.G.A. § 9-3-24). Wage garnishment "
            "follows O.C.G.A. § 18-4-20 with 25% of disposable earnings limit. Homestead "
            "exemption protects up to $21,500 under O.C.G.A. § 44-13-100(a)(1)."
        ),
        "small_claims": (
            "Georgia magistrate courts handle small claims up to $15,000 under O.C.G.A. § 15-10-2. "
            "Filing fees are approximately $45-$75. Cases can be appealed to Superior Court for "
            "trial de novo within 30 days."
        ),
        "contract_disputes": (
            "Georgia follows common law and the UCC (O.C.G.A. Title 11) for goods. The statute of "
            "frauds is at O.C.G.A. § 13-5-30. Written contract SOL is 6 years (O.C.G.A. § 9-3-24); "
            "oral is 4 years (O.C.G.A. § 9-3-25)."
        ),
        "traffic_violations": (
            "Georgia traffic law is in O.C.G.A. Title 40. Speeding is under O.C.G.A. § 40-6-181. "
            "DUI is under O.C.G.A. § 40-6-391. Points accumulate under O.C.G.A. § 40-5-57. License "
            "suspensions are handled by the Department of Driver Services."
        ),
        "family_law": (
            "Georgia divorce is governed by O.C.G.A. § 19-5-1 et seq. The state follows equitable "
            "distribution (O.C.G.A. § 19-5-13). Custody uses best interests standard (O.C.G.A. "
            "§ 19-9-3). Child support guidelines are in O.C.G.A. § 19-6-15."
        ),
        "criminal_records": (
            "Georgia allows record restriction (sealing) under O.C.G.A. § 35-3-37. Certain "
            "offenses are eligible for restriction after completion of sentence. Georgia does not "
            "have a statewide ban-the-box law, though some counties and cities have adopted "
            "ordinances."
        ),
        "immigration": (
            "Georgia's Illegal Immigration Reform and Enforcement Act (O.C.G.A. § 36-80-23) "
            "requires public employers and contractors to use E-Verify. Driver's licenses require "
            "legal presence under O.C.G.A. § 40-5-1. Georgia does not provide in-state tuition "
            "for undocumented students."
        ),
    },
    "KY": {
        "landlord_tenant": (
            "Kentucky Uniform Residential Landlord and Tenant Act (KRS § 383.500-383.715) governs "
            "tenancies. There is no statutory limit on security deposits. Deposits must be returned "
            "within 30-60 days depending on whether deductions are claimed (KRS § 383.580). Eviction "
            "requires a 7-day notice for nonpayment (KRS § 383.660)."
        ),
        "employment_rights": (
            "Kentucky Civil Rights Act (KRS § 344.010 et seq.) prohibits employment discrimination "
            "for employers with 8+ employees. Minimum wage is set by KRS § 337.275. The Kentucky "
            "Wages and Hours Act (KRS Chapter 337) governs timely payment. Whistleblower protection "
            "is under KRS § 61.102."
        ),
        "consumer_protection": (
            "Kentucky Consumer Protection Act (KRS § 367.110 et seq.) prohibits unfair or deceptive "
            "practices. The Lemon Law (KRS § 367.840 et seq.) covers new motor vehicles. The AG "
            "enforces consumer protection."
        ),
        "debt_collections": (
            "Kentucky does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 15 years (KRS § 413.090). Wage garnishment "
            "follows KRS § 425.506 with 25% of disposable earnings limit. Homestead exemption "
            "protects up to $5,000 under KRS § 427.060."
        ),
        "small_claims": (
            "Kentucky small claims court handles disputes up to $2,500 under KRS § 24A.230. "
            "Filing fees are approximately $25-$40. Cases are heard in District Court. Appeals "
            "go to Circuit Court within 10 days."
        ),
        "contract_disputes": (
            "Kentucky follows common law and the UCC (KRS Chapter 355) for goods. The statute "
            "of frauds is at KRS § 371.010. Written contract SOL is 15 years (KRS § 413.090); "
            "oral is 5 years (KRS § 413.120)."
        ),
        "traffic_violations": (
            "Kentucky traffic law is in KRS Title 16. Speeding is under KRS § 189.390. DUI is "
            "under KRS § 189A.010. Points accumulate under KRS § 186.570. License suspensions are "
            "handled by the Transportation Cabinet."
        ),
        "family_law": (
            "Kentucky divorce is governed by KRS § 403.110 et seq. The state follows equitable "
            "distribution (KRS § 403.190). Custody uses best interests standard (KRS § 403.270). "
            "Child support guidelines are in KRS § 403.212. Maintenance factors are in KRS § 403.200."
        ),
        "criminal_records": (
            "Kentucky allows expungement under KRS § 431.073 for certain felonies and KRS § 431.076 "
            "for misdemeanors. Class D felonies may be expunged 5 years after completion of sentence. "
            "Kentucky does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Kentucky does not have sanctuary state policies. Driver's licenses require legal "
            "presence under KRS § 186.412. Kentucky does not provide in-state tuition for "
            "undocumented students. State law enforcement cooperates with federal immigration "
            "authorities."
        ),
    },
    "LA": {
        "landlord_tenant": (
            "Louisiana Civil Code Articles 2668-2729 govern residential leases. There is no "
            "statutory limit on security deposits. Deposits must be returned within 30 days "
            "(La. R.S. 9:3251). Eviction requires a 5-day notice for nonpayment under La. C.C.P. "
            "Art. 4701. Louisiana follows civil law traditions rather than common law."
        ),
        "employment_rights": (
            "Louisiana Employment Discrimination Law (La. R.S. 23:301 et seq.) prohibits "
            "discrimination for employers with 20+ employees. Louisiana follows the federal "
            "minimum wage. The Louisiana Wage Payment Act (La. R.S. 23:631) requires timely "
            "payment upon termination. Workers' compensation is under La. R.S. 23:1021 et seq."
        ),
        "consumer_protection": (
            "Louisiana Unfair Trade Practices and Consumer Protection Law (La. R.S. 51:1401 et seq.) "
            "prohibits unfair or deceptive practices with treble damages. The Lemon Law (La. R.S. "
            "51:1941 et seq.) covers new vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Louisiana does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 10 years (La. C.C. Art. 3499). Wage garnishment "
            "follows La. R.S. 13:3881. Homestead exemption protects up to $35,000 under "
            "La. R.S. 20:1."
        ),
        "small_claims": (
            "Louisiana city courts handle small claims up to $5,000. Justice of the peace courts "
            "handle claims up to $5,000 in rural areas (La. R.S. 13:5200). Filing fees vary by "
            "parish. Appeals go to District Court."
        ),
        "contract_disputes": (
            "Louisiana follows civil law contract principles (La. C.C. Arts. 1906-2057) rather "
            "than common law. The form requirements serve as a statute of frauds equivalent. "
            "Written contract SOL is 10 years (La. C.C. Art. 3499). Louisiana adopted a modified "
            "UCC for sales."
        ),
        "traffic_violations": (
            "Louisiana traffic law is in La. R.S. Title 32. Speeding is under La. R.S. 32:61. "
            "DUI is under La. R.S. 14:98. License suspensions are handled by the Office of Motor "
            "Vehicles under La. R.S. 32:414. Defensive driving can reduce points."
        ),
        "family_law": (
            "Louisiana is a community property state (La. C.C. Art. 2325). Divorce is governed by "
            "La. C.C. Art. 102 (no-fault with living separate). Custody uses best interests standard "
            "(La. C.C. Art. 131). Child support guidelines are in La. R.S. 9:315."
        ),
        "criminal_records": (
            "Louisiana allows expungement under La. C.Cr.P. Art. 971 et seq. Misdemeanor "
            "convictions may be expunged after waiting periods. Felony expungement is limited to "
            "specific offenses. Louisiana does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Louisiana does not have sanctuary state policies. La. R.S. 14:100.13 prohibits "
            "sanctuary city policies. Driver's licenses require legal presence under La. R.S. "
            "32:410. Louisiana does not provide in-state tuition for undocumented students."
        ),
    },
    "MD": {
        "landlord_tenant": (
            "Maryland Real Property Code § 8-101 et seq. governs residential tenancies. Security "
            "deposits are limited to two months' rent (Md. Code, Real Prop. § 8-203) and must be "
            "returned within 45 days. Eviction requires a notice period depending on the lease type "
            "under Real Prop. § 8-402. Rent escrow is available under Real Prop. § 8-211."
        ),
        "employment_rights": (
            "Maryland Fair Employment Practices Act (Md. Code, State Gov't § 20-601 et seq.) "
            "prohibits discrimination. Minimum wage is set by Md. Code, Lab. & Empl. § 3-413. "
            "Maryland Healthy Working Families Act requires paid sick leave (Lab. & Empl. § 3-1301). "
            "Wage payment is governed by Lab. & Empl. § 3-502."
        ),
        "consumer_protection": (
            "Maryland Consumer Protection Act (Md. Code, Com. Law § 13-101 et seq.) prohibits "
            "unfair or deceptive practices. The Lemon Law (Com. Law § 14-1501 et seq.) covers new "
            "vehicles. The AG's Consumer Protection Division enforces the statute."
        ),
        "debt_collections": (
            "Maryland Collection Agency Licensing Act (Md. Code, Bus. Reg. § 7-101 et seq.) "
            "regulates collectors. The statute of limitations on written contracts is 3 years "
            "(Md. Code, Cts. & Jud. Proc. § 5-101). Wage garnishment follows Cts. & Jud. Proc. "
            "§ 11-504. Homestead exemption is not available in Maryland."
        ),
        "small_claims": (
            "Maryland District Court handles small claims up to $5,000 under Md. Code, Cts. & "
            "Jud. Proc. § 4-405. Filing fees range from $34 to $54. Appeals go to Circuit Court "
            "within 30 days for trial de novo."
        ),
        "contract_disputes": (
            "Maryland follows common law and the UCC (Md. Code, Com. Law Title 2) for goods. The "
            "statute of frauds is at Com. Law § 5-901. Written contract SOL is 3 years (Cts. & "
            "Jud. Proc. § 5-101). Non-compete agreements must be reasonable."
        ),
        "traffic_violations": (
            "Maryland Transportation Article governs traffic. Speeding is under Transp. § 21-801.1. "
            "DUI is under Transp. § 21-902. Points accumulate under Transp. § 16-402. License "
            "suspensions are handled by the MVA. Traffic court is in the District Court."
        ),
        "family_law": (
            "Maryland divorce is governed by Md. Code, Fam. Law § 7-101 et seq. The state follows "
            "equitable distribution (Fam. Law § 8-205). Custody uses best interests standard "
            "(Fam. Law § 9-101). Child support guidelines are in Fam. Law § 12-201 et seq."
        ),
        "criminal_records": (
            "Maryland allows expungement under Md. Code, Crim. Proc. § 10-101 et seq. Non-convictions "
            "are eligible immediately. Certain misdemeanors may be expunged after waiting periods. "
            "Maryland's ban-the-box law (Crim. Proc. § 1-209) applies to employers with 15+ employees."
        ),
        "immigration": (
            "Maryland does not have a statewide sanctuary policy, though some counties have adopted "
            "sanctuary policies. The Maryland DREAM Act allows in-state tuition for undocumented "
            "students (Md. Code, Educ. § 15-106.8). Driver's licenses require legal presence."
        ),
    },
    "MS": {
        "landlord_tenant": (
            "Mississippi Residential Landlord and Tenant Act (Miss. Code § 89-8-1 et seq.) governs "
            "tenancies. There is no statutory limit on security deposits. Deposits must be returned "
            "within 45 days (Miss. Code § 89-8-21). Eviction requires a 3-day notice for nonpayment "
            "(Miss. Code § 89-7-27)."
        ),
        "employment_rights": (
            "Mississippi does not have a comprehensive state employment discrimination statute; "
            "private sector employees rely on federal Title VII. The Mississippi Employment Protection "
            "Act (Miss. Code § 71-1-51) covers whistleblower protection. Mississippi follows the "
            "federal minimum wage. Workers' compensation is under Miss. Code § 71-3-1 et seq."
        ),
        "consumer_protection": (
            "Mississippi Consumer Protection Act (Miss. Code § 75-24-1 et seq.) prohibits unfair "
            "or deceptive practices. The Lemon Law (Miss. Code § 63-17-151 et seq.) covers new "
            "vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Mississippi does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 3 years (Miss. Code § 15-1-29). Wage garnishment "
            "follows Miss. Code § 85-3-4. Homestead exemption protects up to $75,000 in value "
            "and 160 acres under Miss. Code § 85-3-21."
        ),
        "small_claims": (
            "Mississippi justice courts handle small claims up to $3,500 under Miss. Code § 9-11-9. "
            "Filing fees are approximately $30-$50. Appeals go to County Court or Circuit Court "
            "within 10 days."
        ),
        "contract_disputes": (
            "Mississippi follows common law and the UCC (Miss. Code Title 75) for goods. The statute "
            "of frauds is at Miss. Code § 15-3-1. Written contract SOL is 3 years (Miss. Code "
            "§ 15-1-29); oral is 3 years."
        ),
        "traffic_violations": (
            "Mississippi traffic law is in Miss. Code Title 63. Speeding is under Miss. Code "
            "§ 63-3-501. DUI is under Miss. Code § 63-11-30. Points accumulate under Miss. Code "
            "§ 63-1-51. License suspensions are handled by the Department of Public Safety."
        ),
        "family_law": (
            "Mississippi divorce is governed by Miss. Code § 93-5-1 et seq. The state follows "
            "equitable distribution (Ferguson v. Ferguson, 639 So.2d 921). Custody uses the "
            "Albright factors (Albright v. Albright, 437 So.2d 1003). Child support guidelines "
            "are in Miss. Code § 43-19-101."
        ),
        "criminal_records": (
            "Mississippi allows expungement under Miss. Code § 99-19-71. First-time offenders of "
            "certain misdemeanors and non-violent felonies may qualify. Waiting periods apply. "
            "Mississippi does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Mississippi Employment Protection Act (Miss. Code § 71-11-1 et seq.) requires E-Verify "
            "for all employers. Driver's licenses require legal presence under Miss. Code § 63-1-19. "
            "Mississippi does not provide in-state tuition for undocumented students."
        ),
    },
    "NC": {
        "landlord_tenant": (
            "North Carolina Residential Rental Agreements Act (N.C.G.S. § 42-38 et seq.) governs "
            "tenancies. Security deposits are limited to two months' rent for month-to-month and "
            "1.5 months for longer terms (N.C.G.S. § 42-51). Deposits must be returned within 30 "
            "days (N.C.G.S. § 42-52). Eviction requires a 10-day notice for nonpayment."
        ),
        "employment_rights": (
            "North Carolina Equal Employment Practices Act (N.C.G.S. § 143-422.1 et seq.) prohibits "
            "discrimination but has limited enforcement mechanisms. The Wage and Hour Act (N.C.G.S. "
            "§ 95-25.1 et seq.) governs minimum wage and timely payment. Retaliatory Employment "
            "Discrimination Act (N.C.G.S. § 95-240) protects workers' comp claimants."
        ),
        "consumer_protection": (
            "North Carolina Unfair and Deceptive Trade Practices Act (N.C.G.S. § 75-1.1) provides "
            "treble damages. The Lemon Law (N.C.G.S. § 20-351 et seq.) covers new vehicles. The "
            "AG's Consumer Protection Division enforces the statute."
        ),
        "debt_collections": (
            "North Carolina Collection Agency Act (N.C.G.S. § 58-70-1 et seq.) governs collectors. "
            "The statute of limitations on written contracts is 3 years (N.C.G.S. § 1-52). North "
            "Carolina does not allow wage garnishment for consumer debts (N.C.G.S. § 1-362). "
            "Homestead exemption protects up to $35,000 under N.C.G.S. § 1C-1601(a)(1)."
        ),
        "small_claims": (
            "North Carolina small claims court handles disputes up to $10,000 under N.C.G.S. "
            "§ 7A-210. Filing fees are approximately $96. Cases are heard by a magistrate. Appeals "
            "go to District Court within 10 days for trial de novo."
        ),
        "contract_disputes": (
            "North Carolina follows common law and the UCC (N.C.G.S. Chapter 25) for goods. The "
            "statute of frauds is at N.C.G.S. § 22-2. Written contract SOL is 3 years (N.C.G.S. "
            "§ 1-52); oral is 3 years."
        ),
        "traffic_violations": (
            "North Carolina traffic law is in N.C.G.S. Chapter 20. Speeding is under N.C.G.S. "
            "§ 20-141. DWI is under N.C.G.S. § 20-138.1. Points accumulate under N.C.G.S. "
            "§ 20-16(a). License suspensions are handled by the DMV."
        ),
        "family_law": (
            "North Carolina divorce requires one year of separation (N.C.G.S. § 50-6). The state "
            "follows equitable distribution (N.C.G.S. § 50-20). Custody uses best interests "
            "standard (N.C.G.S. § 50-13.2). Child support guidelines are in N.C.G.S. § 50-13.4."
        ),
        "criminal_records": (
            "North Carolina allows expunction under N.C.G.S. § 15A-145 et seq. Non-violent "
            "misdemeanors and certain felonies may be expunged after waiting periods. The Second "
            "Chance Act expanded eligibility. North Carolina does not have a statewide ban-the-box "
            "law."
        ),
        "immigration": (
            "North Carolina does not have sanctuary state policies. Driver's licenses require legal "
            "presence under N.C.G.S. § 20-7. North Carolina does not provide in-state tuition for "
            "undocumented students. State law enforcement cooperates with federal immigration "
            "authorities."
        ),
    },
    "SC": {
        "landlord_tenant": (
            "South Carolina Residential Landlord and Tenant Act (S.C. Code § 27-40-10 et seq.) "
            "governs tenancies. There is no statutory limit on security deposits. Deposits must be "
            "returned within 30 days (S.C. Code § 27-40-410). Eviction requires a 5-day notice "
            "for nonpayment (S.C. Code § 27-40-710(B))."
        ),
        "employment_rights": (
            "South Carolina Human Affairs Law (S.C. Code § 1-13-10 et seq.) prohibits employment "
            "discrimination for employers with 15+ employees. South Carolina follows the federal "
            "minimum wage. The Payment of Wages Act (S.C. Code § 41-10-10 et seq.) governs timely "
            "payment. Workers' compensation is under S.C. Code § 42-1-10 et seq."
        ),
        "consumer_protection": (
            "South Carolina Unfair Trade Practices Act (S.C. Code § 39-5-10 et seq.) prohibits "
            "unfair or deceptive practices with treble damages. The Lemon Law (S.C. Code § 56-28-10 "
            "et seq.) covers new vehicles. The AG's Consumer Protection Division enforces the statute."
        ),
        "debt_collections": (
            "South Carolina does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 3 years (S.C. Code § 15-3-530). Wage garnishment "
            "follows S.C. Code § 37-5-104. Homestead exemption protects up to $63,250 under "
            "S.C. Code § 15-41-30(A)(1)."
        ),
        "small_claims": (
            "South Carolina magistrate courts handle small claims up to $7,500 under S.C. Code "
            "§ 22-3-10. Filing fees are approximately $80. Appeals go to Circuit Court within "
            "30 days for trial de novo."
        ),
        "contract_disputes": (
            "South Carolina follows common law and the UCC (S.C. Code Title 36) for goods. The "
            "statute of frauds is at S.C. Code § 32-3-10. Written contract SOL is 3 years (S.C. "
            "Code § 15-3-530); oral is 3 years."
        ),
        "traffic_violations": (
            "South Carolina traffic law is in S.C. Code Title 56. Speeding is under S.C. Code "
            "§ 56-5-1520. DUI is under S.C. Code § 56-5-2930. Points accumulate under S.C. Code "
            "§ 56-1-720. License suspensions are handled by the DMV."
        ),
        "family_law": (
            "South Carolina divorce is governed by S.C. Code § 20-3-10 et seq. The state follows "
            "equitable distribution (S.C. Code § 20-3-620). Custody uses best interests standard "
            "(S.C. Code § 63-15-240). Child support guidelines are in S.C. Code § 63-17-470."
        ),
        "criminal_records": (
            "South Carolina allows expungement under S.C. Code § 22-5-910 and § 22-5-920. "
            "First offense misdemeanors are eligible after 3 years. Certain felonies may qualify "
            "under expanded provisions. South Carolina does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "South Carolina Illegal Immigration Reform Act (S.C. Code § 41-8-10 et seq.) requires "
            "E-Verify for employers. Driver's licenses require legal presence under S.C. Code "
            "§ 56-1-40. South Carolina does not provide in-state tuition for undocumented students."
        ),
    },
    "TN": {
        "landlord_tenant": (
            "Tennessee Uniform Residential Landlord and Tenant Act (Tenn. Code § 66-28-101 et seq.) "
            "governs tenancies. There is no statutory limit on security deposits. Deposits must be "
            "returned within 30 days (Tenn. Code § 66-28-301). Eviction requires a 14-day notice "
            "for nonpayment (Tenn. Code § 66-28-505)."
        ),
        "employment_rights": (
            "Tennessee Human Rights Act (Tenn. Code § 4-21-101 et seq.) prohibits employment "
            "discrimination for employers with 8+ employees. Tennessee follows the federal minimum "
            "wage. The Wage Regulations Act (Tenn. Code § 50-2-101 et seq.) governs timely payment. "
            "Workers' compensation is under Tenn. Code § 50-6-101 et seq."
        ),
        "consumer_protection": (
            "Tennessee Consumer Protection Act (Tenn. Code § 47-18-101 et seq.) prohibits unfair or "
            "deceptive practices with treble damages for willful violations. The Lemon Law (Tenn. "
            "Code § 55-24-101 et seq.) covers new vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Tennessee Collection Service Act (Tenn. Code § 62-20-101 et seq.) regulates collectors. "
            "The statute of limitations on written contracts is 6 years (Tenn. Code § 28-3-109). "
            "Wage garnishment follows Tenn. Code § 26-2-106 with 25% of disposable earnings limit. "
            "Homestead exemption protects up to $5,000 ($7,500 joint) under Tenn. Code § 26-2-301."
        ),
        "small_claims": (
            "Tennessee general sessions courts handle small claims up to $25,000 under Tenn. Code "
            "§ 16-15-501. Filing fees are approximately $40-$100. Appeals go to Circuit Court "
            "within 10 days for trial de novo."
        ),
        "contract_disputes": (
            "Tennessee follows common law and the UCC (Tenn. Code Title 47) for goods. The statute "
            "of frauds is at Tenn. Code § 29-2-101. Written contract SOL is 6 years (Tenn. Code "
            "§ 28-3-109); oral is 6 years."
        ),
        "traffic_violations": (
            "Tennessee traffic law is in Tenn. Code Title 55. Speeding is under Tenn. Code "
            "§ 55-8-152. DUI is under Tenn. Code § 55-10-401. Points accumulate under Tenn. Code "
            "§ 55-50-504. License suspensions are handled by the Department of Safety."
        ),
        "family_law": (
            "Tennessee divorce is governed by Tenn. Code § 36-4-101 et seq. The state follows "
            "equitable distribution (Tenn. Code § 36-4-121). Custody uses best interests standard "
            "(Tenn. Code § 36-6-106). Child support guidelines are in Tenn. Comp. R. & Regs. "
            "1240-02-04."
        ),
        "criminal_records": (
            "Tennessee allows expungement under Tenn. Code § 40-32-101. Eligible offenses include "
            "certain misdemeanors and non-violent felonies. The 2012 amendment expanded eligibility. "
            "Tennessee does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Tennessee does not have sanctuary state policies. Tenn. Code § 55-50-331 requires "
            "legal presence for driver's licenses. Tennessee provides a driving certificate for "
            "certain non-citizens. Tennessee does not provide in-state tuition for undocumented "
            "students."
        ),
    },
    "VA": {
        "landlord_tenant": (
            "Virginia Residential Landlord and Tenant Act (Va. Code § 55.1-1200 et seq.) governs "
            "tenancies. Security deposits are limited to two months' rent (Va. Code § 55.1-1226) "
            "and must be returned within 45 days. Eviction requires a 5-day pay-or-quit notice "
            "(Va. Code § 55.1-1245). Virginia enacted rent stabilization provisions in 2020."
        ),
        "employment_rights": (
            "Virginia Human Rights Act (Va. Code § 2.2-3900 et seq.) prohibits employment "
            "discrimination. Virginia minimum wage is set by Va. Code § 40.1-28.10. The Wage "
            "Payment Act (Va. Code § 40.1-29) governs timely payment. Virginia Values Act expanded "
            "protections to include sexual orientation and gender identity."
        ),
        "consumer_protection": (
            "Virginia Consumer Protection Act (Va. Code § 59.1-196 et seq.) prohibits fraudulent "
            "practices. The Lemon Law (Va. Code § 59.1-207.9 et seq.) covers new vehicles. The "
            "AG's Office of Consumer Protection enforces the statute."
        ),
        "debt_collections": (
            "Virginia does not have a comprehensive state debt collection statute. The statute of "
            "limitations on written contracts is 5 years (Va. Code § 8.01-246). Wage garnishment "
            "follows Va. Code § 34-29 with 25% of disposable earnings limit. Homestead exemption "
            "protects up to $25,000 under Va. Code § 34-4."
        ),
        "small_claims": (
            "Virginia general district courts handle small claims up to $25,000 under Va. Code "
            "§ 16.1-77. Filing fees range from $47 to $117. Appeals go to Circuit Court within "
            "10 days for trial de novo."
        ),
        "contract_disputes": (
            "Virginia follows common law and the UCC (Va. Code Title 8.1A-8.12) for goods. The "
            "statute of frauds is at Va. Code § 11-2. Written contract SOL is 5 years (Va. Code "
            "§ 8.01-246); oral is 3 years (Va. Code § 8.01-248)."
        ),
        "traffic_violations": (
            "Virginia traffic law is in Va. Code Title 46.2. Speeding is under Va. Code § 46.2-870. "
            "DUI is under Va. Code § 18.2-266. Demerit points accumulate under Va. Code § 46.2-492. "
            "License suspensions are handled by the DMV. Reckless driving is a criminal offense "
            "under Va. Code § 46.2-862."
        ),
        "family_law": (
            "Virginia divorce is governed by Va. Code § 20-91 et seq. The state follows equitable "
            "distribution (Va. Code § 20-107.3). Custody uses best interests standard (Va. Code "
            "§ 20-124.3). Child support guidelines are in Va. Code § 20-108.2."
        ),
        "criminal_records": (
            "Virginia allows expungement of charges not leading to conviction under Va. Code "
            "§ 19.2-392.2. Marijuana-related offenses may be sealed under recent legislation. "
            "Virginia's ban-the-box law (Va. Code § 2.2-2812.1) applies to state agencies."
        ),
        "immigration": (
            "Virginia does not have a statewide sanctuary policy. Driver's privilege cards are "
            "available under Va. Code § 46.2-328.3. Virginia provides in-state tuition for certain "
            "undocumented students under Va. Code § 23.1-502."
        ),
    },
    "WV": {
        "landlord_tenant": (
            "West Virginia landlord-tenant law is in W. Va. Code § 37-6-1 et seq. There is no "
            "statutory limit on security deposits. Deposits must be returned within 60 days "
            "(W. Va. Code § 37-6A-2). Eviction requires a notice period that varies by lease type. "
            "The Residential Rental Security Deposit Act governs deposit handling."
        ),
        "employment_rights": (
            "West Virginia Human Rights Act (W. Va. Code § 5-11-1 et seq.) prohibits employment "
            "discrimination for employers with 12+ employees. Minimum wage is set by W. Va. Code "
            "§ 21-5C-2. The Wage Payment and Collection Act (W. Va. Code § 21-5-1 et seq.) governs "
            "timely payment. Workers' compensation is under W. Va. Code § 23-1-1 et seq."
        ),
        "consumer_protection": (
            "West Virginia Consumer Credit and Protection Act (W. Va. Code § 46A-1-101 et seq.) "
            "prohibits unfair or deceptive practices. The Lemon Law (W. Va. Code § 46A-6A-1 et "
            "seq.) covers new vehicles. The AG's Consumer Protection Division enforces the statute."
        ),
        "debt_collections": (
            "West Virginia Consumer Credit and Protection Act covers debt collection practices. "
            "The statute of limitations on written contracts is 10 years (W. Va. Code § 55-2-6). "
            "Wage garnishment follows W. Va. Code § 46A-2-130. Homestead exemption protects up to "
            "$25,000 under W. Va. Code § 38-9-1."
        ),
        "small_claims": (
            "West Virginia magistrate courts handle small claims up to $10,000 under W. Va. Code "
            "§ 50-2-1. Filing fees are approximately $30-$45. Appeals go to Circuit Court within "
            "20 days for trial de novo."
        ),
        "contract_disputes": (
            "West Virginia follows common law and the UCC (W. Va. Code Chapter 46) for goods. The "
            "statute of frauds is at W. Va. Code § 55-1-1. Written contract SOL is 10 years "
            "(W. Va. Code § 55-2-6); oral is 5 years (W. Va. Code § 55-2-6)."
        ),
        "traffic_violations": (
            "West Virginia traffic law is in W. Va. Code Chapter 17C. Speeding is under W. Va. Code "
            "§ 17C-6-1. DUI is under W. Va. Code § 17C-5-2. Points accumulate under W. Va. Code "
            "§ 17B-3-3a. License suspensions are handled by the DMV."
        ),
        "family_law": (
            "West Virginia divorce is governed by W. Va. Code § 48-5-101 et seq. The state follows "
            "equitable distribution (W. Va. Code § 48-7-101). Custody uses best interests standard "
            "(W. Va. Code § 48-9-102). Child support guidelines are in W. Va. Code § 48-13-301."
        ),
        "criminal_records": (
            "West Virginia allows expungement under W. Va. Code § 61-11-25. Non-violent "
            "misdemeanors and certain felonies may be expunged after waiting periods. West Virginia "
            "does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "West Virginia does not have sanctuary state policies. Driver's licenses require legal "
            "presence under W. Va. Code § 17B-2-1. West Virginia does not provide in-state tuition "
            "for undocumented students. State law enforcement cooperates with federal immigration "
            "authorities."
        ),
    },
}
