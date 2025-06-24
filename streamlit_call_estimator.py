import streamlit as st
from typing import List
import math

# Generate connectivity list based on geometric decay
def generate_connectivity_distribution(overall_connectivity: float, retries: int) -> List[float]:
    base = 0.5
    weights = [base ** i for i in range(retries + 1)]
    total_weight = sum(weights)
    connectivity = [round((w / total_weight) * overall_connectivity, 4) for w in weights]
    return connectivity

# Core logic
def calculate_total_time_with_dialing(
    N: int,
    A: float,
    M: int,
    G: float,
    Y: int,
    tier: int,
    whitelisting: bool,
    working_window: float
) -> (float, int, int, List[float]):
    dial_time_per_attempt = 1.0  # fixed at 1 minute
    B = 2.0  # buffer in hours

    if tier == 1:
        D = int(0.30 * N)
    elif tier == 2:
        D = int(0.20 * N)
    elif tier == 3:
        D = int(0.10 * N)
    else:
        raise ValueError("Invalid tier. Must be 1, 2, or 3.")

    overall_connectivity = 0.5 if whitelisting else 0.4
    connectivity = generate_connectivity_distribution(overall_connectivity, Y)

    P0 = connectivity[0]
    retry_probs = []
    residual = 1 - P0
    for i in range(1, Y + 1):
        Pi = residual * connectivity[i]
        retry_probs.append(Pi)
        residual *= (1 - connectivity[i])

    first_attempt_connected = N * P0
    retry_pool = N - first_attempt_connected - D
    retry_connected = retry_pool * sum(retry_probs)
    total_connected = first_attempt_connected + retry_connected

    total_talk_time_min = total_connected * A
    total_attempts = N + (retry_pool * Y)
    total_dial_time_min = total_attempts * dial_time_per_attempt
    total_active_minutes = total_talk_time_min + total_dial_time_min

    active_time_hours = total_active_minutes / (M * 60)
    total_time_hrs = active_time_hours + (Y * G) + B
    working_days = math.ceil(total_time_hrs / working_window)

    return round(total_time_hrs, 2), working_days, D, connectivity

# Streamlit UI
st.title("📞 Call Batch Time Estimator")

st.markdown("📋 Input Parameters")

N = st.number_input("Total Leads (N)", min_value=1, value=1000)
tier = st.selectbox("Customer Tier", [1, 2, 3])
whitelist_option = st.radio("Is Whitelisting Enabled?", ["Yes", "No"])
whitelisting = whitelist_option == "Yes"
A = st.number_input("Average Handling Time per Call (A) in minutes", min_value=0.1, value=2.0)
M = st.number_input("Concurrent Calling Slots (M)", min_value=1, value=20)
G = st.number_input("Retry Gap (G) in hours", min_value=0.0, value=1.0)
Y = st.number_input("Max Number of Retries (Y)", min_value=0, value=2)
working_window = st.number_input("Working Window per Day (in hours)", min_value=1.0, value=8.0)

if st.button("🚀 Estimate Time"):
    try:
        total_time, days, D, connectivity = calculate_total_time_with_dialing(
            N, A, M, G, Y, tier, whitelisting, working_window
        )
        st.success("✅ Calculation Complete")
        st.metric("⏱ Total Time (hrs)", f"{total_time}")
        st.metric("📅 Working Days Needed", f"{days}")
    except Exception as e:
        st.error(f"❌ Error: {e}")

