import simpy
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

def proposal_lifecycle(env, proposal_steps, data_entry):

    with proposal_steps[1]["res"].request() as req:         # Step 1
        yield req
        duration = random.triangular(0.5, 8, 3)
        yield env.timeout(duration)
    
    data_entry.append(round(env.now, 2))

    with proposal_steps[2]["res"].request() as req:         # Step 2
        yield req
        duration = random.triangular(0.083, 24, 8)
        yield env.timeout(duration)

    data_entry.append(round(env.now, 2))

    with proposal_steps[3]["res"].request() as req:         # Step 3
        yield req
        duration = random.triangular(0.083, 24, 3)
        yield env.timeout(duration)

    data_entry.append(round(env.now, 2))

    with proposal_steps[4]["res"].request() as req:         # Step 4
        yield req
        duration = random.triangular(36, 96, 60)
        yield env.timeout(duration)

    data_entry.append(round(env.now, 2))

    with proposal_steps[5]["res"].request() as req:         # Step 5
        yield req
        duration = random.triangular(60, 336, 72)
        yield env.timeout(duration)

    data_entry.append(round(env.now, 2))

# =========================================
#        PARALLELIZABLE FUNCTION
# =========================================

def run_single_simulation(run_id):
    env = simpy.Environment()

    proposal_steps = {                                                                      # simulates the order of signatories using title aliases
        1: {"title": "Team Lead", "res": simpy.Resource(env, capacity=2)},
        2: {"title": "Technical Reviewer", "res": simpy.Resource(env, capacity=1)},
        3: {"title": "Section Chief", "res": simpy.Resource(env, capacity=1)},
        4: {"title": "Records Director", "res": simpy.Resource(env, capacity=1)},
        5: {"title": "Finance Office", "res": simpy.Resource(env, capacity=1)}
    }

    data_entry = []

    env.process(proposal_lifecycle(env, proposal_steps, data_entry))
    env.run()

    return data_entry

# =========================================
#           MODEL EXECUTION
# =========================================

if __name__ == "__main__":
    NUM_RUNS = 5000

    print(f"Starting {NUM_RUNS} simulation runs in parallel...")

    manager = Parallel(n_jobs=-1)
    results = manager( delayed(run_single_simulation)(i) for i in range(NUM_RUNS) )

    print("Simulations complete. Data saved.")

    columns = [
        "Team Lead",
        "Technical Reviewer",
        "Section Chief",
        "Records Director",
        "Finance Office",
    ]

    df = pd.DataFrame(results, columns=columns)

    df_durations = pd.DataFrame()
    df_durations["TL Dur"] = df["Team Lead"]
    df_durations["TechRev Dur"] = df["Technical Reviewer"] - df["Team Lead"]
    df_durations["SecChief Dur"] = df["Section Chief"] - df["Technical Reviewer"]
    df_durations["Director Dur"] = df["Records Director"] - df["Section Chief"]
    df_durations["Finance Dur"] = df["Finance Office"] - df["Records Director"]

    avg_durations = df_durations.mean()

    longest_step = avg_durations.idxmax()
    longest_time = avg_durations.max()

    print("--- Average Step Durations ---")
    print(avg_durations)

    print("=================================================================")
    print(f"The step that takes the longest time: {longest_step}")
    print(f"It takes an average of {longest_time:.2f} simulation hours.")

    # =========================================
    #           DATA VISUALIZATION
    # =========================================

    plt.figure(figsize=(10,6))

    bars = plt.barh(avg_durations.index, avg_durations.values, color="blue")

    longest_step_index = np.argmax(avg_durations.values)
    bars[longest_step_index].set_color("#ff8686")

    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + 0.05,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.2f} hours",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold" if bar == bars[longest_step_index] else "normal",
        )

    plt.title(
        "Average Processing Duration per Workflow Phase (5,000 Runs)",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Average Duration (Simulation Hours)", fontsize=12, labelpad=10)
    plt.ylabel("Workflow Phase", fontsize=12)
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()

    plt.show()