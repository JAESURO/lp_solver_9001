from simplex import solve

is_minimize = input("max/min: ").lower() == "min"
num_products = int(input("Products: "))
num_resources = int(input("Resources: "))

profit_values = [float(input(f"Product {i+1}: ")) for i in range(num_products)]

resource_usage_matrix = []
for r in range(num_resources):
    row = [float(input(f"Resource {r+1}, Product {p+1}: ")) for p in range(num_products)]
    resource_usage_matrix.append(row)

constraint_types = []
for r in range(num_resources):
    ct = input(f"Constraint {r+1} type (<=, >=, =): ").strip()
    if ct == "=>":
        ct = ">="
    if ct not in ["<=", ">=", "="]:
        ct = "<="
    constraint_types.append(ct)

resource_limits = [float(input(f"Constraint {r+1} limit: ")) for r in range(num_resources)]

result = solve(profit_values, resource_usage_matrix, resource_limits, constraint_types, is_minimize)

if len(result) == 2 and result[0] is None:
    print(f"ERROR: {result[1]}")
else:
    solution, optimal, status = result
    for i in range(num_products):
        print(f"Product {i+1}: {solution[i]:.2f}")
    print(f"{'Min Cost' if is_minimize else 'Max Profit'}: {optimal:.2f}")