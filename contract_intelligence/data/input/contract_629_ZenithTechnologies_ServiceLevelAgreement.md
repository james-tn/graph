# SERVICE LEVEL AGREEMENT  
**Contract Reference No.: SLA-ZEN-202504-629**

---

## PREAMBLE & RECITALS

This **SERVICE LEVEL AGREEMENT** (this “**SLA**” or this “**Agreement**”), Contract Reference No. **SLA-ZEN-202504-629**, is made and entered into as of **April 9, 2026** (the “**SLA Effective Date**”), by and between:

**Contoso Enterprises**, a [jurisdiction of incorporation/formation to be inserted] corporation, with its principal place of business at **1000 Contoso Parkway, Suite 500, Dallas, Texas 75201** (“**Contoso**”, “**Client**” or “**Company**”); and  

**Zenith Technologies**, a [jurisdiction of incorporation/formation to be inserted] corporation, with its principal place of business at **2500 Zenith Plaza, 12th Floor, Austin, Texas 78701** (“**Zenith**”, “**Vendor**” or “**Service Provider**”).

Contoso and Zenith may be referred to herein individually as a “**Party**” and collectively as the “**Parties**”.

This SLA is **supplemental to and made pursuant to** that certain **Master Services Agreement** between the Parties dated **April 14, 2025**, Contract Reference No. **MSA-ZEN-202504-539** (file identifier **contract_539**) (the “Master Services Agreement” or “Parent Agreement”).

---

### RECITALS

**SLA-ZEN-202504-629**

WHEREAS, the Parties previously entered into the **Master Services Agreement** dated April 14, 2025, Contract Reference No. **MSA-ZEN-202504-539** (file identifier **contract_539**), (the “**Master Services Agreement**” or “**MSA**”), which sets forth the general terms and conditions governing the provision of services by Zenith to Contoso, including definitions of “Services,” “Deliverables,” “Service Levels,” “Fees,” “Term,” “Payment Terms (Net 45),” and other key provisions, including **Article XII (Service Level Agreements)**;

WHEREAS, pursuant to **Section 2.1 (General)** and **Section 2.2.4 (Managed Services and Support)** of the MSA, Zenith has agreed to provide managed services, support, maintenance, and incident management services to Contoso, in accordance with service level commitments to be further defined in one or more service level agreements and/or Statements of Work (“SOWs”);

WHEREAS, **Section 12.1 (Uptime Commitment)**, **Section 12.3 (Response and Resolution Times)**, and **Section 12.4 (SLA Credits)** of the MSA contemplate detailed performance standards, metrics, and remedies to be specified in applicable SOWs and/or separate SLAs;

WHEREAS, the Parties now desire to enter into this standalone, detailed Service Level Agreement, **SLA-ZEN-202504-629**, which **supplements** and is **entered into pursuant to** the Master Services Agreement (Ref: **MSA-ZEN-202504-539**, file identifier **contract_539**) to define the specific Service Levels, response and resolution times, credits, reporting obligations, and related operational details for managed services and support provided by Zenith to Contoso;

WHEREAS, the Parties acknowledge that the anticipated aggregate contract value specific to the services governed by this SLA is approximately **Two Hundred Sixty-One Thousand Six Hundred Sixty-Four U.S. Dollars (US $261,664)** (the “**SLA Contract Value**”), which forms a subset of and is consistent with the **Contract Value** defined in **Section 1.6** and referenced in **Article III (Fees and Payment Terms)** and **Article IX (Limitation of Liability)** of the MSA (initially anticipated at **US $447,794**);

WHEREAS, the Parties agree that the **risk level for the services covered by this SLA is “High”**, and therefore, in contrast to the “Low” risk profile described in **Section 2.10 (Risk Level; Client-Friendly Bias)** of the MSA, the Parties intend that this SLA shall reflect terms **relatively favorable to the Vendor** with respect to risk allocation, termination flexibility, indemnification, and liability (including **no contractual cap on Vendor’s liability and broader Client indemnification obligations**), while still maintaining consistency with the governing framework of the MSA except where this SLA expressly supersedes;

NOW, THEREFORE, in consideration of the mutual covenants and promises contained herein, and in the Master Services Agreement, and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the Parties hereby agree as follows:

---

## ARTICLE I  
DEFINITIONS

1.1 **Incorporation of MSA Definitions.** Capitalized terms used but not otherwise defined herein shall have the meanings ascribed to them in the **Master Services Agreement (MSA-ZEN-202504-539, contract_539)**, including without limitation “Agreement,” “Services,” “Deliverables,” “Service Levels,” “Business Day,” “Force Majeure Event,” “Work Product,” “Zenith Pre-Existing IP,” “Confidential Information,” “Term,” and “Payment Terms.”

1.2 **“Parent Agreement” or “Master Agreement”** means the Master Services Agreement between the Parties dated April 14, 2025, Contract Reference No. **MSA-ZEN-202504-539** (file identifier **contract_539**), including all SOWs, schedules, and amendments thereto.

1.3 **“Managed Services”** means the ongoing operation, monitoring, management, maintenance, support, and incident response services provided by Zenith to Contoso pursuant to this SLA and any applicable SOW, including services contemplated under **Section 2.2.4 (Managed Services and Support)** of the MSA.

1.4 **“Supported Systems”** means the specific software platforms, applications, integrations, environments, and infrastructure components (whether on-premises, hosted by Zenith, or hosted by a third party administered by Zenith) identified in the applicable SOW as being subject to the Service Levels in this SLA.

1.5 **“Service Levels”** means the quantitative and qualitative performance metrics, including uptime percentages, response times, resolution times, and other standards specified in **Article XII** of this SLA, which refine and supersede, to the extent of conflict, the more general service level provisions in **Article XII of the MSA** for the Supported Systems covered hereunder.

1.6 **“Service Window”** means the periods during which Zenith is obligated to provide specific levels of availability and support, as detailed in **Section 12.2** of this SLA (e.g., 24x7 for Severity 1 incidents, Business Hours for lower severity levels).

1.7 **“Business Hours”** means 8:00 a.m. to 6:00 p.m., Central Time, on Business Days, unless otherwise specified in an applicable SOW.

1.8 **“Incident”** means an unplanned interruption or degradation of a Supported System or Service, or a failure of a Service to meet the applicable Service Levels.

1.9 **“Severity Level”** means the classification of an Incident based on its impact on Contoso’s business operations, as defined in **Section 12.3** of this SLA.

1.10 **“SLA Credits” or “Service Credits”** means the financial credits or other remedies to which Contoso may become entitled due to Zenith’s failure to meet specific Service Levels, as described in **Section 12.6** of this SLA.

1.11 **“Maintenance Window”** means the periods designated by Zenith for planned maintenance that may impact the availability of Supported Systems, as defined in **Section 12.4**.

1.12 **“High-Risk Services”** means the Managed Services that are mission-critical to Contoso’s operations, as specified in the applicable SOW, and explicitly designated as high risk for purposes of this SLA.

1.13 **“SLA Effective Date”** has the meaning set forth in the Preamble and is April 9, 2026.

1.14 **“SLA Expiration Date”** means **April 30, 2028**, unless earlier terminated in accordance with **Article IV** of this SLA or the Parent Agreement.

1.15 **“SLA Term”** means the period commencing on the SLA Effective Date and continuing until the SLA Expiration Date, unless earlier terminated under this SLA or the Master Agreement.

1.16 **“SLA Contract Value”** means the anticipated aggregate fees payable under the SOWs governed by this SLA, initially estimated at **US $261,664**, as referenced in the Recitals.

1.17 **“Net 45 Payment Terms”** means the payment terms defined in **Section 3.3 (Invoicing; Payment Terms)** of the MSA, whereby undisputed invoices are due and payable within forty-five (45) days after Contoso’s receipt.

1.18 **“Change Request”** has the meaning given in **Section 13.1** of this SLA and corresponds generally to “Change Request” as discussed in **Article XIII of the MSA**.

1.19 **“Applicable Law”** has the meaning given in **Section 1.3** of the MSA and applies equally to this SLA.

1.20 **“Personal Data”** has the meaning given in **Article XI of the MSA** and any applicable data processing addendum referenced therein.

---

## ARTICLE II  
SCOPE OF SERVICES / WORK

2.1 **Relationship to Parent Agreement.** This SLA is **executed under and subject to** the terms and conditions of the Master Services Agreement (Ref: **MSA-ZEN-202504-539**, contract_539), as required by **Section 2.1 (General)** of the MSA. In the event of a conflict between the MSA and this SLA with respect to Service Levels, performance metrics, SLA Credits, and operational procedures for the Supported Systems, the terms of this SLA shall control; provided, however, that the **indemnification and general risk allocation framework in the MSA (Articles VIII and IX)** shall continue to apply to the extent not expressly modified by this SLA.

2.2 **Description of Managed Services.** Zenith shall provide the following Managed Services in relation to the Supported Systems, consistent with **Section 2.2.4 (Managed Services and Support)** of the MSA:

  2.2.1 **System Monitoring and Alerting.**  
  (a) 24x7 automated monitoring of system availability, performance thresholds, key application logs, and integration endpoints;  
  (b) configuration and maintenance of alert thresholds and notification channels; and  
  (c) classification of alerts into Incidents with appropriate Severity Levels per **Section 12.3**.

  2.2.2 **Incident Management and Resolution.**  
  (a) intake of Incident reports via designated channels (ticketing system, email, or phone);  
  (b) triage and assignment to appropriate support teams;  
  (c) adherence to response and resolution time targets in **Article XII**; and  
  (d) communication with Contoso regarding status, workarounds, and final resolution.

  2.2.3 **Problem Management.** Identification of recurring Incidents, root cause analysis, and implementation of corrective and preventive actions to reduce Incident frequency and impact.

  2.2.4 **Change and Release Management.** Implementation of changes to configurations, integration endpoints, and related components of the Supported Systems, in accordance with **Article XIII (Change Management)** of this SLA and **Article XIII of the MSA**, including testing, validation, and rollback planning.

  2.2.5 **Routine Maintenance and Patching.** Application of vendor-recommended patches, updates, and security fixes during Maintenance Windows, in coordination with Contoso, consistent with **Section 12.4**.

  2.2.6 **User Support and Service Desk (If Specified in SOW).** First- and second-level support for Contoso’s designated user groups, including ticket handling, basic troubleshooting, and escalation to Zenith technical teams or third-party vendors as necessary.

  2.2.7 **Reporting and Service Reviews.** Monthly service reports detailing uptime metrics, Incident statistics by Severity Level, SLA attainment, root cause analyses of major Incidents, and forward-looking risk assessments; quarterly service review meetings with Contoso’s designated stakeholders.

2.3 **Supported Systems.** The specific applications, platforms, and environments covered by this SLA (e.g., production environment of Contoso’s CRM system, integration layer with ERP, data warehouse ETL jobs) shall be identified in one or more SOWs executed under the Parent Agreement and expressly referencing this SLA. Only those systems listed as “Supported Systems” in such SOWs shall be subject to the Service Levels and SLA Credits defined herein.

2.4 **Deliverables.** Without limiting the definition of “Deliverables” in **Section 1.7 of the MSA**, the following are key Deliverables for this SLA:

  (a) Monthly service performance reports;  
  (b) Root cause analysis documents for Severity 1 and Severity 2 Incidents;  
  (c) Change and release plans for material changes;  
  (d) Updated configuration and operation documentation as required under **Section 2.9 of the MSA**; and  
  (e) Quarterly capacity and performance assessment reports.

Deliverables shall be subject to the acceptance procedures of **Section 2.3 of the MSA**, unless more specific acceptance criteria are included in the applicable SOW.

2.5 **Service Performance Standards.** In addition to the general performance standards in **Section 2.4 of the MSA**, Zenith shall perform the Managed Services:

  (a) consistent with the detailed Service Levels in **Article XII** of this SLA;  
  (b) using Personnel with specialized experience appropriate for high-availability, high-risk managed services; and  
  (c) with proactive identification and mitigation of risks that could affect uptime or data integrity.

2.6 **Client Responsibilities.** In supplement to **Section 2.6 of the MSA**, Contoso shall:

  (a) designate technical and business contacts for Incident escalation and change approvals;  
  (b) ensure that any Contoso-managed components (e.g., on-premise network segments, user devices) meet minimum configuration standards communicated by Zenith;  
  (c) promptly notify Zenith of any changes in business priorities or critical business cycles that may affect scheduling of Maintenance Windows or incident response priorities; and  
  (d) maintain current contact details in Zenith’s support system to enable timely communications.

Zenith’s obligations under the Service Levels are contingent upon Contoso’s fulfillment of these responsibilities, and Zenith shall not be liable for SLA failures to the extent caused by Contoso’s non-compliance, consistent with **Section 2.6 of the MSA**.

2.7 **High-Risk Classification.** The Parties acknowledge that the services under this SLA are classified as **“High-Risk Services”**, and thus the Parties agree to enhanced operational diligence, including tighter monitoring, more frequent reporting, and more robust change controls. At the same time, the Parties agree that risk allocation provisions in this SLA will, in certain respects, be **more favorable to the Vendor** than those set forth in the MSA, as expressly stated in **Articles VIII and IX** herein.

2.8 **Relationship to SOWs.** Each applicable SOW under the MSA that references this SLA shall specify: (a) the Supported Systems; (b) service hours (if different from the defaults set herein); (c) any system-specific metrics or enhanced Service Levels above the base standards defined in **Article XII**; and (d) any system-specific pricing or additional fees, as contemplated by **Article III of the MSA**.

---

## ARTICLE III  
FEES AND PAYMENT TERMS

3.1 **Fees for Managed Services.** Fees for the services covered by this SLA will be set forth in one or more SOWs executed pursuant to the Parent Agreement and will be structured using one or more of the following models:

  (a) **Fixed Monthly Recurring Fees** for baseline Managed Services and support of the Supported Systems;  
  (b) **Usage-Based Fees** (e.g., per active user, per transaction, or per server instance) as specified in the SOW;  
  (c) **Time-and-Materials Fees** for non-recurring activities such as major upgrades, custom enhancements, or one-time remediation projects; and  
  (d) **Performance-Based Fees**, where agreed, linked to specific achievement of mutually defined KPIs.

The Parties acknowledge that the aggregate estimated Fees under SOWs governed by this SLA are anticipated to be approximately **US $261,664** during the SLA Term.

3.2 **Payment Terms – Net 45.** Consistent with **Section 3.3 of the MSA**, Zenith shall invoice Contoso in accordance with the billing schedule set forth in the applicable SOW (e.g., monthly in arrears for recurring fees, upon completion for one-time projects). All undisputed amounts shall be due and payable within **forty-five (45) days** after Contoso’s receipt of the invoice (“**Net 45**”), which is incorporated from the MSA’s **Payment Terms**.

3.3 **Expenses.** In addition to the Fees, Contoso shall reimburse Zenith for reasonable, pre-approved out-of-pocket expenses actually incurred in connection with the services under this SLA (e.g., travel for on-site Incident response or service reviews), in accordance with **Section 3.2 of the MSA** and Contoso’s then-current travel and expense policies, as provided to Zenith.

3.4 **SLA Credits and Fees.** SLA Credits granted pursuant to **Section 12.6** of this SLA shall be calculated as a percentage of the relevant monthly recurring Fees for the affected Supported Systems and shall be applied as credits against subsequent invoices. SLA Credits shall not entitle Contoso to any cash payments, refunds, or offsets against non-related fees, unless expressly stated otherwise in the applicable SOW.

3.5 **Disputed Amounts.** Contoso may withhold payment of any amounts it reasonably and in good faith disputes, in accordance with **Section 3.4 of the MSA**, provided that Contoso: (a) timely pays all undisputed amounts; and (b) provides written notice to Zenith within fifteen (15) days of invoice receipt, specifying the basis for the dispute.

3.6 **Late Payments.** Undisputed amounts not paid when due shall accrue interest as set forth in **Section 3.5 of the MSA** (up to 1.0% per month or lower if required by Applicable Law). Given the high-risk classification and the mission-critical nature of the services, Zenith retains the **right, upon ten (10) Business Days’ written notice after a payment becomes overdue**, to temporarily suspend non-critical portions of the Managed Services if undisputed amounts remain unpaid, provided that Zenith continues to support Severity 1 and Severity 2 Incidents affecting production until payment is made or the Parties agree on a remediation plan.

3.7 **Taxes.** All Fees and other amounts under this SLA are exclusive of Taxes, which shall be handled in accordance with **Section 3.6 of the MSA**.

3.8 **No Charge Items.** Routine reporting and account management activities specifically identified in this SLA and reasonably necessary for Contoso to receive the Managed Services shall be included in the agreed Fees, consistent with **Section 3.7 of the MSA**, unless an SOW expressly provides otherwise.

---

## ARTICLE IV  
TERM AND TERMINATION

4.1 **SLA Term.** This SLA shall commence on the **SLA Effective Date (April 9, 2026)** and, unless earlier terminated in accordance with this **Article IV** or the Parent Agreement, shall continue in effect until **April 30, 2028** (the “**SLA Expiration Date**”).

4.2 **Renewal.** The Parties may renew this SLA beyond the SLA Expiration Date for additional periods as mutually agreed in writing. Any such renewal shall be documented in an amendment or replacement SLA, executed pursuant to **Section 16.2 of the MSA (Amendments)**.

4.3 **Termination for Convenience by Client.** Notwithstanding **Section 4.2 of the MSA**, and in light of the high-risk, mission-critical nature of the services:

  (a) Contoso may terminate this SLA (in whole or with respect to specific Supported Systems) for convenience upon **one hundred eighty (180) days’ prior written notice** to Zenith.  

  (b) During such notice period, Zenith shall continue providing Managed Services and shall reasonably cooperate with Contoso to transition services to Contoso or a replacement provider, subject to additional transition fees as mutually agreed and consistent with the payment obligations herein.

4.4 **Termination for Convenience by Vendor.** Zenith may terminate this SLA (in whole or with respect to specific Supported Systems) for convenience upon **ninety (90) days’ prior written notice** to Contoso, which is shorter than the Client notice period and reflects a Vendor-favorable risk allocation, provided that Zenith shall reasonably cooperate in transitioning services for a mutually agreed transition period not to exceed the notice period, subject to applicable Fees.

4.5 **Termination for Cause.** Either Party may terminate this SLA for cause, consistent with **Section 4.3 of the MSA**, upon written notice if the other Party:

  (a) materially breaches this SLA or the MSA with respect to the Managed Services and fails to cure such breach within thirty (30) days after receipt of written notice describing the breach in reasonable detail; or  

  (b) becomes insolvent or is subject to bankruptcy or similar proceedings that are not dismissed within sixty (60) days.

4.6 **Termination for Chronic SLA Failures.** In addition to the termination rights in the MSA and **Section 12.7** of the MSA, if Zenith fails to meet critical Service Levels (e.g., uptime or Severity 1 response times) in three (3) or more calendar months during any rolling six (6) month period, Contoso may terminate the affected SOW(s) and/or this SLA upon sixty (60) days’ written notice, without early termination penalty, but subject to payment of all accrued Fees.

4.7 **Effect of Termination.** Upon expiration or termination of this SLA:

  (a) Zenith shall cease providing the Managed Services covered by this SLA, except as necessary for orderly transition during any agreed wind-down period;  
  (b) Contoso shall pay all Fees and reimbursable expenses properly incurred through the effective date of termination, in accordance with **Section 4.5(b) of the MSA**;  
  (c) Zenith shall deliver to Contoso any Deliverables, reports, and documentation due or in progress as of the termination date; and  
  (d) the Parties shall promptly return or destroy Confidential Information in accordance with **Section 5.5** of the MSA and **Article V** of this SLA.

4.8 **Effect of Termination of Parent Agreement.** If the Parent Agreement (MSA-ZEN-202504-539) is terminated or expires:

  (a) this SLA shall automatically terminate as of the effective date of such termination or expiration, except to the extent the Parties expressly agree in writing to continue certain Managed Services under separate arrangements;  
  (b) any survival of rights and obligations under the MSA (including under **Articles V, VI, VIII, IX, XI, XIV, and XVI**) shall apply equally to this SLA; and  
  (c) any accrued SLA Credits or claims under this SLA shall be resolved in accordance with **Article XIV (Dispute Resolution)** of the MSA and this SLA.

4.9 **Survival.** Provisions of this SLA that by their nature should survive expiration or termination shall so survive, including without limitation **Articles V (Confidentiality), VI (Intellectual Property Rights), VII (Representations and Warranties), VIII (Indemnification), IX (Limitation of Liability), XI (Data Protection and Privacy), XIV (Dispute Resolution)**, and any payment obligations accrued prior to termination.

---

## ARTICLE V  
CONFIDENTIALITY

5.1 **Confidential Information.** The definition of “Confidential Information” in **Section 5.1 of the MSA** is hereby incorporated by reference and applies fully to all information exchanged under this SLA, including without limitation system architecture diagrams, security configurations, monitoring data, incident reports, and performance metrics.

5.2 **Obligations.** Each Party, as Receiving Party, shall:

  (a) use the Disclosing Party’s Confidential Information solely for purposes of performing or receiving services under the MSA and this SLA;  
  (b) not disclose such Confidential Information to any third party except as permitted under the MSA or this SLA; and  
  (c) protect such Confidential Information using the degree of care specified in **Section 5.3 of the MSA**, which shall in no event be less than reasonable care.

5.3 **Exceptions.** The exceptions to confidentiality in **Section 5.2 of the MSA** (public information, previously known, third-party disclosure, and independent development) shall apply equally to this SLA.

5.4 **Operational Use of Data.** Notwithstanding the foregoing, Zenith may use aggregated and anonymized data derived from its performance of the Managed Services (e.g., performance benchmarks, incident volumes) solely for internal analytics and service improvement, provided that such data does not disclose Contoso’s identity or any Confidential Information.

5.5 **Return or Destruction.** Upon expiration or termination of this SLA or upon request, each Party shall return or destroy the other Party’s Confidential Information in accordance with **Section 5.5 of the MSA**, subject to retention of archival copies for legal compliance.

5.6 **Survival Period.** The confidentiality obligations under this Article V shall survive for **five (5) years** following the expiration or termination of this SLA, consistent with **Section 5.6 of the MSA**, and trade secrets shall be protected for so long as they qualify as trade secrets under Applicable Law.

---

## ARTICLE VI  
INTELLECTUAL PROPERTY RIGHTS

6.1 **Ownership of Work Product.** Ownership of Work Product created in connection with the Managed Services shall be governed by **Article VI of the MSA**, including **Section 6.1 (Ownership of Work Product)**, whereby Contoso owns Work Product specifically created for it, subject to **Section 6.3 (Zenith Pre-Existing IP)**.

6.2 **Zenith Tools and Pre-Existing IP.** The Parties acknowledge that Zenith will utilize various proprietary tools, methodologies, monitoring scripts, runbooks, and frameworks in performing the Managed Services. Such items constitute **Zenith Pre-Existing IP** under **Section 6.3 of the MSA**, and Zenith retains all right, title, and interest thereto. To the extent such Pre-Existing IP is incorporated into the Work Product or is necessary for Contoso’s beneficial use of the Deliverables and Managed Services, Zenith grants Contoso the license set forth in **Section 6.3 of the MSA**, which is **perpetual, irrevocable, worldwide, non-exclusive, royalty-free**, and sublicensable to Contoso’s Affiliates and service providers for internal business operations.

6.3 **Vendor-Favorable Use Restrictions.** In addition to the restrictions in the MSA, and reflecting the high-risk, vendor-favorable nature of this SLA:

  (a) Contoso shall not reverse engineer, decompile, or disassemble any Zenith tools or Pre-Existing IP used in providing the Managed Services, except to the limited extent permitted by Applicable Law;  
  (b) Contoso shall not use Zenith’s Pre-Existing IP or proprietary methodologies to provide services to third parties that are competitive with Zenith’s offerings; and  
  (c) any feedback or suggestions provided by Contoso regarding enhancements to Zenith’s tools or services may be freely used by Zenith without obligation or restriction, and Zenith shall own all right, title, and interest in and to such enhancements.

6.4 **Third-Party Materials.** To the extent third-party software, tools, or cloud services are used in delivering the Managed Services, licensing and use thereof shall be governed by **Section 6.4 (Third-Party Materials)** of the MSA, and Contoso agrees to comply with any flow-down terms applicable to its use of such Third-Party Materials, as communicated by Zenith in writing.

6.5 **Residual Knowledge.** Zenith may use Residual Knowledge in accordance with **Section 6.5 of the MSA**, provided it does not disclose Contoso’s Confidential Information.

6.6 **Protection of IP.** Each Party shall comply with **Section 6.6 of the MSA** regarding the protection of the other Party’s Intellectual Property Rights.

---

## ARTICLE VII  
REPRESENTATIONS AND WARRANTIES

7.1 **Mutual Representations and Warranties.** Each Party reaffirms the mutual representations and warranties in **Section 7.1 of the MSA**, including authority, organization, and no conflicts, and represents that such warranties remain true and correct as of the SLA Effective Date.

7.2 **Zenith Service Warranty.** In addition to the warranties in **Section 7.2 of the MSA**, Zenith warrants that:

  (a) it will perform the Managed Services in a manner designed to meet or exceed the Service Levels specified in **Article XII** of this SLA;  
  (b) it shall maintain appropriate staffing, training, and escalation procedures commensurate with a high-risk, high-availability managed services environment; and  
  (c) it will maintain and apply reasonable security and operational best practices consistent with industry standards for similar services, in alignment with **Article XI (Data Protection and Privacy)** of the MSA and this SLA.

7.3 **Client Warranties.** Contoso warrants that:

  (a) it has all necessary rights to the systems, data, and materials that it makes available to Zenith for purposes of the Managed Services;  
  (b) its use of the Managed Services and Supported Systems will comply with Applicable Law; and  
  (c) it will not knowingly introduce into the Supported Systems any malicious code or tools that could compromise system stability or security.

7.4 **Remedies.** Remedies for breach of warranties in this Article VII shall be consistent with **Section 7.3 of the MSA**, including the right for Zenith to re-perform non-conforming services or, if unable to cure, for Contoso to terminate the affected SOWs and receive a refund of Fees paid for non-conforming services, without prejudice to other rights under this SLA and the MSA.

7.5 **Disclaimer.** Except as expressly provided in the MSA and this SLA, the disclaimers in **Section 7.4 of the MSA** apply equally to the Managed Services.

---

## ARTICLE VIII  
INDEMNIFICATION

8.1 **Indemnification by Zenith.** Zenith’s obligations to indemnify Contoso under **Article VIII of the MSA** are hereby reaffirmed and apply equally to claims arising from Zenith’s performance of the Managed Services under this SLA, including Claims relating to IP infringement, gross negligence, willful misconduct, or violation of Applicable Law.

8.2 **Additional Indemnification by Contoso (Vendor-Favorable).** In addition to the indemnification obligations in **Section 8.2 of the MSA**, and reflecting the high-risk, Vendor-favorable allocation:

  Contoso shall defend, indemnify, and hold harmless the **Zenith Indemnified Parties** from and against any and all Claims and Losses arising out of or relating to:  

  (a) Contoso’s misuse of the Managed Services or Supported Systems in violation of this SLA, the MSA, or Applicable Law;  
  (b) Contoso’s failure to implement reasonable security measures within its own environment that are clearly communicated by Zenith as preconditions for maintaining Service Levels or security posture; and  
  (c) any third-party claims alleging that Contoso’s combination of the Managed Services with non-Zenith systems, software, or data (where such combination is not recommended or approved by Zenith in writing) caused security incidents, downtime, or data loss.

8.3 **Indemnification Procedures.** The procedures in **Section 8.3 of the MSA** (notice, control of defense, and cooperation) shall govern any indemnification claims under this SLA.

8.4 **Exclusive Remedies.** Subject to **Article IX**, indemnification obligations in this Article VIII and **Article VIII of the MSA** shall constitute the indemnifying Party’s sole and exclusive liability for third-party claims of the types described therein.

---

## ARTICLE IX  
LIMITATION OF LIABILITY

9.1 **No Contractual Cap on Liability.** Notwithstanding **Section 9.2 of the MSA**, and in recognition of the high-risk nature of the Managed Services:

  The Parties agree that **no contractual monetary cap shall apply to Zenith’s or Contoso’s liability** arising out of or relating to this SLA or the Managed Services hereunder. Any references in **Section 9.2 of the MSA (Liability Cap)** to a limitation of liability tied to “five (5) times the total Fees” under an SOW shall **not** apply to claims arising solely under this SLA, and are hereby superseded for such claims.

9.2 **Consequential and Similar Damages Included.** Notwithstanding **Section 9.1 of the MSA**, and recognizing that Contoso’s business may suffer significant downstream effects from service interruptions:

  The Parties agree that **neither Party shall be excluded from liability for incidental, indirect, special, exemplary, or consequential damages**, including loss of profits, loss of data, loss of revenue, loss of business opportunities, or loss of goodwill, **to the extent such damages are reasonably foreseeable and causally connected** to a breach of this SLA, a Security Incident, or other wrongful act or omission. The exclusion of such damages in **Section 9.1 of the MSA** is expressly **modified and superseded** with respect to the Managed Services covered by this SLA.

9.3 **Exceptions and Risk Allocation.** Nothing in this Article IX shall limit or exclude liability for: (a) indemnification obligations under **Article VIII of this SLA and the MSA**; (b) breaches of confidentiality obligations under **Article V** of this SLA or **Article V of the MSA**; (c) data protection and Security Incidents as described in **Article XI** of this SLA and **Article XI of the MSA**; or (d) gross negligence or willful misconduct of a Party.

9.4 **Acknowledgment.** The Parties acknowledge that the risk allocation in this Article IX is unusual and more Vendor-favorable in certain respects (e.g., absence of a cap but recognition of potential large damages) in light of the high-risk classification and is a material inducement to Zenith’s agreement to provide high-availability managed services; each Party has had the opportunity to consult legal counsel about these provisions.

---

## ARTICLE X  
INSURANCE

10.1 **Required Coverage.** Zenith shall maintain, at its own cost, during the SLA Term and for at least one (1) year thereafter, insurance policies consistent with **Article X of the MSA**, including:

  (a) **Commercial General Liability** – minimum US $1,000,000 per occurrence; US $2,000,000 aggregate;  
  (b) **Professional Liability / Errors and Omissions** – minimum US $2,000,000 per claim and in aggregate;  
  (c) **Cyber Liability / Data Breach** – minimum US $2,000,000 per claim and in aggregate; and  
  (d) **Workers’ Compensation and Employers’ Liability** as required by Applicable Law.

Given the High-Risk Services, Zenith shall use commercially reasonable efforts to maintain coverage limits appropriate to the criticality of the services and shall notify Contoso if any material decrease occurs.

10.2 **Certificates of Insurance.** Upon Contoso’s request, Zenith shall provide certificates of insurance evidencing the required coverage and naming Contoso as an additional insured on applicable policies, consistent with **Section 10.2 of the MSA**.

10.3 **No Limitation.** Insurance requirements shall not limit Zenith’s or Contoso’s liability under this SLA or the MSA, consistent with **Section 10.3 of the MSA**.

---

## ARTICLE XI  
DATA PROTECTION AND PRIVACY

11.1 **Incorporation of MSA Provisions.** **Article XI (Data Protection and Privacy)** of the MSA is incorporated by reference and applies fully to all processing of Personal Data in connection with the Managed Services under this SLA.

11.2 **Data Processing Addendum.** Where Zenith processes Personal Data on behalf of Contoso in providing the Managed Services, the Parties shall enter into any required data processing addendum (DPA). Such DPA shall be deemed incorporated into this SLA and the MSA, and in case of conflict between this SLA and the DPA concerning data protection, the DPA shall control.

11.3 **Security Measures.** Zenith shall implement and maintain technical and organizational measures as required by **Section 11.2 of the MSA**, including network segmentation, encryption-at-rest and in-transit (where appropriate), robust access controls, periodic penetration testing, vulnerability management, and security monitoring appropriate to the High-Risk Services.

11.4 **Security Incidents; Notification.** In the event of a Security Incident (as defined in **Section 11.3 of the MSA**), Zenith shall:

  (a) notify Contoso in writing without undue delay and within seventy-two (72) hours of confirming the incident;  
  (b) provide regular updates on investigation progress, root cause, and remediation steps; and  
  (c) cooperate with Contoso in fulfilling any legal obligations to regulators or affected individuals, consistent with **Section 11.3 of the MSA**.

11.5 **Data Retention and Deletion.** Zenith shall retain and delete Personal Data and Contoso data as required in **Section 11.5 of the MSA**, including retention of system logs and incident data for at least twelve (12) months or such longer period as required by Applicable Law or mutually agreed for audit and forensic purposes.

11.6 **Cross-Border Transfers.** To the extent Personal Data is transferred internationally, Zenith shall comply with **Section 11.6 of the MSA**, implementing appropriate safeguards such as standard contractual clauses or other legally valid mechanisms.

---

## ARTICLE XII  
SERVICE LEVEL AGREEMENTS (SLAs)

This Article XII refines and expands the general SLA provisions of **Article XII of the MSA** for the High-Risk Services and Supported Systems governed by this SLA. To the extent of any conflict, this Article XII supersedes **Article XII of the MSA** for such services.

12.1 **Uptime Commitment.** For each production Supported System designated as high availability in the applicable SOW, Zenith shall use commercially reasonable efforts to ensure system availability of at least **99.95%** in each calendar month, calculated excluding the following:

  (a) Scheduled Maintenance during approved Maintenance Windows;  
  (b) downtime caused by Force Majeure Events (as defined in **Article XV of the MSA** and this SLA);  
  (c) downtime attributable to Contoso’s systems, networks, or third-party providers under Contoso’s control; and  
  (d) downtime resulting from Contoso’s failure to implement reasonable security or configuration steps previously communicated by Zenith in writing.

12.2 **Service Windows.**

  12.2.1 **Production Systems.** 24 hours per day, 7 days per week (24x7), including holidays.  
  12.2.2 **Non-Production Systems.** Business Hours, unless otherwise specified in the SOW.  
  12.2.3 **Service Desk.** Incident intake available 24x7 for Severity 1 and 2; during Business Hours for Severity 3 and 4, unless otherwise agreed.

12.3 **Incident Severity Levels and Response Targets.**

  - **Severity 1 (Critical Outage):**  
    - Criteria: Complete loss of a critical production business function or system; no workaround; severe impact to revenue or regulatory commitments.  
    - Initial Response: within **15 minutes** (24x7).  
    - Work Continuity: continuous efforts until resolution or mutually accepted workaround.  
    - Target Resolution/Workaround: within **4 hours**.

  - **Severity 2 (High):**  
    - Criteria: Significant degradation of performance or functionality; business operations impacted but critical functions still available; workaround possible but inconvenient.  
    - Initial Response: within **1 hour** (24x7).  
    - Target Resolution: within **8 Business Hours**.

  - **Severity 3 (Medium):**  
    - Criteria: Limited loss of non-critical functionality; moderate business impact; workaround is available.  
    - Initial Response: within **4 Business Hours**.  
    - Target Resolution: within **3 Business Days**.

  - **Severity 4 (Low):**  
    - Criteria: Cosmetic issues, informational inquiries, minor defects with minimal or no business impact.  
    - Initial Response: within **1 Business Day**.  
    - Target Resolution: within **10 Business Days**, or as mutually prioritized.

12.4 **Scheduled Maintenance.**

  (a) Zenith may perform scheduled maintenance during Maintenance Windows agreed with Contoso, typically during off-peak hours (e.g., Sunday 1:00 a.m.–5:00 a.m. Central Time).  
  (b) Zenith shall provide at least **five (5) Business Days’ prior written notice** of any maintenance expected to cause downtime or material performance degradation, except for emergency maintenance (e.g., critical security patches), for which Zenith shall give as much notice as reasonably practicable.  
  (c) Time during scheduled Maintenance Windows is excluded from uptime calculations under **Section 12.1**.

12.5 **Measurement and Reporting.** Zenith shall:

  (a) measure uptime using monitoring tools reasonably acceptable to Contoso;  
  (b) provide monthly SLA reports to Contoso no later than fifteen (15) days after month-end; and  
  (c) retain monitoring data and incident records for at least twelve (12) months.

12.6 **SLA Credits.** If Zenith fails to meet the uptime commitment under **Section 12.1** for a Supported System in a given month, Contoso shall be entitled to Service Credits as follows (example schedule; may be superseded by SOW):

  - Uptime ≥ 99.95%: no credit  
  - 99.5% ≤ Uptime < 99.95%: credit equal to **5%** of the monthly recurring Fee for that Supported System  
  - 99.0% ≤ Uptime < 99.5%: credit equal to **10%** of the monthly recurring Fee  
  - Uptime < 99.0%: credit equal to **20%** of the monthly recurring Fee

Service Credits shall be the **sole and exclusive monetary remedy** for SLA failures, **except** where such failures constitute a material breach giving rise to termination rights under **Section 4.6** or where they result from Zenith’s gross negligence or willful misconduct.

12.7 **Exclusions.** Zenith shall not be deemed to have failed a Service Level to the extent the failure is caused by:

  (a) Force Majeure Events (Article XV);  
  (b) Contoso’s breach of its obligations under the MSA or this SLA;  
  (c) acts or omissions of third parties not under Zenith’s control; or  
  (d) Contoso’s failure to implement patches, configuration changes, or recommended mitigations provided by Zenith in writing and within a reasonable time, where such failure materially contributes to the incident.

---

## ARTICLE XIII  
CHANGE MANAGEMENT

13.1 **Change Requests.** Either Party may submit a written **Change Request** proposing modifications to the Managed Services, Supported Systems, Service Levels, or other aspects of this SLA or relevant SOWs, in accordance with **Article XIII of the MSA**.

13.2 **Impact Assessment.** Upon receipt of a Change Request from Contoso, Zenith shall provide an impact assessment within a reasonable time (typically within ten (10) Business Days), including proposed changes to Fees, timelines, Service Levels, and risk profile.

13.3 **Approval and Change Orders.** No Change Request shall be binding unless agreed in a written Change Order signed by both Parties, consistent with **Section 13.3 of the MSA**. Once executed, such Change Order shall amend this SLA and/or the applicable SOW.

13.4 **Emergency Changes.** For urgent security patches or changes necessary to prevent imminent harm or service disruption, Zenith may implement changes without prior written Change Order, provided that:

  (a) Zenith notifies Contoso as soon as reasonably practicable; and  
  (b) the Parties subsequently document such changes in writing, including any impact on Service Levels or Fees.

13.5 **Proceeding with Existing Scope.** Until a Change Order is executed, each Party shall continue to perform in accordance with the existing SLA and SOWs, as required by **Section 13.4 of the MSA**.

---

## ARTICLE XIV  
DISPUTE RESOLUTION

14.1 **Informal Dispute Resolution.** Disputes arising under or related to this SLA shall be resolved in accordance with **Article XIV of the MSA** (Informal Resolution, Escalation, Mediation, and Litigation/Arbitration). The Parties shall first seek to resolve disputes through operational discussions and executive escalation before resorting to formal proceedings.

14.2 **SLA-Specific Disputes.** For disputes related to SLA measurements, Service Credits, or Incident severity classifications:

  (a) The Parties shall meet (virtually or in person) within ten (10) Business Days of a written dispute notice to review monitoring data, logs, and relevant documentation;  
  (b) If the Parties cannot resolve the dispute at the operational level, the matter shall be escalated to senior executives under **Section 14.2 of the MSA**; and  
  (c) If unresolved, the dispute may proceed to mediation and, if necessary, litigation in the courts specified in **Section 16.8 of the MSA** (Dallas County, Texas).

14.3 **Interim Performance.** During any dispute, Zenith shall continue to provide the Managed Services and Contoso shall continue to pay undisputed amounts, consistent with the MSA.

---

## ARTICLE XV  
FORCE MAJEURE

15.1 **Force Majeure Events.** Force Majeure Events shall have the meaning set forth in **Section 15.1 of the MSA** and include events beyond a Party’s reasonable control that prevent or delay the performance of obligations under this SLA.

15.2 **Notice and Mitigation.** The affected Party shall comply with **Section 15.2 of the MSA**, including prompt notice, description of impact, and efforts to mitigate.

15.3 **Suspension of Performance.** During a Force Majeure Event, performance obligations under this SLA may be suspended in accordance with **Section 15.3 of the MSA**, except that Zenith shall use commercially reasonable efforts to maintain or restore critical services to Contoso’s high-risk Supported Systems as quickly as practicable.

15.4 **Extended Force Majeure.** If a Force Majeure Event continues for more than sixty (60) consecutive days and materially affects the Managed Services, either Party may terminate the affected SOWs and the relevant portions of this SLA in accordance with **Section 15.4 of the MSA**.

---

## ARTICLE XVI  
GENERAL PROVISIONS

16.1 **Reference to Master/Parent Agreement.**  
This **Service Level Agreement is executed under and subject to the terms of Master Services Agreement reference number MSA-ZEN-202504-539 (contract_539)**. Except as expressly modified herein (including, without limitation, **Article IX (Limitation of Liability)** of this SLA superseding **Article IX of the MSA** with respect to the Managed Services), all terms and conditions of the Master Services Agreement remain in full force and effect and are incorporated by reference.

16.2 **Entire Agreement.** This SLA, together with the Master Services Agreement and all applicable SOWs, Change Orders, and DPAs, constitutes the entire agreement between the Parties with respect to the Managed Services and Service Levels described herein and supersedes any prior understandings or agreements specific to such services.

16.3 **Amendments.** No amendment or modification of this SLA shall be effective unless in writing and signed by authorized representatives of both Parties, in accordance with **Section 16.2 of the MSA**, expressly referencing this SLA and, where applicable, the Contract Reference No. **SLA-ZEN-202504-629**.

16.4 **Severability.** If any provision of this SLA is held invalid or unenforceable, such provision shall be modified to the minimum extent necessary to make it enforceable, and the remainder shall remain in full force and effect, consistent with **Section 16.3 of the MSA**.

16.5 **Waiver.** Any waiver of a term under this SLA must comply with **Section 16.4 of the MSA** and shall not be deemed a waiver of any other term or subsequent breach.

16.6 **Assignment.** Assignment of this SLA shall be governed by **Section 16.5 of the MSA**. Any assignment must include this SLA as part of the assigned agreements.

16.7 **Independent Contractors.** The Parties’ relationship remains that of independent contractors, as set forth in **Section 16.6 of the MSA**. Nothing in this SLA creates a partnership, joint venture, or agency relationship.

16.8 **Notices.** All notices under this SLA shall be given in accordance with **Section 16.7 of the MSA** to the addresses specified therein for Contoso and Zenith or such other addresses as a Party may designate in writing.

16.9 **Governing Law and Venue.** This SLA shall be governed by and construed in accordance with the laws of the **State of Texas**, without regard to conflict of law principles, consistent with **Section 16.8 of the MSA**, and any action arising hereunder shall be brought in the state or federal courts located in **Dallas County, Texas**.

16.10 **Publicity.** Publicity provisions in **Section 16.9 of the MSA** apply to this SLA. Zenith shall not reference this SLA or describe Service Levels provided to Contoso in external marketing materials without Contoso’s prior written consent.

16.11 **Counterparts; Electronic Signatures.** This SLA may be executed in counterparts, and electronic signatures shall be treated as originals, consistent with **Section 16.10 of the MSA**.

16.12 **Survival.** Sections of this SLA which by their nature should survive termination or expiration, including Articles **V, VI, VII, VIII, IX, XI, XIV, and XVI**, shall so survive.

---

## SIGNATURES

IN WITNESS WHEREOF, the Parties have caused this Service Level Agreement (Contract Reference No. **SLA-ZEN-202504-629**) to be executed by their duly authorized representatives as of the SLA Effective Date first above written.

**Executed pursuant to MSA-ZEN-202504-539 (contract_539).**

---

### CONTOSO ENTERPRISES  
(“Client” / “Company”)

By: ___________________________________________  
Name: _________________________________________  
Title: __________________________________________  
Date: __________________________________________  

Witness (if applicable): ___________________________  
Name: _________________________________________  
Title: __________________________________________  

---

### ZENITH TECHNOLOGIES  
(“Vendor” / “Service Provider”)

By: ___________________________________________  
Name: _________________________________________  
Title: __________________________________________  
Date: __________________________________________  

Witness (if applicable): ___________________________  
Name: _________________________________________  
Title: __________________________________________  

---

**[End of Service Level Agreement – SLA-ZEN-202504-629]**