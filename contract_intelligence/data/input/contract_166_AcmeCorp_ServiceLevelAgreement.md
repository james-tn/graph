# SERVICE LEVEL AGREEMENT  
**Contract Reference Number: SLA-ACM-202407-166**

---

## SERVICE LEVEL AGREEMENT  
**Between**  
**Contoso Enterprises** and **Acme Corp**  

Effective Date: **July 29, 2024**  
Expiration Date: **August 14, 2027**  
Contract Value: **USD $3,147,471**  
Payment Terms: **Net 60**  
Governing Law: **State of Washington (USA)**  
Risk Level: **High**

---

## PREAMBLE & RECITALS

This **Service Level Agreement** (this "**Agreement**" or this "**SLA**"), Contract Reference Number **SLA-ACM-202407-166**, is entered into as of **July 29, 2024** (the "**Effective Date**"), by and between:

1. **Contoso Enterprises**, a Washington corporation, having its principal place of business at  
   **1000 Contoso Way, Suite 500, Seattle, WA 98101, USA**  
   (hereinafter referred to as "**Contoso**", the "**Client**", or the "**Company**"),

and

2. **Acme Corp**, a Delaware corporation, having its principal place of business at  
   **2000 Acme Plaza, Floor 18, San Francisco, CA 94105, USA**  
   (hereinafter referred to as "**Acme**", the "**Vendor**", or the "**Service Provider**").

Contoso and Acme are sometimes referred to herein individually as a "**Party**" and collectively as the "**Parties**".

### RECITALS

**WHEREAS**, Contoso is engaged in the business of developing, marketing, and supporting enterprise solutions and desires to engage a third-party service provider to deliver certain managed technology services, hosting, and support as further described herein;

**WHEREAS**, Acme is in the business of providing cloud-based hosting, managed infrastructure, application support, and related professional services and represents that it has the requisite expertise, personnel, equipment, and infrastructure to perform such services in accordance with the terms and conditions set forth in this Agreement;

**WHEREAS**, Contoso desires to retain Acme, and Acme desires to be retained by Contoso, to provide the Services (as defined below), subject to and in accordance with the terms and conditions of this Agreement, including the service levels and performance standards specified herein;

**WHEREAS**, the Parties acknowledge that this Agreement is classified by Contoso as **High Risk**, and accordingly, the Parties have agreed to enter into certain risk allocations, including, without limitation, broad indemnification by Client, certain restrictive intellectual property terms favoring Vendor, longer termination notice periods, and uncapped liability;

**NOW, THEREFORE**, in consideration of the mutual covenants and promises contained herein, and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the Parties hereby agree as follows:

---

## ARTICLE I – DEFINITIONS

1.1 **"Affiliate"** means, with respect to a Party, any entity that directly or indirectly controls, is controlled by, or is under common control with such Party, where "control" means the ownership of more than fifty percent (50%) of the voting interests of such entity or the power to direct or cause the direction of the management and policies of such entity, whether through ownership, contract, or otherwise.

1.2 **"Agreement"** or **"SLA"** means this Service Level Agreement, Contract Reference Number **SLA-ACM-202407-166**, including all exhibits, schedules, attachments, Statements of Work, and any written amendments hereto executed by duly authorized representatives of both Parties.

1.3 **"Applicable Law"** means any statute, law, rule, regulation, ordinance, code, directive, or order of any governmental authority having jurisdiction over a Party, the Services, or this Agreement, including, without limitation, laws relating to data protection, privacy, employment, export control, and intellectual property.

1.4 **"Business Day"** means any day other than a Saturday, Sunday, or a day on which banks in Seattle, Washington, USA are authorized or required by law to remain closed.

1.5 **"Confidential Information"** has the meaning set forth in Section 5.1.

1.6 **"Client Data"** means all data, content, records, files, information, materials, and other items (including Personal Data) that are provided, uploaded, transmitted, or otherwise made available by or on behalf of Contoso to Acme in connection with the Services, or that are generated specifically for Contoso by the Services, excluding Acme’s tools, templates, and underlying system data.

1.7 **"Data Protection Laws"** means all data protection, data security, and privacy laws, regulations, and guidance applicable to the processing of Personal Data under this Agreement, including, without limitation, the EU General Data Protection Regulation (Regulation (EU) 2016/679) ("**GDPR**"), the UK General Data Protection Regulation, the California Consumer Privacy Act (Cal. Civ. Code §1798.100 et seq.) ("**CCPA**"), as amended by the California Privacy Rights Act, and any similar applicable laws.

1.8 **"Deliverables"** means any software configurations, reports, specifications, documentation, analyses, integrations, scripts, and other work product (tangible or intangible) that Acme is expressly obligated to deliver to Contoso under this Agreement or any Statement of Work, excluding Acme’s Pre-Existing IP and Acme’s generally applicable platform and services.

1.9 **"Documentation"** means all written or electronic user manuals, technical manuals, specifications, and related materials describing the features, functions, and operation of the Services, as generally made available by Acme to its customers.

1.10 **"Force Majeure Event"** has the meaning set forth in Section 15.1.

1.11 **"Incident"** means any event that is not part of the standard operation of the Services and that causes, or may cause, an interruption to, or a reduction in the quality of, the Services, including, without limitation, unplanned downtime, performance degradation, or security events.

1.12 **"Intellectual Property Rights"** or **"IPR"** means all worldwide rights in, to, or arising out of patents, patent applications, inventions, copyrights, moral rights, trademarks, trade names, service marks, logos, domain names, trade dress, trade secrets, know-how, and all other intellectual property or proprietary rights, whether registered or unregistered, and all applications, registrations, renewals, and extensions thereof.

1.13 **"Maintenance Window"** means a pre-scheduled period during which the Services may be unavailable to permit planned maintenance, upgrades, or repairs, as described in Article XII.

1.14 **"Personal Data"** means any information relating to an identified or identifiable natural person, to the extent such information is processed by Acme on behalf of Contoso in connection with the Services and is subject to Data Protection Laws.

1.15 **"Service Availability"** means the percentage of time during a given calendar month that the production environment of the Services is available for access and use by Contoso, excluding Permitted Downtime (as defined in Article XII).

1.16 **"Services"** means the hosting, managed services, support, professional services, and any other services provided by Acme to Contoso under this Agreement, as more particularly described in Article II and any applicable Statements of Work.

1.17 **"Service Credits"** means the financial or service-based credits issued by Acme to Contoso as the sole and exclusive remedy (except as otherwise expressly stated) for Acme’s failure to meet certain Service Levels, as specified in Article XII.

1.18 **"Service Levels"** means the performance standards, metrics, and thresholds applicable to the Services, including, without limitation, uptime, response time, resolution time, and incident handling, as set forth in Article XII.

1.19 **"Statement of Work"** or **"SOW"** means a written, signed document referencing this Agreement that describes specific Services and Deliverables, timelines, fees, and other project-specific terms.

1.20 **"Third-Party Materials"** means software, content, data, or other materials owned by third parties (other than Affiliates of Acme) and provided or used in connection with the Services.

---

## ARTICLE II – SCOPE OF SERVICES / WORK

2.1 **Overview of Services.**  
Acme shall provide to Contoso the Services described in this Article II and any applicable SOWs. The Services shall include, without limitation, (a) cloud hosting and managed infrastructure for Contoso’s enterprise applications, (b) platform administration and monitoring, (c) incident management and technical support, (d) routine maintenance and updates, and (e) professional services for configuration, integration, and optimization of the hosted environment.

2.2 **Hosting and Infrastructure Services.**  
(a) **Environment.** Acme shall provision and maintain a multi-tenant or dedicated hosting environment, as specified in an applicable SOW, within data centers that meet industry-standard security and availability requirements. Such environment shall include compute resources, storage, networking, load balancing, and backup systems adequate to support Contoso’s anticipated usage as specified by Contoso.  

(b) **Capacity Planning.** Acme shall conduct capacity planning on at least a quarterly basis and shall recommend adjustments to the hosting resources as needed to meet the Service Levels. Any increase in capacity requested by Contoso and approved by Acme shall be subject to additional fees as set forth in Article III or the applicable SOW.  

(c) **Backups.** Acme shall perform daily backups of Client Data stored in the production environment and shall retain such backups for a minimum of thirty (30) days, unless otherwise specified in an SOW or required by Applicable Law. Backup restoration shall be performed upon Contoso’s written request and may be subject to reasonable professional service fees.

2.3 **Application Management and Support.**  
(a) **Monitoring.** Acme shall provide continuous (24x7x365) monitoring of the production environment, including application processes, database performance, server health, and network connectivity.  

(b) **Incident Management.** Acme shall classify Incidents in accordance with severity levels defined in Article XII and shall respond to, and use commercially reasonable efforts to resolve, such Incidents within the applicable response and resolution times.  

(c) **Service Desk.** Acme shall provide a service desk accessible via email, web portal, and phone during the support hours described in Article XII for technical support, incident reporting, and service requests by authorized Contoso personnel.

2.4 **Maintenance and Updates.**  
(a) **Planned Maintenance.** Acme may perform planned maintenance during a Maintenance Window as defined in Article XII. Acme shall provide Contoso with at least five (5) Business Days’ prior notice of any planned maintenance that is reasonably expected to cause Service unavailability.  

(b) **Emergency Maintenance.** In the event of an emergency requiring immediate maintenance to address a critical security vulnerability or threat to Service integrity, Acme may perform such maintenance without prior notice; provided, however, that Acme shall use commercially reasonable efforts to notify Contoso promptly and to minimize any adverse impact on Service Availability.  

(c) **Updates and Upgrades.** Acme may implement updates, patches, and upgrades to the Services from time to time in its discretion, including changes to underlying infrastructure or software, provided that such changes do not materially diminish the core functionality of the Services. Acme shall provide reasonable notice of material changes to the Services.

2.5 **Professional Services and Deliverables.**  
(a) **Implementation and Onboarding.** Acme shall perform initial implementation and onboarding services as described in an applicable SOW, which may include environment setup, configuration, data migration, integration with Contoso’s systems, and validation testing.  

(b) **Custom Configurations and Integrations.** Where specified in an SOW, Acme shall develop custom configurations, connectors, or integrations to third-party systems, subject to Contoso providing necessary access, information, and cooperation. Any scope changes shall be handled pursuant to Article XIII (Change Management).  

(c) **Deliverables.** Acme shall deliver to Contoso the Deliverables identified in each SOW. Unless expressly stated otherwise in such SOW, all delivery dates shall be non-binding estimates, and Acme shall use commercially reasonable efforts to meet such dates. The Parties acknowledge that dependencies on Contoso (e.g., provision of data, approvals, or access) may impact the timelines.

2.6 **Performance Standards.**  
The Services shall be performed in a professional and workmanlike manner, in accordance with generally accepted industry standards for similar services and the Service Levels specified in Article XII. Contoso acknowledges that all performance obligations are subject to: (a) Contoso’s compliance with its obligations under this Agreement; (b) availability and performance of third-party networks and systems; and (c) exclusions and permitted downtimes as defined in Article XII.

2.7 **Contoso Responsibilities.**  
(a) **Cooperation.** Contoso shall provide timely cooperation, information, decisions, approvals, and access to systems, facilities, and personnel as reasonably required by Acme to perform the Services.  

(b) **Authorized Users.** Contoso shall designate authorized users and administrators and shall be responsible for maintaining the confidentiality and security of user credentials, and for all actions taken under such credentials.  

(c) **Use Restrictions.** Contoso shall use the Services solely for lawful business purposes and in accordance with the Documentation and this Agreement. Contoso shall not: (i) use the Services to store or transmit malicious code; (ii) interfere with or disrupt the integrity or performance of the Services or third-party data; (iii) attempt to gain unauthorized access to the Services or related systems; or (iv) reverse engineer or attempt to derive the source code of any software provided by Acme, except to the limited extent permitted by Applicable Law notwithstanding contractual prohibition.

(d) **Compliance.** Contoso shall be solely responsible for determining whether the Services meet Contoso’s regulatory and legal requirements, and for ensuring that its use of the Services complies with all Applicable Laws, including the configuration of privacy settings, security controls, and other parameters within Contoso’s control.

2.8 **Subcontracting.**  
Contoso acknowledges and agrees that Acme may engage subcontractors and third-party service providers to perform portions of the Services; provided that Acme shall remain responsible for the performance of such subcontractors and for compliance with Acme’s obligations under this Agreement.

---

## ARTICLE III – FEES AND PAYMENT TERMS

3.1 **Fees.**  
In consideration for the Services, Contoso shall pay to Acme the fees set forth in this Agreement and any applicable SOWs, which collectively shall not be less than the total Contract Value of **USD $3,147,471** over the Initial Term (as defined in Section 4.1), subject to any authorized adjustments pursuant to Article XIII.

3.2 **Fee Structure.**  
The fees shall consist of some or all of the following components, as specified in the applicable SOW(s):

(a) **Base Subscription Fees.** A recurring monthly or annual fee for access to and use of the hosted Services, calculated based on user counts, capacity, or other usage metrics as specified in the SOW.  

(b) **Professional Services Fees.** Time-and-materials or fixed-fee charges for implementation, configuration, integration, and other professional services.  

(c) **Additional Usage Fees.** Charges for additional storage, bandwidth, or other resources consumed in excess of the baseline amounts set forth in the SOW.  

(d) **Support and Maintenance Fees.** Fees for enhanced support tiers or premium services, if any, beyond the standard support included with the base subscription.

3.3 **Invoicing.**  
Unless otherwise stated in an SOW:

(a) Base subscription and recurring fees shall be invoiced in advance on a quarterly basis.  

(b) Time-and-materials professional services fees shall be invoiced monthly in arrears based on actual hours incurred.  

(c) Fixed-fee professional services may be invoiced (i) fifty percent (50%) upon SOW execution and (ii) fifty percent (50%) upon completion of key milestones identified in the SOW.  

(d) Additional usage fees and reimbursable expenses shall be invoiced monthly in arrears.

3.4 **Payment Terms.**  
All undisputed amounts invoiced by Acme shall be due and payable by Contoso within **sixty (60) days** from the invoice date (**Net 60**). Payments shall be made in U.S. Dollars by wire transfer, ACH, or other mutually agreed method.

3.5 **Late Payments.**  
Any undisputed amount not paid when due shall accrue interest at a rate equal to the lesser of (a) one and one-half percent (1.5%) per month or (b) the maximum rate permitted by Applicable Law, from the due date until the date of payment. In addition, if any undisputed amounts remain unpaid for more than thirty (30) days after written notice of non-payment, Acme may, in its sole discretion, suspend the Services in whole or in part until such amounts are paid in full, without liability to Contoso, and such suspension shall not constitute a breach by Acme.

3.6 **Disputed Amounts.**  
Contoso may withhold payment of invoiced amounts that are subject to a good-faith dispute, provided that Contoso: (a) pays all undisputed amounts by the applicable due date; (b) notifies Acme in writing of the dispute within thirty (30) days of the invoice date, specifying the reasons; and (c) cooperates with Acme in good faith to resolve the dispute promptly. Any portion of a disputed amount finally resolved in Acme’s favor shall be paid by Contoso within thirty (30) days after such resolution.

3.7 **Taxes.**  
All fees are exclusive of any sales, use, value-added, goods and services, withholding, or similar taxes, duties, or other governmental assessments (collectively, "**Taxes**"), except for taxes based on Acme’s net income, property, or employees. Contoso shall be responsible for all applicable Taxes arising from the transactions under this Agreement. If Acme is required to pay any Taxes for which Contoso is responsible, Contoso shall reimburse Acme within thirty (30) days of receiving written notice thereof.

3.8 **Expenses.**  
To the extent specified in an SOW, Contoso shall reimburse Acme for reasonable, pre-approved, out-of-pocket travel and related expenses incurred by Acme in performing the Services. Acme shall provide reasonable supporting documentation for all reimbursable expenses.

3.9 **No Withholding or Set-Off.**  
Except as expressly permitted with respect to disputed amounts under Section 3.6, all payments shall be made without any deduction or withholding for any counterclaim, set-off, recoupment, or other claim.

---

## ARTICLE IV – TERM AND TERMINATION

4.1 **Term.**  
This Agreement shall commence on the Effective Date and shall continue in full force and effect until **August 14, 2027** (the "**Initial Term**"), unless earlier terminated in accordance with this Article IV.

4.2 **Renewal.**  
Upon expiration of the Initial Term, this Agreement shall automatically renew for successive one (1) year periods (each, a "**Renewal Term**") unless either Party provides written notice of non-renewal at least **one hundred eighty (180) days** prior to the end of the then-current term.

4.3 **Termination for Convenience.**  
Contoso may terminate this Agreement, in whole or in part, for convenience upon at least **one hundred eighty (180) days** prior written notice to Acme. Any such termination shall not relieve Contoso of its obligation to pay all fees and expenses incurred or committed by Acme up to the effective date of termination, including any non-cancellable third-party commitments.

4.4 **Termination for Cause.**  
(a) **By Either Party.** Either Party may terminate this Agreement upon written notice if the other Party materially breaches this Agreement and fails to cure such breach within sixty (60) days after receiving written notice thereof from the non-breaching Party.  

(b) **Insolvency.** Either Party may terminate this Agreement immediately upon written notice if the other Party becomes insolvent, files or has filed against it a petition in bankruptcy that is not dismissed within sixty (60) days, or ceases to do business in the ordinary course.

4.5 **Suspension.**  
Without limiting its other rights or remedies, Acme may suspend the Services in whole or in part immediately upon written notice if: (a) Contoso materially breaches Sections 2.7 or 11; (b) Contoso’s use of the Services poses a material security risk, violates Applicable Law, or may subject Acme to third-party liability; or (c) undisputed fees remain unpaid as described in Section 3.5. Acme shall resume the Services promptly upon remedy of the applicable condition.

4.6 **Effect of Termination.**  
Upon expiration or termination of this Agreement for any reason:

(a) All rights of access and use of the Services granted to Contoso shall immediately cease.  

(b) Each Party shall promptly return or destroy (at the disclosing Party’s option) the other Party’s Confidential Information in accordance with Section 5.5.  

(c) Contoso shall pay Acme all amounts due and payable for Services performed and expenses incurred through the effective date of termination, including any applicable early termination fees expressly provided in an SOW.  

(d) Unless otherwise requested by Contoso in writing, Acme shall retain Client Data for a period of thirty (30) days following the effective date of termination, during which Contoso may request a copy of Client Data. Thereafter, Acme may delete Client Data in accordance with its standard data retention and deletion policies, subject to Section 11.8.

4.7 **Survival.**  
Any provision of this Agreement that by its nature should survive expiration or termination shall so survive, including, without limitation, Sections 3.5–3.9, 4.6–4.7, Articles V, VI, VII, VIII, IX, X, XI, XIV, XV, and XVI.

---

## ARTICLE V – CONFIDENTIALITY

5.1 **Definition of Confidential Information.**  
"**Confidential Information**" means any non-public, proprietary, or confidential information disclosed by or on behalf of a Party (the "**Disclosing Party**") to the other Party (the "**Receiving Party**") in connection with this Agreement, whether orally, visually, in writing, or in any other form, that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information and the circumstances of disclosure. Confidential Information includes, without limitation, business plans, pricing, financial information, customer data, processes, technology, product information, security information, network diagrams, and, in the case of Contoso, Client Data.

5.2 **Exclusions.**  
Confidential Information does not include information that: (a) is or becomes publicly available through no breach of this Agreement by the Receiving Party; (b) was lawfully known to the Receiving Party without restriction prior to disclosure by the Disclosing Party; (c) is lawfully received from a third party without restriction on disclosure; or (d) is independently developed by the Receiving Party without use of or reference to the Disclosing Party’s Confidential Information.

5.3 **Obligations.**  
The Receiving Party shall: (a) use the Disclosing Party’s Confidential Information solely for the purpose of performing or receiving the Services under this Agreement; (b) not disclose such Confidential Information to any third party except as expressly permitted herein; and (c) protect such Confidential Information using at least the same degree of care that it uses to protect its own confidential information of similar importance, and in no event less than reasonable care.

5.4 **Permitted Disclosures.**  
The Receiving Party may disclose the Disclosing Party’s Confidential Information to its employees, contractors, Affiliates, and professional advisors who have a "need to know" such information for purposes of this Agreement and who are bound by confidentiality obligations no less protective than those set forth herein. The Receiving Party shall remain responsible for any breach of this Article V by such persons.

5.5 **Compelled Disclosure.**  
If the Receiving Party is required by law, regulation, or court order to disclose any Confidential Information, the Receiving Party shall, to the extent legally permitted, provide the Disclosing Party with prompt written notice and cooperate with the Disclosing Party, at the Disclosing Party’s expense, in seeking a protective order or other appropriate remedy. If no such remedy is obtained, the Receiving Party may disclose only that portion of the Confidential Information that it is legally required to disclose.

5.6 **Return or Destruction.**  
Upon the Disclosing Party’s written request or upon expiration or termination of this Agreement, the Receiving Party shall promptly return or destroy (at the Disclosing Party’s option) all copies of the Disclosing Party’s Confidential Information in its possession or control, except that the Receiving Party may retain (a) one archival copy for legal and compliance purposes and (b) such copies as are stored in routine back-up systems, in each case subject to ongoing confidentiality obligations under this Agreement.

5.7 **Survival.**  
The obligations set forth in this Article V shall remain in effect for a period of **five (5) years** after expiration or termination of this Agreement, except with respect to trade secrets, which shall be protected for so long as they qualify as trade secrets under Applicable Law.

---

## ARTICLE VI – INTELLECTUAL PROPERTY RIGHTS

6.1 **Ownership of Pre-Existing IP.**  
Each Party shall retain all right, title, and interest in and to its Pre-Existing IP. "Pre-Existing IP" means any Intellectual Property Rights owned or controlled by a Party prior to the Effective Date or developed by such Party independently of this Agreement, including enhancements, modifications, and derivative works thereof that are not specifically created for the other Party hereunder.

6.2 **Ownership of Services and Acme IP.**  
Contoso acknowledges and agrees that Acme and its licensors own all right, title, and interest in and to: (a) the Services, including all software, platforms, tools, algorithms, and technologies used to provide the Services; (b) any enhancements, modifications, and derivative works of the Services; (c) all Acme Templates, methodologies, and know-how; and (d) all related Intellectual Property Rights (collectively, "**Acme IP**"). Except for the limited rights expressly granted in this Agreement, no rights are granted to Contoso with respect to Acme IP, whether by implication, estoppel, or otherwise.

6.3 **Ownership of Deliverables.**  
Unless expressly stated otherwise in an SOW, and subject to Section 6.2, Acme shall retain ownership of all Intellectual Property Rights in Deliverables and any underlying Acme IP. Acme hereby grants to Contoso a non-exclusive, worldwide, non-transferable (except as permitted under Section 16.5), non-sublicensable license to use such Deliverables internally for Contoso’s business purposes in connection with its authorized use of the Services, for the term of this Agreement.

6.4 **Client Data.**  
As between the Parties, Contoso retains all right, title, and interest in and to Client Data and all Intellectual Property Rights therein. Contoso grants to Acme a non-exclusive, worldwide, royalty-free license to process Client Data as reasonably necessary for Acme to perform the Services and to improve, secure, and operate its services, including the right to generate aggregated and anonymized data as described in Section 6.5.

6.5 **Aggregated Data.**  
Acme may generate and use aggregated, de-identified, and anonymized data derived from Client Data and Contoso’s use of the Services ("Aggregated Data") for its legitimate business purposes, including product development, analytics, and benchmarking, provided that such Aggregated Data does not identify Contoso or any individual and does not contain Personal Data.

6.6 **Restrictions.**  
Contoso shall not: (a) reproduce, modify, adapt, translate, or create derivative works of the Services or Acme IP; (b) sublicense, lease, or provide access to the Services to any third party, except as expressly permitted; (c) remove or alter any proprietary notices or labels; or (d) use the Services to build a competitive product or service or reverse engineer the Services, except to the limited extent permitted by Applicable Law notwithstanding contractual prohibition.

6.7 **Feedback.**  
If Contoso or any of its users provides feedback, suggestions, or ideas regarding the Services ("Feedback"), Acme may freely use and exploit such Feedback without obligation or restriction, and Contoso hereby assigns all right, title, and interest in and to such Feedback to Acme.

---

## ARTICLE VII – REPRESENTATIONS AND WARRANTIES

7.1 **Mutual Representations and Warranties.**  
Each Party represents and warrants that: (a) it is duly organized, validly existing, and in good standing under the laws of its jurisdiction of incorporation; (b) it has full corporate power and authority to enter into this Agreement and to perform its obligations hereunder; (c) the execution, delivery, and performance of this Agreement have been duly authorized by all necessary corporate action; and (d) this Agreement constitutes a valid and binding obligation enforceable against such Party in accordance with its terms, subject to bankruptcy, insolvency, and other similar laws affecting creditors’ rights and general principles of equity.

7.2 **Acme Warranties.**  
Acme represents and warrants that: (a) it will perform the Services in a professional and workmanlike manner, in accordance with generally accepted industry standards and the Service Levels set forth in Article XII; and (b) the Services, when used by Contoso in accordance with this Agreement and the Documentation, will not infringe any third party’s Intellectual Property Rights in the United States, subject to the limitations in Article VIII.

7.3 **Contoso Warranties.**  
Contoso represents and warrants that: (a) it has and will maintain all rights, licenses, and consents necessary for Acme to process Client Data as contemplated by this Agreement; (b) Client Data does not infringe, misappropriate, or violate the rights of any third party; and (c) Contoso’s use of the Services will comply with Applicable Law and this Agreement.

7.4 **Disclaimer.**  
EXCEPT AS EXPRESSLY PROVIDED IN THIS ARTICLE VII, THE SERVICES AND DELIVERABLES ARE PROVIDED "AS IS" AND "AS AVAILABLE" AND ACME AND ITS LICENSORS DISCLAIM ALL OTHER WARRANTIES, WHETHER EXPRESS, IMPLIED, STATUTORY, OR OTHERWISE, INCLUDING ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, AND NON-INFRINGEMENT, AND ANY WARRANTIES ARISING FROM COURSE OF DEALING OR USAGE OF TRADE. ACME DOES NOT WARRANT THAT THE SERVICES WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ALL DEFECTS WILL BE CORRECTED.

---

## ARTICLE VIII – INDEMNIFICATION

8.1 **Indemnification by Acme.**  
Acme shall defend, indemnify, and hold harmless Contoso and its officers, directors, and employees ("Contoso Indemnitees") from and against any and all third-party claims, demands, suits, or proceedings ("Claims") and all resulting damages, liabilities, costs, and expenses (including reasonable attorneys’ fees) awarded by a court of competent jurisdiction or agreed in a written settlement approved by Acme arising out of or relating to: (a) any allegation that the Services, as provided by Acme and used by Contoso in accordance with this Agreement, infringe or misappropriate any U.S. Intellectual Property Right of a third party; or (b) Acme’s gross negligence or willful misconduct in the performance of the Services.

8.2 **Acme IP Infringement Remedies.**  
If the Services are subject to a Claim of infringement or misappropriation, or in Acme’s reasonable opinion are likely to become so, Acme may, at its option and expense: (a) procure for Contoso the right to continue using the Services; (b) replace or modify the Services so that they become non-infringing while retaining substantially equivalent functionality; or (c) if neither (a) nor (b) is commercially reasonable, terminate the infringing portion of the Services upon written notice and refund to Contoso any prepaid, unused fees for such portion. THIS SECTION 8.2 STATES CONTOSO’S SOLE AND EXCLUSIVE REMEDIES, AND ACME’S ENTIRE LIABILITY, FOR ANY CLAIMS OF INFRINGEMENT OR MISAPPROPRIATION.

8.3 **Indemnification by Contoso (Broad Client Indemnity – High Risk).**  
Contoso shall defend, indemnify, and hold harmless Acme, its Affiliates, and their respective officers, directors, employees, and contractors ("Acme Indemnitees") from and against any and all Claims and all resulting damages, liabilities, costs, and expenses (including reasonable attorneys’ fees) arising out of or relating to: (a) Contoso’s use of the Services in violation of this Agreement or Applicable Law; (b) Client Data, including any allegation that Client Data infringes, misappropriates, or violates any Intellectual Property Rights or privacy or other rights of any third party; (c) Contoso’s failure to obtain any consents or authorizations required under Data Protection Laws; or (d) Contoso’s gross negligence or willful misconduct.

8.4 **Indemnification Procedure.**  
The indemnified Party shall: (a) promptly notify the indemnifying Party in writing of any Claim for which indemnification is sought (provided that failure to give prompt notice shall not relieve the indemnifying Party of its obligations except to the extent materially prejudiced thereby); (b) grant the indemnifying Party sole control of the defense and settlement of the Claim; and (c) provide reasonable cooperation and assistance at the indemnifying Party’s expense. The indemnifying Party shall not settle any Claim that imposes any obligation or admission of liability on the indemnified Party without the indemnified Party’s prior written consent (not to be unreasonably withheld).

---

## ARTICLE IX – LIMITATION OF LIABILITY

9.1 **No Cap on Liability (High Risk).**  
NOTWITHSTANDING ANYTHING TO THE CONTRARY IN THIS AGREEMENT, THERE SHALL BE **NO CONTRACTUAL CAP** ON EITHER PARTY’S LIABILITY UNDER THIS AGREEMENT.

9.2 **Consequential and Related Damages (High Risk – Included).**  
TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, AND GIVEN THE HIGH-RISK CLASSIFICATION ACKNOWLEDGED BY THE PARTIES, **NEITHER PARTY EXCLUDES OR LIMITS** LIABILITY FOR INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE, OR CONSEQUENTIAL DAMAGES, LOSS OF PROFITS, LOSS OF REVENUE, LOSS OF BUSINESS, LOSS OF DATA, OR INTERRUPTION OF BUSINESS ARISING OUT OF OR RELATING TO THIS AGREEMENT, WHETHER IN CONTRACT, TORT (INCLUDING NEGLIGENCE), STRICT LIABILITY, OR OTHERWISE, EVEN IF SUCH PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES OR SUCH DAMAGES WERE OTHERWISE FORESEEABLE.

9.3 **Exceptions.**  
Nothing in this Article IX shall limit or exclude either Party’s liability to the extent such limitation or exclusion is prohibited by Applicable Law.

---

## ARTICLE X – INSURANCE

10.1 **Insurance Coverage.**  
During the term of this Agreement, Acme shall maintain, at its own expense, the following insurance coverage with financially sound and reputable insurers:

(a) **Commercial General Liability** with limits of not less than USD $2,000,000 per occurrence and USD $4,000,000 aggregate, covering bodily injury, property damage, and personal and advertising injury;  

(b) **Professional Liability / Errors & Omissions** (including technology E&O) with limits of not less than USD $5,000,000 per claim and aggregate;  

(c) **Cyber and Network Security Liability** with limits of not less than USD $5,000,000 per claim and aggregate, covering data breaches, privacy violations, network security failures, and media liability;  

(d) **Workers’ Compensation and Employers’ Liability** as required by Applicable Law; and  

(e) **Umbrella/Excess Liability** coverage of not less than USD $5,000,000 in excess of the underlying policies.

10.2 **Certificates of Insurance.**  
Upon Contoso’s reasonable request, Acme shall provide Contoso with certificates of insurance evidencing the coverage required hereunder. Such certificates shall provide that coverage shall not be cancelled or materially reduced without at least thirty (30) days’ prior written notice to Contoso, where such notice is reasonably obtainable.

10.3 **No Limitation.**  
Acme’s maintenance of insurance and its limits under this Article X shall not be construed to limit or restrict Acme’s liability under this Agreement.

---

## ARTICLE XI – DATA PROTECTION AND PRIVACY

11.1 **Roles of the Parties.**  
The Parties acknowledge that, with respect to Personal Data processed in connection with the Services, Contoso is the "controller" (or equivalent term under Data Protection Laws) and Acme is the "processor" (or equivalent term) acting on behalf of Contoso, except where Acme independently determines the purposes and means of processing in which case Acme may be deemed a separate controller.

11.2 **Compliance with Data Protection Laws.**  
Each Party shall comply with all applicable Data Protection Laws in relation to the processing of Personal Data under this Agreement. Acme shall process Personal Data only in accordance with Contoso’s documented instructions, this Agreement, and as required by Applicable Law.

11.3 **Security Measures.**  
Acme shall implement and maintain appropriate technical and organizational measures to protect Personal Data against accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to, Personal Data transmitted, stored, or otherwise processed, taking into account the state of the art, costs of implementation, the nature, scope, context, and purposes of processing, and the risks to the rights and freedoms of natural persons.

11.4 **Subprocessors.**  
Contoso hereby authorizes Acme to engage subprocessors to process Personal Data in connection with the Services, provided that Acme shall enter into written agreements with such subprocessors imposing data protection obligations no less protective than those set forth herein. Acme shall remain liable for the acts and omissions of its subprocessors.

11.5 **Data Subject Rights.**  
Taking into account the nature of the processing, Acme shall provide reasonable assistance to Contoso, at Contoso’s expense, in responding to requests from data subjects to exercise their rights under Data Protection Laws (including rights of access, rectification, erasure, restriction, and data portability).

11.6 **International Transfers.**  
To the extent the Services involve the transfer of Personal Data from the European Economic Area, United Kingdom, or other jurisdictions with data transfer restrictions to a country not deemed to provide an adequate level of protection, the Parties shall implement appropriate transfer mechanisms under Data Protection Laws (such as Standard Contractual Clauses or other approved mechanisms).

11.7 **Data Breach Notification.**  
In the event of a confirmed personal data breach affecting Personal Data processed by Acme under this Agreement, Acme shall notify Contoso without undue delay after becoming aware of the breach and shall provide information reasonably requested by Contoso to comply with its legal obligations, including: (a) the nature of the breach; (b) the categories and approximate number of data subjects and Personal Data records affected; (c) likely consequences; and (d) measures taken or proposed to address the breach. Unless prohibited by law or necessary to mitigate ongoing harm, Acme shall consult with Contoso before any notification to regulatory authorities or data subjects that specifically references Contoso.

11.8 **Data Retention and Deletion.**  
Subject to Section 4.6 and Applicable Law, Acme shall retain Personal Data only for as long as necessary to provide the Services or as required by law. Upon Contoso’s written request or upon termination of this Agreement, Acme shall delete or return Personal Data, except to the extent retention is required by law or necessary to establish, exercise, or defend legal claims. Deletion may take the form of secure deletion from active systems with overwriting in back-up systems in the ordinary course of business.

11.9 **CCPA.**  
For purposes of the CCPA, Acme shall act as a "service provider" (as defined under the CCPA) with respect to Personal Data that constitutes "personal information" of California residents processed on behalf of Contoso. Acme shall not: (a) sell such personal information; (b) retain, use, or disclose such personal information for any purpose other than for the specific purpose of performing the Services; or (c) retain, use, or disclose such personal information outside the direct business relationship between Acme and Contoso, except as permitted by CCPA.

---

## ARTICLE XII – SERVICE LEVEL AGREEMENTS

12.1 **Service Availability.**  
Acme shall use commercially reasonable efforts to achieve a monthly Service Availability of at least **99.9%** for the production environment of the Services, measured over each calendar month, excluding Permitted Downtime.

12.2 **Permitted Downtime.**  
"Permitted Downtime" means: (a) planned maintenance conducted during Maintenance Windows for which Acme has given required notice; (b) emergency maintenance; (c) downtime caused by Contoso’s systems, equipment, or acts or omissions; (d) failures of the public internet or third-party networks outside Acme’s reasonable control; (e) Force Majeure Events; and (f) suspensions authorized under this Agreement.

12.3 **Maintenance Windows.**  
Acme may schedule regular Maintenance Windows between 12:00 a.m. and 4:00 a.m. Pacific Time on Sundays and such additional times as reasonably necessary. Planned maintenance likely to cause Service unavailability shall not exceed eight (8) hours per calendar month, absent emergency circumstances.

12.4 **Incident Severity and Response.**  

- **Severity 1 (Critical):** Complete outage or severe impairment of core functionality with no reasonable workaround.  
  - Initial Response: within 1 hour (24x7)  
  - Target Resolution or Workaround: within 4 hours  

- **Severity 2 (High):** Major functionality impacted or significant performance degradation, but Services still operational.  
  - Initial Response: within 2 hours (business hours)  
  - Target Resolution or Workaround: within 1 Business Day  

- **Severity 3 (Medium):** Non-critical feature issues, minor degradation, or workaround available.  
  - Initial Response: within 4 Business Hours  
  - Target Resolution or Workaround: within 5 Business Days  

- **Severity 4 (Low):** General inquiries, cosmetic issues, or feature requests.  
  - Initial Response: within 1 Business Day  
  - Target Resolution: as scheduled in regular release cycles.

12.5 **Service Credits.**  
If monthly Service Availability falls below 99.9% (excluding Permitted Downtime), Contoso shall be entitled to the following Service Credits, upon written request within thirty (30) days of the end of the applicable month:

- Availability ≥ 99.5% and < 99.9%: 5% of the monthly base subscription fee  
- Availability ≥ 99.0% and < 99.5%: 10% of the monthly base subscription fee  
- Availability < 99.0%: 20% of the monthly base subscription fee

Service Credits shall be applied against future invoices and shall not be redeemable for cash. Service Credits for a month shall not exceed 20% of the monthly base subscription fee.

12.6 **Exclusive Remedies.**  
Except where expressly stated otherwise and subject to Article IX, Service Credits constitute Contoso’s sole and exclusive remedy for Acme’s failure to meet the Service Availability commitments set forth in this Article XII.

---

## ARTICLE XIII – CHANGE MANAGEMENT

13.1 **Change Requests.**  
Either Party may request changes to the scope, Deliverables, timelines, or other aspects of the Services by submitting a written change request ("Change Request") describing the proposed change in reasonable detail.

13.2 **Impact Assessment.**  
Upon receipt of a Change Request from Contoso, Acme shall, within a commercially reasonable time, assess the impact of the proposed change on the scope, fees, timeline, resources, and technical feasibility, and shall provide Contoso with a written response indicating: (a) acceptance of the Change Request; (b) rejection of the Change Request; or (c) a counterproposal.

13.3 **Change Orders.**  
No Change Request shall be effective unless and until the Parties execute a written amendment or change order ("Change Order") specifying the agreed changes and any associated adjustments to fees, timelines, or other terms. Acme shall not be obligated to commence work on any change until the applicable Change Order is fully executed.

13.4 **Impact on Performance.**  
Any changes approved under this Article XIII may affect the performance obligations of Acme, including Service Levels. Acme shall be relieved from compliance with affected obligations to the extent such non-compliance results from Contoso-driven changes, delays, or failures to perform its obligations.

---

## ARTICLE XIV – DISPUTE RESOLUTION

14.1 **Good-Faith Negotiations.**  
In the event of any dispute, controversy, or claim arising out of or relating to this Agreement ("Dispute"), the Parties shall first attempt in good faith to resolve the Dispute by negotiation between senior executives who have authority to settle the Dispute. Either Party may initiate such negotiations by written notice to the other Party, and the Parties shall meet within ten (10) Business Days of such notice.

14.2 **Mediation.**  
If the Dispute is not resolved within thirty (30) days after commencement of negotiations under Section 14.1, the Parties agree to submit the Dispute to non-binding mediation before a mutually agreed mediator in **Seattle, Washington**, with each Party bearing its own costs and sharing the mediator’s fees equally.

14.3 **Arbitration.**  
If the Dispute is not resolved by mediation within sixty (60) days of initiation of mediation, the Dispute shall be finally resolved by binding arbitration administered by the **American Arbitration Association (AAA)** in accordance with its Commercial Arbitration Rules. The arbitration shall take place in Seattle, Washington, before a panel of **three (3) arbitrators** experienced in commercial and technology disputes. The language of the arbitration shall be English. The arbitrators shall have the authority to award any remedy or relief that a court of competent jurisdiction could order or grant, except as limited by this Agreement.

14.4 **Injunctive Relief.**  
Nothing in this Article XIV shall prevent either Party from seeking provisional or injunctive relief in any court of competent jurisdiction to prevent irreparable harm, misuse of intellectual property, or breach of confidentiality obligations.

14.5 **Confidentiality of Proceedings.**  
The existence and content of any mediation or arbitration proceedings, including any awards, shall be treated as Confidential Information and shall not be disclosed by either Party except as required by law or to enforce an arbitration award.

---

## ARTICLE XV – FORCE MAJEURE

15.1 **Definition.**  
A "**Force Majeure Event**" means any event beyond the reasonable control of the affected Party, including, but not limited to, acts of God, natural disasters, pandemics, war, terrorism, civil unrest, labor disputes (excluding those involving the affected Party’s own employees), acts of government, embargoes, power outages, failure of telecommunications or internet service providers, or any other similar events beyond the reasonable control of the affected Party.

15.2 **Notice and Mitigation.**  
The Party affected by a Force Majeure Event shall: (a) promptly notify the other Party in writing of the occurrence of the Force Majeure Event, providing details of its nature and expected duration; and (b) use commercially reasonable efforts to mitigate the impact of the Force Majeure Event and resume performance as soon as reasonably practicable.

15.3 **Suspension of Performance.**  
The obligations of the affected Party shall be suspended during the period of the Force Majeure Event to the extent such obligations cannot be performed due to the Force Majeure Event. The time for performance shall be extended for a period equal to the duration of the Force Majeure Event.

15.4 **Termination for Extended Force Majeure.**  
If a Force Majeure Event continues for more than ninety (90) consecutive days and materially affects the performance of a material part of the Services, either Party may terminate this Agreement upon thirty (30) days’ prior written notice to the other Party.

---

## ARTICLE XVI – GENERAL PROVISIONS

16.1 **Entire Agreement.**  
This Agreement, including all SOWs, exhibits, and attachments, constitutes the entire agreement between the Parties regarding the subject matter hereof and supersedes all prior and contemporaneous understandings, agreements, negotiations, representations, and warranties, whether written or oral, regarding such subject matter.

16.2 **Amendments.**  
No amendment or modification of this Agreement shall be valid or binding unless made in writing and signed by duly authorized representatives of both Parties, expressly referencing this Agreement and the specific provisions being amended.

16.3 **Severability.**  
If any provision of this Agreement is held to be invalid, illegal, or unenforceable, the remaining provisions shall remain in full force and effect, and the invalid, illegal, or unenforceable provision shall be deemed modified to the minimum extent necessary to make it valid, legal, and enforceable.

16.4 **Waiver.**  
No failure or delay by either Party in exercising any right, power, or remedy under this Agreement shall operate as a waiver thereof, nor shall any single or partial exercise thereof preclude any other or further exercise of any right, power, or remedy. Any waiver must be in writing and signed by the waiving Party.

16.5 **Assignment.**  
Neither Party may assign, transfer, or delegate this Agreement or any of its rights or obligations hereunder, whether by operation of law or otherwise, without the prior written consent of the other Party, except that either Party may assign this Agreement without such consent to an Affiliate or in connection with a merger, acquisition, corporate reorganization, or sale of all or substantially all of its assets. Any attempted assignment in violation of this Section 16.5 shall be null and void. This Agreement shall be binding upon and inure to the benefit of the Parties and their respective permitted successors and assigns.

16.6 **Independent Contractors.**  
The Parties are independent contractors, and nothing in this Agreement shall be construed as creating a partnership, joint venture, agency, or employment relationship between the Parties. Neither Party shall have authority to bind the other Party in any way.

16.7 **Notices.**  
All notices, requests, consents, claims, demands, waivers, and other communications hereunder ("Notices") shall be in writing and shall be deemed given: (a) when delivered by hand (with written confirmation of receipt); (b) when received by a nationally recognized overnight courier (with written confirmation of receipt); (c) on the date sent by email with confirmation of transmission, if sent during recipient’s business hours (otherwise on the next Business Day); or (d) on the third (3rd) Business Day after mailing by certified or registered mail (return receipt requested), in each case to the addresses set forth below or to such other address as a Party may designate in writing:

**For Contoso (Client):**  
Contoso Enterprises  
Attn: Legal Department  
1000 Contoso Way, Suite 500  
Seattle, WA 98101, USA  
Email: legal@contoso.com  

**For Acme (Vendor):**  
Acme Corp  
Attn: General Counsel  
2000 Acme Plaza, Floor 18  
San Francisco, CA 94105, USA  
Email: legal@acmecorp.com  

16.8 **Governing Law; Venue.**  
This Agreement shall be governed by and construed in accordance with the laws of the **State of Washington**, without giving effect to any choice or conflict of law provisions. Subject to Article XIV, the Parties agree that any litigation permitted under this Agreement shall be brought exclusively in the state or federal courts located in King County, Washington, and the Parties hereby consent to the personal jurisdiction and venue of such courts.

16.9 **Counterparts; Electronic Signatures.**  
This Agreement may be executed in counterparts, each of which shall be deemed an original and all of which together shall constitute one and the same instrument. Signatures transmitted by facsimile, PDF, or other electronic means shall be deemed to have the same legal effect as originals.

16.10 **Headings.**  
The headings in this Agreement are for convenience only and shall not affect the interpretation of this Agreement.

16.11 **Order of Precedence.**  
In the event of any conflict or inconsistency between the terms of this Agreement and any SOW, the terms of the SOW shall prevail solely with respect to the subject matter of that SOW, unless the SOW expressly states otherwise and identifies the provisions of this Agreement being superseded.

16.12 **Third-Party Beneficiaries.**  
Except as expressly provided in Article VIII with respect to indemnified Parties, this Agreement is intended for the sole benefit of the Parties and their permitted successors and assigns, and nothing herein, express or implied, is intended to or shall confer upon any other person or entity any legal or equitable right, benefit, or remedy.

---

## SIGNATURE BLOCK

IN WITNESS WHEREOF, the Parties hereto have caused this Service Level Agreement, Contract Reference Number **SLA-ACM-202407-166**, to be executed by their duly authorized representatives as of the Effective Date.

### CONTOSO ENTERPRISES  
("Client" or "Company")

By: ________________________________  
Name: ______________________________  
Title: _______________________________  
Date: _______________________________

**Witness (if applicable):**  
Signature: ___________________________  
Name: ______________________________  
Date: _______________________________

---

### ACME CORP  
("Vendor" or "Service Provider")

By: ________________________________  
Name: ______________________________  
Title: _______________________________  
Date: _______________________________

**Witness (if applicable):**  
Signature: ___________________________  
Name: ______________________________  
Date: _______________________________