import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Operating policy cost constants (Support Policy v3.2)
COST_PER_TRANSFER = 305.0
SLA_BREACH_PENALTY = 350.0
GOODWILL_CAP = 500.0

SLA_TARGET_HOURS = {
    "chat": 0.25,      # 15 minutes
    "voice": 2.0,       # 2 hours callback
    "social": 4.0,      # 4 hours
    "email": 8.0        # 8 hours
}

def load_raw_data():
    tickets = pd.read_csv(os.path.join(DATA_DIR, "tickets.csv"))
    agents = pd.read_csv(os.path.join(DATA_DIR, "agents.csv"))
    orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
    products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
    customers = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
    return tickets, agents, orders, products, customers

def reconcile_data(tickets, orders):
    # 1. Deduplicate migrated legacy Freshdesk tickets
    # Pre-migration rows re-imported during reconciliation may duplicate helpdesk rows
    tickets["created_at_dt"] = pd.to_datetime(tickets["created_at"], errors="coerce")
    tickets = tickets.sort_values(by=["ticket_id", "source_system"], ascending=[True, True])
    tickets = tickets.drop_duplicates(subset=["ticket_id"], keep="first").copy()

    # 2. Parse timestamps (Helpdesk displays IST; legacy event log stores UTC)
    tickets["first_response_at_dt"] = pd.to_datetime(tickets["first_response_at"], errors="coerce")
    tickets["resolved_at_dt"] = pd.to_datetime(tickets["resolved_at"], errors="coerce")

    # Correct legacy UTC resolution timestamps to IST (+5h 30m)
    legacy_mask = tickets["source_system"] == "legacy_fd"
    tickets.loc[legacy_mask, "resolved_at_dt"] = tickets.loc[legacy_mask, "resolved_at_dt"] + pd.Timedelta(hours=5, minutes=30)

    # 3. Fallback join for missing order_id (customer_id + product_sku)
    missing_orders = tickets["order_id"].isna() & tickets["product_sku"].notna()
    if missing_orders.any():
        order_lookup = orders[["order_id", "customer_id", "sku"]].drop_duplicates(subset=["customer_id", "sku"])
        merged = tickets.loc[missing_orders, ["customer_id", "product_sku"]].merge(
            order_lookup,
            left_on=["customer_id", "product_sku"],
            right_on=["customer_id", "sku"],
            how="left"
        )
        tickets.loc[missing_orders, "order_id"] = merged["order_id"].values

    # 4. Fill missing transfers (Freshdesk did not track transfers; default legacy to 0)
    tickets["transfers"] = pd.to_numeric(tickets["transfers"], errors="coerce").fillna(0).astype(int)

    # 5. Calculate First-Response SLA Breaches
    tickets["first_response_hours"] = (tickets["first_response_at_dt"] - tickets["created_at_dt"]).dt.total_seconds() / 3600.0
    tickets["sla_target_hours"] = tickets["channel"].str.lower().map(SLA_TARGET_HOURS).fillna(8.0)
    tickets["is_sla_breach"] = (tickets["first_response_hours"] > tickets["sla_target_hours"]) & tickets["first_response_at_dt"].notna()
    tickets["sla_breach_cost_inr"] = np.where(tickets["is_sla_breach"], SLA_BREACH_PENALTY, 0.0)

    # 6. Calculate Internal Transfer Costs
    tickets["transfer_cost_inr"] = tickets["transfers"] * COST_PER_TRANSFER

    return tickets

def run_policy_audits(tickets):
    # Audit 1: Section 5 Violation - Both refund and replacement issued for same order
    dual_payout = tickets[
        (tickets["refund_amount_inr"].fillna(0) > 0) & 
        (tickets["replacement_issued"].astype(str).str.upper() == "Y")
    ].copy()
    dual_payout.to_csv(os.path.join(OUTPUT_DIR, "audit_dual_refund_replacement.csv"), index=False)

    # Audit 2: Section 5 Violation - Goodwill refund exceeding Rs 500 cap
    goodwill_violations = tickets[
        (tickets["refund_reason_code"] == "GW-OTHER") & 
        (tickets["refund_amount_inr"].fillna(0) > GOODWILL_CAP)
    ].copy()
    goodwill_violations.to_csv(os.path.join(OUTPUT_DIR, "audit_goodwill_cap_violations.csv"), index=False)

    return len(dual_payout), len(goodwill_violations)

def main():
    tickets, agents, orders, products, customers = load_raw_data()
    cleaned_tickets = reconcile_data(tickets, orders)
    dual_count, gw_count = run_policy_audits(cleaned_tickets)

    cleaned_path = os.path.join(OUTPUT_DIR, "cleaned_tickets_reconciled.csv")
    cleaned_tickets.to_csv(cleaned_path, index=False)
    print(f"Data reconciliation complete. Saved cleaned dataset to {cleaned_path}")
    print(f"Policy Audits: {dual_count} dual refund/replacement violations, {gw_count} goodwill cap violations.")

if __name__ == "__main__":
    main()