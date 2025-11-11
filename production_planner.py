def solve(profits, usage_matrix, limits):
    num_products = len(profits)
    num_resources = len(limits)
    num_vars = num_products + num_resources
    
    c = [0.0] * num_vars
    for i in range(num_products):
        c[i] = profits[i]
    
    A = []
    for r in range(num_resources):
        row = []
        for p in range(num_products):
            row.append(usage_matrix[r][p])
        for s in range(num_resources):
            if s == r:
                row.append(1.0)
            else:
                row.append(0.0)
        A.append(row)
    
    basic_vars = []
    cb = []
    for i in range(num_resources):
        basic_vars.append(num_products + i)
        cb.append(0.0)
    
    xb = []
    for i in range(num_resources):
        xb.append(limits[i])
    
    for iteration in range(100):
        rel_prof = []
        for j in range(num_vars):
            zj = 0.0
            for i in range(num_resources):
                zj = zj + cb[i] * A[i][j]
            rel_prof.append(c[j] - zj)
        
        max_prof = 0.0
        enter_var = -1
        for j in range(num_vars):
            if rel_prof[j] > max_prof:
                max_prof = rel_prof[j]
                enter_var = j
        
        if enter_var == -1:
            break
        
        min_ratio = float('inf')
        leave_row = -1
        for i in range(num_resources):
            if A[i][enter_var] > 0.000001 and xb[i] > 0.000001:
                ratio = xb[i] / A[i][enter_var]
                if ratio < min_ratio:
                    min_ratio = ratio
                    leave_row = i
        
        if leave_row == -1:
            print("Problem is unbounded")
            return None
        
        pivot = A[leave_row][enter_var]
        
        for j in range(num_vars):
            A[leave_row][j] = A[leave_row][j] / pivot
        xb[leave_row] = xb[leave_row] / pivot
        
        for i in range(num_resources):
            if i != leave_row:
                mult = A[i][enter_var]
                for j in range(num_vars):
                    A[i][j] = A[i][j] - mult * A[leave_row][j]
                xb[i] = xb[i] - mult * xb[leave_row]
        
        basic_vars[leave_row] = enter_var
        cb[leave_row] = c[enter_var]
    
    solution = {}
    for p in range(num_products):
        found = False
        for i in range(num_resources):
            if basic_vars[i] == p:
                solution[p] = xb[i]
                found = True
                break
        if not found:
            solution[p] = 0.0
    
    optimal = 0.0
    for i in range(num_resources):
        optimal = optimal + cb[i] * xb[i]
    
    return solution, optimal

def interactive_mode():
    print("Production Planning Solver")
    print("=" * 40)
    
    num_products = int(input("Number of products: "))
    num_resources = int(input("Number of resources: "))
    
    profits = []
    print("\nProfit for each product:")
    for i in range(num_products):
        p = float(input(f"  Product {i+1}: "))
        profits.append(p)
    
    usage_matrix = []
    print("\nResource usage (how much each product needs):")
    for r in range(num_resources):
        row = []
        print(f"Resource {r+1}:")
        for p in range(num_products):
            u = float(input(f"  Product {p+1}: "))
            row.append(u)
        usage_matrix.append(row)
    
    limits = []
    print("\nResource limits:")
    for r in range(num_resources):
        l = float(input(f"  Resource {r+1}: "))
        limits.append(l)
    
    print("\nSolving...")
    result = solve(profits, usage_matrix, limits)
    
    if result is None:
        return
    
    solution, optimal = result
    
    print("\n" + "=" * 40)
    print("OPTIMAL SOLUTION")
    print("=" * 40)
    for i in range(num_products):
        print(f"Product {i+1}: {solution[i]:.2f}")
    print(f"\nMaximum Profit: {optimal:.2f}")

def example_mode():
    print("Example Problem")
    print("=" * 40)
    print("3 products (A, B, C)")
    print("Maximize Z = 4x1 + 3x2 + 6x3")
    print("\nConstraints:")
    print("  2x1 + 3x2 + 2x3 <= 440")
    print("  4x1 + 0x2 + 3x3 <= 470")
    print("  2x1 + 5x2 + 0x3 <= 430")
    print("=" * 40)
    
    profits = [4.0, 3.0, 6.0]
    usage_matrix = [
        [2.0, 3.0, 2.0],
        [4.0, 0.0, 3.0],
        [2.0, 5.0, 0.0]
    ]
    limits = [440.0, 470.0, 430.0]
    
    result = solve(profits, usage_matrix, limits)
    
    if result is None:
        return
    
    solution, optimal = result
    
    print("\nOPTIMAL SOLUTION")
    print("=" * 40)
    print(f"Product A (x1): {solution[0]:.2f}")
    print(f"Product B (x2): {solution[1]:.2f}")
    print(f"Product C (x3): {solution[2]:.2f}")
    print(f"\nMaximum Profit (Z): {optimal:.2f}")
    print(f"\nExpected: x1=0, x2=380/9≈42.22, x3=470/3≈156.67, Z=3200/3≈1066.67")

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Interactive")
    print("2. Example")
    choice = input("\nChoice (1 or 2): ")
    
    if choice == "2":
        example_mode()
    else:
        interactive_mode()