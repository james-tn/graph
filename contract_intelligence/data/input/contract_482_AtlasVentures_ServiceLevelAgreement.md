# SERVICE LEVEL AGREEMENT  
**Contract Reference No.: SLA-ATL-202411-482**

---

## SERVICE LEVEL AGREEMENT  
between  
**Contoso Enterprises** and **Atlas Ventures**  
(supplementing Master Services Agreement Ref: MSA-ATL-202411-375 / contract_375)

---

This SERVICE LEVEL AGREEMENT (this **“SLA”** or this **“Agreement”**) is made and entered into as of **August 28, 2025** (the **“Effective Date”**), by and between:

- **Contoso Enterprises**, a [●] corporation, with its principal place of business at **1234 Innovation Parkway, Suite 500, Dallas, Texas 75201** (**“Contoso”**, the **“Client”** or the **“Company”**), and  

- **Atlas Ventures**, a [●] limited liability company, with its principal place of business at **9876 Venture Plaza, 12th Floor, Austin, Texas 78701** (**“Atlas”**, the **“Vendor”** or the **“Service Provider”**).

Contoso and Atlas may be referred to herein individually as a **“Party”** and collectively as the **“Parties.”**

This SLA bears **Contract Reference No. SLA-ATL-202411-482** and is expressly entered into **pursuant to and as a supplement to** the Master Services Agreement dated **November 18, 2024**, by and between the same Parties, designated as **Contract Reference No. MSA-ATL-202411-375** and internally identified by Client as **“contract_375”** (the **“Master Agreement”** or **“Parent Agreement”**).

---

## RECITALS

WHEREAS, the Parties entered into the **Master Services Agreement (Contract Reference No. MSA-ATL-202411-375, contract_375)** as of November 18, 2024 (the **“Master Agreement”**) for the provision by Vendor of technology consulting, implementation, integration, managed services, project management, and related professional services as more particularly described in **Article II (Scope of Services / Work)** of the Master Agreement;

WHEREAS, **Section 1.1.17 (definition of “Service Levels”)** and **Article XII (Service Level Agreements)** of the Master Agreement contemplate the establishment of detailed service level commitments, including uptime commitments, response and resolution times, and related service quality standards to be set forth in service level schedules or statements of work supplementing the Master Agreement;

WHEREAS, the Parties now desire to enter into this SLA (Ref: **SLA-ATL-202411-482**) to define and document specific service levels, performance metrics, escalation paths, and related commercial terms for certain **Managed Services** and related **Support Services** (each as defined in **Section 2.2 of the Master Agreement**) that Vendor will provide to Client under the overall contractual framework established by the Master Agreement;

WHEREAS, this SLA is intended to apply in conjunction with, and not in substitution of, the general terms and conditions of the Master Agreement, including without limitation the provisions regarding **Fees and Payment Terms (Article III)**, **Term and Termination (Article IV)**, **Confidentiality (Article V)**, **Intellectual Property Rights (Article VI)**, **Data Protection and Privacy (Article XI)**, and **Service Level Agreements (Article XII)** of the Master Agreement, except to the limited extent expressly modified herein;

NOW, THEREFORE, in consideration of the mutual covenants and agreements contained herein, and intending to be legally bound, the Parties hereby agree as follows:

---

## ARTICLE I. DEFINITIONS

1.1 **Defined Terms.** Capitalized terms used but not otherwise defined in this SLA shall have the meanings ascribed to them in the Master Agreement **MSA-ATL-202411-375 (contract_375)**. In addition, for purposes of this SLA, the following terms shall have the meanings set forth below. Defined terms may be used in the singular or plural, as the context requires.

1.1.1 **“Parent Agreement” or “Master Agreement”** means the **Master Services Agreement (Contract Reference No. MSA-ATL-202411-375, contract_375)** dated November 18, 2024, between Client and Vendor, including all exhibits, schedules, and Statements of Work, as amended from time to time in accordance with Article XVI thereof.

1.1.2 **“Applicable Services”** means the Managed Services, Support Services, monitoring, incident management, performance tuning, and related services that Vendor is obligated to perform for Client under this SLA and any applicable Statement of Work (“SOW”) executed under the Master Agreement and expressly referencing this SLA.

1.1.3 **“Business Day”** has the meaning given in **Section 1.1.3 of the Master Agreement**, namely any day other than a Saturday, Sunday, or a day on which banks in the State of Texas are authorized or required by law to remain closed.

1.1.4 **“Contract Value (SLA)”** means the aggregate estimated contract value for the Applicable Services under this SLA, which the Parties acknowledge and agree is **One Million Six Hundred Ninety-Three Thousand Three Hundred Fifty-Two U.S. Dollars (US$1,693,352)**. For clarity, this amount is part of, and not in addition to, the broader contract value contemplated by the Master Agreement unless the Parties expressly agree otherwise in writing.

1.1.5 **“Covered Systems”** means those production and non-production environments, applications, interfaces, databases, and infrastructure components for which Vendor provides the Applicable Services and to which the Service Levels set forth in this SLA apply, as further specified in the applicable SOW(s).

1.1.6 **“Downtime”** means the total accumulated minutes during which the production instances of the Covered Systems are not available to Client, excluding any **Permitted Downtime** (as defined in **Section 12.1 of the Master Agreement** and further refined in this SLA).

1.1.7 **“Incident”** means any event that is not part of the standard operation of a Covered System and that causes, or may cause, an interruption to, or a reduction in the quality of, the Applicable Services.

1.1.8 **“Major Release”** means a release of software or configuration for a Covered System that introduces significant new functionality, architectural changes, or other substantial modifications, as reasonably determined by Vendor and agreed by Client.

1.1.9 **“Minor Release”** means a release of software or configuration for a Covered System that provides bug fixes, patches, performance improvements, or minor enhancements that do not significantly alter core functionality.

1.1.10 **“Permitted Downtime”** has the meaning set forth in **Section 12.1 of the Master Agreement**, and includes: (a) scheduled maintenance with at least seventy-two (72) hours’ prior notice; (b) emergency maintenance required to address critical security or availability issues; and (c) unavailability caused by Client systems, third-party providers, or Force Majeure Events, as further specified in **Article XV** of the Master Agreement and this SLA.

1.1.11 **“Response Time”** means the time period between Vendor’s receipt of an Incident report (through the agreed support channel) and Vendor’s initial meaningful response as described in **Article XII** of this SLA, measured during the applicable support hours.

1.1.12 **“Resolution Time”** means the time period between Vendor’s receipt of an Incident report and Vendor’s provision of a fix or commercially reasonable workaround that mitigates the materially adverse effect of the Incident, as further defined in Article XII.

1.1.13 **“Service Credits”** means the monetary credits, expressed as a percentage of the monthly Fees for the Applicable Services, to which Client may become entitled if Vendor fails to achieve specified Service Levels, as set forth in **Section 12.6** of this SLA.

1.1.14 **“Service Hours”** means the hours during which Vendor provides support for Incidents, which, unless otherwise specified in an SOW, shall be twenty-four (24) hours per day, seven (7) days per week (“24x7”) for Priority 1 Incidents, and Business Days during normal business hours (8:00 a.m. to 6:00 p.m. Central Time) for all other Incidents.

1.1.15 **“Service Levels”** has the meaning in **Section 1.1.17 of the Master Agreement** and, for purposes of this SLA, includes the specific performance metrics, uptime commitments, Response Times, Resolution Times, and related quality standards defined in Article XII of the Master Agreement, as supplemented and detailed in this SLA.

1.1.16 **“Service Request”** means a non-Incident request initiated by Client for information, access, or execution of a standard operational task that does not arise from a failure of a Covered System (e.g., user creation, configuration changes, non-urgent report modifications).

1.1.17 **“SLA Term”** means the period commencing on the Effective Date and ending on the **Expiration Date of December 31, 2029**, unless earlier terminated in accordance with Article IV of this SLA or the Master Agreement.

1.1.18 **“Uptime Percentage”** means the percentage of total minutes in a calendar month during which the production instances of Covered Systems are available, calculated as:  
Uptime % = (Total Minutes in Month − Downtime Minutes) ÷ (Total Minutes in Month) × 100.

1.1.19 **“Force Majeure Event”** has the meaning given in **Article XV of the Master Agreement**, and includes, among other things, acts of God, natural disasters, pandemics, acts of war or terrorism, governmental actions, strikes, or widespread Internet disruptions beyond a Party’s reasonable control.

---

## ARTICLE II. SCOPE OF SERVICES / WORK

2.1 **Relationship to Master Agreement.**  

2.1.1 This SLA is executed **under and subject to** the terms of the Master Agreement, including, without limitation, **Article II (Scope of Services / Work)** and **Article XII (Service Level Agreements)** thereof.  

2.1.2 In accordance with **Section 2.1 of the Master Agreement**, this SLA sets forth specific Service Levels, performance standards, and operational procedures that apply to the Applicable Services provided by Vendor. For clarity, the general performance standards in **Section 2.4 (Performance Standards)** of the Master Agreement continue to apply and are **supplemented (not replaced)** by this SLA.

2.2 **Description of Applicable Services.**  
Vendor shall provide the following categories of Applicable Services to Client, which are within and elaborative of the **Managed Services and Support Services** referenced in **Sections 2.2.3 and 2.2.2** of the Master Agreement:

2.2.1 **Managed Application Services.**  
Vendor shall provide ongoing management and operation of the Covered Systems, which may include enterprise software applications, middleware, and integrations as described in the applicable SOW(s). Activities include:

  a. **Monitoring & Alerting:** Continuous monitoring (24x7) of system availability, application health, and key performance indicators through Vendor’s monitoring tools; configuration of alerts and thresholds.

  b. **Incident Management:** Logging, classification, prioritization, investigation, and resolution of Incidents in accordance with the priority levels and Response/Resolution Times set forth in **Article XII** of this SLA.

  c. **Problem Management:** Root cause analysis of recurring or critical Incidents, preventive measures, documentation of known errors, and implementation of permanent fixes where commercially reasonable.

  d. **Performance & Capacity Management:** Regular review of system performance, tuning of configurations and resources, and capacity planning to support Client’s anticipated business volumes.

2.2.2 **Infrastructure and Environment Management.**  
To the extent specified in an SOW, Vendor shall manage the infrastructure layers supporting the Covered Systems, including cloud resources, virtual machines, storage, and network configurations. This includes:

  a. Provisioning and deprovisioning of environments;

  b. Implementation of security hardening measures as agreed;

  c. Coordination with cloud or hosting providers when third-party platforms are used; and

  d. Applying system patches and updates in accordance with the patching schedule agreed by the Parties.

2.2.3 **Maintenance, Patching, and Releases.**  
Vendor shall manage Major and Minor Releases and routine maintenance activities, including:

  a. **Minor Releases and Patches:** Regular deployment of Minor Releases and security patches, subject to Client’s approval where required. Vendor shall schedule such deployments during agreed maintenance windows to minimize business impact.

  b. **Major Releases:** Coordination, planning, testing, and deployment of Major Releases, including regression testing, rollback planning, and communication to Client stakeholders.

  c. **Scheduled Maintenance:** Performance of scheduled maintenance during agreed maintenance windows, with at least seventy-two (72) hours’ prior written notice, consistent with **Section 12.1 of the Master Agreement**.

2.2.4 **Service Desk and User Support.**  
Vendor shall provide a centralized Service Desk as a single point of contact for Incidents and Service Requests related to the Covered Systems, including:

  a. Multiple intake channels (e.g., email, ticketing system, and optional phone line as agreed in SOW);

  b. Ticket logging, categorization, prioritization, and tracking until closure;

  c. Communication of status updates to Client’s designated contacts at frequencies appropriate to the Incident’s priority level; and

  d. Handling of user support issues such as access issues, configuration questions, and training-related queries within agreed Service Levels.

2.2.5 **Reporting and Governance.**  
In addition to the project management and reporting obligations under **Section 2.5 of the Master Agreement**, Vendor shall:

  a. Provide monthly Service Level performance reports, including Uptime Percentage, Incident volumes by priority, average Response/Resolution Times, and Service Credits (if any);

  b. Participate in monthly or quarterly service review meetings (as agreed in the relevant SOW) to review SLA performance, capacity planning, risk and issue logs, and continuous improvement initiatives; and

  c. Maintain documentation such as runbooks, standard operating procedures, and architectural diagrams relevant to the Applicable Services.

2.3 **Service Commencement and Transition.**  
2.3.1 The Applicable Services under this SLA shall commence on the Effective Date, or such later date as specified in the applicable SOW(s), following completion of any agreed transition or onboarding activities.  

2.3.2 Vendor shall, if applicable, perform transition services from any incumbent service provider to Vendor, in coordination with Client, consistent with the transition assistance principles described in **Section 4.6(c) of the Master Agreement**.

2.4 **Service Locations.**  
Vendor may perform the Applicable Services from its own facilities, from remote locations, or from other locations agreed by the Parties, provided that Vendor remains responsible for compliance with this SLA and the Master Agreement, including **Confidentiality (Article V)** and **Data Protection and Privacy (Article XI)** of the Master Agreement.

2.5 **Client Responsibilities.**  
Without limiting **Section 2.6 of the Master Agreement**, Client shall:

  a. Provide timely access to relevant Client systems, environments, and personnel as required for Vendor to perform the Applicable Services;

  b. Maintain its own internal networks, devices, and connectivity to Vendor’s service endpoints;

  c. Perform any responsibilities expressly assigned to Client in the applicable SOW(s), including user acceptance testing of Major Releases and approvals of maintenance windows; and

  d. Provide accurate and complete information in Incident reports and Service Requests to facilitate efficient troubleshooting and resolution.

2.6 **Service Exclusions.**  
Unless expressly included in an SOW, the Applicable Services do not include:

  a. Development of new custom software or major functional enhancements (these may be provided under separate SOWs under the Master Agreement);

  b. On-site support at Client facilities (unless expressly agreed and subject to additional Fees); or

  c. Support for third-party systems or components not identified as Covered Systems.

Any such additional services may be requested and documented through the change management process in **Article XIII** of this SLA and **Article XIII of the Master Agreement**.

---

## ARTICLE III. FEES AND PAYMENT TERMS

3.1 **Fees and Contract Value.**  

3.1.1 The Parties acknowledge that the aggregate estimated **Contract Value (SLA)** for the Applicable Services under this SLA is **US$1,693,352**, which may consist of a combination of fixed monthly managed services Fees, variable usage-based Fees, and one-time transition or setup Fees, as detailed in the applicable SOW(s).  

3.1.2 This Contract Value is an estimate only and shall not be construed as a guaranteed minimum spend, consistent with **Section 3.1 of the Master Agreement** and the “No Minimum Purchase” principle in **Section 2.9 of the Master Agreement**.

3.2 **Fee Structure.**  
Unless otherwise specified in the applicable SOW(s):

  a. **Recurring Managed Services Fees:** Vendor shall charge a fixed monthly fee for the Applicable Services, based on the number of Covered Systems, environments, and agreed service hours.

  b. **Variable Fees:** Additional Fees may apply for out-of-scope activities, such as emergency onsite support, major environment changes, or custom reporting, to be agreed in advance through a Change Order under **Section 13.3 of the Master Agreement**.

  c. **Transition/Onboarding Fees:** One-time Fees may be charged for initial transition, knowledge transfer, and setup activities, as specified in the applicable SOW.

3.3 **Payment Terms.**  

3.3.1 The Parties agree that, notwithstanding **Section 3.3 of the Master Agreement (Net 45)**, the specific payment term for all undisputed Fees under this SLA shall be **Net 60 (sixty) days** from Client’s receipt of a correct and undisputed invoice. This constitutes a permitted modification of Section 3.3 solely with respect to the Applicable Services governed by this SLA.  

3.3.2 Invoices shall be issued monthly in arrears (unless otherwise stated in an SOW), detailing recurring Fees, variable Fees (with reasonable supporting detail), and reimbursable expenses (if any).

3.4 **Disputed Amounts; Late Payments.**  
3.4.1 The invoice dispute process set forth in **Section 3.4 of the Master Agreement** shall apply. Client shall notify Vendor of any disputed amounts within fifteen (15) days of receipt and timely pay the undisputed portion.  

3.4.2 Any undisputed amount not paid by the due date shall accrue interest in accordance with **Section 3.5 of the Master Agreement**, which shall apply unchanged to this SLA.

3.5 **Expenses and Reimbursement.**  
Client shall reimburse Vendor for reasonable, documented, pre-approved out-of-pocket expenses incurred in connection with the Applicable Services, in accordance with **Section 3.7 of the Master Agreement**, including travel, lodging, meals, and other ancillary costs, to the extent such expenses are expressly authorized by Client in writing or in the applicable SOW.

3.6 **Taxes.**  
The provisions of **Section 3.8 (Taxes)** and **Section 3.9 (No Withholding)** of the Master Agreement apply mutatis mutandis to this SLA.

---

## ARTICLE IV. TERM AND TERMINATION

4.1 **SLA Term.**  
This SLA shall commence on the **Effective Date (August 28, 2025)** and shall continue in full force and effect until **December 31, 2029** (the **“SLA Expiration Date”**), unless earlier terminated in accordance with this Article IV or the Master Agreement.

4.2 **Relationship to Master Agreement Term.**  
4.2.1 The SLA Term is intended to operate within the overall **Term** of the Master Agreement set forth in **Section 4.1 thereof (through October 17, 2029)**.  

4.2.2 If the Master Agreement is not renewed beyond October 17, 2029, this SLA shall automatically **terminate on the earlier of** (a) the SLA Expiration Date or (b) the effective date of termination or expiration of the Master Agreement, unless the Parties expressly agree in writing to extend the SLA under a successor master agreement.

4.3 **Termination for Convenience.**  

4.3.1 Notwithstanding the client-friendly termination rights in **Section 4.3 of the Master Agreement**, the Parties agree that, due to the high-risk and high-investment nature of the Applicable Services:

  a. **Client** may terminate this SLA, in whole or in part, for convenience only upon **one hundred eighty (180) days’ prior written notice** to Vendor; and  

  b. Vendor may not terminate this SLA for convenience except upon mutual written agreement of the Parties.

4.3.2 The foregoing constitutes a specific modification of Section 4.3 of the Master Agreement solely with respect to this SLA and the Applicable Services defined herein.

4.4 **Termination for Cause.**  
Termination for cause shall be governed by **Section 4.4 of the Master Agreement**, provided that:

  a. Persistent or material failure by Vendor to meet Service Levels, as defined in **Article XII of the Master Agreement and this SLA**, shall constitute a material breach if such failure is not cured within the applicable **Cure Period** specified in **Section 4.4.1 of the Master Agreement**; and  

  b. Either Party may terminate this SLA upon the events of insolvency, bankruptcy, or analogous events described in **Section 4.4.2 of the Master Agreement**, with respect to the other Party.

4.5 **Effect of Termination of Master Agreement.**  
4.5.1 If the Master Agreement is terminated or expires for any reason, this SLA and all Applicable Services shall automatically terminate on the same effective date, unless the Parties expressly agree otherwise in writing.  

4.5.2 Termination of this SLA shall not, by itself, terminate the Master Agreement or any other SOW, except as may be expressly stated in the applicable termination notice, consistent with **Section 4.5 of the Master Agreement**.

4.6 **Effect of Termination of this SLA.**  
Upon expiration or termination of this SLA for any reason:

  a. Vendor shall cease performing the Applicable Services, except as reasonably necessary to wind down activities and provide any agreed transition assistance;  

  b. Client shall pay Vendor for all Applicable Services properly performed and any accepted Deliverables through the effective date of termination, together with any non-cancellable, pre-approved expenses incurred, consistent with **Section 4.6(b) of the Master Agreement**;  

  c. Vendor shall provide transition assistance to Client or a replacement provider on the terms and at the rates set forth in **Section 4.6(c) of the Master Agreement**, provided that if termination is due to Client’s convenience or Client’s uncured material breach, such assistance shall be provided at Vendor’s then-standard rates; and  

  d. Each Party shall return or destroy the other Party’s Confidential Information in accordance with **Section 5.5 of the Master Agreement**.

4.7 **Survival.**  
The rights and obligations of the Parties under those provisions of this SLA which by their nature should survive (including Articles V, VII, VIII, IX, XI, XIV, XV, and XVI) shall survive any expiration or termination of this SLA, in addition to those provisions of the Master Agreement that survive under **Section 4.7 thereof**.

---

## ARTICLE V. CONFIDENTIALITY

5.1 **Relationship to Master Agreement Confidentiality.**  
The confidentiality obligations set out in **Article V (Confidentiality)** of the Master Agreement are hereby incorporated by reference and shall apply fully to all Confidential Information exchanged in connection with this SLA and the Applicable Services.

5.2 **Additional Confidential Information.**  
For purposes of this SLA, Confidential Information (as defined in **Section 5.1 of the Master Agreement**) explicitly includes:

  a. All system diagrams, runbooks, configuration details, and monitoring dashboards related to the Covered Systems;  

  b. Performance metrics, service reports, and SLA-related data that reveal the architecture, security posture, or usage patterns of the Covered Systems; and  

  c. All incident logs and root cause analysis documentation.

5.3 **Use and Disclosure.**  
The Receiving Party shall:

  a. Use the Disclosing Party’s Confidential Information solely for the purpose of performing its obligations or exercising its rights under the Master Agreement and this SLA; and  

  b. Maintain confidentiality and restrict disclosure in accordance with **Section 5.3 of the Master Agreement**.

5.4 **Exceptions; Compelled Disclosure.**  
The exclusions from Confidential Information and the procedures for compelled disclosure set forth in **Sections 5.2 and 5.4 of the Master Agreement** apply mutatis mutandis to this SLA.

5.5 **Survival Period.**  
Notwithstanding **Section 5.7 of the Master Agreement (five (5) years)**, the Parties agree that the confidentiality obligations with respect to Confidential Information disclosed in connection with this SLA shall survive for **five (5) years** after expiration or termination of this SLA, provided that trade secrets and Personal Data shall be protected for so long as they remain protected under applicable law.

---

## ARTICLE VI. INTELLECTUAL PROPERTY RIGHTS

6.1 **Relationship to Master Agreement IP Provisions.**  
The Parties acknowledge and agree that the Intellectual Property Rights provisions set forth in **Article VI of the Master Agreement** (including Sections 6.1 through 6.7) apply to all Deliverables, Vendor Background IP, Third-Party Materials, and Client Materials relating to the Applicable Services under this SLA.

6.2 **Operational Deliverables and Documentation.**  
To the extent Vendor creates deliverables specifically related to the Applicable Services—such as runbooks, standard operating procedures, configuration documentation, and monitoring templates—such materials shall be treated as **“Deliverables”** under the Master Agreement and subject to **Sections 6.2 and 6.3 thereof**, including:

  a. Client’s ownership of Deliverables specifically created for Client (work made for hire or assigned) once Fees are paid; and  

  b. Vendor’s retention of rights in Vendor Background IP incorporated in such Deliverables, with the license to Client described in **Section 6.3 of the Master Agreement**.

6.3 **Use Restrictions.**  
Client shall not use any Vendor Background IP or tools provided as part of the Applicable Services other than as necessary to receive and use the Applicable Services and Deliverables for its internal business purposes, consistent with **Sections 6.3, 6.5, and 6.6 of the Master Agreement**. Vendor shall have no obligation to deliver source code or proprietary toolsets used internally to provide the Applicable Services.

6.4 **Third-Party and Open-Source Components.**  
To the extent the Applicable Services rely on or incorporate Third-Party Materials or open-source software, **Sections 6.4 and 6.7 of the Master Agreement** apply, including Vendor’s obligations to disclose open-source components and the applicable licenses.

---

## ARTICLE VII. REPRESENTATIONS AND WARRANTIES

7.1 **Incorporation of Master Agreement Warranties.**  
The mutual representations and warranties in **Section 7.1 of the Master Agreement** and the Vendor and Client warranties in **Sections 7.2 and 7.3** thereof are incorporated herein by reference and apply fully to the Applicable Services.

7.2 **Additional Vendor SLA Warranties.**  
Vendor additionally represents and warrants that:

  a. It shall use commercially reasonable efforts to maintain the Uptime Percentage and meet the Service Levels set forth in Article XII of the Master Agreement and this SLA;  

  b. It shall maintain appropriate staffing, tools, and processes to provide 24x7 support for Priority 1 Incidents in accordance with this SLA; and  

  c. It will maintain the insurance coverages required under **Article X of the Master Agreement** and this SLA.

7.3 **Remedies.**  
The remedies for breach of warranties set forth in **Section 7.4 of the Master Agreement** apply to this SLA, provided that Service Credits constitute an additional commercial remedy as described in **Section 12.6** of this SLA.

7.4 **Disclaimer.**  
The disclaimer in **Section 7.5 of the Master Agreement** applies equally to the Applicable Services under this SLA.

---

## ARTICLE VIII. INDEMNIFICATION

8.1 **Incorporation of Master Agreement Indemnity.**  
The indemnification obligations set forth in **Article VIII (Indemnification)** of the Master Agreement are incorporated by reference and apply to any Claims arising from or relating to the Applicable Services and this SLA.

8.2 **Additional Client Indemnification (High Risk).**  
In addition to Client’s obligations under **Section 8.2 of the Master Agreement**, Client shall defend, indemnify, and hold harmless the Vendor Indemnitees from and against any and all Claims arising out of or relating to:

  a. Client’s misuse or unauthorized use of the Covered Systems or Applicable Services in violation of this SLA or the Master Agreement;  

  b. Any configuration directives, customizations, or integrations expressly specified by Client that Vendor implements at Client’s direction, to the extent such directives cause or contribute to system failures, data loss, or third-party claims; and  

  c. Any regulatory fines or penalties arising from Client’s failure to comply with Data Protection Laws (as defined in **Section 1.1.7 of the Master Agreement**) in areas where Client is the “controller” or “business” and Vendor acts solely as a “processor” or “service provider” in accordance with Client’s documented instructions.

8.3 **Indemnification Procedures.**  
The procedures in **Section 8.3 of the Master Agreement** (including prompt notice, control of defense, and cooperation) govern any indemnification claims under this SLA.

---

## ARTICLE IX. LIMITATION OF LIABILITY

9.1 **Modification of Master Agreement Liability Limits (High Risk – Uncapped).**  

9.1.1 The Parties expressly agree that, with respect to any liability arising out of or relating to this SLA and the Applicable Services, **the liability cap in Section 9.2 of the Master Agreement shall not apply**. Instead, **neither Party’s aggregate liability shall be contractually capped**, and each Party may be held liable up to the full extent of damages proven under applicable law, subject to the exclusions and qualifications set forth below.

9.2 **Inclusion of Consequential and Other Damages (High Risk).**  
9.2.1 Notwithstanding **Section 9.1 of the Master Agreement**, for claims arising out of or relating to this SLA and the Applicable Services, the Parties agree that **neither Party shall be excluded from liability for indirect, incidental, consequential, special, exemplary, or punitive damages, or loss of profits, revenue, data, or business opportunity**, to the extent such damages are:  

  a. A reasonably foreseeable result of the breach at the time of contracting; and  

  b. Not otherwise excluded by mandatory provisions of applicable law.

9.2.2 Without limiting the foregoing, Vendor acknowledges that a failure to meet critical Service Levels may lead to significant business disruption and lost revenue for Client, and Client acknowledges that its misuse of the Applicable Services or breach of Data Protection obligations may cause substantial harm to Vendor.

9.3 **No Limitation for Certain Categories.**  
The exceptions listed in **Section 9.2 of the Master Agreement** (indemnification obligations, breaches of confidentiality, Client’s payment obligations, gross negligence or willful misconduct) remain fully applicable, and for avoidance of doubt, **these categories likewise remain uncapped** under this SLA.

9.4 **Applicability of Law.**  
Nothing in this Article IX shall limit or exclude any liability that cannot be limited or excluded under applicable law. The Parties acknowledge that the risk allocation in this Article is more favorable to Vendor than in the Master Agreement and reflects the high-risk nature of the Applicable Services and the **Contract Value (SLA)**.

---

## ARTICLE X. INSURANCE

10.1 **Insurance Requirements.**  
Vendor shall maintain, at its own expense, the insurance coverage required under **Article X of the Master Agreement**, and, given the criticality of the Applicable Services, Vendor shall use commercially reasonable efforts to obtain the following minimum limits (which shall supersede any lower limits in Section 10.1 of the Master Agreement solely for this SLA):

  a. **Commercial General Liability:** not less than US$2,000,000 per occurrence and US$4,000,000 in the aggregate;  

  b. **Professional Liability / Errors and Omissions:** not less than US$5,000,000 per claim and in the aggregate;  

  c. **Cyber Liability / Data Breach Insurance:** not less than US$5,000,000 per claim and in the aggregate; and  

  d. Workers’ Compensation and Employer’s Liability as required by applicable law, with employer’s liability limits of not less than US$1,000,000 per accident.

10.2 **Certificates of Insurance.**  
Upon Client’s request, Vendor shall provide updated certificates of insurance evidencing the coverages and shall notify Client in writing of any cancellation or material reduction in coverage, consistent with **Section 10.2 of the Master Agreement**.

10.3 **No Limitation.**  
Vendor’s insurance shall not limit its obligations or liability under this SLA or the Master Agreement, except to the extent expressly required by applicable law.

---

## ARTICLE XI. DATA PROTECTION AND PRIVACY

11.1 **Incorporation of Master Agreement Data Protection Terms.**  
All provisions of **Article XI (Data Protection and Privacy)** of the Master Agreement apply fully to any Personal Data processed in connection with the Applicable Services under this SLA.

11.2 **Processor / Service Provider Role.**  
Vendor acknowledges that, for purposes of the Applicable Services, Client is the “controller” or “business” and Vendor is the “processor” or “service provider” as those terms are used in GDPR and CCPA, and Vendor shall act strictly in accordance with Client’s documented instructions, as described in **Section 11.2 of the Master Agreement**.

11.3 **Security Measures.**  
Vendor shall maintain technical and organizational security measures at least equivalent to those described in **Section 11.3 of the Master Agreement**, and, given the high risk nature of the Applicable Services, Vendor shall additionally:

  a. Implement multi-factor authentication for administrative access to Covered Systems where commercially reasonable;  

  b. Conduct at least annual penetration testing of externally facing components supporting the Covered Systems and remediate critical findings within commercially reasonable timelines; and  

  c. Encrypt Personal Data at rest where reasonably practicable.

11.4 **Data Breach Notification.**  
The Data Breach notification obligations in **Section 11.5 of the Master Agreement** (notification within seventy-two (72) hours, cooperation in investigation and remediation) apply fully to this SLA.

11.5 **Data Retention and Deletion.**  
Upon expiration or termination of this SLA or at Client’s written direction, Vendor shall return or securely delete Personal Data related to the Applicable Services in accordance with **Section 11.8 of the Master Agreement**, subject to any legal retention requirements.

---

## ARTICLE XII. SERVICE LEVEL AGREEMENTS

12.1 **Uptime Commitment.**  
Consistent with **Section 12.1 of the Master Agreement**, Vendor shall use commercially reasonable efforts to ensure that the production instances of the Covered Systems are available at least **99.9%** of the time in each calendar month, measured as the **Uptime Percentage** and excluding **Permitted Downtime**.

12.2 **Priority Levels and Response / Resolution Times.**  
Unless otherwise specified in an SOW, Vendor shall adhere to the following Service Levels, expanding and refining **Section 12.2 of the Master Agreement**:

- **Priority 1 (Critical):** Complete loss of service or severe impact on Client’s critical operations without a viable workaround.  
  - Service Hours: 24x7  
  - Initial Response Time: within **30 minutes**  
  - Target Resolution Time: within **4 hours** or provision of a commercially reasonable workaround that restores critical functionality.

- **Priority 2 (High):** Significant degradation of service with substantial impact on operations, but operations can continue in a reduced capacity or with a workaround.  
  - Service Hours: Business Days (8:00 a.m. – 6:00 p.m. CT)  
  - Initial Response Time: within **2 hours**  
  - Target Resolution Time: within **1 Business Day** or provision of a workaround.

- **Priority 3 (Medium):** Moderate impact issues; non-critical functionality impaired; business impact is limited.  
  - Service Hours: Business Days  
  - Initial Response Time: within **1 Business Day**  
  - Target Resolution Time: within **3 Business Days** or scheduling for inclusion in next Minor Release.

- **Priority 4 (Low):** Minor issues; cosmetic defects; Service Requests; general inquiries.  
  - Service Hours: Business Days  
  - Initial Response Time: within **2 Business Days**  
  - Target Resolution Time: in a future planned release or as mutually agreed.

12.3 **Service Requests.**  
Service Requests shall be processed in accordance with agreed workflows and timelines defined in the applicable SOW. Unless otherwise agreed, standard Service Requests shall be treated as Priority 4 items.

12.4 **Measurement and Reporting.**  
Vendor shall measure Service Levels using its standard monitoring tools and log data in accordance with **Section 12.5 of the Master Agreement** and shall provide monthly SLA performance reports to Client.

12.5 **Service Credits.**  
If Vendor fails to meet the Uptime Commitment, Client shall be entitled to Service Credits as set forth in **Section 12.3 of the Master Agreement**, subject to the following clarifications:

  a. Service Credits shall be calculated as a percentage of the monthly Fees for the affected Covered Systems;  

  b. Client must request Service Credits in writing within thirty (30) days after Vendor’s issuance of the applicable monthly report; and  

  c. Credits shall be applied against subsequent invoices and are not refundable in cash unless no further invoices are expected, in which case the Parties shall settle by payment.

12.6 **Exclusive SLA Monetary Remedy.**  
Service Credits remain Client’s **sole and exclusive monetary remedy** for failure to meet the Service Levels, consistent with **Section 12.6 of the Master Agreement**, but this does **not preclude** Client from seeking other non-monetary remedies (such as specific performance or termination for persistent failure) in accordance with **Section 4.4 of the Master Agreement** and Article XIV of this SLA. For avoidance of doubt, the uncapped liability and inclusion of consequential damages agreed in **Article IX of this SLA** still apply to the extent permitted by law.

---

## ARTICLE XIII. CHANGE MANAGEMENT

13.1 **Incorporation of Master Agreement Change Management.**  
The change management procedures in **Article XIII (Change Management)** of the Master Agreement, including **Sections 13.1 through 13.5**, apply fully to changes in the Applicable Services, Service Levels, or Covered Systems.

13.2 **SLA-Specific Changes.**  
Any modifications to the Service Levels, Uptime Commitment, or Fee structure under this SLA shall be documented in a written **Change Order** referencing both the Master Agreement **MSA-ATL-202411-375 (contract_375)** and this SLA **SLA-ATL-202411-482**, signed by authorized representatives of both Parties.

13.3 **Emergency Changes.**  
Vendor may implement emergency changes necessary to preserve the security or stability of the Covered Systems, consistent with **Section 13.5 of the Master Agreement**, and shall provide prompt notice and documentation to Client, followed by any necessary Change Order.

---

## ARTICLE XIV. DISPUTE RESOLUTION

14.1 **Incorporation of Master Agreement Process.**  
The dispute resolution process in **Article XIV (Dispute Resolution)** of the Master Agreement, including negotiation, escalation, and mediation as prerequisites to litigation, shall apply to any disputes arising under or relating to this SLA.

14.2 **Venue and Governing Law.**  
Consistent with **Section 14.3 of the Master Agreement**, any legal action or proceeding arising out of or relating to this SLA shall be brought exclusively in the state or federal courts located in **Dallas County, Texas**, and this SLA shall be governed by and construed in accordance with the laws of the **State of Texas**, without regard to its conflict of laws principles.

14.3 **Interim Relief; Attorneys’ Fees.**  
The provisions regarding interim relief and attorneys’ fees in **Sections 14.4 and 14.5 of the Master Agreement** apply mutatis mutandis to this SLA.

---

## ARTICLE XV. FORCE MAJEURE

15.1 **Force Majeure Events.**  
The definition of **Force Majeure Event** in **Article XV of the Master Agreement** applies to this SLA. A Force Majeure Event may excuse delay or failure to perform the Applicable Services, including inability to meet Service Levels, to the extent caused by such event and not reasonably mitigable.

15.2 **Notice and Mitigation.**  
The affected Party shall provide notice and use commercially reasonable efforts to mitigate and resume performance as described in **Sections 15.2 and 15.3 of the Master Agreement**.

15.3 **Service Levels During Force Majeure.**  
Downtime or service degradation directly attributable to a Force Majeure Event shall be treated as **Permitted Downtime** and excluded from the Uptime Percentage calculation, provided the affected Party complies with its obligations to notify and mitigate under this Article.

---

## ARTICLE XVI. GENERAL PROVISIONS

16.1 **Reference to Master/Parent Agreement.**  
This Service Level Agreement (Contract Reference No. **SLA-ATL-202411-482**) is executed **under and subject to** the terms of the **Master Services Agreement reference number MSA-ATL-202411-375 (contract_375)**. Except as expressly modified herein, all terms and conditions of the Master Agreement remain in full force and effect and are hereby ratified and confirmed.

16.2 **Order of Precedence.**  
In the event of any conflict or inconsistency between the terms of this SLA and the Master Agreement:

  a. The terms of the Master Agreement shall control, except to the extent this SLA explicitly states that it modifies or supersedes a specific provision of the Master Agreement (e.g., payment terms in **Section 3.3** and termination notice period in **Section 4.3**); and  

  b. With respect to Service Levels and operational procedures, this SLA shall be deemed to provide **additional, more specific terms** within the framework of the Master Agreement.

16.3 **Entire Agreement.**  
This SLA, together with the Master Agreement and any SOWs expressly referencing both, constitutes the entire agreement between the Parties with respect to the subject matter hereof and supersedes all prior or contemporaneous oral or written agreements, proposals, and communications relating to such subject matter.

16.4 **Amendments.**  
This SLA may be amended only by a written instrument expressly stating an intent to amend this SLA and referencing **SLA-ATL-202411-482** and **MSA-ATL-202411-375 (contract_375)**, signed by authorized representatives of both Parties, consistent with **Article XVI of the Master Agreement**.

16.5 **Severability.**  
If any provision of this SLA is held invalid or unenforceable, the remaining provisions shall remain in full force and effect, and the Parties shall negotiate in good faith a valid, enforceable substitute provision that most nearly reflects the original intent.

16.6 **Waiver.**  
No waiver of any breach or default under this SLA shall be effective unless in writing and signed by the waiving Party. No waiver of any breach or default shall be deemed a waiver of any subsequent breach or default.

16.7 **Notices.**  
All notices under this SLA shall be given in accordance with the notice provisions in **Article XVI of the Master Agreement**, and addressed as follows (unless updated pursuant to the Master Agreement):

- **To Client (Contoso Enterprises):**  
  Contoso Enterprises  
  1234 Innovation Parkway, Suite 500  
  Dallas, Texas 75201  
  Attn: Legal Department / CIO  

- **To Vendor (Atlas Ventures):**  
  Atlas Ventures  
  9876 Venture Plaza, 12th Floor  
  Austin, Texas 78701  
  Attn: Legal Department / Account Executive  

16.8 **Assignment.**  
Neither Party may assign or transfer this SLA, in whole or in part, except as permitted under the assignment provisions of the Master Agreement (**Section 16.8 or equivalent**). Any attempted assignment in violation thereof shall be null and void.

16.9 **Independent Contractors.**  
The Parties remain independent contractors as described in the Master Agreement. Nothing in this SLA shall be construed to create a partnership, joint venture, or agency relationship between the Parties.

16.10 **Counterparts; Electronic Signatures.**  
This SLA may be executed in counterparts (including by electronic or digital signatures and PDF), each of which shall be deemed an original and all of which together shall constitute one and the same instrument, consistent with the execution provisions of the Master Agreement.

16.11 **Headings.**  
Section headings are for convenience only and shall not affect the interpretation of this SLA.

---

## SIGNATURES

IN WITNESS WHEREOF, the Parties have caused this Service Level Agreement **SLA-ATL-202411-482** to be executed by their duly authorized representatives as of the Effective Date first written above.

**Executed pursuant to MSA-ATL-202411-375 (contract_375).**

---

### CONTOSO ENTERPRISES  
(the “Client” or “Company”)

By: _________________________________  
Name: _______________________________  
Title: ________________________________  
Date: ________________________________

Witness (if applicable): __________________  
Name: ________________________________  
Title: _________________________________  
Date: _________________________________

---

### ATLAS VENTURES  
(the “Vendor” or “Service Provider”)

By: _________________________________  
Name: _______________________________  
Title: ________________________________  
Date: ________________________________

Witness (if applicable): __________________  
Name: ________________________________  
Title: _________________________________  
Date: _________________________________

---  

**[End of Service Level Agreement – Contract Ref. SLA-ATL-202411-482]**