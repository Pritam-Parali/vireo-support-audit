# EXECUTIVE BRIEFING: SUPPORT WORKLOAD & HEADCOUNT AUDIT

**To:** Priya Raman, Head of Customer Experience  
**From:** Technical Evaluation Lead  
**Date:** 10 October 2026  
**Subject:** Headcount Allocation Recommendation & Support Routing Audit  

---

### 1. Executive Summary & Hiring Decision
Allocating the two approved headcount additions (Rs 9.0 lakh annually) to the Billing team would be an expensive operational error. 

While the helpdesk intake queue indicates that Billing receives 22.4% of total ticket volume, our machine-learning re-audit of 18 months of free-text customer conversations and agent closing notes reveals that **Billing’s true workload represents only 8.7% of genuine customer demand**. Over 60% of tickets routed to Billing are delivery disputes, return requests, or courier inquiries tagged incorrectly by the front-end intake chatbot.

The team actually overwhelmed is **Logistics**, which absorbs **38.2% of total operational workload** despite being initially assigned only 16.1%. Logistics is suffering from severe hand-off cascades, extended resolution times exceeding 28 hours, and repeated first-response SLA breaches. **The two new hires must be assigned to Logistics.**

---

### 2. The Core Financial Goal: Rs 24.8 Lakh Annual Savings
By replacing the intake chatbot's static routing with automated NLP triage and eliminating erroneous transfers, Vireo can achieve the following quantifiable operational target:

> **Target:** Cut ticket transfer rates from **27.6% to below 6.5%**, preventing 8,140 unnecessary hand-offs per year and saving **Rs 24.83 lakh annually** in internal transfer penalties (Rs 305/transfer) and first-response SLA credits (Rs 350/breach).
+---------------------------------------------------------------------------------------+
| Strategic Metric               | Intake Bot Status Quo | With AI Auto-Categorisation  |
+---------------------------------------------------------------------------------------+
| Billing Apparent Volume        | 22.4% of queue        | 8.7% true workload           |
| Logistics True Volume          | 16.1% (assigned)      | 38.2% (actual workload)      |
| Internal Team Transfers        | 27.6% of tickets      | < 6.5% of tickets            |
| Wasted Transfer Overhead       | Rs 32.1 lakh / year   | Rs 7.3 lakh / year           |
| Net Annual Financial Impact    | Status Quo Baseline   | Rs 24.83 lakh savings / year |
+---------------------------------------------------------------------------------------+

---

### 3. Root Cause Analysis
1. **Intake Chatbot Misrouting:** The intake bot assigns tags based on ambiguous single-word customer prompts (e.g., "Where is my order / bill?"). Frontline agents rarely correct tags upon closure, creating an illusion of high Billing volume.
2. **Transfer Penalties:** Every misrouted ticket transferred to Logistics incurs a policy-mandated re-handling cost of Rs 305 and resets response queues, directly triggering automatic Rs 350 customer store credits.
3. **Policy Leakage in Returns Desk:** Our audit discovered dual refund-and-replacement payouts across 142 orders, violating Section 5 of Vireo Operating Policy and leaking unrecovered hardware costs.

---

### 4. Strategic Recommendations
1. **Reassign Headcount to Logistics:** Immediately deploy the two approved hires to Logistics to eliminate the 28-hour backlog and stop first-response SLA penalties.
2. **Implement Intelligent Classifier Routing:** Deploy our NLP classification pipeline into the helpdesk intake tier to route tickets directly to resolving teams with 93.4% validated accuracy.
3. **Lock Dual Payouts:** Enforce a hard stop in the helpdesk UI preventing agents from checking `replacement_issued = Y` when a refund is already registered on the order.