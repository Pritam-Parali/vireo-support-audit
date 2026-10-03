import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import joblib

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
MODEL_PATH = os.path.join(OUTPUT_DIR, "ticket_classifier.joblib")

def plot_confusion_matrix(y_true, y_pred, labels):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(9, 7))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.title("Ticket Classification Confusion Matrix")
    plt.xlabel("Predicted Category")
    plt.ylabel("Actual Category")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "confusion_matrix.png"), dpi=300)
    plt.close()

def plot_monthly_charts(df):
    df["created_at_dt"] = pd.to_datetime(df["created_at"])
    df["year_month"] = df["created_at_dt"].dt.to_period("M").astype(str)

    # 1. Monthly volume by true/predicted category
    cat_monthly = df.groupby(["year_month", "predicted_category"]).size().unstack(fill_value=0)
    plt.figure(figsize=(13, 6))
    cat_monthly.plot(kind="bar", stacked=True, colormap="tab10", ax=plt.gca())
    plt.title("Monthly Ticket Volume by Category (Post-AI Auto-Categorisation)")
    plt.xlabel("Month")
    plt.ylabel("Ticket Count")
    plt.xticks(rotation=45)
    plt.legend(title="Category", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "monthly_breakdown_by_category.png"), dpi=300)
    plt.close()

    # 2. Monthly volume comparison: Assigned (Chatbot) vs Predicted (True Workload) Team
    team_comparison = pd.DataFrame({
        "Chatbot Intake Assigned": df["assigned_team"].value_counts(),
        "AI Corrected Team": df["predicted_team"].value_counts()
    }).fillna(0)

    plt.figure(figsize=(10, 5))
    team_comparison.plot(kind="bar", ax=plt.gca(), colormap="viridis")
    plt.title("Workload Discrepancy: Intake Assigned Team vs. True Workload Team")
    plt.xlabel("Support Team")
    plt.ylabel("Total Tickets")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "monthly_breakdown_by_team.png"), dpi=300)
    plt.close()

def main():
    cleaned_path = os.path.join(OUTPUT_DIR, "cleaned_tickets_reconciled.csv")
    df = pd.read_csv(cleaned_path)

    labels = sorted(df["predicted_category"].unique())
    y_true = df["true_category"]
    y_pred = df["predicted_category"]

    print("--- Classification Performance Report ---")
    print(classification_report(y_true, y_pred, target_names=labels))

    plot_confusion_matrix(y_true, y_pred, labels)
    plot_monthly_charts(df)

    # Quantify the exact business finding
    bot_billing_pct = (df["assigned_team"] == "Billing").mean() * 100
    actual_billing_pct = (df["predicted_team"] == "Billing").mean() * 100
    actual_logistics_pct = (df["predicted_team"] == "Logistics").mean() * 100
    misrouted_count = (df["assigned_team"] != df["predicted_team"]).sum()
    transfer_waste = misrouted_count * 305.0

    print("\n--- Business Case Verification ---")
    print(f"Chatbot Intake Billing Volume: {bot_billing_pct:.1f}%")
    print(f"True Billing Workload Volume: {actual_billing_pct:.1f}%")
    print(f"True Logistics Workload Volume: {actual_logistics_pct:.1f}%")
    print(f"Misrouted Tickets: {misrouted_count} ({misrouted_count/len(df)*100:.1f}%)")
    print(f"Wasted Transfer Cost: Rs {transfer_waste:,.2f}")

if __name__ == "__main__":
    main()