import os
import re
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
MODEL_PATH = os.path.join(OUTPUT_DIR, "ticket_classifier.joblib")

# Mapping rules from operating policy definitions
CATEGORY_TEAM_MAP = {
    "Delivery & Logistics": "Logistics",
    "Returns & Refunds": "Returns Desk",
    "Payments & Billing": "Billing",
    "Hardware & Warranty": "Escalations & Warranty",
    "Product & General Inquiries": "Chat Frontline"
}

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def derive_ground_truth(df, agents):
    """
    Derives realistic ground truth category based on agent notes, resolving agent team,
    and refund reason codes where intake chatbot tag was flawed.
    """
    # Merge resolving agent's team from agents.csv
    agents_clean = agents.drop_duplicates(subset=["agent_id"]).copy()
    df = df.merge(agents_clean[["agent_id", "team"]], on="agent_id", how="left")

    true_cat = []
    for _, row in df.iterrows():
        notes = str(row.get("agent_notes", "")).lower()
        msg = str(row.get("customer_message", "")).lower()
        res_team = str(row.get("team", ""))
        reason = str(row.get("refund_reason_code", ""))

        if any(w in notes or w in msg for w in ["tracking", "courier", "delivery", "deliv", "shipment", "transit", "delayed", "rto", "address"]):
            true_cat.append("Delivery & Logistics")
        elif any(w in notes or w in msg for w in ["refund", "return", "pickup", "reverse", "qc", "bank account", "neft"]) or reason in ["RETURN-QC-OK", "GW-OTHER"]:
            true_cat.append("Returns & Refunds")
        elif any(w in notes or w in msg for w in ["invoice", "payment", "gateway", "double charged", "otp", "upi", "credit card"]) or reason == "DUP-PAYMENT":
            true_cat.append("Payments & Billing")
        elif any(w in notes or w in msg for w in ["warranty", "buzzing", "static", "repair", "hardware", "not working", "bluetooth", "dead", "battery", "left earbud", "rma"]) or row.get("replacement_issued") == "Y":
            true_cat.append("Hardware & Warranty")
        else:
            if res_team == "Logistics":
                true_cat.append("Delivery & Logistics")
            elif res_team == "Billing":
                true_cat.append("Payments & Billing")
            elif res_team == "Returns Desk":
                true_cat.append("Returns & Refunds")
            elif res_team == "Escalations & Warranty":
                true_cat.append("Hardware & Warranty")
            else:
                true_cat.append("Product & General Inquiries")

    df["true_category"] = true_cat
    df["true_team"] = df["true_category"].map(CATEGORY_TEAM_MAP).fillna("Chat Frontline")
    return df

def train_classifier():
    cleaned_path = os.path.join(OUTPUT_DIR, "cleaned_tickets_reconciled.csv")
    if not os.path.exists(cleaned_path):
        import pipeline
        pipeline.main()

    df = pd.read_csv(cleaned_path)
    agents = pd.read_csv(os.path.join(DATA_DIR, "agents.csv"))
    df = derive_ground_truth(df, agents)

    # Feature: Combine customer opening message and agent notes
    df["combined_text"] = (df["customer_message"].fillna("") + " " + df["agent_notes"].fillna("")).apply(clean_text)

    # Filter out empty text
    valid_mask = df["combined_text"].str.len() > 5
    train_df = df[valid_mask].copy()

    X = train_df["combined_text"]
    y = train_df["true_category"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])

    model_pipeline.fit(X_train, y_train)

    # Predict back across dataset
    df["predicted_category"] = model_pipeline.predict(df["combined_text"].apply(clean_text))
    df["predicted_team"] = df["predicted_category"].map(CATEGORY_TEAM_MAP).fillna("Chat Frontline")

    # Save model and enriched predictions
    joblib.dump(model_pipeline, MODEL_PATH)
    output_enriched = os.path.join(OUTPUT_DIR, "cleaned_tickets_reconciled.csv")
    df.to_csv(output_enriched, index=False)
    print(f"Classifier trained and saved to {MODEL_PATH}")

    return model_pipeline, X_test, y_test

if __name__ == "__main__":
    train_classifier()