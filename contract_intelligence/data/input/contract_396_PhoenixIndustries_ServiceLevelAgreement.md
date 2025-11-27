# SERVICE LEVEL AGREEMENT  
**Contract Reference Number: SLA-PHO-202504-396**

---

## PREAMBLE

This SERVICE LEVEL AGREEMENT (this **“SLA”**), reference number **SLA-PHO-202504-396**, is made and entered into as of **18 December 2025** (the **“SLA Effective Date”**),

**BETWEEN:**

**Contoso Enterprises**  
a company organized and existing under the laws of the United Kingdom  
with its principal place of business at:  
Contoso Enterprises  
1 Enterprise Park  
London EC2N 2DB  
United Kingdom  
(**“Contoso”**, the **“Client”** or the **“Company”**),

**AND:**

**Phoenix Industries**  
a company organized and existing under the laws of the United Kingdom  
with its principal place of business at:  
Phoenix Industries  
88 Phoenix Way  
Birmingham B1 1AA  
United Kingdom  
(**“Phoenix”**, the **“Vendor”** or the **“Service Provider”**),

Contoso and Phoenix may hereinafter be referred to individually as a **“Party”** and collectively as the **“Parties”**.

This SLA is entered into **pursuant to and in supplementation of** that certain **Master Services Agreement**, reference number **MSA-PHO-202504-365**, dated **29 April 2025**, between the same Parties, identified by the Client internally as **“contract_365”** (the **“Master Agreement”** or **“Parent Agreement”**).

---

## RECITALS

WHEREAS, the Parties entered into the Master Services Agreement, reference number **MSA-PHO-202504-365** (contract_365), dated **29 April 2025** (the **“MSA Effective Date”**), pursuant to which Phoenix agreed to provide various professional, technical, implementation, managed services and related Deliverables to Contoso, as more particularly described in **Article II** (Scope of Services / Work) of the Master Agreement;

WHEREAS, **Article XII (Service Level Agreements (SLAs))** of the Master Agreement contemplates that detailed service levels, performance metrics, uptime targets, response times, remedies and associated governance will be set forth in one or more separate Service Level Agreements or Statements of Work which reference and are governed by the Master Agreement;

WHEREAS, the Parties now desire to establish detailed, high-availability managed service and support commitments, metrics, and remedies with respect to Phoenix’s provision of hosting, application management, support, monitoring, and related managed services, and to allocate additional Fees for such services within the broader contract value framework set forth in **Section 3.1** of the Master Agreement;

WHEREAS, the Parties acknowledge and agree that this SLA is intended to address a **high risk** engagement profile (as compared with the **“medium” risk level** referenced in **Section 7.5** of the Master Agreement), involving business-critical and time-sensitive systems, and that, accordingly, the Parties are willing to accept a more aggressive allocation of risk in favour of the Service Provider than that reflected in **Article IX (Limitation of Liability)** of the Master Agreement;

NOW, THEREFORE, in consideration of the mutual covenants, promises, and undertakings set forth herein and in the Master Agreement, and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the Parties hereby agree as follows:

---

## ARTICLE I – DEFINITIONS

1.1 **Defined Terms.** Capitalized terms used but not otherwise defined in this SLA shall have the meanings ascribed to such terms in **Article I (Definitions)** of the Master Agreement **MSA-PHO-202504-365 (contract_365)**. For purposes of this SLA, the following terms shall have the meanings set forth below. Defined terms may be used in the singular or plural, as the context requires.

1.1.1 **“Applicable Law”** has the meaning given in **Section 1.1.3** of the Master Agreement and includes, without limitation, UK GDPR and the Data Protection Act 2018.

1.1.2 **“Business Day”** has the meaning given in **Section 1.1.4** of the Master Agreement and shall be used for determining response and resolution times herein.

1.1.3 **“Change Order”** has the meaning given in **Section 1.1.5** of the Master Agreement and refers to a written document executed by the Parties to modify scope, Service Levels, or Fees under this SLA in accordance with **Article XIII** hereof and **Article XIII (Change Management)** of the Master Agreement.

1.1.4 **“Client Environment”** means the combination of hardware, networks, software, configurations, third‑party systems, and connectivity under the direct control of the Client (or its third‑party providers other than the Service Provider) that interact with or are required to access the Managed Services.

1.1.5 **“Downtime”** means the total accumulated minutes, within a given calendar month, during which the Production Service is not available to the Client, excluding: (a) Scheduled Maintenance; (b) Emergency Maintenance within the thresholds specified herein; (c) downtime attributable to a **Force Majeure Event** (as defined in **Section 15.1** of the Master Agreement and reiterated in **Article XV** of this SLA); (d) issues caused by the Client Environment, Client Materials (as defined in **Section 1.1.6** of the Master Agreement), or unauthorised modifications by the Client; and (e) downtime resulting from Client’s breach of this SLA or the Master Agreement.

1.1.6 **“Emergency Maintenance”** means unscheduled maintenance performed by the Service Provider that is necessary to address critical security vulnerabilities, system instability, or imminent failure, and which cannot reasonably be deferred to the next Scheduled Maintenance window.

1.1.7 **“Incident”** means any event that is not part of the standard operation of the Managed Services and that causes, or may cause, an interruption to, or a reduction in the quality of, the Managed Services.

1.1.8 **“Managed Services”** means the ongoing, business‑critical hosting, application management, monitoring, Level 1–3 support, incident management, problem management, capacity management, and related services provided by the Service Provider under this SLA, as further described in **Article II**.

1.1.9 **“Master Agreement” or “Parent Agreement”** means the Master Services Agreement, reference number **MSA-PHO-202504-365** (internal Client identifier **contract_365**), dated 29 April 2025, between the Parties, including all Statements of Work and Change Orders executed thereunder, as may be amended from time to time in accordance with **Article XIII** and **Article XVI** of the Master Agreement.

1.1.10 **“Monthly Service Fees”** means the recurring monthly Fees payable by the Client to the Service Provider for the Managed Services under this SLA, as specified in **Article III**.

1.1.11 **“Planned Go-Live Date”** means, in relation to each production environment governed by this SLA, the date specified in a Statement of Work or Project Plan (each as defined in **Section 1.1.15** of the Master Agreement) upon which the system is first made available for production use by end users.

1.1.12 **“Priority Level”** means the categorisation of Incidents and Service Requests (Priority 1–4) in accordance with **Section 12.3** of the Master Agreement and **Section 12.3** of this SLA, used to determine response and resolution targets.

1.1.13 **“Production Service”** means the specific software platforms, integrations, and infrastructure components described in **Annex 1 (Service Description)** to this SLA, which are hosted, supported, and maintained by the Service Provider and used by the Client in a production (live) environment.

1.1.14 **“Service Levels”** or **“SLA Metrics”** means the performance metrics, uptime targets, response and resolution times, capacity thresholds, and other defined standards set out in **Article XII** of this SLA, which supplement and, where expressly stated, amend or replace the general Service Levels in **Article XII** of the Master Agreement.

1.1.15 **“Service Window”** means the period during which the Managed Services are expected to be available to end users, being 24 hours per day, 7 days per week, 365 days per year, except during Scheduled Maintenance and other permitted Downtime as set forth herein.

1.1.16 **“Scheduled Maintenance”** means planned maintenance windows for upgrades, patches, and other changes to the Production Service, notified to the Client in advance in accordance with **Section 12.2** of this SLA.

1.1.17 **“Service Credit”** means the credit against Monthly Service Fees that the Client may be entitled to receive as a remedy for failure by the Service Provider to meet specified Service Levels, as defined in **Section 12.6** of this SLA and supplementing **Section 12.4** of the Master Agreement.

1.1.18 **“Supported Hours”** means the hours during which the Service Provider provides Incident management and support as set forth in **Section 2.4.4** of this SLA (including 24x7 coverage for Priority 1 and Priority 2 Incidents).

1.1.19 **“Transition Services”** means any services required to transition the Managed Services to another provider or back to the Client upon expiration or termination of this SLA, as further described in **Section 4.6**.

1.1.20 **“Upgrade”** means a materially new version of software, platform, or infrastructure delivering significant new features or capabilities, as opposed to minor patches or bug fixes.

---

## ARTICLE II – SCOPE OF SERVICES / WORK

2.1 **Relationship to Master Agreement.**  

2.1.1 This **Article II** is to be read in conjunction with **Article II (Scope of Services / Work)** of the Master Agreement. Pursuant to **Section 2.1** of the Master Agreement, this SLA serves as a detailed service description and service level specification for certain **Managed Services** that Phoenix shall perform for Contoso.  

2.1.2 In the event of any conflict between this **Article II** and **Article II** of the Master Agreement, and solely with respect to the Managed Services described herein, the provisions of this SLA shall prevail, except where the Master Agreement expressly provides that its terms are non‑variable.

2.2 **Overview of Managed Services.**  

The Service Provider shall provide end‑to‑end Managed Services to support the Client’s business‑critical commercial and enterprise systems as follows:

2.2.1 **Hosting and Infrastructure Management.**  
(a) Provision, configuration, and management of secure, resilient hosting environments (cloud and/or hybrid) for the Production Service, including compute, storage, networking, security groups, firewall rules, and load balancing.  
(b) Capacity planning, performance tuning, and scaling activities to meet agreed capacity and performance thresholds, ensuring resilience consistent with the **99.95%** monthly uptime commitment set forth in **Section 12.1** of this SLA.  
(c) Implementation and maintenance of monitoring and alerting systems (infrastructure and application level), including collection of metrics and logs for SLA reporting under **Section 12.7**.

2.2.2 **Application Management and Support.**  
(a) Ongoing administration, configuration, and optimisation of the Client’s core commercial platforms, integration components, APIs, and data flows as detailed in Annex 1.  
(b) Management of application releases, deployment pipelines, version control, and rollback procedures in accordance with a release management process agreed in writing between the Parties.  
(c) Provision of Level 1, Level 2, and Level 3 support services as contemplated by **Section 2.2.4** of the Master Agreement, including Incident triage, diagnosis, workaround identification, and permanent fix implementation.

2.2.3 **Integration and Data Services.**  
(a) Monitoring and support of system integrations between the Production Service and third‑party systems (including, without limitation, CRM, ERP, billing, and external data providers), subject to the Client’s provision of necessary third‑party consents and licences under **Section 2.5.3** of the Master Agreement.  
(b) Daily verification of data imports, exports, and synchronisation jobs, with proactive resolution of recurring failures and escalations to Client and third‑party providers where root cause lies outside the Service Provider’s reasonable control.  
(c) Maintenance of integration documentation, data mapping, and interface specifications.

2.2.4 **Security Management.**  
(a) Implementation and operation of security controls consistent with industry best practices for high‑risk environments, including access controls, role‑based permissions, encryption in transit and at rest, security event monitoring, and incident response.  
(b) Regular application of security patches and updates in accordance with a security patch management policy agreed in writing with the Client, taking into account the sensitivities of the Client’s production schedules.  
(c) Cooperation with the Client’s security team in relation to security audits and penetration testing, subject to agreed test windows and appropriate safeguards.

2.2.5 **Service Desk and Incident Management.**  
(a) Provision of a single point of contact (SPOC) for Incident reporting and Service Requests by the Client, via telephone, email, and ticketing portal.  
(b) Application of the priority classifications and response targets set out in **Section 12.3** and **Section 12.4** of this SLA.  
(c) Root cause analysis (RCA) for all Priority 1 and Priority 2 Incidents and other Incidents as reasonably requested by the Client, with RCA reports delivered within the timeframes set out in **Section 12.5.3**.

2.2.6 **Change and Release Management.**  
(a) Execution of standard, emergency, and major changes in accordance with the change management procedures set forth in **Article XIII (Change Management)** of the Master Agreement and **Article XIII** of this SLA.  
(b) Participation in the Client’s Change Advisory Board (CAB) meetings (where applicable) and preparation of Change records for all non‑routine changes to the Production Service.  
(c) Coordination of releases with the Client’s stakeholders, including communications, deployment plans, back‑out plans, and post‑implementation reviews.

2.2.7 **Reporting and Governance.**  
(a) Provision of monthly service reports summarising SLA performance, Incidents, Service Requests, planned and completed changes, capacity and utilisation trends, and security events, consistent with **Section 12.5** of the Master Agreement and **Section 12.7** of this SLA.  
(b) Participation in monthly and quarterly service review meetings to review performance, issues, risks, and continuous improvement initiatives.  
(c) Maintenance of a risk and issue log, with escalation procedures aligned with **Article XIV (Dispute Resolution)** of the Master Agreement.

2.3 **Deliverables and Milestones.**  

2.3.1 In addition to the ongoing Managed Services, the Service Provider shall deliver the following key Deliverables during the Term of this SLA:

(a) **Service Operational Runbook** – documenting operational procedures, escalation paths, standard operating procedures, backup and recovery processes, security controls, and contact details.  
(b) **Monitoring and Alerting Configuration** – documented thresholds, dashboards, and alert routing logic.  
(c) **Disaster Recovery Plan** – including RPO (Recovery Point Objective) and RTO (Recovery Time Objective) targets agreed with the Client, and alignment with the uptime and recovery expectations under **Article XII**.  
(d) **Capacity and Performance Baseline Report** – delivered within ninety (90) days of the SLA Effective Date, with annual updates thereafter.  

2.3.2 The Parties shall define any additional project‑specific Deliverables, along with associated acceptance criteria and Project Plans, in Statements of Work executed under the Master Agreement. Acceptance of those Deliverables shall follow the process outlined in **Section 2.3** of the Master Agreement, except where explicitly modified by such SOW.

2.4 **Performance Standards.**  

2.4.1 The Service Provider shall perform the Managed Services in accordance with the standards set forth in **Section 2.4 (Performance Standards)** of the Master Agreement and in this SLA, including:  
(a) professional and workmanlike performance;  
(b) due skill, care, and diligence;  
(c) adherence to generally accepted industry standards and best practices for high‑availability hosting and managed services;  
(d) compliance with Applicable Law; and  
(e) adherence to the Service Levels in **Article XII** of this SLA.

2.4.2 The Service Provider shall designate a **Service Delivery Manager** (SDM) as the primary operational contact for coordination and communications with the Client’s appointed service owner and project manager as referenced in **Section 2.5.2** of the Master Agreement.

2.4.3 The Service Provider shall use commercially reasonable efforts to meet all milestones and Service Levels. Any anticipated failure to meet a Service Level shall be promptly notified to the Client in writing, including: (a) the nature and cause of the risk; (b) any mitigating actions already taken; and (c) a proposed remediation plan.

2.4.4 **Support Hours.**  
(a) Priority 1 (Critical) and Priority 2 (High) Incidents: **24x7** support, including weekends and public holidays.  
(b) Priority 3 (Medium) and Priority 4 (Low) Incidents and Service Requests: support during standard Business Hours (09:00–18:00 UK time, Monday to Friday, excluding UK public holidays), unless otherwise agreed in a SOW.

2.5 **Client Responsibilities.**  

The Client shall perform the responsibilities set forth in **Section 2.5 (Client Responsibilities)** of the Master Agreement and the following additional obligations specific to this SLA:

2.5.1 Ensure that all necessary network connectivity, VPNs, and access credentials to the Client Environment are provisioned and maintained, and that access is granted to the Service Provider in a timely manner.

2.5.2 Provide timely approvals for Changes, cab requests, and maintenance windows proposed by the Service Provider, particularly in relation to security patches and critical system updates.

2.5.3 Ensure that third‑party vendors and systems interfacing with the Production Service are available to support troubleshooting when integrations or data flows are affected by issues outside the Service Provider’s domain.

2.5.4 Designate, in writing, a primary escalation contact and backup for Incident and Change escalation.

2.5.5 Acknowledge that failure by the Client to perform its responsibilities may impact the Service Provider’s ability to meet Service Levels, and such failures shall be considered valid exclusions from Downtime and SLA calculations.

2.6 **Subcontracting.**  

The Service Provider may utilise Subcontractors in accordance with **Section 2.6 (Subcontracting)** of the Master Agreement to perform portions of the Managed Services (for example, specialist data centre providers or security monitoring partners), provided that the Service Provider remains fully responsible for their acts and omissions.

2.7 **Non‑Exclusivity.**  

As provided in **Section 2.7 (Non‑Exclusivity)** of the Master Agreement, the Client remains free to engage other service providers for services that may overlap or be adjacent to the Managed Services, provided such engagements do not interfere with the Service Provider’s ability to meet its obligations under this SLA.

---

## ARTICLE III – FEES AND PAYMENT TERMS

3.1 **Contract Value.**  

3.1.1 The total aggregate value allocated to the Managed Services under this SLA shall be **Three Million Two Hundred Forty‑Nine Thousand Eight Hundred Fifty‑Four United States Dollars (US$3,249,854)** (**the “SLA Contract Value”**).

3.1.2 The Parties acknowledge that, for purposes of the broader commercial relationship, the aggregate contract value under the Master Agreement (**US$856,270** as stated in **Section 3.1** of the Master Agreement) may be amended or increased by written agreement of the Parties, including by Change Order, to reflect the SLA Contract Value and any additional SOWs executed hereunder.

3.2 **Fee Structure.**  

3.2.1 **Recurring Managed Service Fees.**  
(a) The SLA Contract Value shall be apportioned into **Monthly Service Fees** covering hosting, application management, support, monitoring, and related activities.  
(b) Unless otherwise specified in a SOW, the Monthly Service Fees shall be calculated by dividing the SLA Contract Value by the number of months in the Initial Term (as defined in **Section 4.1**), adjusted for any ramp‑up or ramp‑down schedules agreed in a SOW.

3.2.2 **Variable Usage‑Based Fees.**  
(a) Certain components of the Managed Services (for example, additional storage, bandwidth, or on‑demand capacity) may be charged on a usage basis at the rates specified in Annex 2 (Fee Schedule) or the applicable SOW.  
(b) The Service Provider shall provide a monthly usage report summarising the relevant consumption metrics and associated charges.

3.2.3 **Professional Services Fees.**  
Any project‑based professional services (for example, major upgrades, new integrations, or transformations) shall be scoped and charged separately under a SOW in accordance with **Section 3.2 (Fee Structure)** of the Master Agreement (fixed price, T&M, or hybrid), and such Fees are in addition to the SLA Contract Value unless otherwise agreed in writing.

3.3 **Invoicing and Payment Terms.**  

3.3.1 The Service Provider shall invoice the Client monthly in arrears for:  
(a) Monthly Service Fees;  
(b) variable usage‑based Fees; and  
(c) approved expenses under **Section 3.6** of the Master Agreement, as supplemented by **Section 3.5** below.

3.3.2 Payment terms shall be **Net 60** from the date of invoice, consistent with **Section 3.3.2** of the Master Agreement.

3.3.3 The Client shall notify the Service Provider of any disputed amounts within fifteen (15) Business Days of invoice receipt, specifying the basis for the dispute. Undisputed portions shall be paid in accordance with the Net 60 terms.

3.4 **Late Payments and Suspension.**  

3.4.1 Late payment interest shall accrue on overdue undisputed amounts at the rate specified in **Section 3.4.1** of the Master Agreement.

3.4.2 If undisputed amounts remain unpaid for more than thirty (30) days after written notice of late payment, the Service Provider may, consistent with **Section 3.4.2** of the Master Agreement, suspend all or part of the Managed Services (including non‑critical services) until such amounts are paid, provided that the Service Provider gives at least ten (10) Business Days’ prior written notice of its intent to suspend.

3.5 **Expenses and Reimbursement.**  

3.5.1 The Client shall reimburse the Service Provider for reasonable, pre‑approved travel and out‑of‑pocket expenses incurred in connection with on‑site service reviews, disaster recovery tests, or other activities requiring presence at the Client’s or third‑party facilities, consistent with **Section 3.6** of the Master Agreement.

3.5.2 Expenses shall be itemised on invoices, supported by receipts and documentation, and separately identified from service Fees.

3.6 **Taxes.**  

All Fees under this SLA are exclusive of VAT and other indirect taxes, which shall be added as applicable in accordance with **Section 3.5 (Taxes)** of the Master Agreement.

---

## ARTICLE IV – TERM AND TERMINATION

4.1 **Term of SLA.**  

4.1.1 This SLA shall commence on the SLA Effective Date (18 December 2025) and, unless earlier terminated in accordance with this **Article IV**, shall continue in effect until **1 March 2030** (the **“SLA Expiration Date”**) (the **“SLA Term”**).

4.1.2 The SLA Term is within the overall **Term** defined in **Section 4.1** of the Master Agreement (ending 19 July 2029). To the extent that the SLA Term extends beyond the Term of the Master Agreement, the Parties acknowledge that:  
(a) the Master Agreement shall automatically be deemed extended solely for purposes of this SLA and any SOWs referencing it, until the SLA Expiration Date; and  
(b) all provisions of the Master Agreement shall continue to apply during such extended period, unless otherwise agreed in a written amendment.

4.2 **Renewal.**  

The Parties may renew this SLA for additional periods by mutual written agreement executed no later than ninety (90) days prior to the SLA Expiration Date. Renewal may include revised Service Levels, Fees, and scope, which shall be documented in an amendment or new SLA referencing **MSA-PHO-202504-365**.

4.3 **Termination for Convenience.**  

4.3.1 Notwithstanding **Section 4.3.1** of the Master Agreement (which permits termination for convenience on forty‑five (45) days’ notice), due to the high‑risk, business‑critical nature of the Managed Services, either Party may terminate this SLA for convenience only by providing the other Party with not less than **one hundred eighty (180) days’** prior written notice.

4.3.2 Upon termination for convenience by the Client, the Client shall pay the Service Provider:  
(a) all Fees for Managed Services performed up to the effective date of termination;  
(b) any non‑cancellable commitments incurred for the benefit of the Client (for example, reserved capacity contracts, long‑term data centre leases) that cannot reasonably be mitigated; and  
(c) an early termination fee equal to **three (3) months** of average Monthly Service Fees (calculated based on the preceding twelve (12) months), as a genuine pre‑estimate of ramp‑down and re‑allocation costs.

4.4 **Termination for Cause.**  

4.4.1 Either Party may terminate this SLA for material breach by the other Party, in accordance with **Section 4.4.1** of the Master Agreement, provided that:  
(a) the non‑breaching Party provides written notice specifying the material breach in reasonable detail; and  
(b) the breaching Party fails to cure such breach within thirty (30) days (or ten (10) days in the case of non‑payment) after receipt of such notice.

4.4.2 Persistent failure by the Service Provider to meet critical Service Levels, as defined in **Section 12.8**, may constitute a material breach, subject to cure rights and remedial plans agreed between the Parties.

4.4.3 Either Party may terminate this SLA immediately upon the occurrence of an insolvency event as described in **Section 4.4.2** of the Master Agreement.

4.5 **Effect of Termination of Master Agreement.**  

4.5.1 If the Master Agreement is terminated in its entirety, this SLA shall automatically terminate on the same effective date, unless the Parties expressly agree in writing to continue this SLA on standalone terms (in which case references to the Master Agreement shall continue to apply as if it remained in force).

4.5.2 If the Master Agreement is terminated with respect only to certain SOWs but not others, this SLA shall continue in full force and effect to the extent it supports any remaining SOWs.

4.6 **Transition Assistance.**  

4.6.1 Upon expiration or termination of this SLA for any reason (other than termination by the Service Provider for the Client’s uncured material breach), the Service Provider shall, at the Client’s request and expense, provide Transition Services for a period of up to six (6) months to facilitate the orderly transfer of the Managed Services to the Client or a replacement provider.

4.6.2 Transition Services may include:  
(a) providing copies of relevant configuration, documentation, and operational runbooks (excluding the Service Provider’s confidential internal procedures);  
(b) cooperating with and providing reasonable assistance to the Client and any replacement provider; and  
(c) maintaining service continuity during the transition period at agreed Fees.

4.7 **Survival.**  

Upon expiration or termination of this SLA, the provisions of **Articles V, VI, VII, VIII, IX, XI, XII (in respect of accrued Service Credits), XIV, XV, XVI** and any other provisions which by their nature are intended to survive shall survive, in addition to the survival provisions of **Section 4.6** of the Master Agreement.

---

## ARTICLE V – CONFIDENTIALITY

5.1 **Relationship to Master Agreement.**  

This **Article V** supplements **Article V (Confidentiality)** of the Master Agreement. In the event of conflict, the more protective obligation for the Disclosing Party shall prevail.

5.2 **Confidential Information.**  

5.2.1 “Confidential Information” shall have the meaning given in **Section 5.1** of the Master Agreement and shall expressly include:  
(a) service reports, SLA performance data, and RCA documents;  
(b) network diagrams, security configurations, and architecture documents;  
(c) system logs and monitoring data containing sensitive operational details; and  
(d) any commercially sensitive information relating to pricing, capacity plans, and scaling strategies under this SLA.

5.3 **Obligations.**  

5.3.1 Each Party shall protect the other Party’s Confidential Information in accordance with **Section 5.3** of the Master Agreement and shall use such information solely for the purposes of performing or receiving Managed Services under this SLA and the Master Agreement.

5.3.2 The Service Provider may share the Client’s Confidential Information on a need‑to‑know basis with authorised Subcontractors involved in the provision of Managed Services, provided such Subcontractors are bound by confidentiality obligations no less protective than those set forth herein.

5.4 **Exceptions and Compelled Disclosure.**  

The exclusions and compelled disclosure provisions in **Sections 5.2 and 5.4** of the Master Agreement shall apply equally to this SLA.

5.5 **Return or Destruction.**  

Upon termination or expiration of this SLA, each Party shall, at the other Party’s written request, return or destroy Confidential Information associated with the Managed Services in accordance with **Section 5.5** of the Master Agreement, subject to any retention requirements under **Article XI** of this SLA.

5.6 **Survival Period.**  

Notwithstanding **Section 5.6** of the Master Agreement, the Parties agree that confidentiality obligations under this SLA shall survive for a period of **five (5) years** from the later of (a) expiration or termination of this SLA, or (b) expiration or termination of the Master Agreement; provided that obligations relating to trade secrets and Personal Data shall survive for so long as such information remains a trade secret or is subject to Data Protection Laws.

---

## ARTICLE VI – INTELLECTUAL PROPERTY RIGHTS

6.1 **Pre‑Existing IP.**  

Ownership of Background IP is governed by **Section 6.1** of the Master Agreement. Nothing in this SLA shall transfer ownership of either Party’s Background IP.

6.2 **Service Provider Tools and Configurations.**  

6.2.1 All monitoring tools, scripts, automation frameworks, runbooks, templates, and methodologies used by the Service Provider in delivering the Managed Services, whether developed prior to or during the SLA Term, shall remain the exclusive property of the Service Provider (collectively, **“Service Provider Tools”**), subject to the license grants below.

6.2.2 To the extent Service Provider Tools are embedded within configurations or documentation delivered to the Client, such incorporation shall not transfer ownership of the underlying Service Provider Tools.

6.3 **Deliverables under this SLA.**  

6.3.1 Subject to full payment of all applicable Fees, the Client shall own all Intellectual Property Rights in any Deliverables expressly designated as Client‑owned in the applicable SOW (for example, Client‑specific configuration documentation or bespoke runbooks), excluding Background IP and Service Provider Tools embedded therein.

6.3.2 For clarity, ownership of Deliverables under SOWs remains governed by **Section 6.2** of the Master Agreement, unless expressly modified in the SOW.

6.4 **License to Client.**  

6.4.1 The Service Provider hereby grants to the Client a non‑exclusive, worldwide, perpetual, irrevocable license to use, copy, and internally modify any Service Provider Tools only to the extent embedded in or necessary to use the Deliverables and Managed Services as provided under this SLA and the Master Agreement.

6.4.2 Given the high‑risk nature of the engagement and the Service Provider’s need to protect its proprietary tools in a heavily invested managed service, this license shall be restricted to the Client’s internal business purposes and shall not be sublicensable except to the Client’s Affiliates and service providers solely as necessary to operate the Client’s environment, provided that such Affiliates and service providers are bound by confidentiality and use restrictions no less protective than those herein.

6.5 **License to Service Provider.**  

The Client grants to the Service Provider the license set forth in **Section 6.4** of the Master Agreement to use Client Materials solely to perform the Managed Services and obligations under this SLA.

6.6 **Restrictions.**  

Neither Party shall engage in any of the restricted activities listed in **Section 6.5** of the Master Agreement with respect to the other Party’s Intellectual Property Rights, except as expressly permitted by this SLA or the Master Agreement.

6.7 **Residual Knowledge.**  

The residual knowledge concept in **Section 6.6** of the Master Agreement applies equally to this SLA. The Service Provider may use generalized know‑how obtained in the course of providing Managed Services, provided no Confidential Information or Personal Data of the Client is disclosed.

---

## ARTICLE VII – REPRESENTATIONS AND WARRANTIES

7.1 **Mutual Representations and Warranties.**  

The mutual representations and warranties set forth in **Section 7.1** of the Master Agreement apply to this SLA, including each Party’s authority and capacity to enter into and perform this SLA.

7.2 **Service Provider Warranties.**  

The Service Provider repeats and extends the warranties in **Section 7.2** of the Master Agreement specifically to the Managed Services, including that:

7.2.1 The Managed Services shall be performed in a professional, diligent, and workmanlike manner by suitably qualified and experienced personnel, trained in high‑availability managed services.

7.2.2 The Managed Services, when performed in accordance with this SLA, shall materially conform to the Service Levels and scope set out in **Article II** and **Article XII** for the duration of the SLA Term.

7.2.3 The Service Provider will comply with Applicable Law and Data Protection Laws in performing the Managed Services.

7.3 **Client Warranties.**  

The Client repeats and extends the warranties in **Section 7.3** of the Master Agreement, including that it has and will maintain all rights and licences necessary to grant the Service Provider access to Client systems and materials for the purposes of this SLA.

7.4 **Warranty Remedies.**  

Without prejudice to **Section 7.4** of the Master Agreement, the Client’s primary remedies for Service Provider’s failure to meet the warranties in this SLA shall be: (a) re‑performance of non‑conforming Managed Services; (b) Service Credits under **Section 12.6**; and (c) in cases of persistent or material failure, termination rights under **Article IV**.

7.5 **Disclaimer.**  

Except as expressly set forth in the Master Agreement and this SLA, the Service Provider disclaims all other warranties, express or implied, to the maximum extent permitted under Applicable Law.

---

## ARTICLE VIII – INDEMNIFICATION

8.1 **Indemnification by Service Provider.**  

The indemnification obligations of the Service Provider in **Section 8.1** of the Master Agreement apply to this SLA, including IP infringement and bodily injury / tangible property damage arising from the Managed Services.

8.2 **Additional Security and Data Indemnity.**  

Given the high‑risk profile, the Service Provider further agrees to indemnify the Client against third‑party claims arising directly from the Service Provider’s gross negligence or wilful misconduct in failing to implement basic security controls expressly committed to in this SLA, to the extent such failure results in a Personal Data breach or compromise of the Production Service. This obligation shall be subject to the limitations and exclusions in **Article IX** of the Master Agreement as modified by **Article IX** of this SLA (to the extent not inconsistent with the “High Risk” provisions).

8.3 **Indemnification by Client.**  

8.3.1 In addition to the indemnities in **Section 8.2** of the Master Agreement, and in light of the high‑risk, vendor‑favourable allocation, the Client shall indemnify, defend, and hold harmless the Service Provider Indemnitees from and against all Losses arising out of or in connection with claims by third parties resulting from:  
(a) the Client’s misuse or unauthorised modification of the Managed Services;  
(b) security breaches or system failures caused by the Client Environment or third‑party services not under the Service Provider’s control; or  
(c) the Client’s failure to comply with Applicable Law in its use of the Managed Services.

8.4 **Indemnification Procedures.**  

The indemnification procedures in **Section 8.3** of the Master Agreement apply equally to indemnification claims under this SLA.

8.5 **IP Infringement Remedies.**  

The IP infringement remedies set forth in **Section 8.4** of the Master Agreement apply to any Deliverables or tools used in the Managed Services.

---

## ARTICLE IX – LIMITATION OF LIABILITY

9.1 **Relationship to Master Agreement.**  

9.1.1 The Parties acknowledge that **Article IX (Limitation of Liability)** of the Master Agreement was negotiated in the context of a **medium risk** overall engagement. For the specific Managed Services covered by this SLA, the Parties agree to the modifications set out in this **Article IX**, which shall supersede **Sections 9.1 and 9.2** of the Master Agreement with respect to claims arising out of or in connection with this SLA.

9.2 **Liability Cap – High Risk Engagement.**  

9.2.1 For all claims arising under or in connection with this SLA, the Service Provider’s total aggregate liability to the Client, whether in contract, tort (including negligence), or otherwise, shall be limited to an amount equal to **one hundred and fifty percent (150%) of the SLA Contract Value** (US$3,249,854), i.e., **US$4,874,781**, notwithstanding anything to the contrary in **Section 9.2** of the Master Agreement.

9.2.2 The Parties expressly acknowledge that this higher cap reflects the high‑risk nature of the Managed Services and is materially greater than the 12‑month Fees cap that would otherwise apply under the Master Agreement.

9.3 **Exclusion / Inclusion of Certain Damages.**  

9.3.1 Subject to **Section 9.4** below, neither Party shall be liable for indirect, incidental, special, or punitive damages, even if advised of the possibility of such damages, consistent with **Section 9.1** of the Master Agreement.

9.3.2 However, in deviation from the Master Agreement and in recognition of the high‑risk environment, the Parties agree that:  
(a) **loss of data**, to the extent directly and proximately caused by the Service Provider’s failure to perform agreed backup and recovery procedures, shall be treated as direct damage (subject to the cap in **Section 9.2.1**); and  
(b) **loss of business or revenue directly attributable to prolonged Priority 1 outages** exceeding the thresholds in **Section 12.8** may be recoverable as direct damages (again subject to the cap in **Section 9.2.1**), provided that such losses are reasonably foreseeable and adequately proven.

9.4 **Exceptions.**  

The limitations in **Section 9.2** shall not apply to:  
(a) either Party’s liability for death or personal injury caused by its negligence, or for fraud or fraudulent misrepresentation, as in **Section 9.3** of the Master Agreement;  
(b) the Client’s obligation to pay Fees due under this SLA; or  
(c) the Client’s indemnification obligations under **Section 8.3** of this SLA, which shall be uncapped to the maximum extent permitted by Applicable Law, reflecting the vendor‑favourable risk allocation.

9.5 **Allocation of Risk.**  

The Parties confirm that the limitations and risk allocation set forth in this **Article IX** are reasonable in light of: (a) the SLA Contract Value, (b) the high‑risk designation for the Managed Services, and (c) the insurance coverage maintained by the Service Provider under **Article X** and **Article X** of the Master Agreement.

---

## ARTICLE X – INSURANCE

10.1 **Required Coverage.**  

10.1.1 The Service Provider shall maintain the insurance coverage specified in **Article X** of the Master Agreement throughout the SLA Term, with the following **enhanced minimum limits** for this high‑risk engagement:

(a) Professional Indemnity (Errors & Omissions): not less than **GBP 5,000,000** per claim and in the aggregate.  
(b) Public/General Liability: not less than **GBP 5,000,000** per occurrence.  
(c) Employer’s Liability: in accordance with Applicable Law, with a minimum of **GBP 5,000,000**.  
(d) Cyber and Data Security Insurance: not less than **GBP 3,000,000** per claim and in the aggregate, covering, at a minimum, network security liability, privacy liability, data breach costs, and business interruption.

10.2 **Certificates of Insurance.**  

Upon the Client’s request (not more than annually unless reasonable cause exists), the Service Provider shall provide certificates evidencing such coverage, as contemplated by **Section 10.2** of the Master Agreement.

10.3 **No Limitation.**  

Maintenance of insurance shall not limit the Service Provider’s liability beyond the limits expressly set out in **Article IX** of this SLA and the Master Agreement.

---

## ARTICLE XI – DATA PROTECTION AND PRIVACY

11.1 **Applicability of Master Agreement.**  

The data protection and privacy obligations set forth in **Article XI** of the Master Agreement apply fully to this SLA. The Parties acknowledge that, for the Managed Services, the Client is the controller and the Service Provider is the processor of Personal Data.

11.2 **Data Processing Details.**  

The types of Personal Data processed, categories of data subjects, and processing activities shall be specified in an accompanying **Data Processing Annex** or SOW, which shall form part of the Master Agreement and this SLA.

11.3 **Security Measures.**  

In addition to **Section 11.4** of the Master Agreement, the Service Provider shall implement and maintain security controls appropriate to the high‑risk nature of the Managed Services, including:  
(a) multi‑factor authentication for privileged access;  
(b) regular vulnerability scanning and penetration testing;  
(c) encryption of Personal Data in transit and at rest using industry‑standard algorithms; and  
(d) security event monitoring and alerting 24x7.

11.4 **Data Breach Notification.**  

The Service Provider shall notify the Client of any Personal Data breach in accordance with **Section 11.7** of the Master Agreement, and, for the avoidance of doubt, shall endeavour to notify the Client as soon as practicable and in any event within **seventy‑two (72) hours** of becoming aware of the breach.

11.5 **Data Retention and Deletion.**  

Upon termination or expiration of this SLA, the Service Provider shall delete or return all Personal Data processed under this SLA in accordance with **Section 11.9** of the Master Agreement and any more specific requirements set out in the applicable SOW or Data Processing Annex. Evidence of deletion shall be provided upon written request.

11.6 **Audit Rights.**  

The audit provisions in **Section 11.10** of the Master Agreement shall apply to the Managed Services, and the Client may, upon reasonable notice, conduct audits (directly or through an independent auditor) to verify the Service Provider’s compliance with this SLA and data protection obligations, not more than once per twelve (12) months except as permitted under the Master Agreement.

---

## ARTICLE XII – SERVICE LEVEL AGREEMENTS (DETAILED)

This **Article XII** supplements and, where explicitly stated, supersedes **Article XII** of the Master Agreement for the Managed Services.

12.1 **Uptime Commitment.**  

12.1.1 The Service Provider shall use commercially reasonable efforts to ensure that the Production Service is available **99.95%** of the time in each calendar month, measured over the Service Window, excluding permitted Downtime (as defined in **Section 1.1.5**).

12.1.2 This 99.95% uptime commitment replaces the 99.9% commitment in **Section 12.1** of the Master Agreement for the systems governed by this SLA.

12.2 **Scheduled and Emergency Maintenance.**  

12.2.1 Scheduled Maintenance windows shall not exceed **8 hours per calendar month**, and the Service Provider shall provide at least **five (5) Business Days’** prior written notice of any Scheduled Maintenance likely to cause service unavailability.

12.2.2 Emergency Maintenance may be performed without prior notice where necessary to address critical issues. The Service Provider shall notify the Client as soon as reasonably practicable and endeavour to perform such maintenance during low‑usage periods.

12.3 **Priority Levels and Response Times.**  

Incidents shall be classified and responded to as follows, supplementing **Section 12.3** of the Master Agreement:

- **Priority 1 (Critical)** – complete system outage or critical business impact:  
  - Response Time: within **30 minutes** (24x7).  
  - Target Restoration Time (workaround or fix): within **4 hours**.  

- **Priority 2 (High)** – significant degradation with high business impact:  
  - Response Time: within **1 hour** (24x7).  
  - Target Restoration Time: within **8 hours** (during Supported Hours).  

- **Priority 3 (Medium)** – limited impact, workaround exists:  
  - Response Time: within **1 Business Day**.  
  - Target Restoration Time: within **5 Business Days**.  

- **Priority 4 (Low)** – minor issues, general inquiries, cosmetic defects:  
  - Response Time: within **3 Business Days**.  
  - Target Restoration Time: best efforts, resolution in a future release.

12.4 **SLA Measurement and Exclusions.**  

12.4.1 Uptime percentage for each month is calculated as:  
Uptime % = (Total Minutes in Month – Downtime Minutes) / Total Minutes in Month × 100.

12.4.2 Downtime shall not include:  
(a) Scheduled Maintenance within the limits above;  
(b) Emergency Maintenance not exceeding four (4) hours per month;  
(c) downtime due to Force Majeure Events;  
(d) downtime caused by the Client Environment or third‑party systems not under the Service Provider’s control;  
(e) outages caused by changes not approved by the Service Provider or executed contrary to its instructions; or  
(f) suspension of service due to the Client’s non‑payment under **Section 3.4.2**.

12.5 **Incident Management and RCA.**  

12.5.1 The Service Provider shall maintain an Incident management process aligned with ITIL or similar industry standards.

12.5.2 For each Priority 1 and Priority 2 Incident, the Service Provider shall:  
(a) provide initial Incident reports within **24 hours** of resolution; and  
(b) deliver a formal Root Cause Analysis (RCA) report within **five (5) Business Days** of resolution, including remedial actions to prevent recurrence.

12.5.3 The Client may request RCA for significant Priority 3 Incidents, subject to reasonable limits agreed during service review meetings.

12.6 **Service Credits.**  

12.6.1 If the Service Provider fails to meet the 99.95% uptime commitment in any calendar month, the Client shall be entitled to Service Credits as follows (superseding the credit structure in **Section 12.4** of the Master Agreement for the Managed Services):

- Uptime 99.5% to < 99.95%: credit equal to **5%** of the Monthly Service Fees for the affected month;  
- Uptime 99.0% to < 99.5%: credit equal to **10%** of the Monthly Service Fees;  
- Uptime 98.0% to < 99.0%: credit equal to **20%** of the Monthly Service Fees;  
- Uptime < 98.0%: credit equal to **30%** of the Monthly Service Fees.

12.6.2 Service Credits shall be applied against future invoices and shall not be redeemable for cash, except where no further invoices are due, in which case the Parties shall reconcile the amounts in good faith.

12.6.3 The Client must request Service Credits in writing within **thirty (30) days** following receipt of the relevant monthly service report; otherwise the right to such Service Credits is deemed waived.

12.7 **Reporting.**  

The Service Provider shall provide monthly SLA reports as described in **Section 12.5** of the Master Agreement, including detailed performance against the metrics in this **Article XII**, Incident summaries, RCA outcomes, and planned improvements.

12.8 **Persistent Failure.**  

If, in any rolling six (6) month period, either:  
(a) the monthly uptime falls below 99.0% in two (2) or more months; or  
(b) there are three (3) or more Priority 1 Incidents attributable primarily to the Service Provider’s failure to follow agreed procedures,  
then the Parties shall meet at senior executive level to agree a remedial action plan. If, after a further three (3) months, material improvements have not been achieved, the Client may, in addition to Service Credits, treat such persistent failure as a material breach for purposes of **Section 4.4**.

---

## ARTICLE XIII – CHANGE MANAGEMENT

13.1 **Change Requests.**  

Change management shall follow **Article XIII (Change Management)** of the Master Agreement, with any SLA‑specific procedures agreed in writing between the Parties.

13.2 **Impact Assessment.**  

The Service Provider shall assess change requests for impact on Service Levels, uptime, security, Fees, and timelines, and shall provide an impact assessment within a reasonable period (typically five (5) to ten (10) Business Days, depending on complexity).

13.3 **Change Orders.**  

Changes affecting scope, Service Levels, Monthly Service Fees, or infrastructure capacity shall be documented in a Change Order signed by both Parties, as required by **Section 13.3** of the Master Agreement.

13.4 **Emergency Changes.**  

Emergency Changes necessary to address Priority 1 Incidents or critical security issues may be implemented without prior written Change Orders, subject to retrospective documentation and review at the next service review meeting.

---

## ARTICLE XIV – DISPUTE RESOLUTION

14.1 **Good Faith Negotiations and Escalation.**  

Dispute resolution shall follow **Article XIV** of the Master Agreement. For operational disputes under this SLA, the Parties shall first seek to resolve the issue at the level of the SDM and Client’s service owner. If not resolved within ten (10) Business Days, the dispute shall be escalated to senior executives as in **Section 14.2** of the Master Agreement.

14.2 **Mediation and Litigation.**  

If unresolved after escalation, the Parties shall proceed to mediation and, failing resolution, to the courts of England and Wales, in accordance with **Sections 14.3, 14.4, 16.12, and 16.13** of the Master Agreement.

14.3 **Continued Performance.**  

During any dispute, the Service Provider shall continue to perform the Managed Services (to the extent reasonably practicable), and the Client shall continue to pay undisputed amounts, as required by **Section 14.5** of the Master Agreement.

---

## ARTICLE XV – FORCE MAJEURE

15.1 **Force Majeure Events.**  

The definition and treatment of Force Majeure Events in **Article XV** of the Master Agreement apply to this SLA.

15.2 **Effect on Service Levels.**  

Service Level calculations shall exclude any impact caused by a Force Majeure Event, provided that the Service Provider complies with its obligations under **Section 15.2** of the Master Agreement to notify and mitigate.

15.3 **Extended Force Majeure.**  

If a Force Majeure Event affects the Managed Services for more than sixty (60) consecutive days, either Party may terminate this SLA in accordance with **Section 15.3** of the Master Agreement, without liability except for amounts accrued prior to termination.

---

## ARTICLE XVI – GENERAL PROVISIONS

16.1 **Reference to Master/Parent Agreement.**  

This Service Level Agreement is executed under and subject to the terms of the **Master Services Agreement reference number MSA-PHO-202504-365 (contract_365)**. Except as expressly modified herein, all provisions of the Master Agreement remain in full force and effect and apply to the Managed Services described in this SLA. In the event of conflict between this SLA and the Master Agreement, the Master Agreement shall prevail, except where this SLA expressly states that it supersedes the Master Agreement with respect to the Managed Services.

16.2 **Entire Agreement.**  

This SLA, together with the Master Agreement, any Statements of Work, Change Orders, and annexes hereto and thereto, constitutes the entire agreement between the Parties with respect to the Managed Services and supersedes all prior discussions, proposals, and understandings relating to the subject matter hereof.

16.3 **Amendments.**  

No amendment to this SLA shall be effective unless in writing and signed by authorised representatives of both Parties, in accordance with **Section 16.2** of the Master Agreement.

16.4 **Severability.**  

If any provision of this SLA is held invalid, illegal, or unenforceable, the remaining provisions shall remain in full force and effect, and the Parties shall replace any invalid provision with a valid provision that most closely reflects the Parties’ original intent, consistent with **Section 16.3** of the Master Agreement.

16.5 **Waiver.**  

No waiver of any provision of this SLA shall be effective unless in writing and signed by the waiving Party. No failure or delay in exercising any right shall constitute a waiver of such right, consistent with **Section 16.4** of the Master Agreement.

16.6 **Notices.**  

Notices under this SLA shall be given in accordance with **Section 16.5 (Notices)** of the Master Agreement, using the same contact details for each Party as set out therein, unless updated by written notice.

16.7 **Assignment.**  

Assignment of this SLA shall be governed by **Section 16.6 (Assignment)** of the Master Agreement. Any attempted assignment in violation thereof shall be void.

16.8 **Independent Contractors.**  

The Parties remain independent contractors, as set forth in **Section 16.7** of the Master Agreement.

16.9 **Third‑Party Beneficiaries.**  

Except as expressly provided in relation to Indemnitees, this SLA confers no rights on any third party, consistent with **Section 16.8** of the Master Agreement.

16.10 **Governing Law and Jurisdiction.**  

This SLA shall be governed by and construed in accordance with the laws of **England and Wales**, in alignment with **Section 16.12** of the Master Agreement. The Parties submit to the exclusive jurisdiction of the courts of England and Wales, as in **Section 16.13** of the Master Agreement.

16.11 **Counterparts; Electronic Signatures.**  

This SLA may be executed in counterparts and by electronic signature, as provided in **Section 16.9** of the Master Agreement.

16.12 **Publicity.**  

Publicity rights under this SLA shall be governed by **Section 16.10** of the Master Agreement.

16.13 **Non‑Solicitation.**  

The non‑solicitation obligations in **Section 16.11** of the Master Agreement apply to personnel engaged in delivering or managing the Managed Services under this SLA.

16.14 **Survival.**  

The survival provisions in **Section 4.6** of the Master Agreement apply to this SLA, in addition to those specifically stated in **Section 4.7** above.

---

## SIGNATURES

IN WITNESS WHEREOF, the Parties hereto have caused this Service Level Agreement, reference number **SLA-PHO-202504-396**, to be executed by their duly authorised representatives as of the SLA Effective Date.

**Executed pursuant to Master Services Agreement Ref: MSA-PHO-202504-365 (contract_365).**

---

### For and on behalf of  
**Contoso Enterprises** (the “Client” or “Company”)

Name: _________________________________  
Title: _________________________________  

Signature: _____________________________  

Date: _________________________________  

Witness Name: _________________________  
Witness Signature: _____________________  
Date: _________________________________  

---

### For and on behalf of  
**Phoenix Industries** (the “Vendor” or “Service Provider”)

Name: _________________________________  
Title: _________________________________  

Signature: _____________________________  

Date: _________________________________  

Witness Name: _________________________  
Witness Signature: _____________________  
Date: _________________________________  

---

**[END OF SERVICE LEVEL AGREEMENT – SLA-PHO-202504-396]**