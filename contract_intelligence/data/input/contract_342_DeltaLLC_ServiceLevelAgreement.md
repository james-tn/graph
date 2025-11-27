# SERVICE LEVEL AGREEMENT  
**Contract Reference Number: SLA-DEL-202410-342**

---

## SERVICE LEVEL AGREEMENT  
**BETWEEN**  
**Contoso Enterprises** and **Delta LLC**  

**Effective Date:** October 08, 2024  
**Expiration Date:** November 25, 2027  
**Contract Value:** USD $4,932,437  
**Payment Terms:** Net 30  
**Governing Law:** State of Washington  
**Risk Level:** High  

---

## PREAMBLE & RECITALS

This Service Level Agreement, reference number **SLA-DEL-202410-342** (this **“Agreement”** or this **“SLA”**), is made and entered into as of **October 08, 2024** (the **“Effective Date”**), by and between:

1. **Contoso Enterprises**, a corporation duly organized and existing under the laws of the State of Washington, with its principal place of business at:  
   **Contoso Enterprises**  
   500 Pine Street, Suite 2100  
   Seattle, WA 98101  
   United States  
   (**“Contoso”**, the **“Client”**, or the **“Company”**),

and

2. **Delta LLC**, a limited liability company duly organized and existing under the laws of the State of Delaware, authorized to transact business in the State of Washington, with its principal place of business at:  
   **Delta LLC**  
   1200 Harbor Avenue SW, Suite 900  
   Seattle, WA 98116  
   United States  
   (**“Delta”**, the **“Vendor”** or the **“Service Provider”**).

Contoso and Delta may be individually referred to herein as a **“Party”** and collectively as the **“Parties”**.

### RECITALS

WHEREAS, the Client desires to obtain from the Service Provider certain technology services, including managed application hosting, infrastructure operation, support, maintenance, monitoring, incident management, and related professional services, as further described in **Article II (Scope of Services/Work)** of this Agreement;

WHEREAS, the Service Provider is engaged in the business of providing managed IT services, cloud-based hosting, software support, and related professional services, and represents that it has the requisite expertise, personnel, systems, licenses, and resources necessary to perform the Services (as defined below) in accordance with the terms and conditions of this Agreement;

WHEREAS, the Parties desire to define and document the service levels, performance standards, support obligations, uptime commitments, response and resolution times, as well as the respective obligations and responsibilities of the Parties with respect to such Services, all as set forth herein;

WHEREAS, the Parties acknowledge that the Services provided under this Agreement are mission-critical to the Client’s operations and that the Parties have agreed to certain high-risk terms, including uncapped liability and extensive indemnity provisions favoring the Service Provider, as specifically set forth in **Article VIII (Indemnification)** and **Article IX (Limitation of Liability)**;

NOW, THEREFORE, in consideration of the mutual covenants, agreements, representations, warranties, and conditions contained herein, and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the Parties hereby agree as follows:

---

## ARTICLE I – DEFINITIONS

1.1 **“Affiliate”** means, with respect to a Party, any entity that directly or indirectly controls, is controlled by, or is under common control with such Party, where “control” means the ownership of more than fifty percent (50%) of the voting securities of such entity or the power to direct its management.

1.2 **“Agreement”** means this Service Level Agreement, reference number **SLA-DEL-202410-342**, including all Exhibits, Schedules, Statements of Work (“SOWs”), Change Orders, and any addenda or amendments executed in writing by the Parties.

1.3 **“Applicable Law”** means any and all laws, statutes, ordinances, regulations, rules, codes, orders, directives, judgments, decrees, and other requirements of any governmental or regulatory authority that are applicable to a Party, the Services, or this Agreement, including, as applicable, the General Data Protection Regulation (EU) 2016/679 (“GDPR”) and the California Consumer Privacy Act (“CCPA”), each as amended.

1.4 **“Business Day”** means any day other than Saturday, Sunday, or any day on which commercial banks in Seattle, Washington are authorized or required by law to remain closed.

1.5 **“Change Order”** means a written document executed by authorized representatives of both Parties in accordance with **Article XIII (Change Management)** that modifies, adds to, or removes Services, Deliverables, timelines, or fees under this Agreement.

1.6 **“Client Data”** means any and all data, content, records, files, documents, information, or materials, including personal data, that are provided by or on behalf of the Client or its Affiliates, users, or customers to the Service Provider, or that the Service Provider accesses, stores, processes, or generates on behalf of the Client in connection with the Services.

1.7 **“Confidential Information”** has the meaning set forth in **Section 5.1**.

1.8 **“Deliverables”** means any reports, configurations, scripts, software code (excluding Service Provider Tools as defined below), documentation, analyses, designs, plans, or other tangible or intangible items to be delivered by the Service Provider to the Client under this Agreement or under any SOW.

1.9 **“Downtime”** means any period during which the production environment of the Services is not Available (as defined in Section 12.1), excluding Scheduled Maintenance and Excluded Downtime events defined in **Article XII**.

1.10 **“Force Majeure Event”** has the meaning set forth in **Article XV (Force Majeure)**.

1.11 **“Incident”** means an unplanned interruption to, or a reduction in the quality of, the Services, or a failure of a Service component, as reported by the Client or detected by the Service Provider’s monitoring tools.

1.12 **“Personal Data”** or **“Personal Information”** means any information relating to an identified or identifiable natural person and shall be interpreted in accordance with Applicable Law, including GDPR and CCPA where applicable.

1.13 **“Service Credits”** means the financial or service-based remedies provided to the Client for the Service Provider’s failure to meet specific service level targets, as further described in **Article XII (Service Level Agreements)**.

1.14 **“Service Levels”** means the quantitative and qualitative performance standards, including uptime, response times, and resolution times, specified in **Article XII** and any applicable SOWs.

1.15 **“Services”** means collectively the managed hosting, infrastructure management, monitoring, support, maintenance, incident management, and professional services to be provided by the Service Provider under this Agreement and any SOWs, including associated Deliverables.

1.16 **“Service Provider Tools”** means any software, tools, utilities, methodologies, templates, know-how, processes, documentation, or other materials that are owned or controlled by the Service Provider prior to the Effective Date or that are developed by the Service Provider independently of this Agreement and are used in the performance of the Services, along with any enhancements, modifications, or derivatives thereof.

1.17 **“Statement of Work” or “SOW”** means a written document executed by both Parties that describes specific Services, Deliverables, milestones, acceptance criteria, fees, and other terms and conditions applicable to a particular project or engagement under this Agreement.

1.18 **“System”** means the hardware, software, network, and infrastructure environment used or managed by the Service Provider to provide the Services to the Client, including all associated servers, storage, virtualization layers, operating systems, and monitoring tools.

1.19 **“Third-Party Materials”** means any software, hardware, data, or other materials not owned by either Party and licensed, procured, or otherwise provided by a third party that are used in connection with the Services.

1.20 **“Work Product”** means all Deliverables and any other items created, developed, or produced for the Client by the Service Provider in the course of providing the Services, excluding Service Provider Tools and Third-Party Materials, but including any configurations and customizations of the Client’s systems.

---

## ARTICLE II – SCOPE OF SERVICES/WORK

2.1 **General.**  
The Service Provider shall provide to the Client, and the Client hereby engages the Service Provider to provide, the Services described in this **Article II** and as may be further detailed in one or more SOWs executed pursuant to this Agreement. The Services are mission-critical to the Client’s operations and shall be performed on a 24x7x365 basis, unless otherwise expressly stated.

2.2 **Managed Hosting and Infrastructure Services.**  
(a) The Service Provider shall design, implement, host, operate, monitor, and manage a production environment for the Client’s business applications (the **“Hosted Environment”**). This includes:

- Provisioning and management of virtual or physical servers, storage, and networking equipment at one or more data centers or cloud environments selected by the Service Provider.  
- Implementation of appropriate redundancy, load balancing, and high-availability configurations consistent with the Service Levels described in **Article XII**.  
- Continuous performance monitoring of the Hosted Environment, including CPU utilization, memory usage, disk I/O, database performance, and network throughput.  
- Capacity planning and scaling in response to actual or anticipated increases in Client workload, subject to adjustments in fees as set forth in **Article III**.

(b) The Hosted Environment shall be configured in consultation with the Client to support the Client’s core applications, including but not limited to enterprise resource planning (ERP), customer relationship management (CRM), and analytics applications, as specified in the applicable SOWs.

(c) The Service Provider shall maintain the System in a secure, patched, and operational state, applying routine maintenance, including operating system upgrades, security patches, and firmware updates in accordance with industry best practices and the maintenance windows set forth in **Section 12.3**.

2.3 **Application Management and Support Services.**  
(a) The Service Provider shall provide incident management, problem resolution, and operational support for the applications designated in the relevant SOW(s). This includes:

- Level 1 (L1) support: Intake, triage, and initial troubleshooting of incidents reported by the Client’s users via the agreed ticketing system, email, or phone.  
- Level 2 (L2) support: Technical analysis and resolution of issues requiring deeper investigation of configuration, data, or infrastructure components.  
- Level 3 (L3) support: Advanced troubleshooting, including but not limited to code-level debugging, interaction with third-party vendors, and architectural changes as necessary.

(b) The Service Provider shall provide technical support during the hours and with the response and resolution times outlined in **Article XII**. For Priority 1 Incidents (defined in Article XII), the Service Provider shall provide 24x7x365 critical support.

(c) The Service Provider shall maintain an incident management log, track all Incidents from initial report through final resolution, and provide periodic reporting to the Client, including root cause analyses for Severity 1 and Severity 2 Incidents when requested by the Client, in accordance with **Section 12.5**.

2.4 **Security, Backup, and Disaster Recovery.**  
(a) The Service Provider shall implement and maintain administrative, physical, and technical safeguards designed to protect the Hosted Environment and Client Data against unauthorized access, use, disclosure, alteration, or destruction, as further detailed in **Article XI (Data Protection and Privacy)**.

(b) The Service Provider shall implement regular data backup procedures, including:

- Daily incremental backups and weekly full backups of critical databases and configurations, unless otherwise agreed in an SOW;  
- Offsite replication of backup data to a geographically separate location; and  
- Retention of backup data for a minimum of thirty (30) days, or as otherwise specified by the Client in writing and agreed by the Parties.

(c) The Service Provider shall maintain a documented disaster recovery plan (“**DR Plan**”) for the Hosted Environment and shall, upon reasonable request of the Client, provide an executive summary of such DR Plan. The Service Provider shall use commercially reasonable efforts to restore critical Services within the recovery time objectives (RTOs) and recovery point objectives (RPOs) specified in the applicable SOW, subject to the terms of **Article XV (Force Majeure)**.

2.5 **Professional Services and Deliverables.**  
(a) The Service Provider shall perform professional services, which may include architecture design, system integration, configuration, data migration, performance tuning, and project management, as described in applicable SOWs.

(b) The Service Provider shall deliver:

- Architecture and design documents;  
- Implementation plans and migration runbooks;  
- Configuration documentation and system inventories;  
- Operational runbooks and knowledge base articles;  
- Periodic performance and capacity reports; and  
- Any additional Deliverables specified in SOWs.

(c) The Client shall review and provide written acceptance or rejection of Deliverables within ten (10) Business Days after receipt (or such other timeframe as may be stated in the applicable SOW). If the Client fails to provide written notice of acceptance or rejection within such period, the Deliverable shall be deemed accepted. If rejected, the Client shall provide a written description of the deficiencies, and the Service Provider shall use commercially reasonable efforts to correct such deficiencies without additional charge, unless such deficiencies arise from Client Data, Client systems, or Client instructions.

2.6 **Client Responsibilities.**  
The Parties acknowledge that the Service Provider’s ability to perform the Services (including meeting the Service Levels in **Article XII**) is dependent upon the timely and effective performance of the Client’s responsibilities, which include:

(a) Providing necessary access credentials, VPN connectivity, or other secure means of access to the Client’s systems, subject to the Client’s internal security policies;

(b) Providing timely and accurate information, specifications, data, and decisions, and promptly responding to inquiries from the Service Provider;

(c) Maintaining and supporting any Client-owned hardware, software, and network components that interface with the Hosted Environment, except to the extent the Service Provider has expressly agreed to manage such components under an SOW;

(d) Designating a primary point of contact to coordinate communication and approvals; and

(e) Ensuring that its users properly use the Services in accordance with any usage policies provided by the Service Provider and do not abuse or misuse the Services in a way that could adversely affect system performance or security.

2.7 **Service Modifications.**  
The Service Provider may, from time to time, modify the infrastructure, architecture, or components of the Services, provided that such modifications do not materially degrade the agreed Service Levels. Any material change to the scope, nature, or cost of Services shall be handled through the Change Management process in **Article XIII**.

---

## ARTICLE III – FEES AND PAYMENT TERMS

3.1 **Fees.**  
(a) In consideration for the Services, the Client shall pay the Service Provider fees totaling **USD $4,932,437** over the Term of this Agreement, allocated and invoiced as specified in this **Article III** and any applicable SOWs.  

(b) The total Contract Value is composed of:  
  (i) **Base Managed Services Fees**: recurring monthly fees for hosting, infrastructure, monitoring, and standard support;  
  (ii) **Professional Services Fees**: time-and-materials or fixed-fee charges for implementation, migration, and project-based services; and  
  (iii) **Pass-Through Fees**: third-party license or usage-based charges incurred on behalf of the Client, if applicable.

3.2 **Invoicing and Payment Terms.**  
(a) Unless otherwise provided in an SOW, the Service Provider shall invoice the Client monthly in arrears for recurring Services and upon completion of milestones or acceptance of Deliverables for project-based services.  

(b) The Client shall pay all undisputed amounts within **thirty (30) calendar days** from the invoice date (**“Net 30”**), in U.S. dollars, by electronic funds transfer, wire transfer, ACH, or other mutually agreed payment methods.

(c) If the Client disputes any portion of an invoice, the Client shall notify the Service Provider in writing within fifteen (15) calendar days of receipt of such invoice, specifying the disputed amount and the basis for the dispute. The Client shall timely pay all undisputed portions of the invoice. The Parties shall work in good faith to resolve any invoice disputes; any amounts ultimately determined to be payable shall be paid within ten (10) Business Days of such determination.

3.3 **Late Payments.**  
(a) Any undisputed invoice amount not paid when due shall accrue interest at a rate equal to one and one-half percent (1.5%) per month, or the maximum rate permitted by Applicable Law, whichever is lower, from the due date until such amount is paid in full.

(b) If the Client fails to pay any undisputed amount within forty-five (45) days after the due date, the Service Provider may, upon ten (10) Business Days’ prior written notice, suspend performance of the Services (including access to the Hosted Environment) until all past-due amounts and applicable interest are paid in full, without liability to the Client for any resulting delays or failures to meet Service Levels.

3.4 **Expenses and Reimbursements.**  
(a) The Client shall reimburse the Service Provider for reasonable, pre-approved out-of-pocket travel and living expenses incurred in connection with the performance of on-site Services, in accordance with the Client’s travel policies provided in advance in writing.

(b) Expense reimbursement requests shall be supported by appropriate receipts or other documentation and included on the relevant invoice. The Client shall reimburse such expenses in accordance with the payment terms set forth in **Section 3.2**.

3.5 **Taxes.**  
(a) All fees and charges are exclusive of taxes. The Client shall be responsible for all sales, use, value-added, goods and services, and other similar taxes (collectively, **“Taxes”**) imposed by any governmental authority on the Services, excluding taxes based on the Service Provider’s net income, property, or employees.

(b) If the Service Provider is required by law to collect Taxes from the Client, such Taxes shall be separately stated on the invoice and paid by the Client. If the Client is exempt from certain Taxes, the Client shall provide the Service Provider with a valid tax exemption certificate.

3.6 **Fee Adjustments.**  
(a) The Service Provider may adjust recurring fees annually on each anniversary of the Effective Date, not to exceed five percent (5%) of the previous year’s fees for the same Services, upon at least sixty (60) days’ prior written notice to the Client.

(b) Any increase resulting from a material change in the scope or volume of Services requested by the Client shall be handled via a Change Order under **Article XIII**.

---

## ARTICLE IV – TERM AND TERMINATION

4.1 **Term.**  
The term of this Agreement shall commence on the Effective Date and continue in full force and effect until **November 25, 2027** (the **“Expiration Date”**), unless earlier terminated in accordance with this **Article IV** (the **“Term”**).

4.2 **Renewal.**  
Unless either Party provides written notice of non-renewal at least one hundred eighty (180) days prior to the Expiration Date, this Agreement shall automatically renew for successive one (1)-year periods on the same terms and conditions, subject to any fee adjustments pursuant to **Section 3.6**, until terminated by either Party as provided herein.

4.3 **Termination for Convenience.**  
The Client may terminate this Agreement, in whole or in part, for convenience and without cause upon at least **one hundred eighty (180) days’ prior written notice** to the Service Provider. The Service Provider may terminate this Agreement for convenience upon **one hundred eighty (180) days’ prior written notice** to the Client. During any such notice period, the Client remains liable for all fees for Services provided, and any non-cancellable commitments incurred by the Service Provider on the Client’s behalf.

4.4 **Termination for Cause.**  
(a) Either Party may terminate this Agreement immediately upon written notice if the other Party:

  (i) materially breaches this Agreement, and such breach remains uncured thirty (30) days after written notice thereof (or ten (10) days in the case of a monetary breach); or  
  (ii) becomes insolvent, makes a general assignment for the benefit of creditors, suffers or permits the appointment of a receiver for its business or assets, or becomes subject to any bankruptcy or insolvency proceeding which is not dismissed within sixty (60) days.

(b) Notwithstanding the foregoing, the Service Provider shall have the right to immediately suspend or terminate Services, without liability, if the Client’s use of the Services (i) poses a security risk; (ii) violates Applicable Law; or (iii) materially impairs the integrity or availability of the System, provided the Service Provider gives prompt notice and cooperates in good faith with the Client to mitigate any impact.

4.5 **Effect of Termination.**  
Upon expiration or termination of this Agreement for any reason:

(a) The Client shall pay the Service Provider all fees and reimbursable expenses accrued and unpaid through the effective date of termination, plus any termination charges or early termination fees explicitly set forth in the applicable SOW(s).

(b) The Service Provider shall cease providing the Services (unless otherwise agreed in writing) and shall cooperate with the Client, for a period not to exceed ninety (90) days following termination (the **“Transition Period”**), in transitioning the Services to the Client or a successor provider. Such transition assistance shall be provided at the Service Provider’s then-current standard rates unless otherwise agreed.

(c) The Service Provider shall, upon written request and subject to **Article XI**, provide the Client with a final export of Client Data in a commonly used format within a reasonable period. The Parties shall agree in advance on any additional fees for extensive data extraction or transformation.

(d) Each Party shall return or destroy the other Party’s Confidential Information in accordance with **Section 5.4**.

4.6 **Survival.**  
The following provisions shall survive termination or expiration of this Agreement: **Articles V (Confidentiality), VI (Intellectual Property Rights), VII (Representations and Warranties), VIII (Indemnification), IX (Limitation of Liability), XI (Data Protection and Privacy), XIV (Dispute Resolution), XV (Force Majeure), XVI (General Provisions)**, and any other provisions that by their nature are intended to survive.

---

## ARTICLE V – CONFIDENTIALITY

5.1 **Definition of Confidential Information.**  
“**Confidential Information**” means all non-public information disclosed by a Party (the **“Disclosing Party”**) to the other Party (the **“Receiving Party”**) in connection with this Agreement, whether orally or in writing, that is designated as confidential or that a reasonable person would understand to be confidential given the nature of the information and the circumstances of disclosure. Confidential Information includes, without limitation, trade secrets, business plans, pricing, financial data, system architecture, security information, Client Data, Personal Data, and the terms and conditions of this Agreement.

5.2 **Obligations.**  
The Receiving Party shall:

(a) Use the Disclosing Party’s Confidential Information solely to perform its obligations or exercise its rights under this Agreement;  

(b) Not disclose the Confidential Information to any third party except as expressly permitted herein;  

(c) Limit access to the Confidential Information to its employees, contractors, and agents who have a need to know such information for purposes of this Agreement and who are bound by obligations of confidentiality and non-use at least as strict as those set forth herein; and  

(d) Use at least the same degree of care as it uses to protect its own confidential information of a similar nature, but no less than reasonable care, to protect the Disclosing Party’s Confidential Information.

5.3 **Exceptions.**  
Confidential Information does not include information that the Receiving Party can demonstrate:

(a) Was already known to the Receiving Party without restriction at the time of disclosure;  

(b) Becomes publicly known through no breach of this Agreement by the Receiving Party;  

(c) Is received from a third party without breach of any obligation of confidentiality; or  

(d) Is independently developed by the Receiving Party without reference to or use of the Disclosing Party’s Confidential Information.

5.4 **Required Disclosure.**  
The Receiving Party may disclose Confidential Information to the extent required by Applicable Law, regulation, or court order, provided that, to the extent legally permitted, the Receiving Party gives the Disclosing Party prompt written notice and cooperates reasonably with any efforts by the Disclosing Party to seek protective measures.

5.5 **Return or Destruction.**  
Upon written request of the Disclosing Party, or upon termination or expiration of this Agreement, the Receiving Party shall promptly return or destroy all copies of the Disclosing Party’s Confidential Information in its possession or control, except that the Receiving Party may retain (i) one archival copy for legal and compliance purposes, and (ii) information maintained in automated backup systems, which will be destroyed in the ordinary course of business.

5.6 **Survival.**  
The obligations in this **Article V** shall survive for a period of **five (5) years** following the termination or expiration of this Agreement; provided that obligations with respect to trade secrets and Client Data shall survive for so long as such information remains a trade secret or Client Data remains stored or processed by the Service Provider.

---

## ARTICLE VI – INTELLECTUAL PROPERTY RIGHTS

6.1 **Ownership of Client IP and Client Data.**  
(a) As between the Parties, the Client retains all right, title, and interest in and to the Client’s pre-existing intellectual property and Client Data, including all related intellectual property rights.  

(b) The Service Provider acknowledges that Client Data is the exclusive property of the Client and shall be treated as Confidential Information in accordance with **Article V**.

6.2 **Ownership of Service Provider Tools.**  
As between the Parties, the Service Provider retains all right, title, and interest in and to the Service Provider Tools, including any enhancements, modifications, or derivative works thereof, regardless of whether such enhancements are created in connection with the Services or at the suggestion or request of the Client. No rights in the Service Provider Tools are granted to the Client except as expressly set forth in this Agreement.

6.3 **Ownership of Work Product.**  
(a) Subject to **Sections 6.1 and 6.2**, and provided that the Client has paid all applicable fees, the Client shall own all right, title, and interest in and to the Work Product created specifically for and delivered to the Client under this Agreement.

(b) Notwithstanding the foregoing, the Service Provider shall retain ownership of any underlying Service Provider Tools embedded in or used to create the Work Product, and the Service Provider hereby grants to the Client a non-exclusive, perpetual, worldwide, fully paid-up license to use such embedded Service Provider Tools solely as integrated into the Work Product for the Client’s internal business purposes.

6.4 **License Grants to Client.**  
Subject to the terms and conditions of this Agreement and the Client’s payment of applicable fees, the Service Provider hereby grants to the Client a non-exclusive, non-transferable (except as permitted by **Section 16.8**), worldwide license during the Term to access and use the Services, the Hosted Environment, and any Deliverables solely for the Client’s internal business operations.

6.5 **License Grants to Service Provider.**  
The Client hereby grants to the Service Provider a non-exclusive, royalty-free license to use, host, copy, transmit, and display Client Data and Client-owned materials solely as necessary to provide the Services and perform its obligations under this Agreement.

6.6 **Use Restrictions.**  
The Client shall not, and shall not permit any third party to:

(a) Reverse engineer, decompile, disassemble, or otherwise attempt to derive the source code of any proprietary software or Service Provider Tools provided hereunder (except to the limited extent permitted by Applicable Law notwithstanding such restriction);  

(b) Remove, alter, or obscure any proprietary notices or labels;  

(c) Use the Services to provide services to third parties in the nature of a service bureau or managed service provider (unless expressly authorized in writing); or  

(d) Use the Services in violation of any Applicable Law or third-party rights.

6.7 **Third-Party Materials.**  
Any Third-Party Materials provided or made available by the Service Provider are subject to the applicable third-party license terms, which shall be provided to the Client upon request. The Client’s use of such Third-Party Materials shall be governed by those terms and not this Agreement, except to the extent this Agreement imposes additional obligations on the Client.

6.8 **Feedback.**  
The Client may provide suggestions, comments, or other feedback regarding the Services (“**Feedback**”). The Client agrees that the Service Provider shall have a perpetual, irrevocable, worldwide, royalty-free right to use and incorporate such Feedback into its products and services without restriction or compensation to the Client, provided that the Service Provider does not identify the Client as the source of such Feedback without the Client’s prior written consent.

---

## ARTICLE VII – REPRESENTATIONS AND WARRANTIES

7.1 **Mutual Representations and Warranties.**  
Each Party represents and warrants that:

(a) It is duly organized, validly existing, and in good standing under the laws of its jurisdiction of organization;  

(b) It has the full right, power, and authority to enter into this Agreement and to perform its obligations hereunder;  

(c) The execution and delivery of this Agreement and the performance of its obligations do not conflict with or result in a breach of any other agreement to which it is a party; and  

(d) This Agreement constitutes a legal, valid, and binding obligation of such Party, enforceable in accordance with its terms, subject to applicable bankruptcy, insolvency, or similar laws affecting creditors’ rights generally.

7.2 **Service Provider Warranties.**  
The Service Provider represents and warrants that:

(a) The Services will be performed in a professional and workmanlike manner, in accordance with generally accepted industry standards and practices;  

(b) It has and will maintain all necessary licenses, permits, and approvals required to perform the Services under Applicable Law;  

(c) To the Service Provider’s knowledge, the Services and Service Provider Tools, when used as authorized hereunder, will not infringe any third-party intellectual property rights; and  

(d) It will comply with all Applicable Laws in performing the Services, including data protection and privacy laws as set forth in **Article XI**.

7.3 **Client Warranties.**  
The Client represents and warrants that:

(a) It has the right to transmit and use Client Data and any other materials it provides to the Service Provider and that such use by the Service Provider as contemplated by this Agreement will not infringe or violate any third-party rights;  

(b) It will comply with all Applicable Laws in connection with its use of the Services, including laws related to the collection, processing, and transfer of Personal Data; and  

(c) It will not use the Services for any unlawful or unauthorized purposes.

7.4 **Disclaimer.**  
EXCEPT AS EXPRESSLY PROVIDED IN THIS ARTICLE VII, THE SERVICES, DELIVERABLES, AND ANY OTHER MATERIALS PROVIDED BY THE SERVICE PROVIDER ARE PROVIDED “AS IS” AND “AS AVAILABLE,” AND THE SERVICE PROVIDER DISCLAIMS ALL OTHER WARRANTIES, EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND ANY WARRANTIES ARISING FROM COURSE OF DEALING OR USAGE OF TRADE.

---

## ARTICLE VIII – INDEMNIFICATION

8.1 **Indemnification by Client.**  
The Client shall indemnify, defend, and hold harmless the Service Provider, its Affiliates, and their respective officers, directors, employees, contractors, and agents (collectively, the **“Service Provider Indemnified Parties”**) from and against any and all claims, demands, actions, suits, proceedings, damages, losses, liabilities, costs, and expenses (including reasonable attorneys’ fees) (collectively, **“Claims”**) arising out of or relating to:

(a) The Client’s or its users’ misuse of the Services or violation of this Agreement;  

(b) Any allegation that the Client Data or other materials supplied by the Client infringe, misappropriate, or violate any intellectual property or privacy rights of a third party;  

(c) The Client’s failure to comply with Applicable Law, including data protection and privacy laws; or  

(d) Any bodily injury, death, or damage to tangible property caused by the acts or omissions of the Client or its personnel.

8.2 **Indemnification by Service Provider.**  
The Service Provider shall indemnify, defend, and hold harmless the Client, its Affiliates, and their respective officers, directors, employees, contractors, and agents (collectively, the **“Client Indemnified Parties”**) from and against any Claims arising out of or relating to:

(a) Any allegation that the Services or Service Provider Tools, when used in accordance with this Agreement, infringe or misappropriate any U.S. patent, copyright, or trade secret of a third party; or  

(b) The Service Provider’s gross negligence or willful misconduct in performing the Services.

8.3 **Infringement Mitigation.**  
In the event of any claim alleging infringement by the Services or Service Provider Tools, the Service Provider may, at its option and expense:

(a) Procure for the Client the right to continue using the Services;  

(b) Replace or modify the Services so that they become non-infringing while providing substantially equivalent functionality; or  

(c) If (a) and (b) are not commercially reasonable, terminate the affected Services and refund to the Client any prepaid, unused fees.

8.4 **Indemnification Procedures.**  
The indemnified Party shall:

(a) Promptly notify the indemnifying Party in writing of any Claim for which it seeks indemnification, provided that failure to do so shall not relieve the indemnifying Party of its obligations except to the extent it is prejudiced thereby;  

(b) Permit the indemnifying Party to control the defense and settlement of the Claim, provided that the indemnifying Party shall not settle any Claim without the indemnified Party’s prior written consent if such settlement (i) imposes any non-monetary obligations on the indemnified Party, or (ii) does not include a full and unconditional release of the indemnified Party; and  

(c) Provide reasonable cooperation and assistance at the indemnifying Party’s expense.

8.5 **Exclusive Remedy.**  
The indemnification obligations set forth in this **Article VIII** shall be the Parties’ sole and exclusive remedy, and the indemnifying Party’s entire liability, with respect to Claims covered by this Article, subject to **Article IX (Limitation of Liability)**.

---

## ARTICLE IX – LIMITATION OF LIABILITY

9.1 **Uncapped Liability.**  
Given the critical nature of the Services and the high-risk allocation agreed by the Parties, **THE SERVICE PROVIDER’S LIABILITY UNDER THIS AGREEMENT SHALL NOT BE SUBJECT TO A MONETARY CAP**. The Client acknowledges and agrees that the uncapped liability is reflected in the pricing and terms of this Agreement.

9.2 **Types of Damages.**  
NOTWITHSTANDING ANYTHING TO THE CONTRARY, AND CONSISTENT WITH THE HIGH-RISK PROFILE OF THIS AGREEMENT, **NEITHER PARTY SHALL BE EXCLUDED FROM LIABILITY FOR INDIRECT, INCIDENTAL, CONSEQUENTIAL, SPECIAL, OR PUNITIVE DAMAGES**. BOTH PARTIES EXPRESSLY ACKNOWLEDGE THAT, SUBJECT TO ANY APPLICABLE LEGAL LIMITATIONS, EACH PARTY MAY SEEK RECOVERY OF CONSEQUENTIAL, INCIDENTAL, AND INDIRECT DAMAGES, INCLUDING LOST PROFITS, LOSS OF DATA, AND BUSINESS INTERRUPTION, TO THE EXTENT PROVEN.

9.3 **Exceptions.**  
Nothing in this **Article IX** shall limit or exclude:  

(a) Either Party’s liability for death or personal injury caused by its negligence;  

(b) Either Party’s liability for fraud or intentional misconduct;  

(c) The Client’s indemnification obligations under **Section 8.1**;  

(d) The Service Provider’s indemnification obligations under **Section 8.2**; or  

(e) Any liability that cannot be limited or excluded under Applicable Law.

9.4 **Basis of the Bargain.**  
The Parties acknowledge that the provisions of this **Article IX**, including the uncapped liability and allowing consequential damages, were specifically negotiated by the Parties and reflect a material allocation of risk forming part of the basis of the bargain.

---

## ARTICLE X – INSURANCE

10.1 **Insurance Coverage.**  
During the Term, the Service Provider shall, at its own expense, maintain in full force and effect the following insurance coverage with reputable insurers rated at least A- by A.M. Best:

(a) **Commercial General Liability Insurance**: with limits of not less than $5,000,000 per occurrence and $5,000,000 in the aggregate, including coverage for bodily injury, property damage, personal and advertising injury, and contractual liability;

(b) **Professional Liability (Errors & Omissions) Insurance**, including technology errors and omissions: with limits of not less than $10,000,000 per claim and $10,000,000 in the aggregate;

(c) **Cyber Liability / Data Breach Insurance**: with limits of not less than $10,000,000 per claim and $10,000,000 in the aggregate, providing coverage for data breaches, privacy violations, network security failures, regulatory investigations, and notification/remediation costs;

(d) **Workers’ Compensation Insurance**: as required by Applicable Law; and

(e) **Employer’s Liability Insurance**: with limits of not less than $1,000,000 per occurrence.

10.2 **Certificates of Insurance.**  
Upon request, the Service Provider shall provide the Client with certificates of insurance evidencing the coverage required under this **Article X**. The Client may require that it be named as an additional insured or additional interest under applicable policies, to the extent permitted by the insurer.

10.3 **Notice of Cancellation or Material Change.**  
The Service Provider shall use commercially reasonable efforts to ensure that its insurers provide at least thirty (30) days’ prior written notice to the Client of any cancellation or material reduction in coverage of any of the required policies.

---

## ARTICLE XI – DATA PROTECTION AND PRIVACY

11.1 **Compliance with Data Protection Laws.**  
Each Party shall comply with all Applicable Laws relating to data protection and privacy, including, to the extent applicable, **GDPR**, **CCPA**, and any analogous laws in other jurisdictions.

11.2 **Roles of the Parties.**  
For purposes of Applicable Data Protection Law, the Parties agree that the Client is typically the “controller” (or “business” under CCPA) of Personal Data contained in Client Data, and the Service Provider is the “processor” (or “service provider” under CCPA) with respect to such Personal Data, except to the extent the Parties agree otherwise in an applicable data processing agreement (DPA).

11.3 **Data Processing and Use.**  
The Service Provider shall:

(a) Process Personal Data only on documented instructions from the Client, including with respect to transfers to a third country or international organization, unless required by Applicable Law;  

(b) Ensure that persons authorized to process Personal Data are bound by appropriate confidentiality obligations;  

(c) Implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including measures described in **Section 2.4**; and  

(d) Not “sell” Personal Information as that term is defined under CCPA, nor use Personal Data for purposes other than providing the Services, except as required by law or expressly authorized by the Client.

11.4 **Subprocessors.**  
The Service Provider may engage third-party subprocessors to process Client Data, provided that:

(a) The Service Provider enters into written agreements with such subprocessors imposing data protection obligations no less protective than those set forth in this Agreement; and  

(b) The Service Provider remains liable for the acts and omissions of its subprocessors.

11.5 **Data Breach Notification.**  
In the event of any actual or reasonably suspected unauthorized access to, or disclosure of, Client Data processed by the Service Provider that constitutes a “personal data breach” under Applicable Law (a **“Data Breach”**), the Service Provider shall:

(a) Notify the Client without undue delay and, where feasible, within seventy-two (72) hours after becoming aware of the Data Breach;  

(b) Provide the Client with information reasonably required to comply with its legal obligations, including a description of the nature of the breach, the categories and approximate number of data subjects and records affected, and measures taken or proposed to address and mitigate the breach; and  

(c) Cooperate with the Client, at the Client’s reasonable request and expense, in investigating the Data Breach and fulfilling any legal or regulatory requirements, including notifications to data subjects or regulators.

11.6 **Data Retention and Deletion.**  
(a) The Service Provider shall retain Client Data only for as long as necessary to provide the Services or as required by Applicable Law.  

(b) Upon termination of this Agreement or upon written request by the Client, the Service Provider shall, subject to **Section 4.5**, return or securely delete Client Data, except to the extent retention is required by law. The Service Provider may retain anonymized or aggregated data that does not identify the Client or any individual, which may be used for analytics or service improvement purposes.

11.7 **Data Subject Rights Assistance.**  
The Service Provider shall, to the extent legally permitted and to the extent the Client cannot reasonably fulfill such obligations itself, assist the Client in responding to data subject requests to exercise rights under Applicable Data Protection Law (e.g., access, rectification, erasure, restriction, data portability).

---

## ARTICLE XII – SERVICE LEVEL AGREEMENTS

12.1 **Availability Commitment.**  
The Service Provider shall use commercially reasonable efforts to ensure that the production environment of the Services is Available at least **99.9%** of the time, measured on a calendar-month basis. “**Available**” means that the Client’s production users are able to log in to and use the core functional features of the primary application(s) hosted by the Service Provider.

12.2 **Measurement and Exclusions.**  
(a) Availability shall be calculated as:  
Availability (%) = (Total Minutes in Month – Downtime Minutes) / (Total Minutes in Month) × 100.

(b) Downtime shall exclude:  

  (i) Scheduled Maintenance, as described in **Section 12.3**;  
  (ii) Any outage caused by the Client’s network, systems, or misuse of the Services;  
  (iii) Force Majeure Events under **Article XV**;  
  (iv) Outages caused by third-party service providers (e.g., Internet providers, cloud vendors) outside the Service Provider’s reasonable control;  
  (v) Emergency maintenance undertaken to address critical security vulnerabilities, provided the Service Provider gives the Client prompt notice.

12.3 **Scheduled Maintenance.**  
(a) The Service Provider may perform Scheduled Maintenance during predefined maintenance windows, which may be up to four (4) hours per week, generally occurring during off-peak hours (e.g., weekends or late nights in the Client’s primary time zone).  

(b) The Service Provider shall provide at least seventy-two (72) hours’ advance notice of Scheduled Maintenance that may cause temporary unavailability of the Services.

12.4 **Incident Priorities and Response/Resolution Times.**  
The Service Provider will categorize Incidents as follows:

- **Priority 1 (Critical)**: Complete loss of service or major business impact with no workaround. Target initial response time: **30 minutes**, 24x7x365. Target resolution or workaround time: **4 hours**.  
- **Priority 2 (High)**: Significant degradation of service or major feature failure with limited workaround. Target initial response: **1 hour** (within Service Provider business hours or 24x7 if designated in SOW). Target resolution or workaround: **8 hours**.  
- **Priority 3 (Medium)**: Partial loss of non-critical functionality, or minor performance issues. Target initial response: **4 business hours**. Target resolution or workaround: **3 Business Days**.  
- **Priority 4 (Low)**: General inquiries, cosmetic issues, or enhancement requests. Target initial response: **1 Business Day**. Resolution on a best-efforts basis, or as scheduled in future releases.

12.5 **Reporting and Root Cause Analysis.**  
The Service Provider shall provide the Client with:

(a) Monthly reports summarizing key Service Level metrics, including Availability, number of Incidents by severity, and average response and resolution times; and  

(b) Root cause analysis reports for all Priority 1 Incidents and, upon the Client’s request, for Priority 2 Incidents, within ten (10) Business Days after resolution.

12.6 **Service Credits.**  
(a) If Availability in any calendar month falls below 99.9%, the Client shall be entitled to Service Credits as follows:

- Availability 99.0% to 99.899%: Service Credit equal to 5% of the monthly recurring fees for the affected Services;  
- Availability 98.0% to 98.999%: Service Credit equal to 10% of the monthly recurring fees for the affected Services;  
- Availability below 98.0%: Service Credit equal to 15% of the monthly recurring fees for the affected Services.

(b) Service Credits shall be the Client’s sole and exclusive financial remedy for failure to meet Availability commitments, except where such failure results from the Service Provider’s gross negligence or willful misconduct.

(c) To receive a Service Credit, the Client must request it in writing within thirty (30) days after the end of the month in which the Availability failure occurred, and must provide reasonable details supporting the request. Approved Service Credits shall be applied to the Client’s next invoice and are not refundable in cash.

---

## ARTICLE XIII – CHANGE MANAGEMENT

13.1 **Change Requests.**  
Either Party may request changes to the scope, nature, or schedule of the Services or Deliverables (each a **“Change Request”**). All Change Requests shall be submitted in writing and include sufficient detail to evaluate the proposed change and its impact.

13.2 **Change Order Process.**  
Upon receipt of a Change Request, the Service Provider shall evaluate the request and, if the change is feasible, provide the Client with a written proposal that includes:

(a) A description of the proposed change;  

(b) The impact on scope, timeline, and Service Levels;  

(c) Any additional fees or credits associated with the change; and  

(d) Any other relevant terms or assumptions.

If the Parties agree to the terms of the proposal, they shall execute a **Change Order** signed by authorized representatives of both Parties. No Change Request shall be effective until embodied in a fully executed Change Order.

13.3 **Effect on Services and Fees.**  
Upon execution of a Change Order, the Parties’ obligations under the Agreement and applicable SOWs shall be amended to reflect the agreed changes. The Service Provider shall not be obligated to perform any out-of-scope work unless and until a Change Order is executed.

13.4 **Emergency Changes.**  
In the event of an emergency that threatens the stability, security, or availability of the Services, the Service Provider may implement temporary changes without prior written Change Order, provided that:

(a) The Service Provider uses reasonable efforts to minimize disruption to the Client; and  

(b) The Service Provider provides written notice as soon as reasonably practicable describing the change and its impact. Any lasting changes shall be documented in a subsequent Change Order.

---

## ARTICLE XIV – DISPUTE RESOLUTION

14.1 **Negotiation and Escalation.**  
In the event of any dispute, controversy, or claim arising out of or relating to this Agreement (a **“Dispute”**), the Parties shall first attempt in good faith to resolve the Dispute through informal discussions and escalation:

(a) The initiating Party shall provide written notice of the Dispute, describing its nature and basis in reasonable detail;  

(b) The Parties’ project managers shall meet (in person or via teleconference) within ten (10) Business Days to attempt resolution;  

(c) If not resolved, the Dispute shall be escalated to senior executives of each Party, who shall meet within twenty (20) Business Days of escalation to attempt resolution.

14.2 **Mediation.**  
If the Dispute is not resolved through negotiation within thirty (30) days after escalation to senior executives, the Parties shall submit the Dispute to non-binding mediation administered by a mutually agreed mediator in Seattle, Washington. The costs of mediation shall be shared equally, except that each Party shall bear its own attorneys’ fees.

14.3 **Arbitration or Litigation.**  
(a) If the Parties are unable to resolve the Dispute through mediation within sixty (60) days after commencement of mediation, either Party may initiate litigation in accordance with **Section 16.3**.  

(b) The Parties may, by mutual written agreement, elect to submit the Dispute to binding arbitration administered by the American Arbitration Association (AAA) in Seattle, Washington, before a panel of three arbitrators. In such case, the arbitration shall be conducted in English, and the arbitrators shall have the authority to award monetary and equitable relief consistent with this Agreement.

14.4 **Injunctive Relief.**  
Notwithstanding the foregoing, either Party may seek temporary or preliminary injunctive or other equitable relief in any court of competent jurisdiction to prevent or curtail actual or threatened unauthorized disclosure of Confidential Information, infringement of intellectual property rights, or violation of data protection obligations.

---

## ARTICLE XV – FORCE MAJEURE

15.1 **Definition.**  
A **“Force Majeure Event”** means any event or circumstance beyond a Party’s reasonable control, including acts of God, flood, earthquake, war, terrorism, civil unrest, governmental actions, labor disputes (other than those involving the affected Party’s employees), pandemic or epidemic, failure of third-party telecommunications or hosting providers, or other similar events that prevent or delay performance.

15.2 **Notice and Mitigation.**  
The Party affected by a Force Majeure Event shall:

(a) Promptly notify the other Party in writing of the nature and expected duration of the event;  

(b) Use commercially reasonable efforts to mitigate the effects of the Force Majeure Event and resume performance as soon as reasonably practicable; and  

(c) Keep the other Party reasonably informed of the status of its efforts.

15.3 **Excused Performance.**  
During the continuation of a Force Majeure Event, the affected Party’s obligations shall be excused to the extent performance is prevented or delayed. The Service Levels may be suspended during such period to the extent affected by the Force Majeure Event.

15.4 **Extended Force Majeure.**  
If a Force Majeure Event continues for more than sixty (60) consecutive days and materially affects the performance of the Services, either Party may terminate the affected Services or this Agreement upon thirty (30) days’ written notice without liability, except for payment obligations accrued prior to termination.

---

## ARTICLE XVI – GENERAL PROVISIONS

16.1 **Entire Agreement.**  
This Agreement, including all SOWs, Change Orders, and any exhibits or addenda incorporated herein, constitutes the entire agreement between the Parties with respect to the subject matter hereof and supersedes all prior or contemporaneous agreements, proposals, negotiations, representations, and understandings, whether written or oral.

16.2 **Amendments.**  
No amendment or modification of this Agreement shall be effective unless in writing and signed by authorized representatives of both Parties, referencing this Agreement and specifically indicating the intent to amend.

16.3 **Governing Law and Venue.**  
This Agreement shall be governed by and construed in accordance with the laws of the **State of Washington**, without giving effect to any choice or conflict of law rules. Subject to **Article XIV**, the Parties consent to the exclusive jurisdiction of the state and federal courts located in King County, Washington, for any action arising out of or relating to this Agreement.

16.4 **Severability.**  
If any provision of this Agreement is held to be invalid, illegal, or unenforceable by a court of competent jurisdiction, such provision shall be enforced to the maximum extent permissible, and the remaining provisions shall remain in full force and effect.

16.5 **Waiver.**  
No failure or delay by either Party in exercising any right, power, or remedy under this Agreement shall operate as a waiver thereof, nor shall any single or partial exercise thereof preclude any other or further exercise of such right, power, or remedy. Any waiver must be in writing and signed by an authorized representative of the waiving Party.

16.6 **Notices.**  
All notices required or permitted under this Agreement shall be in writing and shall be deemed given when:

(a) Delivered personally;  

(b) Sent by a nationally recognized overnight courier with tracking; or  

(c) Sent by registered or certified mail, return receipt requested, postage prepaid,

in each case addressed to the Parties at the following addresses (or such other addresses as either Party may designate by notice):

**If to Client (Contoso Enterprises):**  
Contoso Enterprises  
Attn: General Counsel  
500 Pine Street, Suite 2100  
Seattle, WA 98101  
United States  

With a copy (which shall not constitute notice) to:  
Contoso Enterprises  
Attn: CIO / IT Operations  
500 Pine Street, Suite 2100  
Seattle, WA 98101  
United States  

**If to Service Provider (Delta LLC):**  
Delta LLC  
Attn: Legal Department  
1200 Harbor Avenue SW, Suite 900  
Seattle, WA 98116  
United States  

With a copy (which shall not constitute notice) to:  
Delta LLC  
Attn: VP, Client Services  
1200 Harbor Avenue SW, Suite 900  
Seattle, WA 98116  
United States  

16.7 **Independent Contractors.**  
The Parties are independent contractors. Nothing in this Agreement shall be construed to create a partnership, joint venture, agency, or employment relationship between the Parties. Neither Party has the authority to bind the other Party in any manner.

16.8 **Assignment.**  
The Client may not assign or transfer this Agreement, in whole or in part, without the prior written consent of the Service Provider, which shall not be unreasonably withheld; provided, however, that the Client may assign this Agreement without consent to an Affiliate or in connection with a merger, acquisition, or sale of all or substantially all of its assets. The Service Provider may assign this Agreement to an Affiliate or in connection with a merger, acquisition, or sale of its business or assets related to the Services, upon notice to the Client. This Agreement shall be binding upon and inure to the benefit of the Parties and their respective successors and permitted assigns.

16.9 **No Third-Party Beneficiaries.**  
Except as expressly provided in **Article VIII** with respect to indemnified parties, this Agreement is for the sole benefit of the Parties and their respective successors and permitted assigns, and nothing herein is intended to confer any rights or remedies upon any other person or entity.

16.10 **Counterparts; Electronic Signatures.**  
This Agreement may be executed in counterparts, each of which shall be deemed an original and all of which together shall constitute one and the same instrument. Signatures transmitted electronically (including by PDF or other electronic means or via electronic signature platforms) shall be deemed original signatures for all purposes.

---

## SIGNATURE BLOCK

IN WITNESS WHEREOF, the Parties hereto have caused this Service Level Agreement, reference number **SLA-DEL-202410-342**, to be executed by their duly authorized representatives as of the dates set forth below.

### For Contoso Enterprises (Client)

Contoso Enterprises  
500 Pine Street, Suite 2100  
Seattle, WA 98101  
United States  

By: _________________________________  
Name: ______________________________  
Title: _______________________________  
Date: _______________________________

Witness (if applicable):  
Signature: ___________________________  
Name: ______________________________  
Date: _______________________________

---

### For Delta LLC (Vendor / Service Provider)

Delta LLC  
1200 Harbor Avenue SW, Suite 900  
Seattle, WA 98116  
United States  

By: _________________________________  
Name: ______________________________  
Title: _______________________________  
Date: _______________________________

Witness (if applicable):  
Signature: ___________________________  
Name: ______________________________  
Date: _______________________________