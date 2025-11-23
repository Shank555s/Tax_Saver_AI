import pandas as pd
import numpy as np
import os

print("🤖 Starting Recommendation Engine...")

# ======================================================
# Load tax results dataset
# ======================================================
TAX_RESULTS_PATH = "datasets/final_tax_results.csv"

try:
    df = pd.read_csv(TAX_RESULTS_PATH)
    print("✅ Loaded tax results successfully!")
except Exception as e:
    raise SystemExit(f"❌ Error loading tax results: {e}")


# ======================================================
# Recommendation Functions
# ======================================================

def suggest_80C(row):
    max_limit = 150000
    current = row["Investment_80C"]
    
    if current < max_limit:
        deficit = max_limit - current
        return f"Invest ₹{deficit:.0f} more in 80C to maximize tax saving."
    return "You have maximized 80C benefits."


def suggest_80D(row):
    max_limit = 25000
    current = row["Medical_Insurance_80D"]

    if current < max_limit:
        deficit = max_limit - current
        return f"Increase health insurance by ₹{deficit:.0f} to reduce taxes."
    return "Your 80D medical insurance tax benefits are fully utilized."


def suggest_nps(row):
    max_limit = 50000
    current = row["NPS_Contribution_80CCD"]

    if current < max_limit:
        deficit = max_limit - current
        return f"Invest ₹{deficit:.0f} in NPS (80CCD) for extra deductions."
    return "NPS tax benefits fully utilized."


def suggest_regime(row):
    if row["Best_Regime"] == "New Regime":
        return f"Switch to New Regime and save ₹{row['Tax_Savings']:.0f}."
    else:
        return f"Stick to Old Regime and save ₹{row['Tax_Savings']:.0f}."


def suggest_expenses(row):
    suggestions = []

    if row["Expense_Ratio"] > 0.7:
        suggestions.append("Your expenses exceed 70% of your salary. Try reducing lifestyle expenses.")

    # Check overspending categories:
    if row["Entertainment"] > 0.15 * row["Annual_Salary"]:
        suggestions.append("Reduce entertainment expenses by 15–20% to save more.")

    if row["Groceries"] > 0.25 * row["Annual_Salary"]:
        suggestions.append("Your grocery expenses are high; consider budgeting strategies.")

    if len(suggestions) == 0:
        return "Your spending pattern is balanced."

    return " ".join(suggestions)


def suggest_hra(row):
    if row["HRA_Received"] > 0 and row["Rent_Paid"] > 0:
        return "You can claim HRA exemption under Old Regime."
    if row["Rent_Paid"] == 0:
        return "You are not paying rent; HRA exemption does not apply."
    return "No HRA-related advice."


# ======================================================
# Generate All Recommendations
# ======================================================
df["Recommendation_80C"] = df.apply(suggest_80C, axis=1)
df["Recommendation_80D"] = df.apply(suggest_80D, axis=1)
df["Recommendation_NPS"] = df.apply(suggest_nps, axis=1)
df["Recommendation_Regime"] = df.apply(suggest_regime, axis=1)
df["Recommendation_Expenses"] = df.apply(suggest_expenses, axis=1)
df["Recommendation_HRA"] = df.apply(suggest_hra, axis=1)


# ======================================================
# Save Recommendations
# ======================================================
OUTPUT_PATH = "datasets/tax_recommendations.csv"
df.to_csv(OUTPUT_PATH, index=False)

print(f"✅ Recommendations generated successfully! Saved at: {os.path.abspath(OUTPUT_PATH)}")
print("🤖 Recommendation Engine Complete!")
