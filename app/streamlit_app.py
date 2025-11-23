import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ======================================================
# Helper Functions for Tax Calculations
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
            tax += (min(taxable_income, upper) - lower) * rate

    if taxable_income <= 700000:  # Section 87A rebate
        return 0

    return tax


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
            tax += (min(taxable_income, upper) - lower) * rate

    if taxable_income <= 500000:  # Section 87A rebate
        return 0

    return tax


# ======================================================
# Cached Loaders
# ======================================================

@st.cache_data
def load_preprocessed():
    path = "datasets/final_preprocessed_dataset.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

@st.cache_data
def load_tax_results():
    path = "datasets/final_tax_results.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

@st.cache_data
def load_recommendations():
    path = "datasets/tax_recommendations.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


# ======================================================
# STREAMLIT UI CONFIG
# ======================================================

st.set_page_config(page_title="Tax Saver AI", layout="wide")
st.title("💰 Tax Saver AI – Optimize Your Tax & Savings")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Tax Comparison", "Recommendations", "Visual Insights", "Personal Calculator"]
)


# ======================================================
# 1️⃣ HOME PAGE
# ======================================================

if page == "Home":
    st.header("📥 Preprocessed Dataset")

    df = load_preprocessed()
    if df is not None:
        st.write("Preview of the dataset used for tax computation:")
        st.dataframe(df.head())
    else:
        st.error("❌ final_preprocessed_dataset.csv not found.")


# ======================================================
# 2️⃣ TAX COMPARISON PAGE
# ======================================================

elif page == "Tax Comparison":
    st.header("📊 Old vs New Tax Regime Comparison")

    df = load_tax_results()
    if df is None:
        st.error("❌ Run tax_engine.py to generate final_tax_results.csv")
    else:
        st.dataframe(df.head())

        fig = px.bar(
            df,
            x="Name",
            y=["Tax_Old_Regime", "Tax_New_Regime"],
            barmode="group",
            title="Tax Comparison — Old Regime vs New Regime"
        )
        st.plotly_chart(fig, use_container_width=True)


# ======================================================
# 3️⃣ RECOMMENDATIONS PAGE
# ======================================================

elif page == "Recommendations":
    st.header("🤖 Personalized Tax-Saving Recommendations")

    df = load_recommendations()
    if df is None:
        st.error("❌ tax_recommendations.csv missing. Run recommendation_engine.py")
    else:
        user = st.selectbox("Select User", df["Name"].unique())
        u = df[df["Name"] == user].iloc[0]

        st.subheader(f"🎯 Best Regime for {u['Name']}")
        st.write(f"**Best Regime:** {u['Best_Regime']}")
        st.write(f"**Tax Savings:** ₹{u['Tax_Savings']:,}")

        st.markdown("---")
        st.subheader("📘 80C Recommendations")
        st.info(u["Recommendation_80C"])

        st.subheader("🏥 Medical Insurance (80D)")
        st.info(u["Recommendation_80D"])

        st.subheader("💼 NPS Contribution Advice")
        st.info(u["Recommendation_NPS"])

        st.subheader("🏠 HRA / Rent Advice")
        st.warning(u["Recommendation_HRA"])

        st.subheader("💳 Spending Advice")
        st.success(u["Recommendation_Expenses"])


# ======================================================
# 4️⃣ VISUAL INSIGHTS PAGE
# ======================================================

elif page == "Visual Insights":
    st.header("📈 Visual Insights")

    df = load_preprocessed()
    if df is None:
        st.error("Dataset missing.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Salary Distribution")
            fig = px.histogram(df, x="Annual_Salary")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Rent Distribution")
            fig = px.box(df, y="Rent_Paid")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Expense Ratio Distribution")
        fig = px.histogram(df, x="Expense_Ratio")
        st.plotly_chart(fig, use_container_width=True)


# ======================================================
# 5️⃣ PERSONAL TAX CALCULATOR (MANUAL INPUT)
# ======================================================

elif page == "Personal Calculator":
    st.header("🧮 Personal Tax Calculator (Manual Input)")

    st.write("Fill the details to calculate tax and get AI-generated advice:")

    with st.form("personal_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=18, max_value=80, value=25)
        city = st.text_input("City")

        st.subheader("💼 Salary Details")
        annual_salary = st.number_input("Annual Salary (₹)", min_value=0, value=700000)

        st.subheader("🏠 Rent & HRA")
        rent_paid = st.number_input("Rent Paid (₹/year)", min_value=0, value=120000)
        hra_received = st.number_input("HRA Received (₹/year)", min_value=0, value=100000)

        st.subheader("📘 Tax-Saving Investments")
        inv_80c = st.number_input("80C Investments (₹)", min_value=0, max_value=150000, value=50000)
        med_80d = st.number_input("80D (Medical Insurance) (₹)", min_value=0, max_value=25000, value=10000)
        nps = st.number_input("NPS Contribution (₹)", min_value=0, max_value=50000, value=0)
        home_interest = st.number_input("Home Loan Interest (24b) (₹)", min_value=0, value=0)
        donations = st.number_input("Donations (80G) (₹)", min_value=0, value=0)

        st.subheader("💳 Annual Expenses")
        groceries = st.number_input("Groceries (₹)", min_value=0, value=60000)
        utilities = st.number_input("Utilities (₹)", min_value=0, value=20000)
        entertainment = st.number_input("Entertainment (₹)", min_value=0, value=30000)
        healthcare = st.number_input("Healthcare (₹)", min_value=0, value=15000)

        submit = st.form_submit_button("Calculate Tax")

    if submit:

        df = pd.DataFrame([{
            "Name": name,
            "Annual_Salary": annual_salary,
            "Rent_Paid": rent_paid,
            "HRA_Received": hra_received,
            "Investment_80C": inv_80c,
            "Medical_Insurance_80D": med_80d,
            "NPS_Contribution_80CCD": nps,
            "Home_Loan_Interest_24b": home_interest,
            "Donations_80G": donations,
            "Groceries": groceries,
            "Utilities": utilities,
            "Entertainment": entertainment,
            "Healthcare": healthcare
        }])

        df["Total_Deductions"] = (
            df["Investment_80C"] +
            df["Medical_Insurance_80D"] +
            df["NPS_Contribution_80CCD"] +
            df["Home_Loan_Interest_24b"] +
            df["Donations_80G"]
        )

        df["Taxable_Income"] = (
            df["Annual_Salary"] - (df["Total_Deductions"] + 50000)
        ).clip(lower=0)

        df["Tax_Old_Regime"] = df["Taxable_Income"].apply(compute_old_regime_tax)
        df["Tax_New_Regime"] = df["Taxable_Income"].apply(compute_new_regime_tax)

        df["Best_Regime"] = np.where(
            df["Tax_New_Regime"] < df["Tax_Old_Regime"],
            "New Regime",
            "Old Regime"
        )

        df["Tax_Savings"] = abs(df["Tax_Old_Regime"] - df["Tax_New_Regime"])

        # ---------- Display Results ----------
        st.subheader("📊 Tax Summary")
        st.write(f"**Best Regime:** {df['Best_Regime'][0]}")
        st.write(f"**Old Regime Tax:** ₹{df['Tax_Old_Regime'][0]:,}")
        st.write(f"**New Regime Tax:** ₹{df['Tax_New_Regime'][0]:,}")
        st.write(f"**Savings:** ₹{df['Tax_Savings'][0]:,}")

        # ---------- Recommendations ----------
        st.subheader("🤖 Recommendations")

        if inv_80c < 150000:
            st.info(f"Invest ₹{150000 - inv_80c} more in 80C.")

        if med_80d < 25000:
            st.info(f"Increase 80D by ₹{25000 - med_80d}.")

        if nps < 50000:
            st.info(f"Invest ₹{50000 - nps} more in NPS.")

        expense_ratio = (
            groceries + utilities + entertainment + healthcare
        ) / annual_salary

        if expense_ratio > 0.7:
            st.warning("Your expenses exceed 70% of your income. Consider reducing unnecessary spending.")
        else:
            st.success("Your spending is well-balanced.")

# ======================================================
st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Tax Saver AI © 2025")
