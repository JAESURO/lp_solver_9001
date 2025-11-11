from simplex import solve


def interactive_mode():
    print("Production Planning Solver")
    print("=" * 40)
    
    is_minimize = input("Optimization type (max/min): ").lower() == "min"
    num_products = int(input("Number of products: "))
    num_resources = int(input("Number of resources: "))
    
    profit_values = [float(input(f"  Product {i+1}: ")) for i in range(num_products)]
    print(f"\n{'Cost' if is_minimize else 'Profit'} for each product:")
    for i, p in enumerate(profit_values):
        print(f"  Product {i+1}: {p}")
    
    resource_usage_matrix = []
    print("\nResource usage:")
    for r in range(num_resources):
        row = [float(input(f"  How much does Product {p+1} need? ")) for p in range(num_products)]
        resource_usage_matrix.append(row)
        print(f"  Resource {r+1}: {row}")
    
    constraint_types = []
    print("\nConstraint types (<=, >=, =):")
    for r in range(num_resources):
        ct = input(f"  Constraint {r+1}: ").strip()
        constraint_types.append(ct if ct in ["<=", ">=", "="] else "<=")
    
    resource_limits = [float(input(f"  Constraint {r+1}: ")) for r in range(num_resources)]
    print("\nResource limits (right-hand side values):")
    for r, l in enumerate(resource_limits):
        print(f"  Constraint {r+1}: {l}")
    
    print("\nSolving...")
    result = solve(profit_values, resource_usage_matrix, resource_limits, constraint_types, is_minimize)
    
    if len(result) == 2 and result[0] is None:
        print(f"\nERROR: {result[1]}")
        return
    
    solution, optimal, status = result
    
    print("\n" + "=" * 40)
    print("OPTIMAL SOLUTION" + (" (Alternative solutions exist)" if status == "ALTERNATE_SOLUTION" else ""))
    print("=" * 40)
    for i in range(num_products):
        print(f"Product {i+1}: {solution[i]:.2f}")
    print(f"\n{'Minimum Cost' if is_minimize else 'Maximum Profit'}: {optimal:.2f}")


if __name__ == "__main__":
    interactive_mode()