def create_tableau(profits, usage_matrix, limits):
    num_products = len(profits)
    num_resources = len(limits)
    num_cols = num_products + num_resources + 1
    num_rows = num_resources + 1
    
    tableau = []
    for i in range(num_rows):
        row = [0.0] * num_cols
        tableau.append(row)
    
    for r in range(num_resources):
        for p in range(num_products):
            tableau[r][p] = usage_matrix[r][p]
        tableau[r][num_products + r] = 1.0
        tableau[r][num_cols - 1] = limits[r]
    
    for p in range(num_products):
        tableau[num_resources][p] = -profits[p]
    
    return tableau

def find_pivot_col(tableau):
    last_row = tableau[-1]
    min_val = 0.0
    min_col = None
    
    for col in range(len(last_row) - 1):
        if last_row[col] < min_val:
            min_val = last_row[col]
            min_col = col
    
    return min_col

def find_pivot_row(tableau, col):
    num_rows = len(tableau) - 1
    best_ratio = float('inf')
    best_row = None
    
    for row in range(num_rows):
        if tableau[row][col] > 0:
            ratio = tableau[row][-1] / tableau[row][col]
            if ratio < best_ratio:
                best_ratio = ratio
                best_row = row
    
    return best_row

def pivot(tableau, row, col):
    pivot_val = tableau[row][col]
    num_cols = len(tableau[0])
    
    for c in range(num_cols):
        tableau[row][c] = tableau[row][c] / pivot_val
    
    for r in range(len(tableau)):
        if r != row:
            mult = tableau[r][col]
            for c in range(num_cols):
                tableau[r][c] = tableau[r][c] - mult * tableau[row][c]

def solve(profits, usage_matrix, limits):
    tableau = create_tableau(profits, usage_matrix, limits)
    num_products = len(profits)
    
    for _ in range(100):
        pivot_col = find_pivot_col(tableau)
        if pivot_col is None:
            break
        
        pivot_row = find_pivot_row(tableau, pivot_col)
        if pivot_row is None:
            print("Problem is unbounded")
            return None
        
        pivot(tableau, pivot_row, pivot_col)
    
    solution = {}
    num_resources = len(limits)
    
    for p in range(num_products):
        found = False
        for r in range(num_resources):
            if abs(tableau[r][p] - 1.0) < 0.000001:
                solution[p] = tableau[r][-1]
                found = True
                break
            elif abs(tableau[r][p]) > 0.000001:
                break
        if not found:
            solution[p] = 0.0
    
    optimal = tableau[-1][-1]
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
    print("2 products, 2 resources")
    print("Profits: P1=$10, P2=$15")
    print("Usage: R1->P1:1,P2:2  R2->P1:2,P2:1")
    print("Limits: R1=100, R2=100")
    print("=" * 40)
    
    profits = [10.0, 15.0]
    usage_matrix = [[1.0, 2.0], [2.0, 1.0]]
    limits = [100.0, 100.0]
    
    result = solve(profits, usage_matrix, limits)
    
    if result is None:
        return
    
    solution, optimal = result
    
    print("\nOPTIMAL SOLUTION")
    print("=" * 40)
    print(f"Product 1: {solution[0]:.2f}")
    print(f"Product 2: {solution[1]:.2f}")
    print(f"\nMaximum Profit: ${optimal:.2f}")

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Interactive")
    print("2. Example")
    choice = input("\nChoice (1 or 2): ")
    
    if choice == "2":
        example_mode()
    else:
        interactive_mode()