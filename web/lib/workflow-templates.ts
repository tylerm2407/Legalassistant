/**
 * Client-side workflow template definitions.
 *
 * These templates are embedded in the frontend so the workflows feature
 * works without a backend connection. Progress is persisted to localStorage.
 * Mirrors backend/workflows/templates/definitions.py.
 */

import type { WorkflowTemplate } from "./shared-types/workflows";

export const WORKFLOW_TEMPLATES: WorkflowTemplate[] = [
  {
    id: "fight_eviction",
    title: "Fight an Eviction",
    description: "Step-by-step guide to defending against an eviction",
    domain: "landlord_tenant",
    estimated_time: "2-6 weeks",
    steps: [
      {
        id: "review_notice",
        title: "Review the Eviction Notice",
        explanation:
          "Carefully read the eviction notice. Identify what type it is (nonpayment, lease violation, no-cause, or illegal activity). Note the deadline to respond and whether you have the right to 'cure' (fix the problem). Check that the notice meets your state's legal requirements for format, delivery method, and notice period.",
        required_documents: ["Eviction notice", "Your lease agreement"],
        tips: [
          "Many eviction notices have technical errors that can be used as a defense",
          "Check if the notice was properly served (method varies by state)",
          "Note the exact date you received the notice — deadlines start from this date",
        ],
        deadlines: [
          "Note the response deadline on the notice (typically 3-30 days)",
        ],
        status: "not_started",
      },
      {
        id: "check_validity",
        title: "Check Notice Validity",
        explanation:
          "Verify that the eviction notice complies with your state's requirements. Common defects include: wrong notice period, improper service method, incorrect address, wrong amount owed, or failure to include required legal language. An invalid notice can be grounds for dismissal.",
        required_documents: [
          "Eviction notice",
          "State landlord-tenant statute",
        ],
        tips: [
          "Look up your state's specific notice requirements",
          "If the notice amount is wrong, this can invalidate it",
          "Check if your landlord used the correct service method",
        ],
        deadlines: [
          "Do this immediately — before your response deadline",
        ],
        status: "not_started",
      },
      {
        id: "gather_evidence",
        title: "Gather Your Evidence",
        explanation:
          "Collect everything that supports your defense: rent payment receipts, bank statements showing payments, photos of property conditions, maintenance request records, communication with landlord (texts, emails), and any witness information. Organize chronologically.",
        required_documents: [
          "Rent payment receipts or bank statements",
          "Photos/videos of property conditions",
          "Written communication with landlord",
          "Maintenance request records",
          "Lease agreement",
        ],
        tips: [
          "Screenshot text messages and save them as files",
          "Organize documents by date",
          "Make copies of everything — never give away your only copy",
        ],
        deadlines: ["Complete before filing your answer"],
        status: "not_started",
      },
      {
        id: "file_answer",
        title: "File Your Answer with the Court",
        explanation:
          "File a written answer with the court before the deadline. Your answer should deny allegations that aren't true and list your defenses. Common defenses include: improper notice, retaliatory eviction, discrimination, breach of habitability, payment already made, or waiver by acceptance of rent.",
        required_documents: [
          "Court answer form",
          "Filing fee or fee waiver application",
        ],
        tips: [
          "Many courts have self-help centers that can help you fill out forms",
          "If you can't afford the filing fee, ask for a fee waiver",
          "Keep a copy of your filed answer with the court stamp",
        ],
        deadlines: [
          "File before the deadline on your summons — missing this usually means losing",
        ],
        status: "not_started",
      },
      {
        id: "request_hearing",
        title: "Request a Hearing",
        explanation:
          "If a hearing isn't automatically scheduled after you file your answer, request one from the court clerk. Some jurisdictions also offer mediation as an alternative — this can sometimes result in a better outcome than trial.",
        required_documents: ["Filed answer with court stamp"],
        tips: [
          "Ask about mediation — it may lead to an agreement that avoids eviction",
          "Confirm the hearing date and location",
          "Request any accommodations you need (interpreter, accessibility)",
        ],
        deadlines: [
          "Hearing is typically set within 1-4 weeks of filing answer",
        ],
        status: "not_started",
      },
      {
        id: "prepare_case",
        title: "Prepare Your Case",
        explanation:
          "Organize your evidence and prepare your testimony. Practice explaining your case clearly and concisely. If you have witnesses, confirm they can attend. Review your state's landlord-tenant laws relevant to your defenses.",
        required_documents: [
          "All evidence organized chronologically",
          "Three copies of each document (you, judge, opposing party)",
          "List of witnesses with contact information",
        ],
        tips: [
          "Practice your presentation — you'll usually have limited time",
          "Focus on facts, not emotions",
          "Dress professionally for court",
          "Arrive early to find the courtroom",
        ],
        deadlines: ["Complete preparation before hearing date"],
        status: "not_started",
      },
      {
        id: "attend_hearing",
        title: "Attend the Hearing",
        explanation:
          "Attend your hearing on time. Be respectful and address the judge as 'Your Honor.' Present your case clearly: state your defenses, show your evidence, and call any witnesses. Listen carefully to the landlord's arguments and be prepared to respond.",
        required_documents: ["All prepared evidence and copies"],
        tips: [
          "Arrive 30 minutes early",
          "Turn off your phone",
          "Stand when speaking to the judge",
          "If you lose, ask about the appeal process and timeline immediately",
        ],
        deadlines: [
          "Attend on the scheduled date — missing means default judgment against you",
        ],
        status: "not_started",
      },
    ],
  },
  {
    id: "file_small_claims",
    title: "File a Small Claims Case",
    description: "How to file and win in small claims court",
    domain: "small_claims",
    estimated_time: "4-8 weeks",
    steps: [
      {
        id: "determine_eligibility",
        title: "Determine Eligibility",
        explanation:
          "Check that your case qualifies for small claims court. Verify: the amount is within your state's limit ($2,500-$25,000 depending on state), you're suing in the right county (where defendant lives or where the issue happened), and the statute of limitations hasn't expired.",
        required_documents: [
          "Evidence of the amount owed",
          "Defendant's address",
        ],
        tips: [
          "Look up your state's specific dollar limit",
          "You can reduce your claim to fit within the limit (you waive the excess)",
          "Some states don't allow attorneys in small claims — this is an advantage",
        ],
        deadlines: [
          "Check the statute of limitations for your type of claim",
        ],
        status: "not_started",
      },
      {
        id: "send_demand",
        title: "Send a Demand Letter",
        explanation:
          "Before filing, send a formal demand letter to the other party via certified mail. This is required in some states and always good practice. State what's owed, why, and give a deadline (14-30 days) to pay before you file suit.",
        required_documents: ["Demand letter", "Certified mail receipt"],
        tips: [
          "Keep the letter professional and factual",
          "Include specific amounts and dates",
          "The certified mail receipt proves they received it",
          "Many cases settle after receiving a demand letter",
        ],
        deadlines: ["Allow 14-30 days for response before filing"],
        status: "not_started",
      },
      {
        id: "file_claim",
        title: "File the Claim",
        explanation:
          "Go to the courthouse (or file online if available) and complete the small claims filing form. Pay the filing fee. You'll receive a case number and hearing date. The court will issue papers to be served on the defendant.",
        required_documents: [
          "Completed claim form",
          "Filing fee",
          "Demand letter copy",
        ],
        tips: [
          "Filing fees are typically $30-$100 — you can recover this if you win",
          "Many courts now allow online filing",
          "Ask the clerk if you need help with the forms",
        ],
        deadlines: ["File before the statute of limitations expires"],
        status: "not_started",
      },
      {
        id: "serve_defendant",
        title: "Serve the Defendant",
        explanation:
          "The defendant must be officially notified of the lawsuit. Service methods vary by state: personal service, certified mail, or process server. The defendant must be served before the hearing date.",
        required_documents: [
          "Court papers to serve",
          "Proof of service form",
        ],
        tips: [
          "Ask the court clerk about available service methods",
          "You cannot serve the papers yourself in most states",
          "Keep the proof of service — you'll need it at the hearing",
        ],
        deadlines: [
          "Service must be completed before the hearing date (usually 10-20 days before)",
        ],
        status: "not_started",
      },
      {
        id: "present_case",
        title: "Present Your Case at Hearing",
        explanation:
          "Attend the hearing with all your evidence organized. Present your case clearly: what happened, what's owed, and your evidence. Show the demand letter and proof it was sent. Be prepared for the defendant's arguments.",
        required_documents: [
          "All evidence with copies for judge and defendant",
          "Demand letter and certified mail receipt",
          "Any contracts or written agreements",
          "Photos, receipts, or other proof of damages",
        ],
        tips: [
          "Practice your presentation — keep it to 5-10 minutes",
          "Lead with the strongest evidence",
          "Bring a calculator if math is involved",
          "Be respectful to the judge and the defendant",
        ],
        deadlines: ["Attend on the scheduled date"],
        status: "not_started",
      },
    ],
  },
  {
    id: "expunge_record",
    title: "Get a Record Expunged",
    description:
      "Step-by-step process to seal or expunge your criminal record",
    domain: "criminal_records",
    estimated_time: "2-6 months",
    steps: [
      {
        id: "check_eligibility",
        title: "Check Eligibility",
        explanation:
          "Research your state's expungement/sealing laws to determine if you're eligible. Factors include: type of offense, time since completion of sentence, whether you have subsequent offenses, and whether all fines and restitution are paid.",
        required_documents: ["Your criminal record (CORI/RAP sheet)"],
        tips: [
          "Many states have online eligibility calculators",
          "Some offenses are never eligible (typically violent felonies, sex offenses)",
          "Some states now offer automatic expungement for certain offenses",
          "Legal aid organizations often provide free eligibility screening",
        ],
        deadlines: [
          "Waiting periods: typically 1-10 years after sentence completion",
        ],
        status: "not_started",
      },
      {
        id: "obtain_records",
        title: "Obtain Your Records",
        explanation:
          "Get a complete copy of your criminal record from the state police, court records, or your state's criminal records bureau. You need the exact case numbers, charges, and dispositions for your petition.",
        required_documents: [
          "Government ID",
          "Fingerprints (if required)",
          "Records request fee",
        ],
        tips: [
          "Request records from BOTH state and court systems",
          "Verify all information is accurate — errors should be corrected first",
          "Keep copies for your records",
        ],
        deadlines: ["Processing time: usually 1-4 weeks"],
        status: "not_started",
      },
      {
        id: "fill_petition",
        title: "Complete the Petition",
        explanation:
          "Fill out the expungement petition form for your court. Include all required information: case numbers, charges, dispositions, evidence of rehabilitation, and reasons for seeking expungement. Many courts have self-help resources.",
        required_documents: [
          "Expungement petition form",
          "Criminal record copy",
          "Proof of sentence completion",
          "Character references (if helpful)",
        ],
        tips: [
          "Court self-help centers can assist with forms",
          "Include evidence of rehabilitation: employment, education, community service",
          "Have someone proofread your petition",
        ],
        deadlines: ["No specific deadline, but don't delay once eligible"],
        status: "not_started",
      },
      {
        id: "file_petition",
        title: "File the Petition",
        explanation:
          "File the completed petition with the court that handled your original case. Pay the filing fee (or request a fee waiver if you qualify). Some states require you to serve the District Attorney.",
        required_documents: [
          "Completed petition",
          "Filing fee or fee waiver",
          "Copies for service",
        ],
        tips: [
          "Filing fees range from $50-$450 depending on state",
          "Ask about fee waivers — many courts offer them based on income",
          "Get a file-stamped copy for your records",
        ],
        deadlines: [
          "DA must usually be served within a specific period after filing",
        ],
        status: "not_started",
      },
      {
        id: "attend_hearing",
        title: "Attend the Hearing",
        explanation:
          "Attend the expungement hearing. Be prepared to explain your rehabilitation and why expungement is warranted. The DA may or may not object. The judge will consider the nature of the offense, time elapsed, and your conduct since the conviction.",
        required_documents: [
          "Filed petition copy",
          "Evidence of rehabilitation",
        ],
        tips: [
          "Dress professionally",
          "Be prepared to answer questions about your rehabilitation",
          "Bring character witnesses if possible",
          "Not all states require a hearing — some are decided on papers",
        ],
        deadlines: ["Attend on the scheduled date"],
        status: "not_started",
      },
      {
        id: "verify_sealing",
        title: "Verify Records Are Sealed",
        explanation:
          "After the court grants expungement, verify that the records have actually been sealed or destroyed. Check with the court, state police, and any online databases. It can take several weeks for records to be updated across all systems.",
        required_documents: ["Court order granting expungement"],
        tips: [
          "Do a background check on yourself after 60 days to verify",
          "Send copies of the court order to agencies that may have your records",
          "Federal records are NOT affected by state expungement",
          "Keep the court order permanently — you may need to show it",
        ],
        deadlines: [
          "Allow 30-90 days for records to be updated across systems",
        ],
        status: "not_started",
      },
    ],
  },
  {
    id: "file_wage_complaint",
    title: "File a Wage Complaint",
    description: "How to recover unpaid wages from your employer",
    domain: "employment_rights",
    estimated_time: "2-6 months",
    steps: [
      {
        id: "document_wages",
        title: "Document Hours and Pay",
        explanation:
          "Gather all evidence of hours worked and pay received. Compare your actual hours to what you were paid. Calculate the exact amount owed, including any overtime, minimum wage violations, or unauthorized deductions.",
        required_documents: [
          "Pay stubs",
          "Time records (even personal notes count)",
          "Employment contract or offer letter",
          "Bank statements showing deposits",
        ],
        tips: [
          "Keep your own daily log of hours — it's admissible evidence even without employer records",
          "Calculate overtime at 1.5x your regular rate for hours over 40/week",
          "Check your state's minimum wage — it may be higher than federal",
        ],
        deadlines: [
          "FLSA claims: 2-year limit (3 years for willful violations)",
        ],
        status: "not_started",
      },
      {
        id: "file_complaint",
        title: "File with State Labor Board",
        explanation:
          "File a wage complaint with your state's Department of Labor or wage board. You can also file with the federal DOL Wage and Hour Division. Include all documentation and a clear calculation of what you're owed.",
        required_documents: [
          "Completed wage complaint form",
          "Supporting documentation",
          "Calculation of wages owed",
        ],
        tips: [
          "You can file both state and federal complaints",
          "Filing is usually free",
          "You can file online in most states",
          "Keep copies of everything you submit",
        ],
        deadlines: [
          "State filing deadlines vary — typically 2-6 years from the violation",
        ],
        status: "not_started",
      },
      {
        id: "follow_up",
        title: "Follow Up on Investigation",
        explanation:
          "After filing, the labor board will investigate. They may contact your employer and request records. Stay responsive to any requests from the investigator. The process typically takes 2-6 months.",
        required_documents: [
          "Case number and investigator contact info",
        ],
        tips: [
          "Respond promptly to any investigator requests",
          "Provide additional evidence as you find it",
          "Keep a log of all communication about the case",
        ],
        deadlines: [
          "Respond to investigator requests within the timeframes given",
        ],
        status: "not_started",
      },
      {
        id: "escalate",
        title: "Escalate if Needed",
        explanation:
          "If the labor board doesn't resolve your case, or if the amount is significant, consider filing in small claims court or hiring an employment attorney. Many employment attorneys work on contingency for wage theft cases.",
        required_documents: [
          "Labor board determination",
          "All original documentation",
        ],
        tips: [
          "Employment attorneys often work on contingency for wage cases",
          "You may be entitled to double or triple damages",
          "Class actions are possible if other employees are affected",
          "Small claims court is an option for smaller amounts",
        ],
        deadlines: [
          "Don't let the statute of limitations expire while waiting for the labor board",
        ],
        status: "not_started",
      },
    ],
  },
  {
    id: "fight_traffic_ticket",
    title: "Fight a Traffic Ticket",
    description: "How to contest a traffic citation in court",
    domain: "traffic_violations",
    estimated_time: "2-6 weeks",
    steps: [
      {
        id: "review_options",
        title: "Review Your Options",
        explanation:
          "Before deciding to fight, understand your options: pay the fine (accept guilt and points), attend traffic school (may avoid points), or fight in court (plead not guilty). Consider the points impact on your license and insurance.",
        required_documents: ["Traffic citation", "Your driving record"],
        tips: [
          "Check if you're eligible for traffic school — this avoids points",
          "Calculate how points would affect your insurance",
          "Consider the cost of fighting vs. paying",
        ],
        deadlines: [
          "Response deadline on the ticket (usually 15-30 days)",
        ],
        status: "not_started",
      },
      {
        id: "prepare_defense",
        title: "Prepare Your Defense",
        explanation:
          "Build your defense by gathering evidence. Request the officer's notes, radar calibration records, and any dashcam footage through discovery. Visit the location and take photos showing speed limit signs, visibility, road conditions.",
        required_documents: [
          "Discovery request form",
          "Photos of the location",
          "Witness information",
        ],
        tips: [
          "Request radar/lidar calibration and maintenance records",
          "Take photos at the same time of day as the alleged violation",
          "Note any obstructed signs or unusual conditions",
        ],
        deadlines: [
          "Discovery requests should be made promptly after pleading not guilty",
        ],
        status: "not_started",
      },
      {
        id: "request_hearing",
        title: "Request a Hearing",
        explanation:
          "Plead not guilty and request a hearing. This can usually be done online, by mail, or in person. You may be able to request a trial by written declaration in some states (no court appearance needed).",
        required_documents: ["Not guilty plea form"],
        tips: [
          "Some states allow trial by written declaration — you don't have to appear",
          "Requesting a hearing sometimes gets assigned to a different officer (who may not show)",
          "Ask for a court date as far out as possible — increases chance officer won't appear",
        ],
        deadlines: [
          "Plea must be entered before the deadline on the ticket",
        ],
        status: "not_started",
      },
      {
        id: "present_case",
        title: "Present Your Case",
        explanation:
          "Attend the hearing and present your defense. If the officer doesn't appear, request dismissal. Present your evidence clearly. Common defenses: equipment not calibrated, speed necessary for safety, incorrect identification of vehicle.",
        required_documents: [
          "All evidence and copies",
          "Calibration records (if obtained)",
        ],
        tips: [
          "Dress professionally",
          "If the officer doesn't show, immediately request dismissal",
          "Be concise and stick to facts",
          "If found guilty, ask about traffic school",
        ],
        deadlines: ["Attend on the scheduled date"],
        status: "not_started",
      },
    ],
  },
  {
    id: "create_basic_will",
    title: "Create a Basic Will",
    description:
      "Step-by-step guide to creating a simple last will and testament",
    domain: "family_law",
    estimated_time: "1-2 weeks",
    steps: [
      {
        id: "inventory_assets",
        title: "Inventory Your Assets",
        explanation:
          "Make a comprehensive list of everything you own: real estate, bank accounts, retirement accounts, investments, vehicles, valuable personal property, digital assets, and life insurance policies. Note current values and any debts secured by these assets.",
        required_documents: [
          "Asset list with approximate values",
          "Debt list",
          "Account information",
        ],
        tips: [
          "Don't forget digital assets: crypto, online accounts, domain names",
          "Note which assets have designated beneficiaries already (retirement, life insurance)",
          "Include sentimental items with specific designations",
        ],
        deadlines: [
          "No deadline, but don't delay — unexpected events happen",
        ],
        status: "not_started",
      },
      {
        id: "choose_beneficiaries",
        title: "Designate Beneficiaries",
        explanation:
          "Decide who will receive your assets. You can leave specific items to specific people (specific bequests) or divide the remainder (residuary estate) among beneficiaries by percentage. Name alternate beneficiaries in case your primary choices predecease you.",
        required_documents: [
          "Beneficiary list with full legal names and relationships",
        ],
        tips: [
          "Always name alternate beneficiaries",
          "Be specific about items and percentages",
          "Consider charitable bequests",
          "Don't forget to update beneficiary designations on retirement accounts and insurance",
        ],
        deadlines: ["N/A"],
        status: "not_started",
      },
      {
        id: "choose_executor",
        title: "Choose an Executor",
        explanation:
          "Select a trusted person to carry out your will (executor/personal representative). This person will manage your estate, pay debts, and distribute assets. Choose someone organized, trustworthy, and willing. Name an alternate executor.",
        required_documents: [
          "Executor's full legal name and contact information",
        ],
        tips: [
          "Ask the person before naming them — it's a significant responsibility",
          "Choose someone in the same state if possible",
          "Consider naming a professional (attorney, bank) for complex estates",
          "If you have minor children, also name a guardian",
        ],
        deadlines: ["N/A"],
        status: "not_started",
      },
      {
        id: "draft_will",
        title: "Draft the Will",
        explanation:
          "Create the will document. You can use a reputable online service, a template from your state court, or hire an estate planning attorney. The will must clearly state it's your will, name beneficiaries and bequests, appoint an executor, and include required legal language for your state.",
        required_documents: [
          "Asset inventory",
          "Beneficiary list",
          "Executor information",
        ],
        tips: [
          "Use your state's specific requirements — they vary",
          "Include a residuary clause (catches anything not specifically mentioned)",
          "Consider including a no-contest clause",
          "Have an attorney review even if you draft it yourself (for complex situations)",
        ],
        deadlines: ["N/A"],
        status: "not_started",
      },
      {
        id: "execute_will",
        title: "Execute (Sign) the Will",
        explanation:
          "Sign the will in the presence of witnesses as required by your state. Most states require two witnesses who are not beneficiaries. Some states recognize self-proving affidavits (notarized) which simplify probate later. Store the original in a safe, accessible place.",
        required_documents: [
          "Drafted will",
          "Two witnesses",
          "Notary (recommended)",
        ],
        tips: [
          "Witnesses should NOT be beneficiaries in the will",
          "Get a self-proving affidavit notarized if your state allows it",
          "Store the original in a fireproof safe or with your attorney",
          "Tell your executor where the will is stored",
          "Review and update your will every 3-5 years or after major life events",
        ],
        deadlines: [
          "Review and update after major life events: marriage, divorce, birth, death, major asset changes",
        ],
        status: "not_started",
      },
    ],
  },
];
