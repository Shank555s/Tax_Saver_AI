'''
        To run: python src/data_preprocessing.py
        This script preprocesses multiple datasets to create a final clean dataset
        suitable for tax-saving analysis.
        Datasets used:
        - Software_Professional_Salaries.csv
        - paysim.csv
        - spending_habits.csv
        - synthetic_tax_user_dataset.csv
        - House_Rent_Dataset.csv    
'''


import pandas as pd
import numpy as np
import os

print("🚀 Starting preprocessing pipeline...")

# === Load all datasets ===
try:
    salary_df = pd.read_csv("datasets/Software_Professional_Salaries.csv")
    paysim_df = pd.read_csv("datasets/paysim.csv")
    spend_df = pd.read_csv("datasets/spending_habits.csv")
    synthetic_df = pd.read_csv("datasets/synthetic_tax_user_dataset.csv")
    rent_df = pd.read_csv("datasets/House_Rent_Dataset.csv")
    print("✅ All datasets loaded successfully!")
except Exception as e:
    raise SystemExit(f"❌ Error loading datasets: {e}")

# === Clean and align column names ===
spend_df.rename(
    columns={
        "Income": "Annual_Salary",
        "Rent": "Rent_Paid",
        "Insurance": "Medical_Insurance_80D",
    },
    inplace=True,
)

if "Rent" in rent_df.columns:
    rent_df["Rent"] = rent_df["Rent"].replace("[^0-9]", "", regex=True).astype(float)
    rent_df["Annual_Rent"] = rent_df["Rent"] * 12

# === Merge median rent by city ===
city_rent = (
    rent_df.groupby("City")["Annual_Rent"]
    .median()
    .reset_index()
    .rename(columns={"Annual_Rent": "Median_Rent"})
)
synthetic_df = synthetic_df.merge(city_rent, on="City", how="left")
synthetic_df["Rent_Paid"] = synthetic_df["Rent_Paid"].fillna(
    synthetic_df["Median_Rent"]
)

# === Merge spending habits on salary ===
spend_df["Annual_Salary"] = spend_df["Annual_Salary"].astype(int)
synthetic_df["Annual_Salary"] = synthetic_df["Annual_Salary"].astype(int)

cols_to_merge = [
    "Annual_Salary",
    "Rent_Paid",
    "Groceries",
    "Utilities",
    "Healthcare",
    "Education",
    "Entertainment",
]
available_cols = [c for c in cols_to_merge if c in spend_df.columns]
synthetic_df = synthetic_df.merge(spend_df[available_cols], on="Annual_Salary", how="left")

# === Ensure valid Rent_Paid column ===
rent_like_cols = [c for c in synthetic_df.columns if "rent" in c.lower()]
if not rent_like_cols:
    synthetic_df["Rent_Paid"] = (synthetic_df["Annual_Salary"] * 0.15).astype(int)
else:
    best_rent_col = max(
        rent_like_cols, key=lambda c: synthetic_df[c].notna().sum()
    )
    synthetic_df["Rent_Paid"] = synthetic_df[best_rent_col].fillna(
        (synthetic_df["Annual_Salary"] * 0.15).astype(int)
    )
    for c in rent_like_cols:
        if c != "Rent_Paid":
            synthetic_df.drop(columns=c, inplace=True, errors="ignore")

# === Fill missing expense fields ===
for col in ["Groceries", "Utilities", "Healthcare", "Education", "Entertainment"]:
    if col not in synthetic_df.columns:
        synthetic_df[col] = np.random.randint(20000, 100000, len(synthetic_df))
    else:
        mask = synthetic_df[col].isna()
        synthetic_df.loc[mask, col] = np.random.randint(20000, 100000, mask.sum())

# === Compute deductions and taxable income ===
synthetic_df["Total_Deductions"] = (
    synthetic_df["Investment_80C"]
    + synthetic_df["Medical_Insurance_80D"]
    + synthetic_df["NPS_Contribution_80CCD"]
    + synthetic_df["Home_Loan_Interest_24b"]
    + synthetic_df["Donations_80G"]
)

synthetic_df["Taxable_Income"] = (
    synthetic_df["Annual_Salary"] - (synthetic_df["Total_Deductions"] + 50000)
).clip(lower=0)

# === Compute expenses and savings ===
expense_cols = [
    c
    for c in [
        "Rent_Paid",
        "Groceries",
        "Utilities",
        "Healthcare",
        "Education",
        "Entertainment",
    ]
    if c in synthetic_df.columns
]
synthetic_df["Total_Expenses"] = synthetic_df[expense_cols].sum(axis=1)
synthetic_df["Savings"] = synthetic_df["Annual_Salary"] - synthetic_df["Total_Expenses"]
synthetic_df["Expense_Ratio"] = (
    synthetic_df["Total_Expenses"] / synthetic_df["Annual_Salary"]
).round(2)

# === Add slight randomness for realism ===
for col, var in zip(["Groceries", "Utilities", "Healthcare"], [5000, 3000, 2000]):
    synthetic_df[col] += np.random.randint(-var, var, len(synthetic_df))

# === Save final clean dataset ===
output_path = "datasets/final_preprocessed_dataset.csv"
synthetic_df.to_csv(output_path, index=False)

print(f"✅ Preprocessing complete! Clean dataset saved at: {os.path.abspath(output_path)}")
print(f"🧾 Rows: {len(synthetic_df)} | Columns: {len(synthetic_df.columns)}")
