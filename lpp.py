import streamlit as st

def solve(profits, usage_matrix, limits, constraint_types=None, minimize=False):
    num_products = len(profits)
    num_resources = len(limits)
    
    if constraint_types is None:
        constraint_types = ["<="] * num_resources
    
    num_slack = sum(1 for ct in constraint_types if ct == "<=")
    num_surplus = sum(1 for ct in constraint_types if ct == ">=")
    num_artificial = sum(1 for ct in constraint_types if ct in [">=", "="])
    num_total_variables = num_products + num_slack + num_surplus + num_artificial

    # Objective coefficients
    objective_coefficients = [0.0] * num_total_variables
    for i in range(num_products):
        objective_coefficients[i] = profits[i]
    
    large_penalty = 1e5
    penalty = large_penalty if minimize else -large_penalty
    for i in range(num_artificial):
        objective_coefficients[num_products + num_slack + num_surplus + i] = penalty
    
    # Build constraint matrix
    constraint_matrix = []
    slack_idx = surplus_idx = artificial_idx = 0
    
    for r in range(num_resources):
        row = usage_matrix[r][:]
        ct = constraint_types[r]
        
        # Slack
        for _ in range(num_slack):
            row.append(1.0 if ct == "<=" and _ == slack_idx else 0.0)
        if ct == "<=":
            slack_idx += 1
        
        # Surplus
        for _ in range(num_surplus):
            row.append(-1.0 if ct == ">=" and _ == surplus_idx else 0.0)
        if ct == ">=":
            surplus_idx += 1
        
        # Artificial
        for _ in range(num_artificial):
            row.append(1.0 if ct in [">=", "="] and _ == artificial_idx else 0.0)
        if ct in [">=", "="]:
            artificial_idx += 1
        
        constraint_matrix.append(row)
    
    # Initial basic variables
    basic_variables = []
    basic_coefficients = []
    slack_idx = artificial_idx = 0
    
    for r in range(num_resources):
        ct = constraint_types[r]
        if ct == "<=":
            basic_variables.append(num_products + slack_idx)
            basic_coefficients.append(0.0)
            slack_idx += 1
        else:
            basic_variables.append(num_products + num_slack + num_surplus + artificial_idx)
            basic_coefficients.append(penalty)
            artificial_idx += 1
    
    basic_values = limits[:]
    visited_bases = set()
    
    for _ in range(200):  # iteration limit
        relative_profits = []
        for v in range(num_total_variables):
            z_value = sum(basic_coefficients[r] * constraint_matrix[r][v] for r in range(num_resources))
            obj = objective_coefficients[v]
            rel_profit = z_value - obj if minimize else obj - z_value
            relative_profits.append(rel_profit)
        
        best_profit = max(relative_profits)
        if best_profit <= 0:
            break
        entering = relative_profits.index(best_profit)
        
        # Ratio test
        ratios = []
        for r in range(num_resources):
            coeff = constraint_matrix[r][entering]
            if coeff > 1e-8:
                ratios.append(basic_values[r] / coeff)
            else:
                ratios.append(float('inf'))
        
        leaving_row = ratios.index(min(ratios))
        if ratios[leaving_row] == float('inf'):
            return None, "UNBOUNDED"
        
        pivot = constraint_matrix[leaving_row][entering]
        constraint_matrix[leaving_row] = [v / pivot for v in constraint_matrix[leaving_row]]
        basic_values[leaving_row] /= pivot
        
        # Eliminate column
        for r in range(num_resources):
            if r != leaving_row:
                mult = constraint_matrix[r][entering]
                constraint_matrix[r] = [
                    constraint_matrix[r][v] - mult * constraint_matrix[leaving_row][v]
                    for v in range(num_total_variables)
                ]
                basic_values[r] -= mult * basic_values[leaving_row]
        
        basic_variables[leaving_row] = entering
        basic_coefficients[leaving_row] = objective_coefficients[entering]
        
        sig = tuple(sorted(basic_variables))
        if sig in visited_bases:
            return None, "CYCLING"
        visited_bases.add(sig)
    
    # Check feasibility (artificial vars)
    for r in range(num_resources):
        if basic_variables[r] >= num_products + num_slack + num_surplus:
            if abs(basic_values[r]) > 1e-6:
                return None, "INFEASIBLE"
    
    # Build solution
    solution = {p: 0.0 for p in range(num_products)}
    for r in range(num_resources):
        if basic_variables[r] < num_products:
            solution[basic_variables[r]] = basic_values[r]
    
    optimal_value = sum(basic_coefficients[r] * basic_values[r] for r in range(num_resources))
    return solution, optimal_value, "OPTIMAL"


# -----------------------------
# Streamlit App
# -----------------------------
def main():
    st.title("📈 Simplex Solver (LP Optimization)")
    st.write("Enter linear programming problem parameters below:")

    num_products = st.number_input("Number of Products", min_value=1, value=2)
    num_resources = st.number_input("Number of Constraints", min_value=1, value=2)

    profits = st.text_input("Enter Profit Coefficients (comma-separated)", "3,5")
    limits = st.text_input("Enter RHS / Limits (comma-separated)", "8,6")

    constraint_types = st.text_input(
        "Enter Constraint Types (e.g., <=, >=, =), comma-separated",
        "<=,<="
    )

    st.write("Enter usage matrix rows (comma-separated for each constraint):")
    usage_matrix = []
    for i in range(num_resources):
        row = st.text_input(f"Row {i+1}:", "1,2" if i == 0 else "2,1")
        usage_matrix.append([float(x) for x in row.split(",")])

    minimize = st.checkbox("Minimize instead of maximize", False)

    if st.button("Solve LP"):
        try:
            profits = [float(x) for x in profits.split(",")]
            limits = [float(x) for x in limits.split(",")]
            constraint_types = [x.strip() for x in constraint_types.split(",")]

            result = solve(profits, usage_matrix, limits, constraint_types, minimize)
            
            if result[0] is None:
                st.error(f"⚠️ {result[1]}")
            else:
                sol, val, status = result
                st.success(f"✅ Status: {status}")
                st.write("### Solution:")
                for k, v in sol.items():
                    st.write(f"Product {k+1}: {v:.4f}")
                st.write(f"**Optimal Value:** {val:.4f}")
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()