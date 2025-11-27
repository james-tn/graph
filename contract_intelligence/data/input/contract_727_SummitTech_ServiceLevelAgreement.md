# SERVICE LEVEL AGREEMENT  
**Contract Reference Number: SLA-SUM-202508-727**

---

## PREAMBLE

This SERVICE LEVEL AGREEMENT (this “**SLA**” or this “**Agreement**”), Contract Reference Number **SLA-SUM-202508-727**, is entered into as of **May 18, 2026** (the “**SLA Effective Date**”), by and between:

- **Contoso Enterprises, Inc.**, a Delaware corporation, with its principal place of business at 4100 Contoso Parkway, Wilmington, DE 19801, USA (“**Contoso**,” the “**Client**” or the “**Company**”), and  

- **Summit Tech Solutions, LLC**, a Delaware limited liability company, with its principal place of business at 920 Summit Avenue, Suite 1400, Newark, DE 19711, USA (“**Summit Tech**,” the “**Vendor**” or the “**Service Provider**”).

Contoso and Summit Tech are sometimes referred to herein individually as a “**Party**” and collectively as the “**Parties**.”

This SLA is **entered into pursuant to and supplements** that certain **Master Services Agreement**, reference number **MSA-SUM-202508-578** (internal identifier: **contract_578**), dated **August 15, 2025** (the “**Master Services Agreement**” or the “**Parent Agreement**”), by and between the same Parties.  

This SLA is intended to constitute a “Service Level Agreement” as that term is used and defined in **Section 1.16** and **Article XII (Service Level Agreements)** of the Master Services Agreement.

---

## RECITALS

WHEREAS, the Parties entered into the Master Services Agreement, Ref. **MSA-SUM-202508-578** (file identifier **contract_578**), effective as of August 15, 2025, pursuant to which Summit Tech agreed to provide information technology, software development, systems integration, maintenance, support, and related professional services to Contoso, as more fully described in **Article II (Scope of Services/Work)** of the Master Services Agreement;

WHEREAS, under **Section 1.16** and **Article XII (Service Level Agreements)** of the Master Services Agreement, the Parties contemplated that certain performance metrics, uptime commitments, response times, and related remedies would be memorialized in one or more Service Level Agreements and/or Statements of Work that reference the Master Services Agreement;

WHEREAS, the Master Services Agreement designated the overall engagement as **“High Risk”** in **Section 2.7**, and the Parties, in light of such high-risk nature, agreed to certain risk allocations that favor the Service Provider, including but not limited to the uncapped liability regime set forth in **Article IX (Limitation of Liability)** and the indemnification provisions in **Article VIII (Indemnification)** of the Master Services Agreement;

WHEREAS, the Parties desire by this SLA to define and document specific service levels, support obligations, performance standards, fees, and remedies applicable to certain managed services, hosting, and support Services (as defined below) to be performed by Summit Tech for Contoso during the period from May 18, 2026 through December 23, 2027;

WHEREAS, the Parties acknowledge that the **contract value** associated with the committed scope of Services under this SLA is **Nine Hundred Thirteen Thousand Nine Hundred Sixty-Two U.S. Dollars (US $913,962)**, which is part of, and incremental to, the total contract value recognized under **Section 3.1** of the Master Services Agreement and may be adjusted only in accordance with the change management provisions of **Article XIII (Change Management)** of the Master Services Agreement and this SLA;

NOW, THEREFORE, in consideration of the mutual promises and covenants contained in this SLA and in the Master Services Agreement, and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the Parties hereby agree as follows:

---

## ARTICLE I  
## DEFINITIONS

1.1 **Incorporation of Master Services Agreement Definitions.** Capitalized terms used but not otherwise defined in this SLA shall have the meanings ascribed to them in **Article I (Definitions)** of the Master Services Agreement (Ref. MSA-SUM-202508-578, contract_578), which is hereby incorporated by reference. Without limiting the foregoing, terms such as “Affiliate,” “Applicable Law,” “Business Day,” “Client Data,” “Confidential Information,” “Deliverables,” “Fees,” “Force Majeure Event,” “Personal Data,” “Services,” “Statement of Work,” and “Third-Party Products” shall have the same meanings as in the Master Services Agreement.

1.2 **“Parent Agreement” or “Master Agreement”** means the **Master Services Agreement** between the Parties, reference number **MSA-SUM-202508-578** (internal identifier **contract_578**), dated August 15, 2025, including all exhibits, schedules, and Statements of Work executed thereunder, as amended, supplemented, or modified from time to time in accordance with its terms.

1.3 **“SLA Effective Date”** has the meaning set forth in the Preamble and indicates the date on which this SLA becomes effective between the Parties.

1.4 **“SLA Term”** means the period from the SLA Effective Date through the SLA Expiration Date (each as defined herein), unless earlier terminated in accordance with **Article IV** of this SLA and **Article IV (Term and Termination)** of the Master Services Agreement.

1.5 **“SLA Expiration Date”** means **December 23, 2027**, unless extended by mutual written agreement of the Parties pursuant to Section 4.2 of this SLA.

1.6 **“Managed Services”** means the ongoing, recurring services performed by the Service Provider for the operation, monitoring, maintenance, and support of production systems, applications, and related infrastructure for the Company, as further described in **Article II** of this SLA and in any applicable Statement of Work referencing this SLA.

1.7 **“Supported Systems”** means those production applications, environments, databases, middleware components, and infrastructure elements that are expressly identified in an applicable Statement of Work or schedule to this SLA as being within the scope of the Managed Services and subject to the Service Levels defined herein.

1.8 **“Service Levels”** means the performance metrics, uptime commitments, response times, resolution targets, and other quantitative or qualitative performance standards set forth in **Article XII** of this SLA, as may be further detailed in an applicable Statement of Work.

1.9 **“Service Credit”** means the credit against future Fees payable by the Company to the Service Provider as the exclusive monetary remedy for specific Service Level failures, as set forth in **Section 12.5** below and consistent with **Section 12.4** of the Master Services Agreement.

1.10 **“Incident”** means any unplanned interruption to, or reduction in the quality of, a Supported System or Service, including a failure to meet the defined Service Levels. Incidents are categorized by Priority levels as set forth in **Section 12.3** of this SLA.

1.11 **“Change Request”** and **“Change Order”** have the meanings assigned in **Article XIII (Change Management)** of the Master Services Agreement and are further applied in **Article XIII** of this SLA with respect to changes to Service Levels, Supported Systems, or scope of Services.

1.12 **“SLA Fee Component”** means the portion of the Fees under this SLA specifically attributable to the ongoing Managed Services and support obligations, as opposed to any one-time project or implementation fees. The SLA Fee Component is used for calculation of Service Credits.

1.13 **“High Risk Engagement”** refers to the characterization of the engagement under the Master Services Agreement as “High Risk” pursuant to **Section 2.7** thereof and is reflected in the uncapped liability and risk allocation set forth in **Articles VIII and IX** of the Master Services Agreement and mirrored in this SLA.

1.14 **“Root Cause Analysis” or “RCA”** means a written analysis conducted by the Service Provider following certain material Incidents or repeated failures of Service Levels, which identifies the underlying cause(s) of the Incident and sets forth proposed corrective and preventive measures.

1.15 **“Maintenance Window”** or **“Scheduled Maintenance”** means pre-planned periods during which the Service Provider may suspend or degrade parts of the Services or Supported Systems in order to perform maintenance, upgrades, patches, or other changes, as defined in **Section 12.2** of the Master Services Agreement and further detailed in **Section 12.2** of this SLA.

1.16 **“Emergency Maintenance”** means any maintenance that is, in the Service Provider’s reasonable judgment, necessary to address an imminent or actual material security vulnerability, severe performance degradation, or other condition that, if not addressed promptly, could lead to a Priority 1 Incident or material harm to the Company’s systems or business operations.

1.17 **“Contract Value (SLA)”** means the total committed value of this SLA of **US $913,962**, which is acknowledged by the Parties as a subset of and in addition to the contract value referenced in **Section 3.1** of the Master Services Agreement.

1.18 **“Net 60 Payment Terms”** means the Company shall pay all undisputed invoices within sixty (60) calendar days from the invoice date, as provided in **Section 3.3** of this SLA, which supplements but does not modify the general payment terms set forth in **Section 3.3** of the Master Services Agreement except as expressly stated herein with respect to this SLA.

---

## ARTICLE II  
## SCOPE OF SERVICES / WORK

2.1 **Relationship to Master Services Agreement.**  

2.1.1 This SLA supplements and is entered into under **Article II (Scope of Services/Work)** and **Article XII (Service Level Agreements)** of the Master Services Agreement. The Services defined herein constitute “Services” within the meaning of **Section 1.17** of the Master Services Agreement.

2.1.2 In the event of any direct conflict between the terms of this SLA and the Master Services Agreement, the Master Services Agreement shall control, except where this SLA expressly states that it is intended to supersede a specific provision of the Master Services Agreement with respect to the Services covered hereunder and references the relevant section of the Master Services Agreement. For the avoidance of doubt, this SLA **supplements and further specifies** the baseline Service Levels described in **Article XII** of the Master Services Agreement.

2.2 **Overview of Services.**  

During the SLA Term, the Service Provider shall provide the following categories of Services to the Company, in accordance with this Article II and subject to the Service Levels in **Article XII**:

(a) **Production Application Hosting and Operations.** The Service Provider shall host and operate certain mission-critical enterprise applications of the Company, including but not limited to:  
   - Customer relationship management (CRM) platform;  
   - Order management system (OMS);  
   - Data integration middleware; and  
   - Supporting databases and application servers,  
   in a production environment described in the applicable Statement of Work. The Service Provider shall be responsible for monitoring, incident management, and routine operational tasks necessary to maintain availability and performance in accordance with the Service Levels.

(b) **Application and Infrastructure Monitoring.** The Service Provider shall implement and maintain monitoring of the Supported Systems, including system health, capacity, performance, and security event monitoring, using industry-standard tools. Monitoring thresholds, alerting rules, and notification procedures shall be documented and agreed in writing and shall align with the Intended levels of uptime (at least **99.9% monthly availability** as further detailed in **Article XII**).

(c) **Incident Management and Support Services.** Consistent with **Section 2.3.4 (Maintenance, Support, and Managed Services)** of the Master Services Agreement, the Service Provider shall provide incident management and technical support for the Supported Systems, including a 24x7 contact channel for Priority 1 and Priority 2 Incidents and Business Day support for Priority 3 and Priority 4 Incidents. Response and resolution targets are specified in **Section 12.3** of this SLA.

(d) **Preventive Maintenance, Patching, and Upgrades.** The Service Provider shall plan and execute regular preventive maintenance, including application of security patches, performance tuning, and periodic upgrades to the Supported Systems and underlying infrastructure. Such activities will be scheduled during Maintenance Windows and carried out so as to minimize impact on production use, consistent with the “Scheduled Maintenance” exclusions in **Section 12.5** of the Master Services Agreement and **Section 12.4** of this SLA.

(e) **Service Desk and End-User Support.** Where specified in an applicable Statement of Work, the Service Provider shall provide first- and/or second-level support to end-users, including incident logging, initial triage, and escalation to specialized support teams as necessary. Support hours, communication channels, and service levels for the service desk shall be as defined in such Statement of Work.

(f) **Reporting and Service Review.** The Service Provider shall prepare and deliver periodic Service Level reports, including monthly availability statistics, incident metrics, trend analyses, and Service Credit computations (if any). The Parties shall conduct regular service review meetings (at least quarterly) to discuss performance, upcoming changes, risk issues, and continuous improvement actions.

2.3 **Detailed Deliverables and Timelines.**

2.3.1 **Onboarding and Transition-In.** Within thirty (30) days following the SLA Effective Date, the Service Provider shall complete a transition-in phase, which shall include:

   (a) Detailed inventory and documentation of all Supported Systems;  
   (b) Deployment or integration of monitoring tools;  
   (c) Agreement on incident classification and prioritization criteria;  
   (d) Implementation of communication and escalation procedures; and  
   (e) Confirmation of access, connectivity, and security configurations.

The Company shall cooperate as required under **Section 2.6 (Company Responsibilities)** of the Master Services Agreement, including providing necessary system access, documentation, and internal contacts.

2.3.2 **Ongoing Deliverables.** During the SLA Term, the Service Provider shall deliver the following recurring outputs:

   (a) **Monthly SLA Reports** detailing uptime, incidents by priority, resolution performance against targets, Service Credit calculations (if any), and summary of any RCAs performed;  
   (b) **Quarterly Capacity and Performance Assessments** with recommendations for scaling, optimization, or changes;  
   (c) **Security and Compliance Updates** at least semi-annually, including a summary of applied patches, vulnerability assessments, and any material security incidents.

2.3.3 **Performance Standards.** In addition to the performance standards specified in **Section 2.5 (Performance Standards)** of the Master Services Agreement (requiring Services to be performed in a professional and workmanlike manner and in accordance with generally accepted industry standards), the Service Provider shall comply with the specific performance metrics and obligations set forth in **Article XII** of this SLA. Failure to meet one or more Service Levels shall entitle the Company to Service Credits, subject to the limitations and exclusions stated herein and in the Master Services Agreement, but shall not, by itself, constitute a material breach unless such failures are repeated and material, as further referenced in **Article IV** of this SLA.

2.4 **Scope Exclusions.**

Unless expressly stated in an applicable Statement of Work, the Services under this SLA do not include:

   (a) Development of new application functionality or major enhancements (which shall be governed by separate Statements of Work under **Article II** of the Master Services Agreement);  
   (b) On-site desktop support or physical hardware maintenance at Company premises;  
   (c) Procurement of Third-Party Products or licenses, except as expressly agreed;  
   (d) Any services necessitated by the Company’s failure to comply with its responsibilities under **Section 2.6** of the Master Services Agreement or this SLA.

Any such excluded services may be requested via a Change Request and, if agreed, added by a Change Order in accordance with **Article XIII** hereof and **Article XIII** of the Master Services Agreement.

2.5 **Company Responsibilities.**

The Company’s responsibilities under **Section 2.6** of the Master Services Agreement apply to this SLA and include, in particular:

   (a) Providing accurate and timely information about business priorities when classifying Incidents;  
   (b) Ensuring internal networks, end-user devices, and connectivity not managed by the Service Provider meet reasonable standards;  
   (c) Promptly reviewing and approving Deliverables and reports within agreed timeframes; and  
   (d) Participating in root cause and service review meetings as reasonably requested.

The Service Provider shall not be liable for delays or SLA failures resulting from the Company’s failure to fulfill these responsibilities, consistent with **Section 2.6** of the Master Services Agreement.

---

## ARTICLE III  
## FEES AND PAYMENT TERMS

3.1 **Contract Value.**

3.1.1 The Parties acknowledge and agree that the **initial aggregate contract value under this SLA** is **US $913,962** (“Contract Value (SLA)”), which is a portion of, and additive to, the contract value described in **Section 3.1** of the Master Services Agreement.  

3.1.2 The Contract Value (SLA) reflects the estimated Fees for the Managed Services and related obligations set forth in this SLA and applicable Statements of Work during the SLA Term. This Contract Value may be increased or decreased only by mutual written agreement via Change Orders, consistent with **Article XIII (Change Management)** of the Master Services Agreement and **Article XIII** of this SLA.

3.2 **Fee Structure.**

Unless otherwise specified in an applicable Statement of Work referencing this SLA, the Fees under this SLA shall consist of the following components:

   (a) **Recurring Managed Services Fees.** A fixed monthly fee for Managed Services and hosting of the Supported Systems (“Monthly Managed Services Fee”), which in aggregate shall equal the SLA Fee Component and shall amount to US $913,962 over the SLA Term. The allocation per month shall be specified in the applicable Statement of Work (e.g., a uniform monthly amount or tiered amounts by year).  

   (b) **Variable Usage-Based Fees (if applicable).** Additional fees based on transaction volumes, storage usage, or other consumption metrics as defined in the applicable Statement of Work.  

   (c) **One-Time Transition or Setup Fees.** Any one-time fees for transition-in, setup, or onboarding activities shall be separately identified and invoiced as milestones, consistent with the milestone-based structure described in **Section 3.2(c)** of the Master Services Agreement.

3.3 **Payment Terms (Net 60).**

3.3.1 Notwithstanding the general “Net 45” terms set forth in **Section 3.3(a)** of the Master Services Agreement, the Parties expressly agree that for Fees due under this SLA, the payment terms shall be **Net 60**, such that all undisputed invoices issued by the Service Provider hereunder shall be payable by the Company within sixty (60) calendar days from the invoice date.

3.3.2 All other invoicing and dispute procedures set forth in **Sections 3.3(b) and 3.3(c)** of the Master Services Agreement shall apply, including the Company’s obligation to notify the Service Provider in writing of any disputed portion of an invoice within fifteen (15) days of receipt and the requirement to pay all undisputed portions.

3.4 **Late Payment.**

Any undisputed amount that remains unpaid after the due date shall accrue interest in accordance with **Section 3.4** of the Master Services Agreement (i.e., at the lesser of 1.5% per month or the maximum rate permitted by Applicable Law). The Service Provider’s rights to suspend Services for non-payment, as set forth in **Section 3.4** of the Master Services Agreement, shall apply to the Services under this SLA.

3.5 **Taxes.**

Tax responsibilities relating to the Services and Deliverables hereunder shall be governed by **Section 3.5** of the Master Services Agreement. All Fees under this SLA are exclusive of taxes, and the Company shall be responsible for any applicable taxes, except for taxes based on the Service Provider’s net income.

3.6 **Expenses and Reimbursement.**

3.6.1 To the extent that the Services under this SLA require travel or out-of-pocket expenditures (e.g., for on-site support, hardware replacement coordination), such expenses shall be reimbursable pursuant to **Section 3.6** of the Master Services Agreement, provided they are pre-approved in writing by the Company.  

3.6.2 The Service Provider shall provide reasonable supporting documentation for reimbursable expenses upon request, and the Company shall reimburse approved expenses within sixty (60) days of receipt of the applicable invoice, aligning with the Net 60 payment terms of this SLA.

3.7 **No Withholding of Payments as Exclusive Remedy.**

The restriction on withholding or offsetting payments set forth in **Section 3.7** of the Master Services Agreement shall apply fully to Fees and expenses under this SLA. The Company’s remedies for alleged breaches of this SLA shall be as provided in this SLA and the Master Services Agreement, and not through unilateral withholding of undisputed amounts.

---

## ARTICLE IV  
## TERM AND TERMINATION

4.1 **SLA Term.**

This SLA shall commence on the **SLA Effective Date** (May 18, 2026) and, unless earlier terminated as provided herein or in the Master Services Agreement, shall remain in effect until **December 23, 2027** (the “SLA Expiration Date”).

4.2 **Renewal.**

The SLA Term may be extended by mutual written agreement of the Parties, executed no later than sixty (60) days prior to the SLA Expiration Date, consistent with the renewal provisions of **Section 4.2** of the Master Services Agreement. Any renewal shall be on terms mutually agreed by the Parties and may include revised pricing or Service Levels.

4.3 **Termination for Convenience.**

4.3.1 Consistent with **Section 4.3** of the Master Services Agreement, either Party may terminate this SLA (in whole or in part with respect to any related Statement of Work) for convenience by providing the other Party with at least **one hundred eighty (180) days’ prior written notice**.  

4.3.2 Termination of this SLA for convenience shall not automatically terminate the Master Services Agreement, but termination of the Master Services Agreement will have the effect described in **Section 4.6** below.

4.4 **Termination for Cause.**

Either Party may terminate this SLA or any affected Statement of Work for material breach by the other Party, subject to the cure process in **Section 4.4** of the Master Services Agreement. Specifically:

   (a) The non-breaching Party shall provide written notice specifying the nature of the breach and granting a thirty (30) day cure period;  
   (b) If the breach is not cured within such cure period, the non-breaching Party may terminate the SLA or affected Statement of Work upon written notice.

4.5 **Termination Triggered by Parent Agreement.**

4.5.1 In the event the Master Services Agreement is terminated or expires for any reason, this SLA shall automatically terminate on the effective date of such termination or expiration, without the need for additional notice, except to the extent the Parties expressly agree otherwise in writing.  

4.5.2 Upon such termination, the rights and obligations of the Parties shall be governed by **Section 4.5 (Effect of Termination)** and **Section 4.6 (Survival)** of the Master Services Agreement, as supplemented by this **Section 4.6**.

4.6 **Effect of Termination.**

Upon expiration or termination of this SLA for any reason:

   (a) The Company shall pay the Service Provider for all Services performed and Deliverables provided through the effective date of termination, including any unpaid Fees, expenses, and approved committed costs, as required by **Section 4.5(a)** of the Master Services Agreement. In the case of termination by the Company for convenience, the Company shall also pay any reasonable wind-down costs actually incurred by the Service Provider in connection with an orderly cessation of Services;  

   (b) The Parties shall return or destroy Confidential Information as described in **Section 5.5** of the Master Services Agreement and **Section 5.5** of this SLA;  

   (c) The Service Provider shall cooperate with the Company to facilitate a transition of the Services to the Company or a third party in a commercially reasonable manner, as contemplated by **Section 4.5(c)** of the Master Services Agreement, which may include the provision of transition assistance services on a time and materials basis;  

   (d) The SLA-specific provisions that are intended by their nature to survive termination (including but not limited to payment obligations, confidentiality, intellectual property rights, indemnification, limitation of liability, data protection, and dispute resolution) shall survive in accordance with **Section 4.6** of the Master Services Agreement and **Article XVI** of this SLA.

---

## ARTICLE V  
## CONFIDENTIALITY

5.1 **Relationship to Master Agreement.**

The confidentiality framework set forth in **Article V (Confidentiality)** of the Master Services Agreement applies fully to this SLA. The provisions below are intended to supplement, and not limit or replace, the obligations under the Master Services Agreement.

5.2 **Definition of Confidential Information.**

For purposes of this SLA, “Confidential Information” has the meaning set forth in **Section 5.1** of the Master Services Agreement and includes, without limitation, any detailed architecture diagrams, security configurations, monitoring thresholds, incident reports, RCAs, and SLA performance reports generated under this SLA.

5.3 **Obligations.**

Each Party shall comply with the obligations in **Section 5.2** of the Master Services Agreement, including:

   (a) Using Confidential Information solely to perform or receive Services under this SLA and the Master Services Agreement;  
   (b) Restricting disclosure to employees, Affiliates, subcontractors, and advisors with a need to know and under confidentiality obligations at least as restrictive; and  
   (c) Exercising at least reasonable care to protect Confidential Information.

5.4 **Exceptions and Compelled Disclosure.**

The exceptions set forth in **Section 5.3** (public domain, independently developed, lawfully received, or already known information) and the compelled disclosure provisions in **Section 5.4** (allowing disclosure when legally required, with notice and cooperation) of the Master Services Agreement apply equally to Confidential Information exchanged under this SLA.

5.5 **Return or Destruction.**

Upon termination or expiration of this SLA, or upon a Party’s written request, the other Party shall return or securely destroy Confidential Information relating specifically to this SLA, consistent with **Section 5.5** of the Master Services Agreement, subject to retention for compliance or backup purposes as described there.

5.6 **Survival.**

The confidentiality obligations under this **Article V** shall survive termination or expiration of this SLA for a period of **five (5) years**, consistent with **Section 5.6** of the Master Services Agreement, and in the case of trade secrets or Personal Data, for so long as such information remains trade secret or Personal Data under Applicable Law.

---

## ARTICLE VI  
## INTELLECTUAL PROPERTY RIGHTS

6.1 **Pre-Existing IP.**

The allocation of Intellectual Property Rights under **Article VI** of the Master Services Agreement applies to any Deliverables, tools, or materials provided under this SLA.

   (a) The Service Provider retains ownership of all **Service Provider Pre-Existing IP** under **Section 6.1** of the Master Services Agreement;  
   (b) The Company retains ownership of all **Company Pre-Existing IP** under **Section 6.2** of the Master Services Agreement.

6.2 **Deliverables Under This SLA.**

To the extent the Service Provider creates any Deliverables specifically identified in a Statement of Work under this SLA as “Company-Owned Deliverables” (such as configuration documentation, operating procedures, or custom monitoring scripts), the ownership and license rights shall be as set forth in **Section 6.3** of the Master Services Agreement, which grants ownership to the Company, subject to the Service Provider’s continuing rights in its Pre-Existing IP and the license described in **Section 6.3(b)**.

6.3 **Operational Artifacts.**

Operational artifacts generated as part of the Managed Services (e.g., log files, monitoring data, incident tickets, RCAs) shall be used by the Service Provider for the purpose of delivering Services and improving its tools and processes. To the extent such artifacts contain Company Confidential Information or Client Data, they shall be handled in accordance with **Articles V and XI** of the Master Services Agreement and this SLA. The Company shall have a right to access and receive copies of such artifacts as reasonably required for its internal business purposes.

6.4 **Restrictions.**

The usage restrictions in **Section 6.6** of the Master Services Agreement (prohibiting reverse engineering, removal of proprietary notices, and use for competing services) apply to any software or tools provided by the Service Provider under this SLA.

6.5 **Feedback.**

Any Feedback provided by the Company in relation to the Services under this SLA shall be subject to **Section 6.7** of the Master Services Agreement, which grants the Service Provider a broad license to use such Feedback, provided Company Confidential Information is not disclosed.

---

## ARTICLE VII  
## REPRESENTATIONS AND WARRANTIES

7.1 **Mutual Representations and Warranties.**

The mutual representations and warranties set forth in **Section 7.1** of the Master Services Agreement (organization, authority, due authorization, and enforceability) are hereby reaffirmed by each Party with respect to this SLA.

7.2 **Service Provider Warranties.**

The Service Provider reiterates and applies to this SLA the warranties in **Section 7.2** of the Master Services Agreement, including that:

   (a) The Services under this SLA will be performed in a professional and workmanlike manner and in accordance with generally accepted industry standards;  
   (b) To the Service Provider’s knowledge as of delivery, Deliverables (if any) do not infringe third-party IPR when used as authorized;  
   (c) The Service Provider will comply with all Applicable Laws in the performance of the Services, including data protection and privacy laws as set forth in **Article XI** of both the Master Services Agreement and this SLA; and  
   (d) The Service Provider maintains all necessary licenses, permits, and approvals to perform the Services.

7.3 **Company Warranties.**

The Company reiterates and applies to this SLA the warranties in **Section 7.3** of the Master Services Agreement, including that it has the right to provide Client Data, will comply with Applicable Law, and will not use the Services for unlawful purposes.

7.4 **Disclaimer.**

Except as expressly provided in this SLA and **Article VII** of the Master Services Agreement, the Services, Deliverables, and materials provided under this SLA are furnished “AS IS” and “AS AVAILABLE,” and the Service Provider disclaims all other warranties to the fullest extent permitted by law, as described in **Section 7.4** of the Master Services Agreement.

---

## ARTICLE VIII  
## INDEMNIFICATION

8.1 **Incorporation of Master Services Agreement.**

The indemnification obligations set forth in **Article VIII (Indemnification)** of the Master Services Agreement apply to the Services and Deliverables provided under this SLA. The provisions herein are intended to clarify their application to the specific Services.

8.2 **Indemnification by the Company.**

In addition to the obligations in **Section 8.1** of the Master Services Agreement, the Company shall indemnify, defend, and hold harmless the Service Provider Indemnitees from and against any Losses arising out of or related to:

   (a) The Company’s misuse of the Supported Systems or Services in violation of this SLA, the Master Services Agreement, or Applicable Law;  
   (b) Any configuration or customization directed by the Company that causes a security breach, data loss, or other Incident, except to the extent caused by the Service Provider’s failure to follow reasonable professional practices or documented instructions;  
   (c) Any claims arising from Client Data provided by the Company for processing within the Supported Systems, except to the extent directly caused by the Service Provider’s breach of **Article XI** of the Master Services Agreement or this SLA.

8.3 **Indemnification by the Service Provider.**

The Service Provider’s obligations under **Section 8.2** of the Master Services Agreement (including IP infringement and data protection-related indemnities) apply to any Deliverables and Personal Data processing under this SLA.

8.4 **Indemnification Procedures.**

The procedures in **Section 8.3** of the Master Services Agreement regarding notice, control of defense, and cooperation apply to all indemnification claims hereunder.

8.5 **Infringement Remedies.**

The remedies in **Section 8.4** of the Master Services Agreement (procure rights, modify, replace, or terminate and refund prepaid Fees) apply if any component of the Supported Systems or Deliverables provided by the Service Provider under this SLA becomes the subject of a third-party infringement claim.

---

## ARTICLE IX  
## LIMITATION OF LIABILITY

9.1 **Uncapped Liability and High-Risk Engagement.**

Consistent with the high-risk designation in **Section 2.7** and the liability regime in **Article IX** of the Master Services Agreement, the Parties agree that there shall be **no contractual cap** on the liability of either Party under this SLA. The uncapped liability and the allowance for all types of damages (including consequential, special, and punitive) as set forth in **Sections 9.1 and 9.2** of the Master Services Agreement are hereby incorporated and apply to all claims arising under or in connection with this SLA.

9.2 **Types of Damages.**

Subject to **Section 9.3** of the Master Services Agreement, each Party shall be liable for all direct and indirect damages, including consequential and special damages, arising out of or relating to this SLA, even if advised of the possibility of such damages, consistent with **Section 9.2** of the Master Services Agreement.

9.3 **Exceptions and Unexcluded Liabilities.**

The exceptions set forth in **Section 9.3** of the Master Services Agreement (for gross negligence, willful misconduct, death or personal injury, fraud, breaches of confidentiality or data protection, and non-excludable statutory liabilities) apply fully to this SLA.

9.4 **Allocation of Risk.**

The Parties acknowledge that the Fees and terms of this SLA reflect the allocation of risk in **Article IX** of the Master Services Agreement, including the uncapped nature of liability, and that the economic terms would have been materially different absent such risk allocation.

---

## ARTICLE X  
## INSURANCE

10.1 **Required Coverage.**

The insurance requirements set forth in **Article X** of the Master Services Agreement (commercial general liability, professional liability, cyber liability, workers’ compensation, and automobile liability) apply to the Services under this SLA. The Service Provider represents that such coverage is in place and will be maintained throughout the SLA Term and for at least one (1) year thereafter.

10.2 **Certificates of Insurance.**

Upon the Company’s reasonable request, the Service Provider shall provide certificates of insurance evidencing the required coverage, as contemplated by **Section 10.2** of the Master Services Agreement.

10.3 **No Limitation.**

The existence of such insurance does not limit the Service Provider’s obligations or liability under this SLA, consistent with **Section 10.3** of the Master Services Agreement.

---

## ARTICLE XI  
## DATA PROTECTION AND PRIVACY

11.1 **Application of Master Services Agreement.**

The data protection and privacy obligations set forth in **Article XI (Data Protection and Privacy)** of the Master Services Agreement apply in full to any processing of Personal Data in connection with the Managed Services and Supported Systems governed by this SLA.

11.2 **Roles of the Parties.**

Consistent with **Section 11.2** of the Master Services Agreement, the Company acts as the data “controller,” and the Service Provider acts as the “processor” with respect to Personal Data processed as part of the Services under this SLA.

11.3 **Security Measures.**

The Service Provider shall implement technical and organizational measures appropriate to the risk of processing Personal Data within the Supported Systems, as required by **Section 11.3(c)** of the Master Services Agreement. Such measures shall include, where appropriate: encryption, access controls, logging, vulnerability management, and regular security patches.

11.4 **Data Breach Notification and Management.**

In the event of a Personal Data breach affecting Services under this SLA, the notification and response obligations in **Section 11.4** of the Master Services Agreement shall apply, including notification within seventy-two (72) hours of becoming aware of the breach and cooperation with the Company’s reporting and remediation efforts.

11.5 **Data Retention, Return, and Deletion.**

Upon termination or expiration of this SLA, the Service Provider shall, at the Company’s option, return or delete Personal Data processed under this SLA, consistent with **Section 11.3(g)** and **Section 11.6** of the Master Services Agreement, subject to any legal retention requirements.

11.6 **Data Transfers.**

To the extent any Services under this SLA involve cross-border transfers of Personal Data, the Parties shall implement appropriate safeguards in accordance with **Section 11.5** of the Master Services Agreement and any data transfer addenda executed between the Parties.

---

## ARTICLE XII  
## SERVICE LEVEL AGREEMENTS

12.1 **General.**

This Article XII sets forth the specific Service Levels applicable to the Managed Services and Supported Systems under this SLA and supplements the baseline SLA framework in **Article XII** of the Master Services Agreement.

12.2 **Availability / Uptime Commitment.**

12.2.1 The Service Provider shall use commercially reasonable efforts to ensure that each production Supported System is available not less than **99.9%** of the time in each calendar month, measured 24x7, excluding:

   (a) **Scheduled Maintenance** windows agreed in advance and occurring during low-utilization periods;  
   (b) **Emergency Maintenance**, to the extent reasonably necessary;  
   (c) Downtime caused by Force Majeure Events (as defined in **Article XV** of the Master Services Agreement and this SLA); and  
   (d) Downtime attributable to the Company’s systems, networks, or actions.

12.2.2 The definition of “Scheduled Maintenance” in **Section 12.2(b)** of the Master Services Agreement shall apply. The Service Provider shall provide at least five (5) Business Days’ prior notice for Scheduled Maintenance that is expected to cause material downtime.

12.3 **Incident Classification, Response, and Resolution Targets.**

The Service Provider shall classify and respond to Incidents in accordance with the following target timeframes (which reflect and expand upon **Section 12.3** of the Master Services Agreement):

- **Priority 1 (Critical)** – Complete outage of a production Supported System or severe impact on core business operations with no workaround available.  
  - Response Time: within **1 hour** of receipt of the Incident report (24x7).  
  - Target Resolution or Workaround: within **8 hours**.

- **Priority 2 (High)** – Significant degradation or partial outage of a production Supported System, or impairment of critical functionality, where a workaround may exist but is not sustainable for prolonged use.  
  - Response Time: within **4 hours** of receipt (24x7).  
  - Target Resolution or Workaround: within **24 hours**.

- **Priority 3 (Medium)** – Non-critical functionality impaired or performance issues with minor impact on business operations.  
  - Response Time: within **1 Business Day**.  
  - Target Resolution or Workaround: within **5 Business Days**.

- **Priority 4 (Low)** – Minor issues, cosmetic defects, or general inquiries that do not materially affect operations.  
  - Response Time: within **2 Business Days**.  
  - Resolution: on a commercially reasonable efforts basis.

The Parties may refine these definitions and targets in an applicable Statement of Work.

12.4 **Service Credits and Remedies.**

12.4.1 **Uptime Service Credits.** If the monthly uptime for a Supported System falls below the 99.9% commitment, the Company shall be entitled to the following Service Credits with respect to the SLA Fee Component applicable to that Supported System for the affected month:

   - Uptime between 99.0% and 99.89%: credit equal to **5%** of the monthly Managed Services Fee for the affected Supported System;  
   - Uptime between 98.0% and 98.99%: credit equal to **10%** of such monthly fee;  
   - Uptime below 98.0%: credit equal to **20%** of such monthly fee.

12.4.2 **Claiming Service Credits.** Service Credits shall be applied as a credit against future invoices and shall not be redeemable for cash, consistent with **Section 12.4(b)** of the Master Services Agreement. The Company must request Service Credits in writing within thirty (30) days following the end of the month in which the SLA breach occurred, providing reasonable supporting details.

12.4.3 **Exclusive Monetary Remedy for SLA Failures.** Service Credits constitute the Company’s **exclusive monetary remedy** for failures to meet the Service Levels, without prejudice to the Company’s rights to seek other remedies (including termination for material breach) under **Article IV** of this SLA and **Article XIV (Dispute Resolution)** of the Master Services Agreement, subject to the liability rules in **Article IX** of the Master Services Agreement.

12.5 **Root Cause Analysis and Continuous Improvement.**

For any Priority 1 Incident or repeated SLA failure over two consecutive months, the Service Provider shall perform an RCA and present it to the Company within ten (10) Business Days of the Incident or the end of the second month, as applicable, including proposed corrective and preventive actions. The Parties shall collaborate in good faith to implement commercially reasonable improvements.

12.6 **Exclusions.**

SLA commitments, including uptime and response targets, shall not apply to performance or availability issues resulting from any of the exclusions set forth in **Section 12.5** of the Master Services Agreement, including but not limited to:

   (a) Force Majeure Events;  
   (b) Actions or omissions of the Company or third parties;  
   (c) Use of non-supported configurations or non-compliant integrations;  
   (d) Scheduled Maintenance or Emergency Maintenance;  
   (e) Incidents arising from Client Data corruption caused by the Company.

---

## ARTICLE XIII  
## CHANGE MANAGEMENT

13.1 **Change Requests and Change Orders.**

The Change Management process set forth in **Article XIII** of the Master Services Agreement applies to changes to the scope, Service Levels, Supported Systems, or Fees under this SLA. Either Party may submit a Change Request, and the Service Provider shall respond with a Change Order proposal specifying the impact on scope, Fees, and timelines, in accordance with **Section 13.2** of the Master Services Agreement.

13.2 **Impact on Service Levels.**

Any change that materially affects the architecture, volume, or nature of the Supported Systems may require a corresponding adjustment to Service Levels or Fees. The Parties shall document such adjustments in a Change Order before implementation. The Service Provider shall not be obligated to meet Service Levels that were established based on assumptions that are materially altered without a mutually agreed Change Order.

13.3 **Emergency Changes.**

In exceptional circumstances where immediate action is required to prevent or mitigate significant harm to the Company’s systems or operations, the Company may verbally authorize the Service Provider to implement an emergency change consistent with **Section 13.4** of the Master Services Agreement. Such change and its commercial impact shall be documented in a Change Order as soon as reasonably practicable.

---

## ARTICLE XIV  
## DISPUTE RESOLUTION

14.1 **Negotiation and Escalation.**

In the event of any dispute arising out of or relating to this SLA, the negotiation and escalation procedures in **Section 14.1** of the Master Services Agreement shall apply. The Parties shall first attempt to resolve the dispute through discussions between designated project managers, followed by escalation to senior executives if unresolved.

14.2 **Mediation.**

If the dispute is not resolved through escalation within thirty (30) days, the Parties may pursue non-binding mediation in Wilmington, Delaware, as described in **Section 14.2** of the Master Services Agreement.

14.3 **Arbitration or Litigation; Venue.**

If the dispute remains unresolved, either Party may initiate litigation in the state or federal courts located in **New Castle County, Delaware**, as provided in **Section 14.3** of the Master Services Agreement. The Parties submit to the exclusive jurisdiction of such courts and waive objections based on improper venue or forum non conveniens.

14.4 **Interim Relief and Attorneys’ Fees.**

Either Party may seek interim or injunctive relief to protect its rights, as permitted by **Section 14.4** of the Master Services Agreement. The prevailing Party in any action to enforce this SLA shall be entitled to recover reasonable attorneys’ fees and costs pursuant to **Section 14.5** of the Master Services Agreement.

---

## ARTICLE XV  
## FORCE MAJEURE

15.1 **Force Majeure Events.**

The definition of “Force Majeure Event” in **Section 15.1** of the Master Services Agreement applies to this SLA and includes events beyond a Party’s reasonable control, such as natural disasters, war, terrorism, epidemics, government actions, or major telecommunications failures not caused by the affected Party.

15.2 **Notice and Suspension.**

The affected Party shall provide prompt notice of any Force Majeure Event and may have its performance obligations under this SLA (other than payment obligations) suspended for the duration of the Force Majeure Event, as described in **Sections 15.2 and 15.3** of the Master Services Agreement.

15.3 **Extended Force Majeure.**

If a Force Majeure Event continues for more than sixty (60) consecutive days and materially affects performance of the Services, either Party may terminate this SLA in accordance with **Section 15.4** of the Master Services Agreement, without liability except for payment obligations accrued prior to the date of termination.

---

## ARTICLE XVI  
## GENERAL PROVISIONS

16.1 **Reference to Master/Parent Agreement.**

This Service Level Agreement is executed under and subject to the terms of **Master Services Agreement** reference number **MSA-SUM-202508-578** (file identifier **contract_578**). Except as expressly modified or supplemented herein, all terms and conditions of the Master Services Agreement remain in full force and effect and shall govern the Parties’ relationship with respect to the Services described in this SLA.

16.2 **Governing Law.**

This SLA and any dispute arising out of or relating hereto shall be governed by and construed in accordance with the laws of the **State of Delaware**, without giving effect to any choice-of-law or conflict-of-laws rules, consistent with **Section 16.1** of the Master Services Agreement.

16.3 **Entire Agreement; Hierarchy.**

This SLA, together with the Master Services Agreement (Ref. MSA-SUM-202508-578, contract_578) and any applicable Statements of Work that reference both, constitutes the entire agreement between the Parties with respect to the specific subject matter hereof (Service Levels and Managed Services for the Supported Systems), and supersedes all prior or contemporaneous understandings relating thereto. In case of conflict:

   (a) The Master Services Agreement shall control over this SLA, except where this SLA expressly states that it supersedes a specific provision of the Master Services Agreement with respect to the Services hereunder;  
   (b) This SLA shall control over any conflicting terms in a Statement of Work solely with respect to Service Levels and related remedies, unless such Statement of Work explicitly states that it is intended to supersede a particular provision of this SLA and references the relevant section.

16.4 **Amendments.**

No modification or amendment of this SLA shall be effective unless in writing and signed by authorized representatives of both Parties, expressly stating that it amends SLA-SUM-202508-727 and referencing the Master Services Agreement, consistent with **Section 16.3** of the Master Services Agreement.

16.5 **Severability.**

If any provision of this SLA is held invalid or unenforceable by a court of competent jurisdiction, the remaining provisions shall remain in full force and effect. The Parties shall in good faith replace any invalid provision with a valid one that most closely approximates the Parties’ original intent, consistent with **Section 16.4** of the Master Services Agreement.

16.6 **Waiver.**

No failure or delay by either Party in exercising any right or remedy under this SLA shall operate as a waiver thereof. Any waiver must be in writing and signed by the waiving Party, consistent with **Section 16.5** of the Master Services Agreement.

16.7 **Notices.**

All notices under this SLA shall be given in accordance with **Section 16.6 (Notices)** of the Master Services Agreement and addressed as follows:

**For the Company (Contoso Enterprises, Inc.):**  
Attn: General Counsel  
Contoso Enterprises, Inc.  
4100 Contoso Parkway  
Wilmington, DE 19801 USA  
Email: legal@contoso.com  

With a copy (which shall not constitute notice) to:  
Attn: CIO  
Email: cio@contoso.com  

**For the Service Provider (Summit Tech Solutions, LLC):**  
Attn: Legal Department  
Summit Tech Solutions, LLC  
920 Summit Avenue, Suite 1400  
Newark, DE 19711 USA  
Email: legal@summittech.com  

With a copy (which shall not constitute notice) to:  
Attn: Account Director – Contoso Account  
Email: contoso.account@summittech.com  

16.8 **Assignment.**

The assignment provisions in **Section 16.7** of the Master Services Agreement apply to this SLA. The Company may not assign this SLA or its rights or obligations hereunder without the Service Provider’s prior written consent, except as allowed under the Master Services Agreement. The Service Provider may assign this SLA to an Affiliate or in connection with a merger, acquisition, or sale of substantially all its assets, as permitted by the Master Services Agreement.

16.9 **Independent Contractors.**

The Parties’ relationship under this SLA remains that of independent contractors, as described in **Section 16.8** of the Master Services Agreement. Nothing in this SLA creates a partnership, joint venture, or agency relationship between the Parties.

16.10 **No Third-Party Beneficiaries.**

Except as expressly provided in **Article VIII (Indemnification)** of the Master Services Agreement regarding Indemnitees, this SLA is for the sole benefit of the Parties and not for any third party, consistent with **Section 16.9** of the Master Services Agreement.

16.11 **Counterparts; Electronic Signatures.**

This SLA may be executed in counterparts, each of which shall be deemed an original, and all of which together constitute one instrument. Signatures transmitted electronically (including via PDF or electronic signature platform) shall be deemed original signatures and fully binding on the Parties.

---

## SIGNATURE PAGE

IN WITNESS WHEREOF, the Parties hereto have caused this Service Level Agreement, **Contract Reference Number SLA-SUM-202508-727**, to be executed by their duly authorized representatives as of the SLA Effective Date first written above.

**Executed pursuant to MSA-SUM-202508-578 (contract_578).**

---

### CONTOSO ENTERPRISES, INC.  
(“Contoso” or the “Company”)

By: _________________________________  
Name: _______________________________  
Title: ________________________________  
Date: ________________________________  

Witness (if required): ________________  
Name: _______________________________  
Title: ________________________________  
Date: ________________________________  

---

### SUMMIT TECH SOLUTIONS, LLC  
(“Summit Tech” or the “Service Provider”)

By: _________________________________  
Name: _______________________________  
Title: ________________________________  
Date: ________________________________  

Witness (if required): ________________  
Name: _______________________________  
Title: ________________________________  
Date: ________________________________  

---

**[End of Service Level Agreement – SLA-SUM-202508-727]**