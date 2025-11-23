
import pandas as pd
import numpy as np
import os

print("🧮 Starting Tax Engine...")

# ======================================================
# 1️⃣ Load preprocessed dataset
# ======================================================
DATA_PATH = "datasets/final_preprocessed_dataset.csv"


try:
    df = pd.read_csv(DATA_PATH)
    print("✅ Loaded preprocessed dataset successfully!")
except Exception as e:
    raise SystemExit(f"❌ Error loading cleaned dataset: {e}")


# ======================================================
# 2️⃣ NEW REGIME TAX SLABS (Post-Budget 2023)
# ======================================================
def compute_new_regime_tax(taxable_income):
    tax = 0

    slabs = [
        (0, 300000, 0),
        (300000, 600000, 0.05),
        (600000, 900000, 0.10),
        (900000, 1200000, 0.15),
        (1200000, 1500000, 0.20),
        (1500000, float("inf"), 0.30),
    ]

    for lower, upper, rate in slabs:
        if taxable_income > lower:
            taxable_amount = min(taxable_income, upper) - lower
            tax += taxable_amount * rate

    # Rebate under 87A (income ≤ ₹7 lakh)
    if taxable_income <= 700000:
        return 0

    return tax


# ======================================================
# 3️⃣ OLD REGIME TAX SLABS
# ======================================================
def compute_old_regime_tax(taxable_income):
    tax = 0

    slabs = [
        (0, 250000, 0),
        (250000, 500000, 0.05),
        (500000, 1000000, 0.20),
        (1000000, float("inf"), 0.30),
    ]

    for lower, upper, rate in slabs:
        if taxable_income > lower:
            taxable_amount = min(taxable_income, upper) - lower
            tax += taxable_amount * rate

    # Rebate under 87A (≤ ₹5 lakh)
    if taxable_income <= 500000:
        return 0

    return tax


# ======================================================
# 4️⃣ Apply both tax systems for every user
# ======================================================
df["Tax_Old_Regime"] = df["Taxable_Income"].apply(compute_old_regime_tax)
df["Tax_New_Regime"] = df["Taxable_Income"].apply(compute_new_regime_tax)

# Best Regime Recommendation
df["Best_Regime"] = np.where(
    df["Tax_New_Regime"] < df["Tax_Old_Regime"], "New Regime", "Old Regime"
)

# Absolute Tax Savings
df["Tax_Savings"] = abs(df["Tax_Old_Regime"] - df["Tax_New_Regime"])


# ======================================================
# 5️⃣ Save final results
# ======================================================
OUTPUT_FILE = "datasets/final_tax_results.csv"
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Tax calculations complete! Results saved to: {os.path.abspath(OUTPUT_FILE)}")
print(f"🧾 Rows processed: {len(df)}")
print(f"📊 Columns available: {len(df.columns)}")
print("Tax Engine complete!")
