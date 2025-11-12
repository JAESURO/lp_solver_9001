# lp_solver_9001

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Description
`lp_solver_9001` is a lightweight Python package for solving **Linear Programming (LP)** problems using the **Simplex method**.  
It can handle optimization problems that aim to minimize or maximize a linear objective function subject to linear constraints.

## Features
- Solves standard linear programming problems.  
- Supports both **maximization** and **minimization** problems.  
- Implements the **Simplex algorithm** in a standalone module (`simplex.py`).  
- Example use case included in `production_planner.py`.  
- Works with **pure Python** (no external dependencies).  

## Installation
```bash
git clone https://github.com/JAESURO/lp_solver_9001.git
cd lp_solver_9001
# optional: create a virtual environment
python3 -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
# run the main example
python3 lpp.py
