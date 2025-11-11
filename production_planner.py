def solve(profits, usage_matrix, limits, minimize=False):
    num_products = len(profits)
    num_resources = len(limits)
    num_total_variables = num_products + num_resources
    
    objective_coefficients = [0.0] * num_total_variables
    for product_index in range(num_products):
        objective_coefficients[product_index] = profits[product_index]
    
    constraint_matrix = []
    for resource_index in range(num_resources):
        constraint_row = []
        for product_index in range(num_products):
            constraint_row.append(usage_matrix[resource_index][product_index])
        for slack_index in range(num_resources):
            if slack_index == resource_index:
                constraint_row.append(1.0)
            else:
                constraint_row.append(0.0)
        constraint_matrix.append(constraint_row)
    
    basic_variables = []
    basic_coefficients = []
    for resource_index in range(num_resources):
        slack_variable_index = num_products + resource_index
        basic_variables.append(slack_variable_index)
        basic_coefficients.append(0.0)
    
    basic_values = []
    for resource_index in range(num_resources):
        if limits[resource_index] < 0:
            return None, "INFEASIBLE: Negative resource limit detected"
        basic_values.append(limits[resource_index])
    
    visited_bases = set()
    max_iterations = 100
    
    for iteration in range(max_iterations):
        relative_profits = []
        for variable_index in range(num_total_variables):
            z_value = 0.0
            for resource_index in range(num_resources):
                coefficient = basic_coefficients[resource_index]
                matrix_value = constraint_matrix[resource_index][variable_index]
                z_value = z_value + coefficient * matrix_value
            
            objective_coef = objective_coefficients[variable_index]
            if minimize:
                relative_profit = z_value - objective_coef
            else:
                relative_profit = objective_coef - z_value
            relative_profits.append(relative_profit)
        
        best_relative_profit = 0.0
        entering_variable = -1
        for variable_index in range(num_total_variables):
            if relative_profits[variable_index] > best_relative_profit:
                best_relative_profit = relative_profits[variable_index]
                entering_variable = variable_index
        
        if entering_variable == -1:
            break
        
        best_ratio = float('inf')
        leaving_row = -1
        for resource_index in range(num_resources):
            coefficient = constraint_matrix[resource_index][entering_variable]
            if coefficient > 0.000001:
                ratio = basic_values[resource_index] / coefficient
                if ratio >= 0 and ratio < best_ratio:
                    best_ratio = ratio
                    leaving_row = resource_index
        
        if leaving_row == -1:
            return None, "UNBOUNDED: Problem has unbounded solution"
        
        pivot_element = constraint_matrix[leaving_row][entering_variable]
        
        for variable_index in range(num_total_variables):
            constraint_matrix[leaving_row][variable_index] = constraint_matrix[leaving_row][variable_index] / pivot_element
        basic_values[leaving_row] = basic_values[leaving_row] / pivot_element
        
        for resource_index in range(num_resources):
            if resource_index != leaving_row:
                multiplier = constraint_matrix[resource_index][entering_variable]
                for variable_index in range(num_total_variables):
                    old_value = constraint_matrix[resource_index][variable_index]
                    pivot_row_value = constraint_matrix[leaving_row][variable_index]
                    constraint_matrix[resource_index][variable_index] = old_value - multiplier * pivot_row_value
                old_basic_value = basic_values[resource_index]
                pivot_row_basic_value = basic_values[leaving_row]
                basic_values[resource_index] = old_basic_value - multiplier * pivot_row_basic_value
        
        basic_variables[leaving_row] = entering_variable
        basic_coefficients[leaving_row] = objective_coefficients[entering_variable]
        
        base_signature = tuple(sorted(basic_variables))
        if base_signature in visited_bases:
            return None, "DEGENERATE: Cycling detected (degenerate solution)"
        visited_bases.add(base_signature)
    
    solution = {}
    for product_index in range(num_products):
        found_in_basis = False
        for resource_index in range(num_resources):
            if basic_variables[resource_index] == product_index:
                solution[product_index] = basic_values[resource_index]
                found_in_basis = True
                break
        if not found_in_basis:
            solution[product_index] = 0.0
    
    optimal_value = 0.0
    for resource_index in range(num_resources):
        coefficient = basic_coefficients[resource_index]
        value = basic_values[resource_index]
        optimal_value = optimal_value + coefficient * value
    
    relative_profits_final = []
    for variable_index in range(num_total_variables):
        z_value = 0.0
        for resource_index in range(num_resources):
            coefficient = basic_coefficients[resource_index]
            matrix_value = constraint_matrix[resource_index][variable_index]
            z_value = z_value + coefficient * matrix_value
        
        objective_coef = objective_coefficients[variable_index]
        if minimize:
            relative_profit = z_value - objective_coef
        else:
            relative_profit = objective_coef - z_value
        relative_profits_final.append(relative_profit)
    
    has_alternate_solution = False
    for product_index in range(num_products):
        is_basic_variable = False
        for resource_index in range(num_resources):
            if basic_variables[resource_index] == product_index:
                is_basic_variable = True
                break
        
        if not is_basic_variable:
            relative_profit_value = relative_profits_final[product_index]
            if abs(relative_profit_value) < 0.000001:
                has_alternate_solution = True
                break
    
    if has_alternate_solution:
        status = "ALTERNATE_SOLUTION"
    else:
        status = "OPTIMAL"
    
    return solution, optimal_value, status


def interactive_mode():
    print("Production Planning Solver")
    print("=" * 40)
    
    optimization_type = input("Optimization type (max/min): ").lower()
    is_minimize = optimization_type == "min"
    
    num_products = int(input("Number of products: "))
    num_resources = int(input("Number of resources: "))
    
    profit_values = []
    cost_or_profit_label = "Cost" if is_minimize else "Profit"
    print(f"\n{cost_or_profit_label} for each product:")
    for product_index in range(num_products):
        value = float(input(f"  Product {product_index + 1}: "))
        profit_values.append(value)
    
    resource_usage_matrix = []
    print("\nResource usage:")
    print("For each resource, enter how much of that resource each product needs")
    print("Example: If Product 1 needs 2 units of Resource 1, enter 2")
    for resource_index in range(num_resources):
        usage_row = []
        print(f"\nResource {resource_index + 1}:")
        for product_index in range(num_products):
            usage_value = float(input(f"  How much does Product {product_index + 1} need? "))
            usage_row.append(usage_value)
        resource_usage_matrix.append(usage_row)
        print(f"  You entered: {usage_row}")
    
    resource_limits = []
    print("\nResource limits:")
    for resource_index in range(num_resources):
        limit_value = float(input(f"  Resource {resource_index + 1}: "))
        resource_limits.append(limit_value)
    
    print("\nSolving...")
    result = solve(profit_values, resource_usage_matrix, resource_limits, is_minimize)
    
    if len(result) == 2 and result[0] is None:
        error_message = result[1]
        print(f"\nERROR: {error_message}")
        return
    
    solution_dict, optimal_value, solution_status = result
    
    print("\n" + "=" * 40)
    if solution_status == "OPTIMAL":
        print("OPTIMAL SOLUTION")
    elif solution_status == "ALTERNATE_SOLUTION":
        print("OPTIMAL SOLUTION (Alternative solutions exist)")
    print("=" * 40)
    
    for product_index in range(num_products):
        product_value = solution_dict[product_index]
        print(f"Product {product_index + 1}: {product_value:.2f}")
    
    if is_minimize:
        result_label = "Minimum Cost"
    else:
        result_label = "Maximum Profit"
    print(f"\n{result_label}: {optimal_value:.2f}")


if __name__ == "__main__":
    interactive_mode()