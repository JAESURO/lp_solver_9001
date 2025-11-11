def solve(profits, usage_matrix, limits, constraint_types=None, minimize=False):
    num_products = len(profits)
    num_resources = len(limits)
    
    if constraint_types is None:
        constraint_types = ["<="] * num_resources
    
    num_slack = sum(1 for ct in constraint_types if ct == "<=")
    num_surplus = sum(1 for ct in constraint_types if ct == ">=")
    num_artificial = sum(1 for ct in constraint_types if ct in [">=", "="])
    num_total_variables = num_products + num_slack + num_surplus + num_artificial
    
    objective_coefficients = [0.0] * num_total_variables
    for i in range(num_products):
        objective_coefficients[i] = profits[i]
    
    large_penalty = 100000.0
    penalty = large_penalty if minimize else -large_penalty
    for i in range(num_artificial):
        objective_coefficients[num_products + num_slack + num_surplus + i] = penalty
    
    constraint_matrix = []
    slack_idx = surplus_idx = artificial_idx = 0
    
    for r in range(num_resources):
        row = usage_matrix[r][:]
        ct = constraint_types[r]
        
        for s in range(num_slack):
            row.append(1.0 if ct == "<=" and s == slack_idx else 0.0)
        if ct == "<=":
            slack_idx += 1
        
        for s in range(num_surplus):
            row.append(-1.0 if ct == ">=" and s == surplus_idx else 0.0)
        if ct == ">=":
            surplus_idx += 1
        
        for a in range(num_artificial):
            row.append(1.0 if ct in [">=", "="] and a == artificial_idx else 0.0)
        if ct in [">=", "="]:
            artificial_idx += 1
        
        constraint_matrix.append(row)
    
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
    
    for iteration in range(200):
        relative_profits = []
        for v in range(num_total_variables):
            z_value = 0.0
            for r in range(num_resources):
                z_value = z_value + basic_coefficients[r] * constraint_matrix[r][v]
            objective_coef = objective_coefficients[v]
            if minimize:
                relative_profit = z_value - objective_coef
            else:
                relative_profit = objective_coef - z_value
            relative_profits.append(relative_profit)
        
        best_relative_profit = 0.0
        entering_variable = -1
        for v in range(num_total_variables):
            if relative_profits[v] > best_relative_profit:
                best_relative_profit = relative_profits[v]
                entering_variable = v
        
        if entering_variable == -1:
            break
        
        best_ratio = float('inf')
        leaving_row = -1
        for r in range(num_resources):
            coefficient = constraint_matrix[r][entering_variable]
            if coefficient > 0.000001:
                ratio = basic_values[r] / coefficient
                if ratio >= 0 and ratio < best_ratio:
                    best_ratio = ratio
                    leaving_row = r
        
        if leaving_row == -1:
            return None, "UNBOUNDED: Problem has unbounded solution"
        
        pivot_element = constraint_matrix[leaving_row][entering_variable]
        
        for v in range(num_total_variables):
            constraint_matrix[leaving_row][v] = constraint_matrix[leaving_row][v] / pivot_element
        basic_values[leaving_row] = basic_values[leaving_row] / pivot_element
        
        for r in range(num_resources):
            if r != leaving_row:
                multiplier = constraint_matrix[r][entering_variable]
                for v in range(num_total_variables):
                    constraint_matrix[r][v] = constraint_matrix[r][v] - multiplier * constraint_matrix[leaving_row][v]
                basic_values[r] = basic_values[r] - multiplier * basic_values[leaving_row]
        
        basic_variables[leaving_row] = entering_variable
        basic_coefficients[leaving_row] = objective_coefficients[entering_variable]
        
        base_signature = tuple(sorted(basic_variables))
        if base_signature in visited_bases:
            return None, "DEGENERATE: Cycling detected (degenerate solution)"
        visited_bases.add(base_signature)
    
    for r in range(num_resources):
        if basic_variables[r] >= num_products + num_slack + num_surplus:
            if abs(basic_values[r]) > 0.000001:
                return None, "INFEASIBLE: Artificial variable in basis with non-zero value"
    
    solution = {}
    for p in range(num_products):
        found = False
        for r in range(num_resources):
            if basic_variables[r] == p:
                solution[p] = basic_values[r]
                found = True
                break
        if not found:
            solution[p] = 0.0
    
    optimal_value = 0.0
    for r in range(num_resources):
        if basic_variables[r] < num_products:
            optimal_value = optimal_value + basic_coefficients[r] * basic_values[r]
    
    relative_profits_final = []
    for v in range(num_total_variables):
        z_value = 0.0
        for r in range(num_resources):
            z_value = z_value + basic_coefficients[r] * constraint_matrix[r][v]
        objective_coef = objective_coefficients[v]
        if minimize:
            relative_profit = z_value - objective_coef
        else:
            relative_profit = objective_coef - z_value
        relative_profits_final.append(relative_profit)
    
    has_alternate_solution = False
    for p in range(num_products):
        is_basic = False
        for r in range(num_resources):
            if basic_variables[r] == p:
                is_basic = True
                break
        if not is_basic:
            if abs(relative_profits_final[p]) < 0.000001:
                has_alternate_solution = True
                break
    
    if has_alternate_solution:
        status = "ALTERNATE_SOLUTION"
    else:
        status = "OPTIMAL"
    
    return solution, optimal_value, status