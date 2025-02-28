import streamlit as st
import numpy as np

def simplex(tableau, big_m):
    iterations = 0
    max_iterations = 100  # Safety limit to prevent infinite loops
    
    while iterations < max_iterations:
        iterations += 1
        
        if (tableau[0, :-1] >= 0).all():
            break  # Optimal solution found
        
        pivot_col = np.argmin(tableau[0, :-1])
        
        if (tableau[1:, pivot_col] <= 0).all():
            st.error("Problem is unbounded: No valid pivot row found.")
            return None
        
        ratios = np.zeros(tableau.shape[0] - 1)
        for i in range(1, tableau.shape[0]):
            if tableau[i, pivot_col] > 0:
                ratios[i-1] = tableau[i, -1] / tableau[i, pivot_col]
            else:
                ratios[i-1] = np.inf
        
        if np.min(ratios) == np.inf:
            st.error("No feasible pivot found.")
            return None
            
        pivot_row = np.argmin(ratios) + 1
        pivot_value = tableau[pivot_row, pivot_col]
        
        tableau[pivot_row, :] /= pivot_value
        
        for r in range(tableau.shape[0]):
            if r != pivot_row:
                tableau[r, :] -= tableau[r, pivot_col] * tableau[pivot_row, :]
                
    if iterations >= max_iterations:
        st.warning("Maximum iterations reached. Solution may not be optimal.")
        
    return tableau

# Streamlit app
st.title("Big M Method Solver")

# User input for coefficients
revenue_x = st.number_input("Enter Profit per unit from Residential buildings (X):", value=0.0)
revenue_y = st.number_input("Enter Profit per unit from Commercial buildings (Y):", value=0.0)

# User input for constraints
labor_coeff_x = st.number_input("Enter labor coefficient for Residential buildings (X):", value=0.0)
labor_coeff_y = st.number_input("Enter labor coefficient for Commercial buildings (Y):", value=0.0)
labor_rhs = st.number_input("Enter labor constraint RHS:", value=0.0)

budget_coeff_x = st.number_input("Enter budget coefficient for Residential buildings (X):", value=0.0)
budget_coeff_y = st.number_input("Enter budget coefficient for Commercial buildings (Y):", value=0.0)
budget_rhs = st.number_input("Enter budget constraint RHS:", value=0.0)

# Define tableau dimensions
num_vars = 2       # x and y
num_constraints = 2  # Labor and Budget constraints
num_slack = 2        # One slack variable per constraint

# Initialize tableau with zeros
tableau = np.zeros((num_constraints + 1, num_vars + num_slack + 1))

# Set objective function coefficients (negative for maximization)
tableau[0, 0:num_vars] = [-revenue_x, -revenue_y]

# Set constraint coefficients
tableau[1, 0] = labor_coeff_x
tableau[1, 1] = labor_coeff_y
tableau[1, 2] = 1
tableau[1, -1] = labor_rhs

tableau[2, 0] = budget_coeff_x
tableau[2, 1] = budget_coeff_y
tableau[2, 3] = 1
tableau[2, -1] = budget_rhs

st.write("Initial tableau:")
st.write(tableau)

# Call the simplex function
final_tableau = simplex(tableau, big_m=1000)

# Extract and display the results
if final_tableau is not None:
    x_val = 0
    y_val = 0
    
    for j in range(num_vars):
        one_count = 0
        one_row = -1
        
        for i in range(1, num_constraints + 1):
            if abs(final_tableau[i, j] - 1.0) < 1e-10:
                one_count += 1
                one_row = i
            elif abs(final_tableau[i, j]) > 1e-10:
                one_count = -1
                break
                
        if one_count == 1:
            if j == 0:
                x_val = final_tableau[one_row, -1]
            elif j == 1:
                y_val = final_tableau[one_row, -1]
    
    for j in range(num_vars):
        is_unit = False
        for i in range(1, num_constraints + 1):
            if abs(final_tableau[i, j] - 1.0) < 1e-10:
                if all(abs(final_tableau[k, j]) < 1e-10 for k in
                       range(1, num_constraints + 1) if k != i):
                    is_unit = True
                    break
        
        if not is_unit:
            if j == 0:
                x_val = 0
            elif j == 1:
                y_val = 0
    
    revenue = revenue_x * x_val + revenue_y * y_val
    
    st.success("Optimal solution:")
    st.write(f"x = {x_val:.2f}")
    st.write(f"y = {y_val:.2f}")
    st.write(f"Revenue = ${revenue:.2f}")
else:
    st.error("The simplex algorithm could not find a solution.")