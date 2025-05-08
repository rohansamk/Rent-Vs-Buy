import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("🏡 Rent vs Buy: Cost-Benefit Calculator")

# --- USER INPUTS ---
house_price = st.number_input("Enter the house price ($)", value=500000)
down_payment = st.number_input("Enter the down payment ($)", value=100000)
annual_interest_rate = st.number_input("Annual loan interest rate (%)", value=6.0) / 100
loan_tenure_years = st.slider("Loan tenure (years)", min_value=1, max_value=30, value=10)

rental_yield = st.number_input("Rental yield (% of house price)", value=4.0) / 100
rent_increase_rate = st.number_input("Expected annual rent increase rate (%)", value=3.0) / 100
investment_return_rate = st.number_input("Annual investment return rate (%)", value=7.0) / 100
house_price_increase_rate = st.number_input("Annual real estate capital appreciation (%)", value=6.0) / 100

# --- CALCULATIONS ---
loan_amount = house_price - down_payment
emi_months = loan_tenure_years * 12
monthly_interest_rate = annual_interest_rate / 12
emi = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**emi_months / ((1 + monthly_interest_rate)**emi_months - 1)
annual_emi = emi * 12

initial_rent = house_price * rental_yield
current_investment = down_payment

# Lists to track yearly values
year_list, rent_list, emi_list, difference_list = [], [], [], []
investment_list, house_value_list, principal_left_list, value_of_house_owned_list = [], [], [], []

# Initial values
current_rent = initial_rent
current_house_value = house_price
remaining_principal = loan_amount

for year in range(1, loan_tenure_years + 1):
    difference = annual_emi - current_rent
    current_investment = (current_investment + difference) * (1 + investment_return_rate)
    current_house_value *= (1 + house_price_increase_rate)

    for _ in range(12):
        interest_payment = remaining_principal * monthly_interest_rate
        principal_payment = emi - interest_payment
        remaining_principal -= principal_payment
    remaining_principal = max(remaining_principal, 0)

    value_of_house_owned = current_house_value - remaining_principal

    # Append data
    year_list.append(year)
    rent_list.append(current_rent)
    emi_list.append(annual_emi)
    difference_list.append(difference)
    investment_list.append(current_investment)
    house_value_list.append(current_house_value)
    principal_left_list.append(remaining_principal)
    value_of_house_owned_list.append(value_of_house_owned)

    current_rent *= (1 + rent_increase_rate)

# --- DATAFRAMES ---
cba_table = pd.DataFrame({
    "Year": year_list,
    "Annual Rent": rent_list,
    "Annual EMI": emi_list,
    "Difference (EMI - Rent)": difference_list,
    "Compounded Investment": investment_list
})

future_values_table = pd.DataFrame({
    "Year": year_list,
    "House Value (in Millions)": [v / 1_000_000 for v in house_value_list],
    "Investment Amount (in Millions)": [v / 1_000_000 for v in investment_list],
    "Principal Left (in Millions)": [v / 1_000_000 for v in principal_left_list],
    "Value of House Owned (in Millions)": [v / 1_000_000 for v in value_of_house_owned_list]
})

# --- OUTPUT ---
st.subheader(f"📊 Monthly EMI: ${emi:,.2f}")
#st.subheader("📈 Total EMI Paid (in Millions)")
#total_emi = annual_emi * loan_tenure_years / 1_000_000
#st.write(f"{round(total_emi, 4)} Million")
st.subheader(f"📈 Total EMI to be Paid over {loan_tenure_years} Years: {round(annual_emi * loan_tenure_years / 1_000_000, 4)} Million")


# --- PLOT ---
st.subheader("📉 House Value vs Investment Over Time")
fig, ax = plt.subplots()
ax.plot(year_list, [v / 1_000_000 for v in house_value_list], label="House Value", marker='o')
ax.plot(year_list, [v / 1_000_000 for v in investment_list], label="Investment", marker='x')
ax.plot(year_list, [v / 1_000_000 for v in principal_left_list], label="Principal Left", marker='x')
ax.plot(year_list, [v / 1_000_000 for v in value_of_house_owned_list], label="Value of House Owned", marker='x')
ax.set_xlabel("Year")
ax.set_ylabel("Value (in Millions)")
ax.legend()
ax.grid(True)
st.pyplot(fig)

st.markdown("### 🧾 Summary After Loan Period")

final_investment = investment_list[-1]
final_rent = rent_list[-1] / 12  # Monthly rent at end
final_house_value = house_value_list[-1]

st.markdown(f"""
**After {loan_tenure_years} years**:

- 🏠 The **buyer** has fully owned the house, which is now worth **${final_house_value:,.0f}**.
- 💰 The **renter** has an investment value of **${final_investment:,.0f}**.
- 🏷️ The **renter’s monthly rent** at that point is **${final_rent:,.0f}**.
""")



st.subheader("📋 Cost-Benefit Analysis Table")
st.dataframe(cba_table)

st.subheader("🏡 Future Value Comparison (in Millions)")
st.dataframe(future_values_table)

