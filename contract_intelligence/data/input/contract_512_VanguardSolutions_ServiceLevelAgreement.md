# SERVICE LEVEL AGREEMENT  
**Contract Reference Number: SLA-VAN-202501-512**

---

## SERVICE LEVEL AGREEMENT  
**Between**  
**Contoso Enterprises** and **Vanguard Solutions**  
**Effective Date: 30 September 2025**  
**Expiration Date: 20 March 2027**

---

### PREAMBLE

This SERVICE LEVEL AGREEMENT (this **“SLA”** or this **“Agreement”**), bearing Contract Reference Number **SLA-VAN-202501-512**, is entered into as of **30 September 2025** (the **“SLA Effective Date”**), by and between:

- **Contoso Enterprises**, a company duly incorporated and existing under the laws of the United Kingdom, having its principal place of business at 100 Bishopsgate, London EC2N 4AG, United Kingdom (**“Contoso”**, the **“Client”** or the **“Company”**); and  

- **Vanguard Solutions**, a company duly incorporated and existing under the laws of the United Kingdom, having its principal place of business at 200 Aldersgate Street, London EC1A 4HD, United Kingdom (**“Vanguard”**, the **“Vendor”** or the **“Service Provider”**).

Client and Vendor are hereinafter sometimes referred to individually as a **“Party”** and collectively as the **“Parties”**.

This SLA is entered into **pursuant to and in supplementation of** that certain **Master Services Agreement**, Contract Reference Number **MSA-VAN-202501-453**, internal identifier **contract_453**, dated **29 January 2025** (the **“Master Services Agreement”** or **“MSA”**) between the same Parties.

---

### RECITALS

WHEREAS, the Parties entered into the Master Services Agreement, Ref: **MSA-VAN-202501-453** (internal identifier **contract_453**), effective as of 29 January 2025, which sets forth the general terms and conditions governing Vendor’s provision of professional, consulting, implementation, support, managed services, and related services to Client, including, inter alia, the definitions in **Article I**, the scope framework in **Article II**, the fees and payment provisions in **Article III**, and the service level framework in **Article XII (Service Level Agreements)**;

WHEREAS, under **Section 1.1.15** of the MSA, the term **“Service Levels”** is defined by reference to **Article XII**, which establishes certain baseline service availability, response and resolution targets, monitoring, reporting, and service credit mechanisms (including **SLA Credits** as defined in **Section 1.1.17** and addressed in **Section 12.4**);

WHEREAS, **Article II (Scope of Services / Work)** of the MSA contemplates that the Parties may enter into additional documents, including Statements of Work (SOWs) and service level agreements, to describe in greater detail the Services, Deliverables, performance metrics, and service-level related commitments applicable to particular managed services engagements;

WHEREAS, Client now wishes to engage Vendor, under the Master Services Agreement, for the provision of certain **managed services and support**, including high-availability production support, monitoring, incident management, problem resolution, and maintenance services as described in **Section 2.2.4 (Managed Services and Support)** of the MSA, and the Parties desire to set out specific service levels and associated terms in this SLA;

WHEREAS, this SLA is intended to **supplement** (and not replace) the Master Services Agreement, by providing more detailed service level commitments, performance indicators, reporting obligations, and related commercial and operational terms for the managed services engagement described herein, all of which are to be interpreted consistently with the MSA, including but not limited to **Articles V (Confidentiality), VI (Intellectual Property Rights), VII (Representations and Warranties), VIII (Indemnification), IX (Limitation of Liability), X (Insurance), XI (Data Protection and Privacy) and XII (Service Level Agreements)** of the MSA;

NOW, THEREFORE, in consideration of the mutual covenants, promises, and agreements contained herein, and other good and valuable consideration, the sufficiency and receipt of which are hereby acknowledged, the Parties hereby agree as follows:

---

## ARTICLE I – DEFINITIONS

1.1 **Defined Terms.** Capitalized terms used but not defined in this SLA shall have the meanings given to them in the Master Services Agreement (Ref: **MSA-VAN-202501-453**, internal identifier **contract_453**). For purposes of this SLA, the following additional terms shall have the meanings set forth below:

1.1.1 **“Agreement”** or **“SLA”** has the meaning set forth in the Preamble and refers to this Service Level Agreement, Contract Reference Number **SLA-VAN-202501-512**, including all schedules and attachments hereto, as may be amended in writing in accordance with **Article XVI**.

1.1.2 **“Parent Agreement”** or **“Master Agreement”** means the Master Services Agreement between the Parties dated 29 January 2025, Contract Reference Number **MSA-VAN-202501-453**, internal identifier **contract_453**, including all Schedules, Exhibits, and Statements of Work executed thereunder, as amended or supplemented from time to time.

1.1.3 **“Managed Services”** means the ongoing operational support, monitoring, incident management, problem resolution, maintenance, and related services to be provided by Vendor to Client under this SLA, consistent with and as a subset of the **“Managed Services and Support”** described in **Section 2.2.4** of the Master Agreement.

1.1.4 **“Supported Systems”** means the specific systems, platforms, applications, integrations, environments, and related infrastructure identified in **Schedule 1 (Supported Systems and Environments)** to this SLA, as may be updated in accordance with **Article XIII (Change Management)**.

1.1.5 **“Service Levels”** means the performance standards, including uptime commitments, incident response and resolution times, and other qualitative and quantitative metrics described in **Article XII of the Master Agreement** and further detailed and customized in **Article XII of this SLA**.

1.1.6 **“Service Window”** means the period during which Vendor is obligated to provide the Services and meet the relevant Service Levels for the Supported Systems. Unless otherwise specified in Schedule 1, the standard Service Window shall be twenty-four (24) hours per day, seven (7) days per week, including public holidays.

1.1.7 **“Maintenance Window”** means the period reserved for planned maintenance activities, including upgrades, patching, and non-critical configuration changes, during which the Supported Systems may be partially or fully unavailable and such unavailability shall be excluded from uptime calculations, subject to the notice and scheduling requirements set out herein.

1.1.8 **“Incident”** means any unplanned interruption to, or reduction in the quality or performance of, the Services or the Supported Systems that prevents or materially impairs the normal functioning thereof, as reported by Client or detected by Vendor’s monitoring tools.

1.1.9 **“Severity Level”** means the classification of an Incident (P1, P2, P3, or P4) based on business impact and urgency, as further defined in **Section 12.2** of the Master Agreement and in **Section 12.2** of this SLA.

1.1.10 **“SLA Credits”** has the meaning given in **Section 1.1.17 of the Master Agreement** and is further described in **Section 12.4 of the Master Agreement** and **Section 12.4 of this SLA**; it refers to service credits payable in the form of reduced future Fees as the sole monetary remedy for Service Level failures (subject to Client’s other contract rights).

1.1.11 **“Monthly Measurement Period”** means each calendar month during the Term of this SLA, for which Service Levels, performance metrics, and SLA Credits are measured and calculated.

1.1.12 **“Availability”** or **“Service Availability”** means, for each Monthly Measurement Period, the percentage of time during the relevant Service Window that the production instance(s) of the Supported Systems are capable of performing their primary functions, excluding downtime permitted under this SLA and the Master Agreement (including downtime due to scheduled maintenance, emergency maintenance, Force Majeure Events as defined in **Section 15.1 of the Master Agreement**, Client-caused issues, or other agreed exclusions).

1.1.13 **“Business Day”** has the meaning given in **Section 1.1.4 of the Master Agreement** and shall be used for calculation of response and resolution times for P2–P4 Incidents as applicable.

1.1.14 **“Change Request”** and **“Change Order”** have the meanings given in **Sections 13.1 and 13.2 of the Master Agreement**, as applied to changes to the Services, Service Levels, Supported Systems, scope, or other aspects of this SLA.

1.1.15 **“Client Data”** has the meaning set forth in **Section 1.1.6 of the Master Agreement**, and includes without limitation any data processed by Vendor as part of the Managed Services.

1.1.16 **“Confidential Information”** has the meaning set forth in **Section 5.1 of the Master Agreement** and includes Service performance and SLA reporting, except to the extent otherwise agreed.

1.1.17 **“Force Majeure Event”** has the meaning set forth in **Section 15.1 of the Master Agreement** and includes events impacting the provision of the Services under this SLA.

1.1.18 **“Fees”** means the fees payable by Client to Vendor for the Services under this SLA, as set out in **Article III** below and consistent with **Article III of the Master Agreement**.

1.1.19 **“Term”** has the meaning given in **Section 4.1** of this SLA, and is related to, but separate from, the Term of the Master Agreement as defined in **Section 4.1 of the Master Agreement**.

1.1.20 **“Transition Assistance”** means the assistance Vendor shall provide upon termination or expiry of this SLA or the Master Agreement to facilitate the orderly transition of the Managed Services to Client or another provider, consistent with **Section 4.6.4 of the Master Agreement** and as further set out in **Section 4.6** of this SLA.

---

## ARTICLE II – SCOPE OF SERVICES / WORK

2.1 **General Scope.**  
This SLA sets out the detailed service levels and operational provisions applicable to the **Managed Services** to be provided by Vendor to Client under and pursuant to the Master Agreement. In accordance with **Article II (Scope of Services / Work)** of the Master Agreement, Vendor shall perform the Services and provide the Deliverables described herein, together with any related Statement of Work executed under the Master Agreement that references this SLA.

2.2 **Relationship to Master Agreement.**  
The Parties acknowledge and agree that:

2.2.1 This SLA **supplements the Master Services Agreement dated 29 January 2025 (Ref: MSA-VAN-202501-453; internal identifier contract_453)** and shall be read and construed in conjunction therewith.  

2.2.2 The Services under this SLA fall within the categories of Services described in **Sections 2.2.2 (Implementation and Integration Services)** and **2.2.4 (Managed Services and Support)** of the Master Agreement, with the Managed Services phase being the primary subject of this SLA.  

2.2.3 The project management and governance structure described in **Section 2.4 of the Master Agreement** shall apply to this SLA, and Vendor shall provide regular status and service level reports as further described in **Section 12.3 of the Master Agreement** and **Section 12.3 of this SLA**.

2.3 **Specific Services.**  
Vendor shall provide, at a minimum, the following Managed Services for the Supported Systems:

2.3.1 **Monitoring and Alerting.**  
(a) 24x7 monitoring of the Supported Systems for availability, performance, errors, and capacity thresholds.  
(b) Automated alerting to Vendor’s support teams upon detection of Incidents or anomalies, with classification according to Severity Levels.  
(c) Maintenance of monitoring configurations and rules to ensure accurate detection of material issues.  

2.3.2 **Incident Management and Resolution.**  
(a) End-to-end Incident management from logging through resolution and closure, including triage, root cause analysis, remediation, and communication with Client.  
(b) Adherence to response and resolution targets as set forth in **Section 12.2 of the Master Agreement** and further refined in **Article XII of this SLA**.  
(c) Classification of Incidents into P1–P4 Severity Levels, giving priority to P1 Critical Incidents (production outages or major business impact) as described in **Section 12.2 of the Master Agreement**.  
(d) Escalation to appropriate Vendor technical specialists and, where required, to third-party vendors or service providers (subject to Client’s approvals where reasonably required).

2.3.3 **Problem Management and Root Cause Analysis.**  
(a) For recurring or significant Incidents (including any P1 or P2 Incident), Vendor shall perform a root cause analysis (“RCA”) to identify underlying problems, contributing factors, and corrective/preventive actions.  
(b) Vendor shall provide written RCA reports to Client within ten (10) Business Days following resolution of any P1 Incident and within fifteen (15) Business Days for P2 Incidents, including recommended remedial actions.  
(c) Vendor shall, subject to Client’s approval as needed, implement agreed preventive measures to reduce the likelihood of recurrence.

2.3.4 **Maintenance and Patching.**  
(a) Application of security patches, bug fixes, minor version upgrades, and other maintenance activities reasonably necessary to maintain the stability, security, and performance of the Supported Systems.  
(b) Planning and scheduling of **Maintenance Windows**, with at least five (5) Business Days’ prior written notice for planned maintenance and as much prior notice as reasonably practicable for emergency maintenance.  
(c) Compliance with Client’s change management procedures (to the extent provided to Vendor in writing) and with **Article XIII (Change Management)** of the Master Agreement.

2.3.5 **Service Requests and Minor Enhancements.**  
(a) Handling of service requests relating to configuration changes, access administration, parameter adjustments, and other minor changes that do not constitute material scope changes under **Article XIII of the Master Agreement**.  
(b) Vendor shall fulfil such requests within timelines agreed by the Parties, taking into account priority and complexity, and subject to capacity and any applicable Fees described in **Article III** of this SLA.

2.3.6 **Reporting and Governance.**  
(a) Monthly Service Level and performance reports, covering Availability, Incidents by Severity, mean time to respond (MTTRsp) and mean time to resolve (MTTR), trends, and SLA Credits, as required in **Section 12.3 of the Master Agreement**.  
(b) Quarterly service review meetings (or more frequently if mutually agreed) between Vendor’s service management personnel and Client’s designated representatives, to review performance, continuous improvement initiatives, and any required adjustments.

2.4 **Deliverables.**  
In addition to the ongoing operational Services, Vendor shall provide the following Deliverables (as that term is defined in **Section 1.1.8 of the Master Agreement**):

2.4.1 **Service Run-Books and Operational Documentation** detailing procedures, standard operating processes, escalation paths, contact matrices, and recovery procedures.  

2.4.2 **Monitoring Dashboards and Configurations**, including documentation of monitored metrics and thresholds.  

2.4.3 **Monthly and Quarterly Reports** as described in Section 2.3.6.  

2.4.4 **Root Cause Analysis Reports** for certain Incidents as described above.  

All Deliverables shall conform in all material respects to the requirements specified in this SLA and any applicable SOW, consistent with **Section 2.3 of the Master Agreement**.

2.5 **Client Responsibilities.**  
The Client responsibilities set forth in **Section 2.5 of the Master Agreement** apply to this SLA. Without limitation, Client shall:

2.5.1 Provide Vendor with timely access to appropriate personnel, facilities, networks, systems, and Client Data as needed for Vendor to perform the Services.  
2.5.2 Provide accurate and timely information and approvals reasonably required by Vendor.  
2.5.3 Ensure its own systems and third-party services interfacing with the Supported Systems are properly licensed, maintained, and operated in accordance with relevant instructions.  

Vendor shall not be liable for delays or failures caused by Client’s failure to fulfil such responsibilities, in accordance with the last paragraph of **Section 2.5** of the Master Agreement, provided Vendor has given prompt written notice and uses commercially reasonable efforts to mitigate the impact.

2.6 **Service Standards.**  
Vendor shall perform the Services:

2.6.1 With due skill, care, and diligence and in accordance with generally accepted industry standards, as required in **Section 2.7 of the Master Agreement**;  
2.6.2 In compliance with Applicable Law and Client’s applicable written policies communicated in advance; and  
2.6.3 Using appropriately qualified and experienced personnel, properly supervised by Vendor.

---

## ARTICLE III – FEES AND PAYMENT TERMS

3.1 **Contract Value.**  
The Parties acknowledge that the estimated total contract value under this SLA for the Term, across all Services and Deliverables described herein, is **USD $1,926,249** (the **“SLA Contract Value”**). This amount is an estimate only and does not constitute a commitment by Client to purchase a specific volume of Services. The SLA Contract Value forms part of, and is not in addition to, the aggregate estimated contract value under the Master Agreement as referenced in **Section 3.1 of the Master Agreement (USD $1,897,079)**, it being understood that the Parties may adjust such estimates as additional SOWs and SLAs are executed.

3.2 **Fee Structure.**  
Fees under this SLA shall be structured as follows, consistent with **Section 3.2 of the Master Agreement**:

3.2.1 **Base Managed Services Fee.** A recurring fixed **monthly base fee** for Managed Services, covering monitoring, incident management, standard maintenance, reporting, and governance, as detailed in **Schedule 2 (Fee Schedule)**.  

3.2.2 **Variable Usage-Based Fees.** Additional time-and-materials (T&M) Fees for (a) approved minor enhancements and service requests exceeding a baseline number per month, (b) project work, and (c) ad hoc consulting requested by Client, billed at the daily or hourly rates set out in Schedule 2 or the relevant SOW.  

3.2.3 **Change Orders.** Any material changes to scope under **Article XIII (Change Management)** of this SLA and the Master Agreement may result in Fee adjustments, to be documented in a Change Order pursuant to **Section 13.2 of the Master Agreement**.

3.3 **Invoicing.**  
Unless otherwise specified in a related SOW:

3.3.1 Vendor shall invoice Client **monthly in arrears** for the Base Managed Services Fee and any variable Fees incurred in the preceding month, consistent with **Section 3.3.1 of the Master Agreement**.  
3.3.2 Invoices shall itemize the Services performed, applicable SOW or reference to this SLA, time period, applicable rates, and any approved expenses, in line with **Section 3.3.2 of the Master Agreement**.  
3.3.3 For T&M Services, Vendor shall maintain accurate records of time spent by its personnel and shall provide such records upon Client’s request, as per **Section 3.3.3 of the Master Agreement**.

3.4 **Payment Terms – Net 30.**  
Notwithstanding **Section 3.4 of the Master Agreement (Net 60)**, the Parties hereby agree that, for all amounts payable under this SLA:

3.4.1 All undisputed amounts shall be payable by Client within **thirty (30) calendar days** from the date of receipt of a valid invoice (**“Net 30”**).  
3.4.2 Client may withhold payment of any disputed portion of an invoice, provided that it pays the undisputed portion in accordance with this Section 3.4 and notifies Vendor of the dispute (with reasonable details) within fifteen (15) Business Days after receipt of the invoice, consistent with dispute mechanisms in **Section 3.4 of the Master Agreement**.  
3.4.3 For clarity, this Net 30 term **amends and supersedes** the Net 60 payment term in **Section 3.4 of the Master Agreement** solely with respect to the Services and Fees governed by this SLA.

3.5 **Late Payment.**  
Any undisputed amounts not paid within the applicable payment term shall accrue interest at the rate set out in **Section 3.5 of the Master Agreement**, from the due date until payment, without prejudice to Vendor’s other rights. Vendor’s right to suspend Services under the conditions stated in **Section 3.5 of the Master Agreement** shall apply to this SLA.

3.6 **Taxes.**  
All Fees are exclusive of Taxes, which shall be payable in accordance with **Section 3.6 of the Master Agreement**.

3.7 **Expenses and Reimbursement.**  
Vendor shall be entitled to reimbursement of reasonable, pre-approved out-of-pocket expenses incurred in connection with the Services, consistent with **Section 3.7 of the Master Agreement** and any additional requirements in Schedule 2.

3.8 **Set-Off.**  
Client may set off amounts owed by Vendor to Client against amounts payable to Vendor in accordance with **Section 3.8 of the Master Agreement**.

3.9 **Audits.**  
Client shall have audit rights with respect to Fees, expenses, and time records as set out in **Section 3.9 of the Master Agreement**, which shall apply mutatis mutandis to this SLA.

---

## ARTICLE IV – TERM AND TERMINATION

4.1 **Term.**  
This SLA shall commence on the **SLA Effective Date** and, unless terminated earlier in accordance with this Article IV or the Master Agreement, shall remain in force until **20 March 2027** (the **“SLA Expiration Date”**) (the **“Term”** of this SLA).

4.2 **Relationship to Master Agreement Term.**  
This SLA is contingent upon the Master Agreement remaining in force. If the Master Agreement expires on its Expiration Date (17 October 2029, as specified in **Section 4.1 of the Master Agreement**) while this SLA is still within its Term, the Parties agree that the Master Agreement shall continue to govern this SLA until the SLA’s Expiration Date, unless otherwise agreed in writing.

4.3 **Termination for Convenience.**  

4.3.1 **By Client.** In line with the low risk profile of this engagement and consistent with **Section 4.3 of the Master Agreement**, Client may terminate this SLA, in whole or in part, for convenience at any time upon not less than **thirty (30) days’** prior written notice to Vendor.  

4.3.2 **By Vendor.** Vendor may terminate this SLA for convenience only upon not less than **sixty (60) days’** prior written notice to Client, provided that no active SOW specifically dependent on this SLA would thereby be rendered incapable of continued performance, unless Client agrees otherwise in writing, consistent with **Section 4.3 of the Master Agreement**.

4.4 **Termination for Cause.**  
Either Party may terminate this SLA immediately upon written notice to the other Party if:

4.4.1 The other Party commits a material breach of this SLA or the corresponding provisions of the Master Agreement (including chronic Service Level failures as defined in **Section 12.5 of the Master Agreement** and adopted in **Section 12.5 of this SLA**), which, if capable of remedy, is not remedied within thirty (30) days of written notice specifying the breach and requiring its remedy; or  

4.4.2 The other Party becomes insolvent or subject to insolvency events described in **Section 4.4.2 of the Master Agreement**.

4.5 **Effect of Termination of Master Agreement.**  

4.5.1 If the Master Agreement is terminated in its entirety for any reason, this SLA shall automatically terminate on the effective date of such termination, without the need for further notice, subject to any survival provisions herein and in the Master Agreement.  

4.5.2 If the Master Agreement terminates only in respect of particular SOW(s) not related to this SLA, this SLA shall remain in force unless expressly terminated in the termination notice or by mutual agreement.

4.6 **Effect of Termination of this SLA.**  
Upon expiration or termination of this SLA for any reason:

4.6.1 Vendor shall cease performance of the Services governed by this SLA and take reasonable steps to protect Client’s interests, including preservation of Client Data, in line with **Section 4.6.1 of the Master Agreement**.  
4.6.2 Client shall pay Vendor for Services performed and Deliverables accepted (or deemed accepted) up to the effective date of termination, together with approved unreimbursed expenses, subject to set-off and dispute rights, consistent with **Section 4.6.2 of the Master Agreement**.  
4.6.3 Except where termination is for cause by Client due to Vendor’s material breach, Vendor shall be entitled to payment for work-in-progress and authorized third-party charges as described in **Section 4.6.3 of the Master Agreement**.  
4.6.4 Upon Client’s written request, Vendor shall provide **Transition Assistance** for up to ninety (90) days at mutually agreed reasonable rates, consistent with **Section 4.6.4 of the Master Agreement**.  
4.6.5 Each Party shall return or destroy the other’s Confidential Information in accordance with **Section 5.4 of the Master Agreement** and **Article V** of this SLA.

4.7 **Survival.**  
Those provisions of this SLA which by their nature are intended to survive termination or expiration (including but not limited to Articles V, VI, VII, VIII, IX, XI, XIV, XV, XVI, and Sections 3.5, 3.6, 3.9, 4.5, and 4.6) shall so survive, in addition to the survival provisions in **Section 4.7 of the Master Agreement**.

---

## ARTICLE V – CONFIDENTIALITY

5.1 **Reference to Master Agreement.**  
The Parties acknowledge and agree that all confidentiality obligations set forth in **Article V (Confidentiality)** of the Master Agreement apply in full to this SLA, including to all Service-related information, Client Data, and Vendor technical information exchanged hereunder.

5.2 **SLA Confidential Information.**  
Without limiting **Section 5.1**:

5.2.1 **Client Confidential Information** shall include, without limitation, non-public information about Client’s systems, business processes, security posture, incident reports, Client Data, and any other information disclosed in connection with the Services.  
5.2.2 **Vendor Confidential Information** shall include, without limitation, proprietary methodologies, tools, monitoring configurations, internal procedures, and financial or pricing information disclosed to Client.  
5.2.3 Service level performance data, RCA reports, and service reports shall be deemed Confidential Information of both Parties.

5.3 **Obligations.**  
The Receiving Party shall comply with the obligations in **Section 5.3 of the Master Agreement**, including using Confidential Information solely to exercise its rights and perform its obligations under this SLA and the Master Agreement, employing at least reasonable care to protect such information, and limiting disclosure to those with a need to know who are bound by confidentiality obligations.

5.4 **Exceptions, Return, and Destruction.**  
The exceptions in **Section 5.2 of the Master Agreement** (public domain, prior knowledge, third-party disclosure, independent development) apply. On termination or expiration, return and destruction obligations shall follow **Section 5.4 of the Master Agreement**, including retention only as required by law or in backup systems.

5.5 **Compelled Disclosure and Survival.**  
Compelled disclosure shall follow **Section 5.5** of the Master Agreement. Confidentiality obligations shall survive for **five (5) years** from termination or expiration of this SLA, as in **Section 5.6 of the Master Agreement**, and trade secrets shall be protected for so long as they remain trade secrets.

---

## ARTICLE VI – INTELLECTUAL PROPERTY RIGHTS

6.1 **Incorporation of Master Agreement Terms.**  
The Parties acknowledge that **Article VI (Intellectual Property Rights)** of the Master Agreement governs ownership and licensing of Client Background IP, Vendor Background IP, Vendor Materials, Deliverables, and Third Party Materials. This SLA does not alter such allocations but applies them to the Deliverables and Services described herein.

6.2 **Ownership of Deliverables.**  
All Deliverables created specifically under this SLA shall be treated as **“Deliverables”** under **Section 1.1.8 and Article VI of the Master Agreement**. Subject to Sections 6.2 and 6.3 of the Master Agreement:

6.2.1 Client shall own all IPR in Deliverables (excluding Vendor Background IP and Vendor Materials embedded therein), subject to payment in full of all applicable Fees.  
6.2.2 Vendor retains ownership of Vendor Background IP and Vendor Materials as per **Sections 6.2 and 6.3 of the Master Agreement**.

6.3 **Licenses.**  
Vendor grants Client the licenses described in **Section 6.3 (for Vendor Materials)** and **Section 6.4 (for Vendor Background IP embedded in Deliverables)** of the Master Agreement, sufficient for Client to make full internal use of the Deliverables and Services for its internal business purposes.

6.4 **Third Party Materials.**  
Where Third Party Materials are integrated into Deliverables or Services, Vendor shall identify them and applicable license terms in Schedule 1 or an SOW, consistent with **Section 6.5 of the Master Agreement**.

6.5 **Residual Knowledge.**  
Vendor’s rights to use residual knowledge are as described in **Section 6.6 of the Master Agreement**, subject to confidentiality obligations.

6.6 **No Implied Licenses; Infringement Mitigation.**  
No implied licenses are granted beyond those expressly set forth herein and in the Master Agreement (see **Section 6.7**). IP infringement mitigation obligations in **Section 6.8 of the Master Agreement** apply to any infringement allegations arising from Deliverables or Services under this SLA.

---

## ARTICLE VII – REPRESENTATIONS AND WARRANTIES

7.1 **Mutual Representations.**  
Each Party reaffirms the mutual representations in **Section 7.1 of the Master Agreement**, including due organization, authority to enter into this SLA, and non-conflict with other obligations.

7.2 **Vendor Warranties – Services.**  
In addition to the warranties in **Section 7.2 of the Master Agreement**, Vendor warrants that:

7.2.1 The Managed Services will be performed in accordance with this SLA, including the Service Levels in **Article XII**, using appropriately skilled personnel; and  
7.2.2 For the Term of this SLA, the Services will materially conform to the description in **Article II** and applicable Schedules, provided that Client operates the Supported Systems in accordance with Vendor’s reasonable instructions.

7.3 **Client Warranties.**  
Client reaffirms the warranties in **Section 7.3 of the Master Agreement**, including its rights to provide Client Data and compliance with Applicable Law.

7.4 **Disclaimer.**  
Except as expressly provided in the Master Agreement and this SLA, all other warranties are disclaimed as set forth in **Section 7.4 of the Master Agreement**.

---

## ARTICLE VIII – INDEMNIFICATION

8.1 **Vendor Indemnity.**  
Vendor’s indemnification obligations set forth in **Section 8.1 of the Master Agreement** apply to Services and Deliverables under this SLA, including:

8.1.1 Indemnity for Vendor’s gross negligence or wilful misconduct in performing the Managed Services;  
8.1.2 IP infringement claims relating to Deliverables and Services (excluding Client Background IP and Third Party Materials supplied by Client); and  
8.1.3 Personal Data breaches arising from Vendor’s material breach of Article XI of the Master Agreement and this SLA.

8.2 **Client Indemnity.**  
Client’s indemnity obligations in **Section 8.2 of the Master Agreement** apply, including indemnity for Client’s gross negligence or unlawful use of the Services and any IP infringement claims relating to Client Data or Client Background IP.

8.3 **Exclusions and Procedure.**  
Exclusions from Vendor’s IP indemnity in **Section 8.3** and the indemnification procedures in **Section 8.4 of the Master Agreement** apply in full to this SLA.

8.4 **Exclusive Remedies.**  
The indemnification obligations, together with Vendor’s IP mitigation obligations under **Section 6.8 of the Master Agreement**, are the exclusive remedies for related Claims, subject to Article IX and **Section 8.5 of the Master Agreement**.

---

## ARTICLE IX – LIMITATION OF LIABILITY

9.1 **Cap on Liability.**  
Subject to the exceptions in **Section 9.3 of the Master Agreement** (which also apply here):

9.1.1 The total aggregate liability of each Party arising out of or in connection with this SLA and the Services hereunder (whether in contract, tort, or otherwise) shall not exceed an amount equal to **two (2) times** the total Fees paid or payable by Client to Vendor under this SLA during the **twelve (12) months preceding** the event giving rise to such liability, consistent with **Section 9.1 of the Master Agreement**.

9.2 **Exclusion of Certain Damages.**  
Neither Party shall be liable to the other for any excluded categories of damages listed in **Section 9.2 of the Master Agreement**, including loss of profits, loss of business, and indirect or consequential damages, subject to Section 9.3.

9.3 **Exceptions.**  
The exceptions set out in **Section 9.3 of the Master Agreement** apply, including exceptions for death or personal injury, fraud, certain indemnification obligations, breaches of confidentiality, and other liabilities that cannot be limited by law.

9.4 **Mitigation.**  
Each Party shall use reasonable efforts to mitigate Losses, as required in **Section 9.4 of the Master Agreement**.

---

## ARTICLE X – INSURANCE

10.1 **Vendor Insurance.**  
Vendor shall maintain insurance coverage in accordance with **Article X of the Master Agreement**, including public/general liability, professional indemnity, cyber and data security, and employer’s liability insurance, in the specified minimum amounts.

10.2 **Certificates and Primary Coverage.**  
Upon request, Vendor shall provide certificates of insurance evidencing such coverage and notify Client of any material change, cancellation, or non-renewal, as required under **Sections 10.2 and 10.3 of the Master Agreement**.

---

## ARTICLE XI – DATA PROTECTION AND PRIVACY

11.1 **Applicability of Master Agreement.**  
The Parties shall comply with **Article XI (Data Protection and Privacy)** of the Master Agreement in connection with any processing of Personal Data under this SLA.

11.2 **Roles of the Parties.**  
Client shall be the controller and Vendor the processor (or equivalent terms) as described in **Section 11.2 of the Master Agreement**, except where an SOW specifies that Vendor acts as an independent controller for certain limited activities.

11.3 **Processing, Security, and Sub-Processors.**  
Vendor’s obligations regarding processing instructions, security measures, sub-processor engagement, international transfers, data subject rights, and audits shall be as set forth in **Sections 11.3–11.10 of the Master Agreement**.

11.4 **Data Breach Notification.**  
In the event of a Personal Data breach affecting Personal Data processed under this SLA, Vendor shall notify Client in accordance with **Section 11.8 of the Master Agreement**, including within 72 hours (where feasible) and with the required information.

11.5 **Retention and Deletion.**  
Upon termination or expiration of this SLA or on Client’s request, Vendor shall delete or return Personal Data as set forth in **Section 11.9 of the Master Agreement**.

---

## ARTICLE XII – SERVICE LEVEL AGREEMENTS

12.1 **Service Availability.**  
For the Managed Services and Supported Systems under this SLA, Vendor shall use commercially reasonable efforts to ensure that the production instances of the Supported Systems are available no less than **99.9%** of the time during each Monthly Measurement Period, calculated in accordance with the formula and exclusions referenced in **Section 12.1 of the Master Agreement** and further specified in Schedule 1. Exclusions shall include:

12.1.1 Scheduled Maintenance Windows agreed in advance;  
12.1.2 Emergency maintenance (with reasonable efforts to provide prior notice);  
12.1.3 Downtime caused by Force Majeure Events (as defined in **Section 15.1 of the Master Agreement**); and  
12.1.4 Downtime attributable to Client systems, third-party services under Client’s control, or Client’s misuse of the Services.

12.2 **Incident Response and Resolution Targets.**  
Vendor shall meet the following targets, which build upon **Section 12.2 of the Master Agreement**:

- **Critical Severity (P1)** – Production outage or major business impact:  
  - Initial Response: within **1 hour**, 24x7.  
  - Target Resolution / Workaround: within **4 hours** of Incident logging.  

- **High Severity (P2)** – Significant business impact but not complete outage:  
  - Initial Response: within **2 hours** during Business Days.  
  - Target Resolution / Workaround: within **8 Business Hours**.  

- **Medium Severity (P3)** – Limited business impact or partial degradation:  
  - Initial Response: within **4 Business Hours**.  
  - Target Resolution: within **3 Business Days**.  

- **Low Severity (P4)** – Minor issues or information requests:  
  - Initial Response: within **1 Business Day**.  
  - Target Resolution: typically within **10 Business Days**, or as mutually agreed.

12.3 **Monitoring and Reporting.**  
Vendor shall:

12.3.1 Continuously monitor Service Availability and Incident metrics;  
12.3.2 Provide **monthly Service Level reports** to Client, as required by **Section 12.3 of the Master Agreement**, detailing performance against Service Levels, major Incidents, RCA outcomes, planned improvements, and any SLA Credits;  
12.3.3 Participate in service review meetings as described in Section 2.3.6 of this SLA.

12.4 **SLA Credits.**  
If Vendor fails to meet the Service Levels, Vendor shall provide Client with **SLA Credits** in accordance with **Section 12.4 of the Master Agreement** and the more specific calculations set out in Schedule 2. SLA Credits:

12.4.1 Shall be applied against future Fees payable under this SLA;  
12.4.2 Shall not be redeemable for cash;  
12.4.3 Shall constitute Client’s sole and exclusive **monetary** remedy for Service Level failures, without prejudice to Client’s rights to terminate for chronic failure under Section 12.5 and **Section 4.4** of this SLA and the Master Agreement.

12.5 **Chronic Failure.**  
If Vendor fails to meet the same critical Service Level (e.g., P1 resolution or Availability) in three (3) consecutive calendar months, or fails to meet any critical Service Level in five (5) or more calendar months in any rolling twelve (12) month period, such failure shall constitute a **material breach**, giving Client the right to terminate this SLA (and any dependent SOWs) for cause under **Section 4.4** of this SLA and **Section 4.4 of the Master Agreement**, as referenced in **Section 12.5 of the Master Agreement**.

---

## ARTICLE XIII – CHANGE MANAGEMENT

13.1 **Change Requests and Orders.**  
Change management for this SLA, including changes to scope, Service Levels, Supported Systems, or Fee structure, shall follow **Article XIII (Change Management)** of the Master Agreement. Either Party may submit a **Change Request** in writing, and Vendor will respond with a **Change Order** detailing impacts on scope, timelines, fees, and Service Levels, as described in **Section 13.2 of the Master Agreement**.

13.2 **Approval and Urgent Changes.**  
No Change Request is effective unless documented in a Change Order signed by both Parties, as provided in **Section 13.3 of the Master Agreement**. The Parties may agree to expedited or provisional approvals for urgent changes (e.g., security patches) via email between authorized representatives, with formal documentation to follow, consistent with **Section 13.4 of the Master Agreement**.

---

## ARTICLE XIV – DISPUTE RESOLUTION

14.1 **Informal Resolution and Escalation.**  
Dispute resolution procedures in **Article XIV of the Master Agreement** apply to any Dispute arising from or relating to this SLA. The Parties shall seek to resolve Disputes through informal negotiations between project managers, followed by escalation to senior executives as described in **Sections 14.1 and 14.2 of the Master Agreement**.

14.2 **Mediation and Litigation.**  
If unresolved, either Party may propose mediation (per **Section 14.3 of the Master Agreement**) and, failing resolution, may submit the Dispute to the exclusive jurisdiction of the courts of England and Wales in accordance with **Section 14.4** and **Section 16.10 of the Master Agreement**.

---

## ARTICLE XV – FORCE MAJEURE

15.1 **Force Majeure Events.**  
The definition and consequences of Force Majeure Events in **Article XV of the Master Agreement** apply to this SLA. In particular, the Parties’ obligations are suspended to the extent affected by a Force Majeure Event, except for monetary payment obligations (subject to system operability) as in **Section 15.3 of the Master Agreement**.

15.2 **Extended Force Majeure.**  
If a Force Majeure Event continues for more than sixty (60) consecutive days and materially affects the Services under this SLA, either Party may terminate the affected portions of this SLA for convenience upon fifteen (15) days’ written notice, consistent with **Section 15.4 of the Master Agreement**.

---

## ARTICLE XVI – GENERAL PROVISIONS

16.1 **Reference to Master/Parent Agreement.**  
This Service Level Agreement **is executed under and subject to the terms of Master Services Agreement reference number MSA-VAN-202501-453 (internal identifier contract_453)**. In the event of any conflict between the terms of this SLA and the terms of the Master Agreement, the terms of the Master Agreement shall prevail, except where this SLA expressly and specifically states that it amends a particular provision of the Master Agreement (e.g., the Net 30 payment term in Section 3.4 above).

16.2 **Entire Agreement; Relationship to Master Agreement.**  
This SLA, together with the Master Agreement and any SOWs referencing this SLA, constitutes the complete and exclusive understanding between the Parties with respect to the subject matter of the Services and Service Levels described herein and supersedes all prior or contemporaneous agreements or understandings relating thereto. It is expressly acknowledged that **Section 16.1 of the Master Agreement** remains in full force and effect for matters not expressly governed herein.

16.3 **Amendments.**  
No amendment or modification of this SLA shall be effective unless in writing and signed by authorized representatives of both Parties, consistent with **Section 16.2 of the Master Agreement**. Email exchanges shall not constitute an amendment unless explicitly stated and electronically signed as permitted by Applicable Law.

16.4 **Severability.**  
If any provision of this SLA is held to be invalid, illegal, or unenforceable, such provision shall be modified to the minimum extent necessary to make it enforceable while preserving the Parties’ intent, and the remaining provisions shall remain in full force, as contemplated in **Section 16.3 of the Master Agreement**.

16.5 **Waiver.**  
No failure or delay by either Party in exercising any right under this SLA shall operate as a waiver of such right, nor shall any single or partial exercise preclude further exercise, consistent with **Section 16.4 of the Master Agreement**.

16.6 **Notices.**  
All notices under this SLA shall be in writing and delivered in accordance with the notice provisions of the Master Agreement, directed to the following addresses (or such other addresses as a Party may designate in writing):

**For Client (Contoso Enterprises):**  
100 Bishopsgate  
London EC2N 4AG  
United Kingdom  
Attn: Legal Department / Vendor Management  

**For Vendor (Vanguard Solutions):**  
200 Aldersgate Street  
London EC1A 4HD  
United Kingdom  
Attn: Legal Department / Account Director  

16.7 **Assignment.**  
Assignment restrictions in **Section 16.5 of the Master Agreement** apply to this SLA. Neither Party may assign this SLA except as permitted under the Master Agreement.

16.8 **Independent Contractors.**  
The relationship of the Parties is that of independent contractors, as acknowledged in **Section 16.6 of the Master Agreement**. Nothing in this SLA shall be construed as creating an agency, partnership, or joint venture.

16.9 **Governing Law and Jurisdiction.**  
This SLA shall be governed by and construed in accordance with the laws of the United Kingdom (specifically, the laws of England and Wales), and the Parties submit to the exclusive jurisdiction of the courts of England and Wales, consistent with **Section 16.10 of the Master Agreement**.

16.10 **Counterparts; Electronic Signatures.**  
This SLA may be executed in one or more counterparts, each of which shall be deemed an original, but all of which together shall constitute one and the same instrument, in accordance with **Section 16.8 of the Master Agreement**. Signatures transmitted electronically (including PDF and electronic signature platforms) shall be deemed original.

---

## SIGNATURES

IN WITNESS WHEREOF, the Parties hereto have caused this Service Level Agreement, Contract Reference Number **SLA-VAN-202501-512**, to be executed by their duly authorized representatives as of the SLA Effective Date.

**Executed pursuant to MSA-VAN-202501-453 (internal identifier contract_453).**

---

### For Contoso Enterprises  
(“Client” or “Company”)

Name: ________________________________  
Title: _________________________________  

Signature: ____________________________  

Date: ________________________________  

Witness (if required): __________________________  
Name of Witness: _______________________  
Address of Witness: _____________________  

---

### For Vanguard Solutions  
(“Vendor” or “Service Provider”)

Name: ________________________________  
Title: _________________________________  

Signature: ____________________________  

Date: ________________________________  

Witness (if required): __________________________  
Name of Witness: _______________________  
Address of Witness: _____________________  

---

**[End of Service Level Agreement – Contract Reference Number: SLA-VAN-202501-512]**