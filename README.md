
# Delivery Optimization System

## Overview

This project focuses on solving a logistics problem where deliveries need to be assigned to three agents in an efficient and balanced way. The goal is to distribute deliveries such that the total distance handled by each agent is as equal as possible, while also considering delivery priority.

The system reads delivery data from a CSV file, applies multiple algorithms, compares their performance, and automatically selects the best one.



## Problem Statement

Given a list of delivery locations with distance and priority:

* Assign deliveries to 3 agents
* Prioritize high-priority deliveries
* Ensure workload is balanced across agents
* Generate a final delivery plan



## Input Format

The system expects a file named `input.csv` with the following columns:

* LocationID
* Distance
* Priority (High, Medium, Low)

Example:

LocationID,Distance,Priority
L1,10,High
L2,25,Medium
L3,5,High


## How the System Works

### 1. Data Loading and Validation

* Reads the CSV file
* Checks if required columns exist
* Ensures distance is numeric and non-negative
* Validates priority values

If any issue is found, the system stops with an error message.



### 2. Data Preprocessing

* Converts priority into numeric values:

  * High → 3
  * Medium → 2
  * Low → 1
* Sorts deliveries by:

  * Priority (highest first)
  * Distance (shortest first)


### 3. Algorithms Used

#### Greedy Algorithm (Load Balancing)

Assigns each delivery to the agent with the lowest current workload.

* Fast and efficient
* Works well for most cases
* May not always give the best balance



#### Round Robin

Assigns deliveries in a fixed order:

A1 → A2 → A3 → repeat

* Simple approach
* Ensures equal number of tasks
* Does not consider distance, so balance may be poor



#### Dynamic Programming (Approximate)

Attempts to split deliveries into groups with nearly equal total distance.

* Produces better-balanced results
* Uses more memory
* Slower compared to greedy



## Performance Evaluation

Each algorithm is evaluated using three factors:

1. Maximum distance assigned to any agent (load balance)
2. Execution time
3. Memory usage


### Scoring Method

A weighted score is used to select the best algorithm:

Score =
(Max Distance × 0.6) +
(Execution Time × 1000 × 0.3) +
(Memory × 0.05)

Lower score indicates better performance.



## Output

The system generates a delivery plan with:

* Agent assignment
* Order of deliveries
* Distance for each delivery
* Cumulative distance
* Total distance per agent

The output can also be downloaded as a CSV file.



## Visualization

The system displays charts showing how deliveries are distributed among agents. This helps in visually understanding load balancing.



## Example Result

Based on the sample input:

* Greedy gives fast results but slightly uneven distribution
* Round Robin performs poorly in balancing
* Dynamic Programming provides the best balance

Therefore, the system selects Dynamic Programming as the best algorithm.



## Edge Cases Handled

The system handles the following cases:

* Missing input file
* Empty dataset
* Missing or incorrect columns
* Invalid priority values
* Non-numeric distance values
* Negative distances



## Technologies Used

* Python
* Streamlit
* Pandas
* Matplotlib



## How to Run

Install required libraries:

pip install streamlit pandas matplotlib

Run the application:

streamlit run app.py



## Conclusion

This project demonstrates how different algorithmic approaches can be applied to a real-world delivery optimization problem. By comparing multiple strategies and evaluating them based on performance metrics, the system ensures that the most suitable algorithm is selected automatically.

Dynamic Programming provides the most balanced solution, while Greedy offers a faster alternative.
