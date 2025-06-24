
from typing import List
import math

def generate_connectivity_distribution(overall_connectivity: float, retries: int) -> List[float]:
    base = 0.5
    weights = [base ** i for i in range(retries + 1)]
    total_weight = sum(weights)
    connectivity = [round((w / total_weight) * overall_connectivity, 4) for w in weights]
    return connectivity

def calculate_total_time_with_dialing(
    N: int,
    A: float,
    M: int,
    G: float,
    Y: int,
    tier: int,
    whitelisting: bool,
    working_window: float
) -> (float, int, List[float]):
    dial_time_per_attempt = 1.0  # fixed at 1 minute
    B = 2.0  # fixed buffer time in hours

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

def main():
    print(" Call Batch Time Estimator \n")

    try:
        N = int(input("Enter total number of leads (N): "))
        tier = int(input("Enter customer tier (1, 2, or 3): "))
        whitelisted_input = input("Is whitelisting enabled? (true/false): ").strip().lower()
        whitelisting = whitelisted_input == "true"
        A = float(input("Enter average handling time per call in minutes (A): "))
        M = int(input("Enter number of concurrent calling slots (M): "))
        G = float(input("Enter retry gap in hours (G): "))
        Y = int(input("Enter max number of retries (Y): "))
        working_window = float(input("Enter working window per day in hours: "))

        result_hours, days_needed, D, connectivity = calculate_total_time_with_dialing(
            N, A, M, G, Y, tier, whitelisting, working_window
        )

        print(f"\nEstimated Total Time to complete call batch: {result_hours} hours")
        print(f"Estimated Working Days Required: {days_needed} day(s)")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
