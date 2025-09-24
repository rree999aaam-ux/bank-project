# PyBank

A **mini banking system** built with **Python** and **CSV**.  
This project simulates a simple bank that allows customers to create accounts, login, deposit, withdraw, and transfer money.

## Features
- Add new customer and store data in CSV file.
- Customer login and logout.
- Deposit and withdraw money.
- Transfer between accounts or to other customers.
- Overdraft rules:
  - $35 overdraft fee if balance goes negative.
  - Account deactivates after more than 2 overdrafts.
  - Account reactivates when balances are non-negative.
- Transaction log saved to `transactions.log`.

## Requirements
- 4 classes:
  - `Customer`
  - `Account` (with `CheckingAccount` and `SavingsAccount`)
  - `Bank`
  - (Optional) `Transaction` / logging system
- `Pybank.csv` file to store account information.
- `banking.py` file to hold the project code.
- `import csv` package used for file handling.

## How to Run
1. Clone the repository:
   ```bash
   git clone <your-repo-link>
   cd bank-project

