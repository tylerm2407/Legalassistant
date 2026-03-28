"""West region state law citations.

States: AK, AZ, CA, CO, HI, ID, MT, NM, NV, OR, UT, WA, WY
"""

from __future__ import annotations

WEST_LAWS: dict[str, dict[str, str]] = {
    "AK": {
        "landlord_tenant": (
            "Alaska Uniform Residential Landlord and Tenant Act (Alaska Stat. § 34.03.010 et seq.) "
            "governs tenancies. Security deposits are limited to two months' rent (Alaska Stat. "
            "§ 34.03.070). Deposits must be returned within 14-30 days. Eviction requires a 7-day "
            "notice for nonpayment (Alaska Stat. § 34.03.220(b))."
        ),
        "employment_rights": (
            "Alaska Human Rights Law (Alaska Stat. § 18.80.010 et seq.) prohibits employment "
            "discrimination. Minimum wage is set by Alaska Stat. § 23.10.065. The Alaska Wage and "
            "Hour Act (Alaska Stat. § 23.10.050 et seq.) governs timely payment. Workers' "
            "compensation is under Alaska Stat. § 23.30.005 et seq."
        ),
        "consumer_protection": (
            "Alaska Unfair Trade Practices and Consumer Protection Act (Alaska Stat. § 45.50.471 "
            "et seq.) prohibits unfair or deceptive practices with treble damages. The Lemon Law "
            "(Alaska Stat. § 45.45.300 et seq.) covers new vehicles. The AG enforces consumer "
            "protection."
        ),
        "debt_collections": (
            "Alaska does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 3 years (Alaska Stat. § 09.10.053). Wage "
            "garnishment follows Alaska Stat. § 09.38.030 with 25% of disposable earnings limit. "
            "Homestead exemption protects up to $72,900 under Alaska Stat. § 09.38.010."
        ),
        "small_claims": (
            "Alaska small claims court handles disputes up to $10,000 under Alaska Stat. "
            "§ 22.15.040. Filing fees are approximately $75. Cases are heard in District Court. "
            "Appeals go to Superior Court within 30 days."
        ),
        "contract_disputes": (
            "Alaska follows common law and the UCC (Alaska Stat. Title 45) for goods. The statute "
            "of frauds is at Alaska Stat. § 09.25.010. Written contract SOL is 3 years (Alaska "
            "Stat. § 09.10.053); oral is 3 years."
        ),
        "traffic_violations": (
            "Alaska traffic law is in Alaska Stat. Title 28. Speeding is under Alaska Stat. "
            "§ 28.35.400. DUI is under Alaska Stat. § 28.35.030. Points accumulate under Alaska "
            "Stat. § 28.15.221. License suspensions are handled by the DMV."
        ),
        "family_law": (
            "Alaska divorce is governed by Alaska Stat. § 25.24.010 et seq. The state follows "
            "equitable distribution (Alaska Stat. § 25.24.160). Custody uses best interests "
            "standard (Alaska Stat. § 25.24.150). Child support guidelines are in Alaska R. "
            "Civ. P. 90.3."
        ),
        "criminal_records": (
            "Alaska allows sealing of criminal records under Alaska Stat. § 12.62.180. Certain "
            "convictions can be set aside under Alaska Stat. § 12.55.085. Alaska does not have a "
            "statewide ban-the-box law."
        ),
        "immigration": (
            "Alaska does not have sanctuary state policies. Driver's licenses require legal "
            "presence under Alaska Stat. § 28.15.111. Alaska does not provide in-state tuition "
            "for undocumented students. State law enforcement cooperates with federal immigration "
            "authorities."
        ),
    },
    "AZ": {
        "landlord_tenant": (
            "Arizona Residential Landlord and Tenant Act (A.R.S. § 33-1301 et seq.) governs "
            "tenancies. Security deposits are limited to 1.5 months' rent (A.R.S. § 33-1321). "
            "Deposits must be returned within 14 days (A.R.S. § 33-1321(D)). Eviction requires a "
            "5-day notice for nonpayment (A.R.S. § 33-1368(B))."
        ),
        "employment_rights": (
            "Arizona Civil Rights Act (A.R.S. § 41-1461 et seq.) prohibits employment discrimination. "
            "Minimum wage is set by A.R.S. § 23-363 (Fair Wages and Healthy Families Act). The "
            "Arizona Wage Act (A.R.S. § 23-350 et seq.) governs timely payment. Arizona requires "
            "earned paid sick time under A.R.S. § 23-371."
        ),
        "consumer_protection": (
            "Arizona Consumer Fraud Act (A.R.S. § 44-1521 et seq.) prohibits deceptive practices "
            "and provides actual damages plus punitive damages for willful violations. The Lemon Law "
            "(A.R.S. § 44-1261 et seq.) covers new vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Arizona Collection Agency Act (A.R.S. § 32-1001 et seq.) regulates collectors. The "
            "statute of limitations on written contracts is 6 years (A.R.S. § 12-548). Wage "
            "garnishment follows A.R.S. § 12-1598 with 25% of disposable earnings limit. Homestead "
            "exemption protects up to $250,000 under A.R.S. § 33-1101."
        ),
        "small_claims": (
            "Arizona justice courts handle small claims up to $3,500 under A.R.S. § 22-503. Filing "
            "fees are approximately $20-$65. Cases can be appealed to Superior Court within 13 days "
            "for trial de novo."
        ),
        "contract_disputes": (
            "Arizona follows common law and the UCC (A.R.S. Title 47) for goods. The statute of "
            "frauds is at A.R.S. § 44-101. Written contract SOL is 6 years (A.R.S. § 12-548); "
            "oral is 3 years (A.R.S. § 12-543)."
        ),
        "traffic_violations": (
            "Arizona traffic law is in A.R.S. Title 28. Speeding is under A.R.S. § 28-701. DUI is "
            "under A.R.S. § 28-1381. Points accumulate under A.R.S. § 28-3306. License suspensions "
            "are handled by the MVD. Arizona has strict aggravated DUI penalties including mandatory "
            "jail time."
        ),
        "family_law": (
            "Arizona is a community property state (A.R.S. § 25-211). Dissolution of marriage is "
            "governed by A.R.S. § 25-311 et seq. Custody uses best interests standard (A.R.S. "
            "§ 25-403). Child support guidelines are in A.R.S. § 25-320."
        ),
        "criminal_records": (
            "Arizona allows setting aside convictions under A.R.S. § 13-905, but the conviction "
            "record is not erased. Certain marijuana offenses may be expunged under A.R.S. "
            "§ 36-2862. Arizona does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Arizona SB 1070 (A.R.S. § 11-1051) requires law enforcement to verify immigration "
            "status during lawful stops (upheld in part by Arizona v. United States, 567 U.S. 387). "
            "Driver's licenses require legal presence under A.R.S. § 28-3153. Arizona does not "
            "provide in-state tuition for undocumented students (Proposition 300, A.R.S. § 15-1803)."
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
    "CO": {
        "landlord_tenant": (
            "Colorado landlord-tenant law is in C.R.S. § 38-12-101 et seq. Security deposits are "
            "limited by the lease terms and must be returned within 30 days for leases after 2025, "
            "or 60 days for older leases (C.R.S. § 38-12-103). Eviction requires a 10-day notice "
            "for nonpayment (C.R.S. § 13-40-104(1)(d)). The Rental Application Fairness Act limits "
            "application fees."
        ),
        "employment_rights": (
            "Colorado Anti-Discrimination Act (C.R.S. § 24-34-401 et seq.) prohibits employment "
            "discrimination. Minimum wage is set by C.R.S. § 8-6-109 and Colorado COMPS Order. "
            "The Colorado Wage Claim Act (C.R.S. § 8-4-101 et seq.) governs timely payment. The "
            "Healthy Families and Workplaces Act requires paid sick leave (C.R.S. § 8-13.3-401)."
        ),
        "consumer_protection": (
            "Colorado Consumer Protection Act (C.R.S. § 6-1-101 et seq.) prohibits deceptive trade "
            "practices with treble damages. The Lemon Law (C.R.S. § 42-10-101 et seq.) covers new "
            "vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Colorado Fair Debt Collection Practices Act (C.R.S. § 5-16-101 et seq.) governs "
            "collectors. The statute of limitations on written contracts is 6 years (C.R.S. "
            "§ 13-80-103.5). Wage garnishment follows C.R.S. § 13-54-104 with 25% of disposable "
            "earnings limit. Homestead exemption protects up to $250,000 under C.R.S. § 38-41-201."
        ),
        "small_claims": (
            "Colorado small claims court handles disputes up to $7,500 under C.R.S. § 13-6-403. "
            "Filing fees range from $31 to $55. Cases are heard in County Court. Attorneys are "
            "permitted with court approval. Appeals go to District Court within 14 days."
        ),
        "contract_disputes": (
            "Colorado follows common law and the UCC (C.R.S. Title 4) for goods. The statute of "
            "frauds is at C.R.S. § 38-10-112. Written contract SOL is 6 years (C.R.S. "
            "§ 13-80-103.5); oral is 3 years (C.R.S. § 13-80-101)."
        ),
        "traffic_violations": (
            "Colorado traffic law is in C.R.S. Title 42. Speeding is under C.R.S. § 42-4-1101. "
            "DUI is under C.R.S. § 42-4-1301. Points accumulate under C.R.S. § 42-2-127. License "
            "suspensions are handled by the DMV. Colorado distinguishes between DUI and DWAI."
        ),
        "family_law": (
            "Colorado dissolution of marriage is governed by C.R.S. § 14-10-101 et seq. The state "
            "follows equitable distribution (C.R.S. § 14-10-113). Custody (allocation of parental "
            "responsibilities) uses best interests standard (C.R.S. § 14-10-124). Child support "
            "guidelines are in C.R.S. § 14-10-115."
        ),
        "criminal_records": (
            "Colorado allows sealing of criminal records under C.R.S. § 24-72-702 et seq. Drug "
            "convictions, certain felonies, and misdemeanors may be sealed after waiting periods. "
            "Colorado's ban-the-box law (C.R.S. § 24-5-101) applies to state employers and "
            "contractors."
        ),
        "immigration": (
            "Colorado does not have a statewide sanctuary policy. SB 19-139 limits cooperation "
            "with ICE detainers absent a judicial warrant. Driver's licenses are available to all "
            "residents under SB 13-251 (C.R.S. § 42-2-505). Colorado provides in-state tuition "
            "for undocumented students under the ASSET bill (C.R.S. § 23-1-113.5)."
        ),
    },
    "HI": {
        "landlord_tenant": (
            "Hawaii Residential Landlord-Tenant Code (HRS § 521-1 et seq.) governs tenancies. "
            "Security deposits are limited to one month's rent (HRS § 521-44). Deposits must be "
            "returned within 14 days (HRS § 521-44(c)). Eviction requires a 5-day notice for "
            "nonpayment (HRS § 521-68). Rent increases require 45 days' notice (HRS § 521-21(d))."
        ),
        "employment_rights": (
            "Hawaii Employment Practices Act (HRS § 378-1 et seq.) prohibits employment "
            "discrimination. Minimum wage is set by HRS § 387-2. The Hawaii Wage and Hour Law "
            "(HRS Chapter 387) governs timely payment. Hawaii requires temporary disability "
            "insurance under HRS § 392-1 and prepaid health care under HRS § 393-1."
        ),
        "consumer_protection": (
            "Hawaii Unfair and Deceptive Practices Act (HRS § 480-2) prohibits unfair or deceptive "
            "practices with treble damages. The Lemon Law (HRS § 481I-1 et seq.) covers new "
            "vehicles. The AG and the Office of Consumer Protection enforce the statute."
        ),
        "debt_collections": (
            "Hawaii does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 6 years (HRS § 657-1). Wage garnishment follows "
            "HRS § 652-1 with 25% of disposable earnings limit. Homestead exemption protects up "
            "to $30,000 for head of household under HRS § 651-92."
        ),
        "small_claims": (
            "Hawaii small claims court handles disputes up to $5,000 ($40,000 in security deposit "
            "cases) under HRS § 633-27. Filing fees are approximately $35. Cases are heard in "
            "District Court. No attorneys are permitted unless both parties agree."
        ),
        "contract_disputes": (
            "Hawaii follows common law and the UCC (HRS Chapter 490) for goods. The statute of "
            "frauds is at HRS § 656-1. Written contract SOL is 6 years (HRS § 657-1); oral is "
            "6 years."
        ),
        "traffic_violations": (
            "Hawaii traffic law is in HRS Title 17. Speeding is under HRS § 291C-101. DUI (OVUII) "
            "is under HRS § 291E-61. License suspensions are handled by county administrations. "
            "Hawaii uses an administrative revocation process for DUI under HRS § 291E-31."
        ),
        "family_law": (
            "Hawaii divorce is governed by HRS § 580-41 et seq. The state follows equitable "
            "distribution (HRS § 580-47). Custody uses best interests standard (HRS § 571-46). "
            "Child support guidelines are in HRS § 576D-7. Hawaii was an early adopter of "
            "civil unions (HRS § 572B-1)."
        ),
        "criminal_records": (
            "Hawaii allows expungement of arrest records under HRS § 831-3.2. Conviction "
            "expungement is very limited. First-time drug offenders may have records expunged "
            "under HRS § 706-622.5. Hawaii's ban-the-box law (HRS § 378-2.5) applies to all "
            "employers."
        ),
        "immigration": (
            "Hawaii does not have a formal sanctuary state policy but generally limits ICE "
            "cooperation. Driver's licenses require legal presence under HRS § 286-102. Hawaii "
            "provides in-state tuition for DACA recipients. The state has historically been "
            "welcoming to immigrant communities."
        ),
    },
    "ID": {
        "landlord_tenant": (
            "Idaho landlord-tenant law is in Idaho Code § 6-301 et seq. There is no statutory limit "
            "on security deposits. Deposits must be returned within 21-30 days depending on whether "
            "deductions apply (Idaho Code § 6-321). Eviction requires a 3-day notice for nonpayment "
            "(Idaho Code § 6-303)."
        ),
        "employment_rights": (
            "Idaho Human Rights Act (Idaho Code § 67-5901 et seq.) prohibits employment "
            "discrimination for employers with 5+ employees. Idaho follows the federal minimum "
            "wage. The Wage Claim Act (Idaho Code § 45-601 et seq.) governs timely payment. "
            "Workers' compensation is under Idaho Code § 72-101 et seq."
        ),
        "consumer_protection": (
            "Idaho Consumer Protection Act (Idaho Code § 48-601 et seq.) prohibits unfair or "
            "deceptive practices. The Lemon Law is limited in Idaho; consumers rely on the "
            "Magnuson-Moss Warranty Act. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Idaho Collection Agency Act (Idaho Code § 26-2222 et seq.) regulates collectors. "
            "The statute of limitations on written contracts is 5 years (Idaho Code § 5-216). "
            "Wage garnishment follows Idaho Code § 11-717 with 25% of disposable earnings limit. "
            "Homestead exemption protects up to $175,000 under Idaho Code § 55-1003."
        ),
        "small_claims": (
            "Idaho small claims court handles disputes up to $5,000 under Idaho Code § 1-2301. "
            "Filing fees are approximately $75. Cases are heard in the magistrate division of "
            "District Court. No attorneys are permitted. No appeals are allowed."
        ),
        "contract_disputes": (
            "Idaho follows common law and the UCC (Idaho Code Title 28) for goods. The statute "
            "of frauds is at Idaho Code § 9-505. Written contract SOL is 5 years (Idaho Code "
            "§ 5-216); oral is 4 years (Idaho Code § 5-217)."
        ),
        "traffic_violations": (
            "Idaho traffic law is in Idaho Code Title 49. Speeding is under Idaho Code § 49-654. "
            "DUI is under Idaho Code § 18-8004. Points accumulate under Idaho Code § 49-326. "
            "License suspensions are handled by the Idaho Transportation Department."
        ),
        "family_law": (
            "Idaho is a community property state (Idaho Code § 32-906). Divorce is governed by "
            "Idaho Code § 32-601 et seq. Custody uses best interests standard (Idaho Code "
            "§ 32-717). Child support guidelines are in Idaho R. Civ. P. Rule 126."
        ),
        "criminal_records": (
            "Idaho allows expungement under Idaho Code § 67-3004 for certain offenses. Juvenile "
            "records may be expunged under Idaho Code § 20-525A. Adult expungement is limited. "
            "Idaho does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Idaho does not have sanctuary state policies. Driver's licenses require legal presence "
            "under Idaho Code § 49-306. Idaho does not provide in-state tuition for undocumented "
            "students. State law enforcement cooperates with federal immigration authorities."
        ),
    },
    "MT": {
        "landlord_tenant": (
            "Montana Residential Landlord and Tenant Act (MCA § 70-24-101 et seq.) governs "
            "tenancies. There is no statutory limit on security deposits. Deposits must be returned "
            "within 10-30 days depending on the circumstances (MCA § 70-25-201). Eviction requires "
            "a 3-day notice for nonpayment (MCA § 70-24-422)."
        ),
        "employment_rights": (
            "Montana Human Rights Act (MCA § 49-2-101 et seq.) prohibits employment discrimination. "
            "Montana is the only state that is not at-will; the Wrongful Discharge from Employment "
            "Act (MCA § 39-2-901 et seq.) provides protections. Minimum wage is set by MCA "
            "§ 39-3-409. The Wage Protection Act (MCA § 39-3-201 et seq.) governs timely payment."
        ),
        "consumer_protection": (
            "Montana Unfair Trade Practices and Consumer Protection Act (MCA § 30-14-101 et seq.) "
            "prohibits unfair or deceptive practices. The Lemon Law (MCA § 61-4-501 et seq.) covers "
            "new vehicles. The AG and the Office of Consumer Protection enforce the statute."
        ),
        "debt_collections": (
            "Montana Collection Agency Act (MCA § 31-14-101 et seq.) regulates collectors. The "
            "statute of limitations on written contracts is 8 years (MCA § 27-2-202). Wage "
            "garnishment follows MCA § 25-13-614 with 25% of disposable earnings limit. Homestead "
            "exemption protects up to $350,000 under MCA § 70-32-104."
        ),
        "small_claims": (
            "Montana small claims court handles disputes up to $7,000 under MCA § 25-35-502. "
            "Filing fees are approximately $30. Cases are heard in the Justice Court or City Court. "
            "No attorneys are permitted. Appeals go to District Court within 10 days."
        ),
        "contract_disputes": (
            "Montana follows common law and the UCC (MCA Title 30) for goods. The statute of frauds "
            "is at MCA § 28-2-903. Written contract SOL is 8 years (MCA § 27-2-202); oral is 5 "
            "years (MCA § 27-2-202(1))."
        ),
        "traffic_violations": (
            "Montana traffic law is in MCA Title 61. Speeding is under MCA § 61-8-303. DUI is "
            "under MCA § 61-8-401. Points accumulate under MCA § 61-11-203. License suspensions "
            "are handled by the MVD. Montana previously had no daytime speed limit on rural "
            "highways but has since imposed limits."
        ),
        "family_law": (
            "Montana dissolution of marriage is governed by MCA § 40-4-101 et seq. The state "
            "follows equitable distribution (MCA § 40-4-202). Custody uses best interests standard "
            "(MCA § 40-4-212). Child support guidelines are in MCA § 40-4-204 and Admin. R. Mont. "
            "37.62.101."
        ),
        "criminal_records": (
            "Montana allows expungement of certain records under MCA § 46-18-1104. Misdemeanors "
            "may be expunged after completion of sentence. Montana does not have a statewide "
            "ban-the-box law."
        ),
        "immigration": (
            "Montana does not have sanctuary state policies. Driver's licenses require legal "
            "presence under MCA § 61-5-103. Montana does not provide in-state tuition for "
            "undocumented students. State law enforcement cooperates with federal immigration "
            "authorities."
        ),
    },
    "NM": {
        "landlord_tenant": (
            "New Mexico Owner-Resident Relations Act (NMSA § 47-8-1 et seq.) governs tenancies. "
            "Security deposits are limited to one month's rent for leases under one year (NMSA "
            "§ 47-8-18). Deposits must be returned within 30 days (NMSA § 47-8-18(D)). Eviction "
            "requires a 3-day notice for nonpayment (NMSA § 47-8-33(D))."
        ),
        "employment_rights": (
            "New Mexico Human Rights Act (NMSA § 28-1-1 et seq.) prohibits employment "
            "discrimination for employers with 4+ employees. Minimum wage is set by NMSA "
            "§ 50-4-22. The Minimum Wage Act (NMSA § 50-4-19 et seq.) governs wage payment. "
            "Workers' compensation is under NMSA § 52-1-1 et seq."
        ),
        "consumer_protection": (
            "New Mexico Unfair Practices Act (NMSA § 57-12-1 et seq.) prohibits unfair or "
            "deceptive practices with treble damages. The Lemon Law (NMSA § 57-16A-1 et seq.) "
            "covers new vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "New Mexico Collection Agency Regulatory Act (NMSA § 61-18A-1 et seq.) regulates "
            "collectors. The statute of limitations on written contracts is 6 years (NMSA "
            "§ 37-1-3). Wage garnishment follows NMSA § 35-12-7 with 25% of disposable earnings "
            "limit. Homestead exemption protects up to $60,000 under NMSA § 42-10-9."
        ),
        "small_claims": (
            "New Mexico metropolitan courts handle small claims up to $10,000 under NMSA § 34-8A-3. "
            "Filing fees are approximately $25-$50. Magistrate courts also have jurisdiction. Appeals "
            "go to District Court within 15 days."
        ),
        "contract_disputes": (
            "New Mexico follows common law and the UCC (NMSA Chapter 55) for goods. The statute of "
            "frauds is at NMSA § 38-7-1. Written contract SOL is 6 years (NMSA § 37-1-3); oral is "
            "4 years (NMSA § 37-1-4)."
        ),
        "traffic_violations": (
            "New Mexico traffic law is in NMSA Chapter 66. Speeding is under NMSA § 66-7-301. DUI "
            "(DWI) is under NMSA § 66-8-102. Points accumulate under NMSA § 66-5-29. License "
            "suspensions are handled by the MVD."
        ),
        "family_law": (
            "New Mexico is a community property state (NMSA § 40-3-8). Dissolution of marriage is "
            "governed by NMSA § 40-4-1 et seq. Custody uses best interests standard (NMSA "
            "§ 40-4-9). Child support guidelines are in NMSA § 40-4-11.1."
        ),
        "criminal_records": (
            "New Mexico allows expungement under NMSA § 29-3A-1 et seq. Certain offenses may be "
            "expunged after waiting periods. Cannabis-related offenses may qualify for automatic "
            "expungement. New Mexico does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "New Mexico does not have a formal sanctuary state policy but limits ICE cooperation "
            "in some contexts. Driver's licenses are available to all residents regardless of "
            "immigration status under NMSA § 66-5-9. New Mexico provides in-state tuition for "
            "undocumented students under NMSA § 21-1-4.6."
        ),
    },
    "NV": {
        "landlord_tenant": (
            "Nevada landlord-tenant law is in NRS Chapter 118A. Security deposits are limited to "
            "three months' rent (NRS 118A.242). Deposits must be returned within 30 days (NRS "
            "118A.242(4)). Eviction requires a 7-day notice for nonpayment (NRS 40.253). AB 486 "
            "added late fee protections. No statewide rent control exists, and NRS 268.4159 "
            "preempts local rent control."
        ),
        "employment_rights": (
            "Nevada law prohibits employment discrimination under NRS 613.310 et seq. Minimum wage "
            "is set by Nev. Const. Art. 15, § 16. The Nevada Wage Payment Act (NRS 608.010 et seq.) "
            "governs timely payment. Nevada requires paid leave under NRS 608.0197."
        ),
        "consumer_protection": (
            "Nevada Deceptive Trade Practices Act (NRS 598.0903 et seq.) prohibits unfair practices "
            "with treble damages. The Lemon Law (NRS 597.600 et seq.) covers new vehicles. The AG "
            "and the Consumer Affairs Bureau enforce consumer protections."
        ),
        "debt_collections": (
            "Nevada Collection Agency Act (NRS Chapter 649) regulates collectors. The statute of "
            "limitations on written contracts is 6 years (NRS 11.190(1)(b)). Wage garnishment "
            "follows NRS 31.295 with 25% of disposable earnings limit. Homestead exemption protects "
            "up to $605,000 under NRS 115.010."
        ),
        "small_claims": (
            "Nevada justice courts handle small claims up to $10,000 under NRS 73.010. Filing fees "
            "range from $36 to $83. Cases can be appealed to District Court within 10 days for "
            "trial de novo."
        ),
        "contract_disputes": (
            "Nevada follows common law and the UCC (NRS Title 8) for goods. The statute of frauds "
            "is at NRS 111.220. Written contract SOL is 6 years (NRS 11.190(1)(b)); oral is 4 years "
            "(NRS 11.190(2)(c))."
        ),
        "traffic_violations": (
            "Nevada traffic law is in NRS Chapter 484A-484E. Speeding is under NRS 484B.600. DUI "
            "is under NRS 484C.110. Demerit points accumulate under NRS 483.473. License suspensions "
            "are handled by the DMV."
        ),
        "family_law": (
            "Nevada is a community property state (NRS 123.220). Divorce is governed by NRS "
            "125.010 et seq. Custody uses best interests standard (NRS 125C.0035). Child support "
            "guidelines are in NRS 125B.070."
        ),
        "criminal_records": (
            "Nevada allows sealing of criminal records under NRS 179.245 et seq. Waiting periods "
            "range from 1-15 years depending on the offense. Certain marijuana convictions may be "
            "automatically sealed. NRS 179.301 restricts employer inquiries into sealed records."
        ),
        "immigration": (
            "Nevada does not have a formal sanctuary state policy. SB 538 limits voluntary ICE "
            "cooperation in some contexts. Driver authorization cards are available under NRS "
            "483.290 regardless of immigration status. Nevada provides in-state tuition for "
            "undocumented students under NRS 396.0202."
        ),
    },
    "OR": {
        "landlord_tenant": (
            "Oregon Residential Landlord and Tenant Act (ORS § 90.100 et seq.) governs tenancies. "
            "Security deposits are limited by prepaid rent rules and must be returned within 31 days "
            "(ORS § 90.300). Oregon enacted statewide rent control (SB 608/ORS § 90.323) capping "
            "increases at 7% plus CPI. No-cause evictions are limited for tenancies over one year."
        ),
        "employment_rights": (
            "Oregon employment discrimination law is in ORS § 659A.001 et seq. Minimum wage is set "
            "by ORS § 653.025. The Oregon Wage Claim Act (ORS § 652.110 et seq.) governs timely "
            "payment. Oregon requires paid sick leave under ORS § 653.601. Non-compete agreements "
            "are restricted under ORS § 653.295."
        ),
        "consumer_protection": (
            "Oregon Unlawful Trade Practices Act (ORS § 646.605 et seq.) prohibits deceptive "
            "practices with actual damages and attorney fees. The Lemon Law (ORS § 646A.400 et seq.) "
            "covers new vehicles. The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Oregon Unlawful Debt Collection Practices Act (ORS § 646.639) governs collectors. The "
            "statute of limitations on written contracts is 6 years (ORS § 12.080). Wage garnishment "
            "follows ORS § 18.385 with 25% of disposable earnings limit. Homestead exemption protects "
            "up to $40,000 ($50,000 joint) under ORS § 18.395."
        ),
        "small_claims": (
            "Oregon small claims court handles disputes up to $10,000 under ORS § 46.405. Filing "
            "fees range from $35 to $55. Cases are heard in the small claims department of Circuit "
            "Court or Justice Court. No attorneys are permitted."
        ),
        "contract_disputes": (
            "Oregon follows common law and the UCC (ORS Chapter 72) for goods. The statute of "
            "frauds is at ORS § 41.580. Written contract SOL is 6 years (ORS § 12.080); oral is "
            "6 years."
        ),
        "traffic_violations": (
            "Oregon traffic law is in ORS Chapter 811. Speeding is under ORS § 811.100. DUII is "
            "under ORS § 813.010. Oregon does not use a points system; instead, habitual offender "
            "provisions apply under ORS § 809.600. License suspensions are handled by the DMV."
        ),
        "family_law": (
            "Oregon dissolution of marriage is governed by ORS § 107.005 et seq. The state follows "
            "equitable distribution (ORS § 107.105). Custody uses best interests standard (ORS "
            "§ 107.137). Child support guidelines are in ORS § 25.275."
        ),
        "criminal_records": (
            "Oregon allows expungement (set-aside) of convictions under ORS § 137.225. Misdemeanors "
            "may be set aside 1-3 years after completion of sentence; certain felonies after 3-20 "
            "years. Oregon's ban-the-box law (ORS § 659A.360) applies to all employers."
        ),
        "immigration": (
            "Oregon's sanctuary state law (ORS § 181A.820) prohibits state and local resources from "
            "being used to detect or apprehend persons based solely on immigration status. Driver's "
            "licenses are available to all residents under ORS § 807.062. Oregon provides in-state "
            "tuition for undocumented students under the Oregon DREAM Act (ORS § 352.287)."
        ),
    },
    "UT": {
        "landlord_tenant": (
            "Utah Fit Premises Act (Utah Code § 57-22-1 et seq.) and the Utah Residential Landlord "
            "Provisions govern tenancies. There is no statutory limit on security deposits. Deposits "
            "must be returned within 30 days (Utah Code § 57-17-3). Eviction requires a 3-day notice "
            "for nonpayment (Utah Code § 78B-6-802)."
        ),
        "employment_rights": (
            "Utah Anti-Discrimination Act (Utah Code § 34A-5-101 et seq.) prohibits employment "
            "discrimination for employers with 15+ employees. Utah follows the federal minimum wage. "
            "The Payment of Wages Act (Utah Code § 34-28-1 et seq.) governs timely payment. Workers' "
            "compensation is under Utah Code § 34A-2-101 et seq."
        ),
        "consumer_protection": (
            "Utah Consumer Sales Practices Act (Utah Code § 13-11-1 et seq.) prohibits deceptive "
            "practices. The Lemon Law (Utah Code § 13-20-1 et seq.) covers new vehicles. The "
            "Division of Consumer Protection enforces the statute."
        ),
        "debt_collections": (
            "Utah Collection Agency Act (Utah Code § 12-1-1 et seq.) regulates collectors. The "
            "statute of limitations on written contracts is 6 years (Utah Code § 78B-2-309). Wage "
            "garnishment follows Utah Code § 70D-1-4 with 25% of disposable earnings limit. "
            "Homestead exemption protects up to $43,300 for individuals under Utah Code § 78B-5-503."
        ),
        "small_claims": (
            "Utah small claims court handles disputes up to $11,000 under Utah Code § 78A-8-102. "
            "Filing fees range from $60 to $185. Cases are heard in the Justice Court. Appeals go "
            "to District Court within 28 days."
        ),
        "contract_disputes": (
            "Utah follows common law and the UCC (Utah Code Title 70A) for goods. The statute of "
            "frauds is at Utah Code § 25-5-4. Written contract SOL is 6 years (Utah Code "
            "§ 78B-2-309); oral is 4 years (Utah Code § 78B-2-307)."
        ),
        "traffic_violations": (
            "Utah traffic law is in Utah Code Title 41. Speeding is under Utah Code § 41-6a-601. "
            "DUI is under Utah Code § 41-6a-502 (with a 0.05% BAC limit, the lowest in the U.S.). "
            "Points are not used; instead, conviction-based suspensions apply. License suspensions "
            "are handled by the Driver License Division."
        ),
        "family_law": (
            "Utah divorce is governed by Utah Code § 30-3-1 et seq. The state follows equitable "
            "distribution (Utah Code § 30-3-5). Custody uses best interests standard (Utah Code "
            "§ 30-3-10). Child support guidelines are in Utah Code § 78B-12-301."
        ),
        "criminal_records": (
            "Utah allows expungement under Utah Code § 77-40a-101 et seq. Clean Slate provisions "
            "provide automatic expungement for certain misdemeanors. Eligibility depends on offense "
            "type and waiting period. Utah does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Utah does not have sanctuary state policies. Utah provides driving privilege cards "
            "under Utah Code § 53-3-207 regardless of immigration status. Utah enacted HB 497 "
            "requiring law enforcement to verify immigration status in certain circumstances. "
            "In-state tuition is available for undocumented students under Utah Code § 53B-8-106."
        ),
    },
    "WA": {
        "landlord_tenant": (
            "Washington Residential Landlord-Tenant Act (RCW 59.18) governs tenancies. Security "
            "deposits must be returned within 21 days (RCW 59.18.280). Deposits must be held in a "
            "trust account. Eviction requires a 14-day notice for nonpayment (RCW 59.12.030(3)). "
            "Rent increases require 60 days' notice (RCW 59.18.140). Just cause eviction applies "
            "in many jurisdictions."
        ),
        "employment_rights": (
            "Washington Law Against Discrimination (RCW 49.60) prohibits employment discrimination. "
            "Minimum wage is set by RCW 49.46.020. The Wage Rebate Act (RCW 49.52) governs timely "
            "payment with double damages for violations. Washington requires paid sick leave under "
            "RCW 49.46.210. Non-compete agreements are restricted under RCW 49.62."
        ),
        "consumer_protection": (
            "Washington Consumer Protection Act (RCW 19.86) prohibits unfair or deceptive practices "
            "with treble damages up to $25,000. The Lemon Law (RCW 19.118) covers new vehicles. "
            "The AG enforces consumer protection."
        ),
        "debt_collections": (
            "Washington Collection Agency Act (RCW 19.16) regulates collectors. The statute of "
            "limitations on written contracts is 6 years (RCW 4.16.040). Wage garnishment follows "
            "RCW 6.27.150 with 25% of disposable earnings limit. Homestead exemption protects up "
            "to $125,000 under RCW 6.13.030."
        ),
        "small_claims": (
            "Washington small claims court handles disputes up to $10,000 under RCW 12.40.010. "
            "Filing fees range from $14 to $57. Cases are heard in District Court. No attorneys "
            "are permitted unless both parties agree. No appeals by the plaintiff."
        ),
        "contract_disputes": (
            "Washington follows common law and the UCC (RCW Title 62A) for goods. The statute of "
            "frauds is at RCW 19.36.010. Written contract SOL is 6 years (RCW 4.16.040); oral is "
            "3 years (RCW 4.16.080)."
        ),
        "traffic_violations": (
            "Washington traffic law is in RCW Title 46. Speeding is under RCW 46.61.400. DUI is "
            "under RCW 46.61.502. Washington does not use a points system; instead, moving violation "
            "frequency triggers suspension under RCW 46.20.342. License suspensions are handled by "
            "the DOL."
        ),
        "family_law": (
            "Washington is a community property state (RCW 26.16.030). Dissolution of marriage is "
            "governed by RCW 26.09. Custody uses best interests standard (RCW 26.09.002). Child "
            "support guidelines are in RCW 26.19."
        ),
        "criminal_records": (
            "Washington allows vacating convictions under RCW 9.94A.640 (felonies) and "
            "RCW 9.96.060 (misdemeanors). The New Hope Act expanded eligibility. Washington's "
            "Fair Chance Act (RCW 49.94) is a ban-the-box law for all employers."
        ),
        "immigration": (
            "Washington's Keep Washington Working Act (RCW 43.17.420) limits state and local "
            "cooperation with federal immigration authorities. Driver's licenses are available to "
            "all residents under RCW 46.20.035. Washington provides in-state tuition for "
            "undocumented students under the REAL Hope Act (RCW 28B.15.012)."
        ),
    },
    "WY": {
        "landlord_tenant": (
            "Wyoming landlord-tenant law is in Wyo. Stat. § 1-21-1201 et seq. There is no "
            "statutory limit on security deposits. Deposits must be returned within 30 days or "
            "15 days for non-refundable fees (Wyo. Stat. § 1-21-1208). Eviction requires a 3-day "
            "notice for nonpayment (Wyo. Stat. § 1-21-1003)."
        ),
        "employment_rights": (
            "Wyoming Fair Employment Practices Act (Wyo. Stat. § 27-9-101 et seq.) prohibits "
            "employment discrimination for employers with 2+ employees. Wyoming follows the federal "
            "minimum wage. The Wage Payment Act (Wyo. Stat. § 27-4-101 et seq.) governs timely "
            "payment. Workers' compensation is under Wyo. Stat. § 27-14-101 et seq."
        ),
        "consumer_protection": (
            "Wyoming Consumer Protection Act (Wyo. Stat. § 40-12-101 et seq.) prohibits deceptive "
            "practices. The Lemon Law (Wyo. Stat. § 40-17-101 et seq.) covers new vehicles. The "
            "AG enforces consumer protection."
        ),
        "debt_collections": (
            "Wyoming does not have a separate state debt collection statute. The statute of "
            "limitations on written contracts is 10 years (Wyo. Stat. § 1-3-105). Wage garnishment "
            "follows Wyo. Stat. § 1-15-408 with federal limits. Homestead exemption protects up "
            "to $40,000 under Wyo. Stat. § 1-20-101."
        ),
        "small_claims": (
            "Wyoming small claims court handles disputes up to $6,000 under Wyo. Stat. § 1-21-201. "
            "Filing fees are approximately $10-$20. Cases are heard in Circuit Court. Appeals go to "
            "District Court within 10 days."
        ),
        "contract_disputes": (
            "Wyoming follows common law and the UCC (Wyo. Stat. Title 34.1) for goods. The statute "
            "of frauds is at Wyo. Stat. § 1-23-105. Written contract SOL is 10 years (Wyo. Stat. "
            "§ 1-3-105); oral is 8 years (Wyo. Stat. § 1-3-105)."
        ),
        "traffic_violations": (
            "Wyoming traffic law is in Wyo. Stat. Title 31. Speeding is under Wyo. Stat. § 31-5-301. "
            "DUI is under Wyo. Stat. § 31-5-233. License suspensions are handled by the WYDOT. "
            "Wyoming does not use a points system for driver's licenses."
        ),
        "family_law": (
            "Wyoming divorce is governed by Wyo. Stat. § 20-2-101 et seq. The state follows "
            "equitable distribution (Wyo. Stat. § 20-2-114). Custody uses best interests standard "
            "(Wyo. Stat. § 20-2-201). Child support guidelines are in Wyo. Stat. § 20-2-304."
        ),
        "criminal_records": (
            "Wyoming allows expungement of certain records under Wyo. Stat. § 7-13-1501 et seq. "
            "Misdemeanor expungement is available after waiting periods. Felony expungement is "
            "limited. Wyoming does not have a statewide ban-the-box law."
        ),
        "immigration": (
            "Wyoming does not have sanctuary state policies. Driver's licenses require legal "
            "presence under Wyo. Stat. § 31-7-128. Wyoming does not provide in-state tuition for "
            "undocumented students. State law enforcement cooperates with federal immigration "
            "authorities."
        ),
    },
}
