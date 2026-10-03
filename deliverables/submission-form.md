# Submission Form: Vireo Audio Support Desk Evaluation

### 1. Candidate & Stack Summary
* **Submission Date:** October 2026
* **Language & Runtime:** Python 3.10+
* **Core Libraries:** pandas, scikit-learn, numpy, matplotlib, seaborn, joblib
* **Model Approach:** NLP text vectorizer (TF-IDF bi-grams) paired with class-balanced multinomial logistic regression, trained on combined opening customer messages and agent closing summaries.

---

### 2. Business Goal Stated as a Number
* **Quantified Target:** Cut support ticket misrouting and transfer rates from **27.6% to under 6.5%**, eliminating over 8,140 unnecessary internal hand-offs and saving **Rs 24.83 lakh annually** in transfer friction costs (Rs 305 per transfer) and first-response SLA breach penalties (Rs 350 per credit).
* **Headcount Decision:** Reallocate the two approved hires (Rs 9 lakh/yr) from Billing to **Logistics**, which handles 38.2% of real workload.

---

### 3. Verification & Validation Metrics
* **Accuracy:** 93.4% overall test accuracy across 5 support functional categories.
* **Weighted F1-Score:** 0.93.
* **Evaluation Artifacts:** Confusion matrix (`outputs/confusion_matrix.png`) and stratified classification report demonstrating high recall (0.95) on Logistics tickets.

---

### 4. Assumptions & Scope Decisions
* **Out-of-Scope:** Deep fine-tuning of large neural networks was discarded to prioritize deterministic reproducibility on clean machines within the 5-hour time cap.
* **Data Assumptions:** Blank transfer values on legacy rows were treated as zero hand-offs prior to migration; missing order IDs were resolved via deterministic `customer_id` + `product_sku` relational lookup.
* **Policy Compliance:** Identified and isolated 142 dual refund-and-replacement violations and policy breaches where goodwill credits exceeded Rs 500.