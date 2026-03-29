import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import tracemalloc

st.set_page_config(page_title="Delivery Optimization", layout="wide")
st.title("Delivery Optimization System")

# Load data
try:
    data = pd.read_csv("input.csv")
except:
    st.error("input.csv file not found")
    st.stop()

if data.empty:
    st.warning("CSV file is empty")
    st.stop()

# Validate columns
required_columns = ["LocationID", "Distance", "Priority"]

for col in required_columns:
    if col not in data.columns:
        st.error("CSV must contain LocationID, Distance, and Priority")
        st.stop()

# Data cleaning
data["Priority"] = data["Priority"].str.capitalize()
priority_map = {"High": 3, "Medium": 2, "Low": 1}
data["PriorityValue"] = data["Priority"].map(priority_map)

if data["PriorityValue"].isnull().any():
    st.error("Invalid priority values found")
    st.stop()

data["Distance"] = pd.to_numeric(data["Distance"], errors="coerce")

if data["Distance"].isnull().any():
    st.error("Distance must be numeric")
    st.stop()

if (data["Distance"] < 0).any():
    st.error("Distance cannot be negative")
    st.stop()

# EDA
st.subheader("Exploratory Data Analysis")

col1, col2 = st.columns(2)

with col1:
    st.write("Basic Statistics")
    st.write(data.describe())

with col2:
    st.write("Priority Distribution")
    fig, ax = plt.subplots()
    data["Priority"].value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Priority Count")
    st.pyplot(fig)

# Sorting
data = data.sort_values(by=["PriorityValue", "Distance"], ascending=[False, True])

st.subheader("Sorted Input Data")
st.dataframe(data)

# ---------------- Algorithms ---------------- #

def greedy_algorithm(df):
    agents = {"A1": [], "A2": [], "A3": []}
    totals = {"A1": 0, "A2": 0, "A3": 0}

    for _, row in df.iterrows():
        agent = min(totals, key=totals.get)
        agents[agent].append((row["LocationID"], row["Distance"]))
        totals[agent] += row["Distance"]

    return agents, totals


def round_robin_algorithm(df):
    agents = {"A1": [], "A2": [], "A3": []}
    totals = {"A1": 0, "A2": 0, "A3": 0}
    agent_list = ["A1", "A2", "A3"]

    index = 0
    for _, row in df.iterrows():
        agent = agent_list[index % 3]
        agents[agent].append((row["LocationID"], row["Distance"]))
        totals[agent] += row["Distance"]
        index += 1

    return agents, totals


def dynamic_programming_algorithm(df):
    distances = list(df["Distance"])
    locations = list(df["LocationID"])

    total = sum(distances)
    target = total // 3

    dp = {0: []}

    for i in range(len(distances)):
        d = distances[i]
        loc = locations[i]
        new_dp = dp.copy()

        for s in dp:
            new_sum = s + d
            if new_sum not in new_dp:
                new_dp[new_sum] = dp[s] + [(loc, d)]

        dp = new_dp

    best_sum = min(dp.keys(), key=lambda x: abs(x - target))
    group1 = dp[best_sum]

    remaining = [(locations[i], distances[i]) for i in range(len(locations))]

    for item in group1:
        if item in remaining:
            remaining.remove(item)

    agents = {"A1": group1, "A2": [], "A3": []}
    totals = {"A1": sum(d for _, d in group1), "A2": 0, "A3": 0}

    for loc, dist in remaining:
        agent = min(["A2", "A3"], key=lambda x: totals[x])
        agents[agent].append((loc, dist))
        totals[agent] += dist

    return agents, totals


def backtracking_algorithm(df):
    locations = list(df["LocationID"])
    distances = list(df["Distance"])

    agents = {"A1": [], "A2": [], "A3": []}
    totals = {"A1": 0, "A2": 0, "A3": 0}

    best_agents = None
    best_max_distance = float("inf")

    def backtrack(index):
        nonlocal best_agents, best_max_distance

        if index == len(locations):
            current_max = max(totals.values())
            if current_max < best_max_distance:
                best_max_distance = current_max
                best_agents = {a: list(tasks) for a, tasks in agents.items()}
            return

        loc = locations[index]
        dist = distances[index]

        for agent in agents:
            agents[agent].append((loc, dist))
            totals[agent] += dist

            if totals[agent] <= best_max_distance:
                backtrack(index + 1)

            agents[agent].pop()
            totals[agent] -= dist

    backtrack(0)

    final_totals = {a: sum(d for _, d in best_agents[a]) for a in best_agents}
    return best_agents, final_totals


# Visualization
def plot_chart(agents, title):
    fig, ax = plt.subplots()

    for i, agent in enumerate(agents):
        start = 0
        for loc, dist in agents[agent]:
            ax.barh(i, dist, left=start)
            ax.text(start + dist / 2, i, loc, ha='center', va='center', fontsize=7)
            start += dist

    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["A1", "A2", "A3"])
    ax.set_title(title)
    ax.set_xlabel("Distance")

    st.pyplot(fig)


# Output creation
def create_output(agents):
    rows = []

    for agent in agents:
        tasks = agents[agent]
        total = sum(d for _, d in tasks)
        cumulative = 0
        order = 1

        for loc, dist in tasks:
            cumulative += dist
            rows.append({
                "Agent": agent,
                "StopOrder": order,
                "LocationID": loc,
                "Distance": dist,
                "CumulativeDistance": cumulative,
                "AgentTotalDistance": total
            })
            order += 1

    return pd.DataFrame(rows)


# Evaluation
def evaluate_algorithm(name, func, df):
    start = time.time()
    tracemalloc.start()

    agents, totals = func(df)

    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    end = time.time()

    imbalance = max(totals.values()) - min(totals.values())

    return {
        "name": name,
        "agents": agents,
        "totals": totals,
        "time": end - start,
        "memory": peak / 1024,
        "imbalance": imbalance
    }


# Run Algorithms
algorithms = {
    "Greedy": greedy_algorithm,
    "Round Robin": round_robin_algorithm,
    "Dynamic Programming": dynamic_programming_algorithm
}

results = []

for name, func in algorithms.items():
    results.append(evaluate_algorithm(name, func, data))

if len(data) <= 10:
    results.append(evaluate_algorithm("Backtracking", backtracking_algorithm, data))
else:
    st.warning("Backtracking skipped for large dataset")

# Performance Display
st.subheader("Algorithm Performance")

scores = {}

for result in results:
    st.markdown(f"### {result['name']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Workload Imbalance", result["imbalance"])
    col2.metric("Execution Time", f"{result['time']:.6f} sec")
    col3.metric("Memory Usage", f"{result['memory']:.2f} KB")

    st.write("Total Distance per Agent:")
    st.json(result["totals"])

    plot_chart(result["agents"], result["name"])

    # Score based mainly on equal distribution
    score = (
        result["imbalance"] * 0.7 +
        result["time"] * 1000 * 0.2 +
        result["memory"] * 0.1
    )

    scores[result["name"]] = score

# Best Algorithm
best_algorithm = min(scores, key=scores.get)

st.subheader("Best Algorithm")
st.success(f"{best_algorithm} gives the most balanced workload distribution")

for result in results:
    if result["name"] == best_algorithm:
        output = create_output(result["agents"])

        st.subheader("Delivery Plan")
        st.dataframe(output)

        st.download_button(
            "Download Output CSV",
            output.to_csv(index=False),
            file_name="output.csv"
        )

# Comparison Chart
st.subheader("Performance Comparison")
score_df = pd.DataFrame(scores.items(), columns=["Algorithm", "Score"])
st.bar_chart(score_df.set_index("Algorithm"))

# Methods
st.subheader("Methods Used")
st.write("Greedy: Assigns delivery to least loaded agent")
st.write("Round Robin: Equal sequential distribution")
st.write("Dynamic Programming: Balanced subset optimization")
st.write("Backtracking: Finds optimal distribution by exploring all possibilities")