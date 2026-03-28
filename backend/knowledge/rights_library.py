"""Know Your Rights library with pre-built legal guides.

Provides structured rights guides organized by legal domain, covering
the most common legal scenarios people face. Guides are state-aware
and include plain-English explanations, specific rights, action steps,
relevant deadlines, and statute citations.
"""

from __future__ import annotations

from pydantic import BaseModel


class RightsGuide(BaseModel):
    """A structured legal rights guide for a specific scenario.

    Attributes:
        id: Unique guide identifier (domain_slug format).
        domain: Legal domain this guide belongs to.
        title: Human-readable guide title.
        description: Brief one-line summary.
        explanation: Plain-English explanation of the legal situation.
        your_rights: List of specific rights the user has.
        action_steps: Ordered list of steps to take.
        deadlines: Key deadlines and time limits to be aware of.
        common_mistakes: Mistakes to avoid in this situation.
        when_to_get_a_lawyer: When professional help is recommended.
    """

    id: str
    domain: str
    title: str
    description: str
    explanation: str
    your_rights: list[str]
    action_steps: list[str]
    deadlines: list[str]
    common_mistakes: list[str]
    when_to_get_a_lawyer: str


# ---------- Guide Definitions ----------

RIGHTS_GUIDES: list[RightsGuide] = [
    # --- LANDLORD / TENANT ---
    RightsGuide(
        id="tenant_eviction_defense",
        domain="landlord_tenant",
        title="Eviction Defense",
        description="Understanding your rights when facing eviction",
        explanation=(
            "An eviction (also called an unlawful detainer or summary process) is a legal "
            "proceeding where your landlord asks a court to order you to leave. You cannot be "
            "forced out without a court order — self-help eviction (changing locks, removing "
            "belongings, shutting off utilities) is illegal in every state."
        ),
        your_rights=[
            "You must receive proper written notice before any court filing",
            "You have the right to appear in court and present your defense",
            "You cannot be locked out or have utilities shut off without a court order",
            "You may have the right to cure (fix the problem) before eviction proceeds",
            "Retaliatory evictions are illegal — landlords cannot evict you for complaining about conditions",
            "You may be entitled to a jury trial in some states",
            "You have the right to assert habitability defenses if conditions are poor",
        ],
        action_steps=[
            "Read the eviction notice carefully — note the type (nonpayment, lease violation, no-cause) and deadline",
            "Check if the notice complies with your state's requirements (proper form, delivery method, time period)",
            "Gather evidence: photos, repair requests, rent receipts, lease copy, communication records",
            "File an answer with the court before the deadline — failing to respond usually means automatic loss",
            "Request a hearing date if one is not automatically set",
            "Prepare your defense and organize your evidence chronologically",
            "Attend the hearing — bring copies of all documents for the judge and opposing party",
        ],
        deadlines=[
            "Response deadline: Usually 5-30 days after receiving the notice (varies by state)",
            "Cure period: Typically 3-14 days to fix a lease violation or pay rent (if allowed)",
            "Appeal deadline: Usually 5-10 days after judgment",
        ],
        common_mistakes=[
            "Ignoring the eviction notice or court summons — this guarantees a default judgment against you",
            "Moving out before the court process is complete — you may lose claims for damages",
            "Not documenting habitability issues before they become relevant",
            "Withholding rent without following your state's proper procedure",
        ],
        when_to_get_a_lawyer=(
            "If you're facing eviction for any reason other than simple nonpayment, if you believe "
            "the eviction is retaliatory or discriminatory, or if losing your housing would cause "
            "severe hardship. Many areas have free legal aid for tenants facing eviction."
        ),
    ),
    RightsGuide(
        id="tenant_security_deposit",
        domain="landlord_tenant",
        title="Security Deposit Recovery",
        description="Getting your security deposit back when you move out",
        explanation=(
            "When you move out, your landlord must return your security deposit within a "
            "state-specific timeframe (usually 14-30 days) along with an itemized list of any "
            "deductions. Landlords can only deduct for actual damages beyond normal wear and tear, "
            "unpaid rent, or cleaning if the unit wasn't left in reasonable condition."
        ),
        your_rights=[
            "Right to receive your deposit back within your state's required timeframe",
            "Right to an itemized statement of any deductions with receipts",
            "Normal wear and tear cannot be deducted (faded paint, worn carpet, minor nail holes)",
            "Many states require deposits be held in separate accounts",
            "Some states require landlords to pay interest on deposits",
            "If landlord fails to return on time, you may be entitled to double or triple damages",
        ],
        action_steps=[
            "Document the unit's condition at move-in AND move-out with dated photos/video",
            "Provide your landlord with a forwarding address in writing",
            "Wait for the state-required return period to pass",
            "If not returned, send a formal demand letter via certified mail",
            "If still not returned, file in small claims court — most cases qualify",
            "Bring your documentation, lease, and demand letter to court",
        ],
        deadlines=[
            "Return deadline: 14-45 days after move-out depending on state",
            "Small claims filing: Check your state's statute of limitations (usually 2-6 years)",
            "Demand letter: Send within 30 days of the return deadline passing",
        ],
        common_mistakes=[
            "Not doing a move-in/move-out inspection with documentation",
            "Not providing a forwarding address in writing",
            "Accepting a partial return without reserving the right to claim the rest",
            "Waiting too long to take action after the deadline passes",
        ],
        when_to_get_a_lawyer=(
            "Generally not needed — small claims court is designed for this. Consider legal help "
            "if the amount is large or the landlord has a pattern of withholding deposits."
        ),
    ),
    RightsGuide(
        id="tenant_habitability",
        domain="landlord_tenant",
        title="Habitability Rights",
        description="When your rental has serious maintenance problems",
        explanation=(
            "Every state has an implied warranty of habitability — your landlord must maintain "
            "the property in livable condition. This covers essential services like heat, hot water, "
            "plumbing, electricity, structural safety, and pest control. If conditions are "
            "uninhabitable, you have legal remedies."
        ),
        your_rights=[
            "Right to a habitable dwelling with working essential systems",
            "Right to request repairs in writing and have them made in a reasonable time",
            "Right to withhold rent (in some states, following proper procedure)",
            "Right to repair and deduct (fix it yourself and deduct cost from rent, in some states)",
            "Right to report code violations to local housing authorities without retaliation",
            "Right to terminate lease if conditions are truly uninhabitable",
        ],
        action_steps=[
            "Document all issues with photos, video, and written descriptions with dates",
            "Notify your landlord in writing (email or certified mail) requesting repairs",
            "Keep copies of all communication and note response times",
            "If no response, contact your local housing code enforcement or health department",
            "Consider rent withholding or repair-and-deduct ONLY if your state allows it and you follow proper procedure",
            "If conditions are dangerous, contact local authorities immediately",
        ],
        deadlines=[
            "Repair request response: Landlords typically have 14-30 days for non-emergency repairs",
            "Emergency repairs (no heat, flooding, gas leak): Must be addressed within 24-48 hours",
            "Code violation complaints: No deadline, but file promptly for safety",
        ],
        common_mistakes=[
            "Not putting repair requests in writing — verbal requests are hard to prove",
            "Withholding rent without following your state's specific legal procedure",
            "Not documenting conditions before and after",
            "Abandoning the unit without proper notice",
        ],
        when_to_get_a_lawyer=(
            "If conditions pose immediate health or safety risks, if your landlord retaliates "
            "against you for requesting repairs, or if you need to break your lease due to "
            "uninhabitable conditions."
        ),
    ),

    # --- EMPLOYMENT ---
    RightsGuide(
        id="employment_wage_theft",
        domain="employment_rights",
        title="Wage Theft",
        description="When your employer doesn't pay what you're owed",
        explanation=(
            "Wage theft occurs when an employer fails to pay you what you've earned. This includes "
            "unpaid wages, withheld tips, unpaid overtime, misclassification as an independent "
            "contractor, off-the-clock work, illegal deductions, or not paying minimum wage. "
            "It's the most common workplace violation in America."
        ),
        your_rights=[
            "Right to be paid at least the applicable minimum wage (federal, state, or local — whichever is highest)",
            "Right to overtime pay (1.5x) for hours over 40/week for non-exempt employees under FLSA",
            "Right to receive all earned tips without employer taking a share (beyond valid tip pools)",
            "Right to receive final paycheck within your state's required timeframe",
            "Right to file a wage complaint with your state labor board or the federal DOL",
            "Right to sue for unpaid wages plus liquidated damages (often double the amount owed)",
            "Protection from retaliation for filing a wage claim",
        ],
        action_steps=[
            "Document everything: keep your own records of hours worked, pay stubs, and pay dates",
            "Calculate exactly what you're owed — compare hours worked to pay received",
            "Raise the issue with your employer in writing first (email creates a record)",
            "File a complaint with your state's Department of Labor or wage board",
            "Alternatively, file with the federal DOL Wage and Hour Division",
            "Consider small claims court for amounts within the limit",
            "If amount is large, consult an employment attorney (many work on contingency)",
        ],
        deadlines=[
            "FLSA claims: 2-year statute of limitations (3 years for willful violations)",
            "State claims: Varies by state, typically 2-6 years",
            "Final paycheck: Due immediately to 30 days after separation depending on state",
        ],
        common_mistakes=[
            "Not keeping your own records of hours worked",
            "Assuming you're not entitled to overtime because you're salaried (salary alone doesn't determine exemption)",
            "Waiting too long to file a claim and missing the statute of limitations",
            "Not filing both state and federal claims when possible",
        ],
        when_to_get_a_lawyer=(
            "If you're owed a significant amount, if the issue affects multiple employees (potential "
            "class action), or if your employer retaliates against you for raising the issue. Many "
            "employment attorneys take wage cases on contingency."
        ),
    ),
    RightsGuide(
        id="employment_wrongful_termination",
        domain="employment_rights",
        title="Wrongful Termination",
        description="Understanding if your firing was illegal",
        explanation=(
            "Most US employment is 'at-will,' meaning you can be fired for any reason or no reason. "
            "However, there are important exceptions: you cannot be fired for discriminatory reasons "
            "(race, sex, age, disability, religion, etc.), for whistleblowing, for filing a workers' "
            "comp claim, for taking FMLA leave, or for exercising other protected rights."
        ),
        your_rights=[
            "Protection from discrimination-based termination under Title VII, ADA, ADEA, and state laws",
            "Protection from retaliation for reporting illegal activity (whistleblower protections)",
            "Right to file with the EEOC within 180-300 days of discriminatory termination",
            "Right to unemployment benefits if terminated without cause",
            "Right to COBRA health insurance continuation (employers with 20+ employees)",
            "Right to receive final paycheck per state requirements",
            "Right to review your personnel file in many states",
        ],
        action_steps=[
            "Document why you believe the termination was wrongful — gather emails, reviews, witness names",
            "Request your personnel file and any termination documentation in writing",
            "File for unemployment benefits immediately",
            "File an EEOC charge if discrimination is suspected (required before lawsuit)",
            "File a whistleblower complaint with the relevant agency if applicable",
            "Consult an employment attorney — most offer free initial consultations",
            "Do not sign any severance agreement without understanding what you're giving up",
        ],
        deadlines=[
            "EEOC charge: Must be filed within 180 days (300 days if state has a fair employment agency)",
            "Unemployment filing: File as soon as possible after termination",
            "State discrimination claims: Varies, often 1-3 years",
            "Whistleblower claims: 30-180 days depending on the statute",
        ],
        common_mistakes=[
            "Missing the EEOC filing deadline — this bars your right to sue",
            "Signing a severance agreement that waives your right to file claims",
            "Not documenting the reasons given for termination",
            "Badmouthing your employer on social media before consulting a lawyer",
        ],
        when_to_get_a_lawyer=(
            "Always consult an attorney for wrongful termination claims. Many employment attorneys "
            "work on contingency. You need legal advice before signing any severance agreements."
        ),
    ),
    RightsGuide(
        id="employment_discrimination",
        domain="employment_rights",
        title="Workplace Discrimination",
        description="Recognizing and fighting employment discrimination",
        explanation=(
            "Employment discrimination occurs when an employer treats you differently because of a "
            "protected characteristic: race, color, religion, sex (including pregnancy and sexual "
            "orientation), national origin, age (40+), disability, or genetic information. This "
            "covers hiring, firing, pay, promotions, harassment, and other terms of employment."
        ),
        your_rights=[
            "Protection from discrimination in all aspects of employment",
            "Right to reasonable accommodation for disability or religious practice",
            "Right to equal pay for equal work regardless of gender",
            "Right to a workplace free from harassment based on protected characteristics",
            "Right to file a complaint without retaliation",
            "Right to file with the EEOC and/or state agency",
        ],
        action_steps=[
            "Document specific incidents: dates, times, what was said/done, witnesses",
            "Report the discrimination through your employer's internal complaint process",
            "File a charge with the EEOC (required before filing a federal lawsuit)",
            "Cooperate with the EEOC investigation",
            "If the EEOC issues a right-to-sue letter, you have 90 days to file suit",
            "Consider filing a parallel state complaint for additional protections",
        ],
        deadlines=[
            "EEOC charge: 180 days (300 days with state agency) from discriminatory act",
            "Federal lawsuit: 90 days after receiving right-to-sue letter from EEOC",
            "State claims: Varies by state, often 1-3 years",
        ],
        common_mistakes=[
            "Not documenting incidents as they happen",
            "Quitting without reporting — this can weaken your claim",
            "Missing the EEOC filing deadline",
            "Not filing both state and federal claims",
        ],
        when_to_get_a_lawyer=(
            "Consult an employment attorney if you believe you've been discriminated against. "
            "Many offer free consultations and work on contingency."
        ),
    ),

    # --- CONSUMER PROTECTION ---
    RightsGuide(
        id="consumer_refund_rights",
        domain="consumer_protection",
        title="Return and Refund Rights",
        description="Your rights when products or services don't deliver",
        explanation=(
            "While there's no federal law requiring refunds for purchases you simply regret, you "
            "have strong protections when products are defective, services aren't delivered, or "
            "sellers engage in deceptive practices. State consumer protection laws often provide "
            "remedies beyond the retailer's own return policy."
        ),
        your_rights=[
            "Right to a refund for defective products under implied warranty of merchantability",
            "Right to dispute credit card charges within 60 days under the Fair Credit Billing Act",
            "Right to a full refund for undelivered goods or services",
            "State consumer protection laws often allow treble (3x) damages for deceptive practices",
            "Right to cancel certain contracts within a cooling-off period (3 days for door-to-door sales)",
            "FTC Mail Order Rule: sellers must ship within promised time or offer a refund",
        ],
        action_steps=[
            "Contact the seller directly first — document the request in writing",
            "Dispute the charge with your credit card company if seller doesn't cooperate",
            "File a complaint with your state Attorney General's consumer protection division",
            "File a complaint with the FTC at reportfraud.ftc.gov",
            "File a complaint with the Better Business Bureau",
            "Consider small claims court for amounts within the limit",
        ],
        deadlines=[
            "Credit card dispute: 60 days from the billing statement date",
            "Warranty claims: Varies by state implied warranty laws",
            "FTC cooling-off period: 3 days for door-to-door sales over $25",
            "State consumer protection claims: Typically 2-4 years",
        ],
        common_mistakes=[
            "Not keeping receipts and purchase documentation",
            "Waiting too long to dispute a credit card charge",
            "Accepting a store credit when you're entitled to a full refund",
            "Not sending a demand letter before filing suit (required in many states)",
        ],
        when_to_get_a_lawyer=(
            "For high-value purchases, pattern of deceptive practices, or if the seller is unresponsive. "
            "Many consumer protection statutes allow recovery of attorney fees."
        ),
    ),
    RightsGuide(
        id="consumer_lemon_law",
        domain="consumer_protection",
        title="Lemon Law",
        description="When your new vehicle has repeated defects",
        explanation=(
            "Every state has a lemon law covering new vehicles with substantial defects that the "
            "dealer cannot fix after a reasonable number of attempts. If your car qualifies as a "
            "lemon, you're entitled to a replacement or refund. Some states also cover used vehicles "
            "or leased vehicles."
        ),
        your_rights=[
            "Right to a replacement vehicle or full refund if your vehicle qualifies as a lemon",
            "Manufacturer must have a reasonable number of repair attempts (usually 3-4 for the same issue)",
            "Vehicle must not be out of service for more than 30 cumulative days",
            "Right to recover attorney fees in most states if you prevail",
            "Coverage typically applies during the manufacturer's warranty period",
            "Some states cover used vehicles purchased from dealers with implied warranties",
        ],
        action_steps=[
            "Keep detailed records of every repair visit: dates, mileage, description of problem, work done",
            "Get written repair orders for every visit — never accept verbal promises",
            "Notify the manufacturer in writing after multiple repair attempts",
            "Check if your state requires manufacturer arbitration before lawsuit",
            "File a lemon law claim with your state's consumer protection agency",
            "Consult a lemon law attorney (most work on contingency)",
        ],
        deadlines=[
            "Filing deadline: Typically within the warranty period or 1-2 years of purchase",
            "Notification to manufacturer: Required in most states before filing",
            "Arbitration: If required, usually must be completed within 40 days",
        ],
        common_mistakes=[
            "Not keeping written repair orders for every visit",
            "Accepting repeated verbal assurances that the problem is fixed",
            "Trading in the vehicle before pursuing a lemon law claim",
            "Not notifying the manufacturer in writing as required",
        ],
        when_to_get_a_lawyer=(
            "Lemon law attorneys typically work on contingency (manufacturer pays fees if you win). "
            "Consult one after the 2nd failed repair attempt for the same issue."
        ),
    ),
    RightsGuide(
        id="consumer_debt_collection",
        domain="debt_collections",
        title="Debt Collection Harassment",
        description="Your rights when debt collectors contact you",
        explanation=(
            "The Fair Debt Collection Practices Act (FDCPA) strictly regulates how third-party debt "
            "collectors can contact you. They cannot harass, threaten, or deceive you. You have the "
            "right to verify the debt, dispute it, and tell collectors to stop contacting you. "
            "Many states have additional protections."
        ),
        your_rights=[
            "Right to written validation of the debt within 5 days of first contact",
            "Right to dispute the debt in writing within 30 days — collector must verify",
            "Right to tell collectors to stop contacting you (send a cease letter)",
            "Collectors cannot call before 8am or after 9pm",
            "Collectors cannot contact your workplace if you tell them not to",
            "Collectors cannot threaten arrest, use profanity, or misrepresent the debt",
            "Collectors cannot discuss your debt with anyone except your spouse or attorney",
            "Right to sue collectors who violate the FDCPA for $1,000 plus actual damages",
        ],
        action_steps=[
            "Request written debt validation — do this within 30 days of first contact",
            "Verify the debt is actually yours and the amount is correct",
            "Check the statute of limitations — you may not be legally obligated to pay old debts",
            "Send a cease-and-desist letter via certified mail if harassment continues",
            "Document every call: date, time, what was said, collector's name",
            "File complaints with the CFPB and your state AG",
            "Consult with a consumer attorney if violations are severe",
        ],
        deadlines=[
            "Debt validation request: Within 30 days of first collector contact",
            "FDCPA lawsuit: 1 year from the date of the violation",
            "Statute of limitations on debt: 3-10 years depending on state and debt type",
        ],
        common_mistakes=[
            "Acknowledging the debt or making a payment on time-barred debt (can restart the clock)",
            "Not requesting validation in writing within the 30-day window",
            "Ignoring collection lawsuits — always file an answer",
            "Giving bank account information to collectors over the phone",
        ],
        when_to_get_a_lawyer=(
            "If a collector files a lawsuit, if you're being harassed despite a cease letter, or "
            "if you want to countersue for FDCPA violations. Many consumer attorneys work on contingency."
        ),
    ),

    # --- TRAFFIC ---
    RightsGuide(
        id="traffic_ticket_fight",
        domain="traffic_violations",
        title="Fighting a Traffic Ticket",
        description="Your options when you receive a traffic citation",
        explanation=(
            "You always have the right to contest a traffic ticket in court. Many tickets can be "
            "reduced or dismissed, especially if the officer doesn't appear, the equipment wasn't "
            "properly calibrated, or there were mitigating circumstances. You usually have options "
            "beyond just paying or fighting: traffic school, deferred adjudication, or plea bargaining."
        ),
        your_rights=[
            "Right to plead not guilty and request a court hearing",
            "Right to see the evidence against you (radar calibration records, officer's notes)",
            "Right to cross-examine the officer who issued the ticket",
            "Right to present your own evidence and witnesses",
            "Right to appeal an unfavorable decision",
            "Right to traffic school in many states to avoid points",
            "Right to a continuance if you need more time to prepare",
        ],
        action_steps=[
            "Read the ticket carefully — note the deadline to respond and court information",
            "Decide: pay (accept guilt), attend traffic school (if eligible), or fight in court",
            "If fighting: plead not guilty by the deadline on the ticket",
            "Request discovery: officer's notes, radar calibration records, dashcam footage",
            "Prepare your defense: photos of the scene, witness statements, speed limit signs",
            "Attend the hearing — dress professionally and be respectful",
            "If guilty verdict, ask about traffic school or payment plans",
        ],
        deadlines=[
            "Response deadline: Usually 15-30 days from ticket date",
            "Traffic school election: Must choose before trial in most states",
            "Appeal: Usually 30 days from conviction",
        ],
        common_mistakes=[
            "Ignoring the ticket — this can result in a warrant and license suspension",
            "Paying the ticket without considering traffic school options",
            "Not checking whether the officer's equipment was properly calibrated",
            "Admitting guilt when speaking with the officer (can be used in court)",
        ],
        when_to_get_a_lawyer=(
            "For serious violations (DUI, reckless driving, hit-and-run), if points would suspend "
            "your license, or if the ticket carries criminal penalties. Traffic attorneys typically "
            "charge a flat fee."
        ),
    ),
    RightsGuide(
        id="traffic_dui_process",
        domain="traffic_violations",
        title="DUI/DWI Process",
        description="Understanding the DUI legal process and your rights",
        explanation=(
            "A DUI (Driving Under the Influence) or DWI charge triggers both criminal proceedings "
            "and administrative license suspension. These are separate processes with different "
            "deadlines. You have constitutional rights throughout the criminal process, and you "
            "may have defenses even if you failed a breath test."
        ),
        your_rights=[
            "Right to remain silent — you do not have to answer questions about drinking",
            "Right to refuse field sobriety tests in most states (but chemical tests may be required under implied consent)",
            "Right to an attorney — request one immediately upon arrest",
            "Right to an independent blood test after the state's test",
            "Right to challenge the traffic stop itself (was there probable cause?)",
            "Right to a DMV hearing to contest license suspension (separate from court)",
            "Right to a jury trial for DUI charges",
        ],
        action_steps=[
            "Request a DMV hearing immediately — you usually have only 7-15 days",
            "Hire a DUI attorney as soon as possible",
            "Document everything: where you were, what you consumed, timeline, witnesses",
            "Request maintenance and calibration records for the breathalyzer",
            "Request dashcam and bodycam footage from the traffic stop",
            "Attend all court appearances and comply with any pre-trial conditions",
            "Explore diversion programs if available for first-time offenders",
        ],
        deadlines=[
            "DMV hearing request: 7-15 days from arrest (varies by state — this is CRITICAL)",
            "Arraignment: Usually within 48-72 hours of arrest",
            "Diversion program application: Varies, often within 30 days of arraignment",
        ],
        common_mistakes=[
            "Missing the DMV hearing deadline — automatic license suspension",
            "Talking to police without an attorney present",
            "Posting about the arrest on social media",
            "Not requesting calibration records for the breathalyzer",
        ],
        when_to_get_a_lawyer=(
            "ALWAYS hire a DUI attorney. DUI carries serious consequences: jail time, license loss, "
            "insurance increases, and a criminal record. This is not a do-it-yourself legal matter."
        ),
    ),

    # --- FAMILY LAW ---
    RightsGuide(
        id="family_divorce_basics",
        domain="family_law",
        title="Divorce Basics",
        description="Understanding the divorce process and your rights",
        explanation=(
            "Divorce (dissolution of marriage) ends your legal marriage and divides assets, debts, "
            "and if applicable, determines custody and support. Every state offers no-fault divorce. "
            "The process can be uncontested (agreed) or contested. Understanding property division "
            "rules (community property vs. equitable distribution) in your state is crucial."
        ),
        your_rights=[
            "Right to file for divorce in your state after meeting residency requirements",
            "Right to an equitable (fair) division of marital property and debts",
            "Right to request spousal support (alimony/maintenance) based on circumstances",
            "Right to request temporary orders for support, custody, and possession of the home during proceedings",
            "Right to discovery — access to your spouse's financial information",
            "Right to mediation or collaborative divorce as alternatives to litigation",
            "Right to modify support and custody orders when circumstances change significantly",
        ],
        action_steps=[
            "Gather financial documents: tax returns, bank statements, retirement accounts, property deeds, debts",
            "Open individual bank accounts and credit cards if you don't have them",
            "Document all marital assets and debts",
            "Consult with a family law attorney (many offer free initial consultations)",
            "File for divorce and serve your spouse (or negotiate an uncontested filing)",
            "Request temporary orders if needed for support, custody, or restraining",
            "Attend mediation if ordered or voluntarily to resolve disputes",
        ],
        deadlines=[
            "Residency requirement: 30 days to 1 year depending on state",
            "Waiting period: Many states require 30-180 days between filing and finalization",
            "Response deadline: Spouse typically has 20-30 days to respond after being served",
            "Financial disclosure: Usually required within 45-60 days of filing",
        ],
        common_mistakes=[
            "Hiding assets — courts penalize this severely",
            "Moving out of the family home without legal advice (can affect property rights)",
            "Using children as leverage in negotiations",
            "Not requesting temporary orders when needed for financial stability",
            "Agreeing to terms without understanding their long-term financial impact",
        ],
        when_to_get_a_lawyer=(
            "Always consult an attorney for divorce, especially if children, significant assets, "
            "or business ownership are involved. Uncontested divorces can sometimes be handled with "
            "limited attorney assistance or online services."
        ),
    ),
    RightsGuide(
        id="family_custody_basics",
        domain="family_law",
        title="Child Custody Basics",
        description="Understanding custody types, rights, and the best interests standard",
        explanation=(
            "Child custody determines who makes decisions for and lives with your children. There are "
            "two types: legal custody (decision-making authority for education, health, religion) and "
            "physical custody (where the child lives). Both can be sole or joint. Courts decide based "
            "on the 'best interests of the child' standard."
        ),
        your_rights=[
            "Both parents have equal rights to custody absent a court order",
            "Right to petition for custody or modification of existing orders",
            "Right to parenting time (visitation) even without custody",
            "Right to access your child's school and medical records",
            "Right to be consulted on major decisions if you have joint legal custody",
            "Right to object to relocation if the custodial parent wants to move",
            "Right to request a custody evaluation by a neutral professional",
        ],
        action_steps=[
            "Document your involvement in your children's lives (school, medical, activities)",
            "Propose a detailed parenting plan covering schedules, holidays, and decision-making",
            "Keep communication with the other parent civil and in writing (text/email)",
            "Never speak negatively about the other parent in front of the children",
            "File for custody through the family court in your county",
            "Comply with all temporary orders during the proceedings",
            "Consider mediation before contested hearings",
        ],
        deadlines=[
            "Emergency custody: Can be filed immediately if child is in danger",
            "Modification: Can be requested when there's a substantial change in circumstances",
            "Relocation notice: Usually 30-60 days before a planned move",
        ],
        common_mistakes=[
            "Withholding the child from the other parent without a court order",
            "Not following custody orders exactly as written",
            "Involving children in adult disputes",
            "Not documenting the other parent's violations of custody orders",
        ],
        when_to_get_a_lawyer=(
            "Always recommended for contested custody. Free consultations are widely available. "
            "Legal aid may help if you can't afford an attorney."
        ),
    ),

    # --- CRIMINAL RECORDS ---
    RightsGuide(
        id="criminal_expungement",
        domain="criminal_records",
        title="Record Expungement",
        description="Clearing your criminal record",
        explanation=(
            "Expungement (or sealing) of criminal records can remove past convictions or arrests "
            "from public view, making it easier to find employment, housing, and education. "
            "Eligibility varies by state, but generally depends on the type of offense, time since "
            "completion of sentence, and whether you have subsequent offenses."
        ),
        your_rights=[
            "Right to petition for expungement or sealing if you meet your state's eligibility criteria",
            "Right to have automatically sealed records in many states for certain dispositions",
            "Once expunged, right to legally deny the arrest or conviction on most applications",
            "Right to restoration of rights (voting, firearms) in some cases",
            "Protection from employer discrimination based on sealed records in many states",
            "Right to a hearing on your expungement petition",
        ],
        action_steps=[
            "Check your state's eligibility requirements for your specific conviction type",
            "Obtain a copy of your complete criminal record (CORI, RAP sheet, etc.)",
            "Verify all conditions of your sentence are complete (fines paid, probation done)",
            "Wait for the required time period to pass",
            "File the petition with the court that handled your case",
            "Attend the hearing and be prepared to explain your rehabilitation",
            "After approval, verify the records are actually sealed/expunged",
        ],
        deadlines=[
            "Waiting period: Typically 1-10 years after completion of sentence depending on state and offense",
            "Filing fee: Usually $50-$450 depending on state",
            "Processing time: 2-6 months after filing in most states",
        ],
        common_mistakes=[
            "Not completing all sentence conditions before applying",
            "Forgetting to clear court fines, fees, or restitution",
            "Not checking if you have pending cases (disqualifies most petitions)",
            "Assuming federal records are also sealed (they are not)",
        ],
        when_to_get_a_lawyer=(
            "For felony expungements, complex cases, or if your first petition was denied. "
            "Many legal aid organizations help with expungement for free."
        ),
    ),

    # --- SMALL CLAIMS ---
    RightsGuide(
        id="small_claims_filing",
        domain="small_claims",
        title="Filing a Small Claims Case",
        description="How to sue in small claims court without a lawyer",
        explanation=(
            "Small claims court is designed for regular people to resolve disputes without attorneys. "
            "It's simpler, faster, and cheaper than regular court. Depending on your state, you can "
            "sue for $2,500 to $25,000. Common cases include unpaid debts, property damage, security "
            "deposits, breach of contract, and defective products."
        ),
        your_rights=[
            "Right to sue without an attorney in an informal setting",
            "Right to present your case and evidence directly to a judge",
            "Right to subpoena witnesses and documents",
            "Right to appeal an unfavorable decision (in most states)",
            "Right to collect the judgment through garnishment, liens, or levy",
        ],
        action_steps=[
            "Determine if your case is within the dollar limit for your state",
            "Send a demand letter to the other party first (required in some states)",
            "File the claim at the courthouse where the defendant lives or where the issue occurred",
            "Pay the filing fee ($30-$100 typically)",
            "Have the defendant properly served (court clerk can advise on methods)",
            "Prepare your evidence: contracts, photos, receipts, correspondence, witness list",
            "Present your case clearly and concisely at the hearing",
        ],
        deadlines=[
            "Statute of limitations: 2-6 years depending on claim type and state",
            "Demand letter: Send at least 14-30 days before filing",
            "Service of process: Defendant must be served before the hearing date",
        ],
        common_mistakes=[
            "Suing in the wrong court — file where defendant lives or where the event happened",
            "Not bringing organized evidence to the hearing",
            "Not sending a demand letter first (required in some states, always good practice)",
            "Not showing up — your case will be dismissed",
        ],
        when_to_get_a_lawyer=(
            "Generally not needed — that's the point of small claims court. Consider help if the "
            "case involves complex legal issues or if you're the defendant in a large claim."
        ),
    ),

    # --- CONTRACTS ---
    RightsGuide(
        id="contract_breach",
        domain="contract_disputes",
        title="Breach of Contract",
        description="What to do when someone breaks a contract with you",
        explanation=(
            "A breach of contract occurs when one party fails to perform their obligations under "
            "an agreement. Remedies typically include monetary damages, specific performance (forcing "
            "the other party to do what they promised), or contract rescission (cancellation). The "
            "strength of your case depends on having a clear agreement and documented breach."
        ),
        your_rights=[
            "Right to sue for actual damages caused by the breach",
            "Right to consequential damages if they were foreseeable at contract formation",
            "Right to specific performance for unique goods or property",
            "Right to rescind (cancel) the contract and be restored to your pre-contract position",
            "Right to liquidated damages if specified in the contract",
            "Duty to mitigate: you must take reasonable steps to minimize your losses",
        ],
        action_steps=[
            "Review the contract carefully — identify the specific term that was breached",
            "Document the breach: what was promised, what was delivered (or not), and when",
            "Notify the other party in writing that they are in breach",
            "Give them a reasonable opportunity to cure (fix) the breach if appropriate",
            "Send a formal demand letter with a deadline for resolution",
            "File in small claims court (if within limit) or hire an attorney for larger amounts",
        ],
        deadlines=[
            "Statute of limitations: 4-6 years for written contracts, 2-4 years for oral (varies by state)",
            "Notice of breach: Send promptly after discovering the breach",
            "Demand letter response: Give 14-30 days to respond",
        ],
        common_mistakes=[
            "Not keeping a copy of the signed contract",
            "Not documenting the breach as it happens",
            "Failing to mitigate damages (this can reduce your recovery)",
            "Continuing to perform under the contract after the other party breaches",
        ],
        when_to_get_a_lawyer=(
            "For contracts involving large amounts, complex terms, or business relationships. "
            "Small straightforward breaches can often be handled in small claims court."
        ),
    ),

    # --- IMMIGRATION ---
    RightsGuide(
        id="immigration_rights_overview",
        domain="immigration",
        title="Immigration Rights Overview",
        description="Know your rights regardless of immigration status",
        explanation=(
            "Everyone in the United States has constitutional rights regardless of immigration "
            "status. This includes the right to remain silent, the right to an attorney in criminal "
            "cases, protection from unreasonable searches, and due process. Understanding these "
            "rights is essential for protecting yourself and your family."
        ),
        your_rights=[
            "Right to remain silent — you do not have to answer questions about your immigration status",
            "Right to refuse consent to search of your person, car, or home",
            "Right to an attorney in criminal proceedings (not guaranteed in immigration court)",
            "Right to a hearing before an immigration judge before deportation (in most cases)",
            "Right to contact your consulate if detained",
            "Right to apply for asylum regardless of how you entered the country",
            "Right to not sign any documents you don't understand",
            "ICE cannot arrest you inside a courthouse in most jurisdictions",
        ],
        action_steps=[
            "Carry a know-your-rights card (available from ACLU and immigrant rights organizations)",
            "Memorize an emergency contact number for an immigration attorney",
            "Create a family safety plan in case of detention",
            "Keep copies of important documents in a safe place someone you trust can access",
            "Do not open the door for ICE without a judicial warrant (signed by a judge, not just ICE)",
            "If detained, state that you want to remain silent and want a lawyer",
            "Do not sign any documents without understanding them — request an interpreter",
        ],
        deadlines=[
            "Asylum application: Must apply within 1 year of arriving in the US (some exceptions)",
            "Voluntary departure: If granted, strict deadline to leave (failure bars future relief)",
            "Appeal of removal order: 30 days to file with the Board of Immigration Appeals",
        ],
        common_mistakes=[
            "Volunteering information about your status to police or ICE",
            "Signing voluntary departure forms without understanding the consequences",
            "Not attending immigration court hearings (results in removal order)",
            "Using fake documents (creates criminal issues on top of immigration issues)",
        ],
        when_to_get_a_lawyer=(
            "Always consult an immigration attorney before any interaction with USCIS or ICE. "
            "Many organizations provide free or low-cost immigration legal services."
        ),
    ),

    # --- DEBT ---
    RightsGuide(
        id="debt_bankruptcy_basics",
        domain="debt_collections",
        title="Bankruptcy Basics",
        description="Understanding when and how bankruptcy can help",
        explanation=(
            "Bankruptcy is a federal legal process that helps individuals eliminate or restructure "
            "overwhelming debt. Chapter 7 eliminates most unsecured debt in about 4 months. "
            "Chapter 13 creates a 3-5 year repayment plan. Bankruptcy immediately stops collections, "
            "lawsuits, garnishments, and foreclosure (the automatic stay)."
        ),
        your_rights=[
            "Right to file bankruptcy regardless of the amount of debt",
            "Automatic stay: immediately stops all collection activity upon filing",
            "Right to keep exempt property (home, car, retirement accounts in most cases)",
            "Right to reaffirm debts you want to keep paying (like a car loan)",
            "Protection from employer discrimination based on bankruptcy filing",
            "Right to rebuild credit after discharge",
        ],
        action_steps=[
            "Complete credit counseling from an approved agency (required before filing)",
            "Gather all financial documents: debts, income, assets, expenses",
            "Determine if Chapter 7 or Chapter 13 is right for your situation",
            "File the petition and required schedules with the bankruptcy court",
            "Attend the 341 meeting of creditors (usually a brief hearing)",
            "Complete a debtor education course (required before discharge)",
            "Receive your discharge and begin rebuilding credit",
        ],
        deadlines=[
            "Credit counseling: Must be completed within 180 days before filing",
            "Debtor education: Must be completed before discharge is granted",
            "341 meeting: Usually 20-40 days after filing",
            "Objection to discharge: Creditors have 60 days after 341 meeting",
            "Refiling: 8 years between Chapter 7 filings, 2 years for Chapter 13",
        ],
        common_mistakes=[
            "Paying back family or friends before filing (can be reversed as preferential transfers)",
            "Running up credit card debt right before filing (can be deemed fraudulent)",
            "Not disclosing all assets (can result in denial of discharge or criminal charges)",
            "Transferring property before filing to hide it from creditors",
        ],
        when_to_get_a_lawyer=(
            "Strongly recommended for bankruptcy. While Chapter 7 can technically be filed pro se, "
            "the process has many pitfalls. Many bankruptcy attorneys offer free consultations and "
            "affordable payment plans."
        ),
    ),
    RightsGuide(
        id="debt_garnishment",
        domain="debt_collections",
        title="Wage Garnishment Rights",
        description="Protecting your income from creditor garnishment",
        explanation=(
            "Wage garnishment is when a creditor takes money directly from your paycheck to pay a "
            "debt. In most cases, a creditor needs a court judgment before garnishing wages (exceptions: "
            "taxes, child support, student loans). Federal and state laws limit how much can be taken "
            "and protect certain income from garnishment entirely."
        ),
        your_rights=[
            "Federal law limits garnishment to 25% of disposable earnings or the amount above 30x minimum wage",
            "Many states have lower limits than the federal maximum",
            "Social Security, SSI, VA benefits, and retirement benefits are generally exempt",
            "Right to claim exemptions and challenge the garnishment in court",
            "Employer cannot fire you for a single garnishment under federal law",
            "Right to head-of-household exemption in some states (protects more of your income)",
            "Right to challenge the underlying judgment if you weren't properly served",
        ],
        action_steps=[
            "Review the garnishment order — verify the amount and that it's legally valid",
            "Check if the garnishment exceeds federal or state limits",
            "File a claim of exemption if protected income is being garnished",
            "Contact the creditor to negotiate a payment plan (may stop garnishment)",
            "Consider bankruptcy if garnishment creates severe financial hardship",
            "Respond to any court filings within the deadlines",
        ],
        deadlines=[
            "Exemption claim: Usually 10-30 days after receiving garnishment notice",
            "Challenge to judgment: Varies by state",
            "Bankruptcy filing: Can be done at any time to invoke automatic stay",
        ],
        common_mistakes=[
            "Ignoring garnishment notices — you lose the chance to claim exemptions",
            "Not realizing that exempt income (SSI, VA) can be protected",
            "Quitting your job to avoid garnishment (doesn't solve the underlying debt)",
            "Not checking if the garnishment exceeds legal limits",
        ],
        when_to_get_a_lawyer=(
            "If a significant portion of your income is being garnished, if exempt income is being "
            "taken, or if you're considering bankruptcy. Legal aid may help if you can't afford an attorney."
        ),
    ),
]


def get_all_guides() -> list[RightsGuide]:
    """Return all available rights guides.

    Returns:
        Complete list of RightsGuide objects.
    """
    return RIGHTS_GUIDES


def get_guides_by_domain(domain: str) -> list[RightsGuide]:
    """Return all guides for a specific legal domain.

    Args:
        domain: The legal domain to filter by.

    Returns:
        List of RightsGuide objects matching the domain.
    """
    return [g for g in RIGHTS_GUIDES if g.domain == domain]


def get_guide_by_id(guide_id: str) -> RightsGuide | None:
    """Return a specific guide by its ID.

    Args:
        guide_id: The unique guide identifier.

    Returns:
        The matching RightsGuide, or None if not found.
    """
    return next((g for g in RIGHTS_GUIDES if g.id == guide_id), None)


def get_domains() -> list[dict[str, object]]:
    """Return a summary of available domains with guide counts.

    Returns:
        List of dicts with domain name and guide count.
    """
    domain_counts: dict[str, int] = {}
    for guide in RIGHTS_GUIDES:
        domain_counts[guide.domain] = domain_counts.get(guide.domain, 0) + 1

    domain_labels: dict[str, str] = {
        "landlord_tenant": "Housing & Tenant Rights",
        "employment_rights": "Employment & Workplace",
        "consumer_protection": "Consumer Protection",
        "debt_collections": "Debt & Collections",
        "small_claims": "Small Claims Court",
        "contract_disputes": "Contracts & Agreements",
        "traffic_violations": "Traffic & Driving",
        "family_law": "Family Law",
        "criminal_records": "Criminal Records",
        "immigration": "Immigration",
    }

    return [
        {
            "domain": domain,
            "label": domain_labels.get(domain, domain.replace("_", " ").title()),
            "guide_count": count,
        }
        for domain, count in domain_counts.items()
    ]
