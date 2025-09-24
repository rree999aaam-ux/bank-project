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


## App Functionality

| Feature | Description |
|--------|-------------|
| Add Customer | Create a new customer with checking and savings accounts. |
| Login / Logout | Secure login and logout for each customer. |
| Deposit | Add money to checking or savings accounts. |
| Withdraw | Withdraw money with a $100 limit per transaction and overdraft rules. |
| Transfer (Internal) | Transfer funds between a customer's own checking and savings accounts. |
| Transfer (External) | Transfer funds from one customer to another customer's account. |
| Overdraft Policy | $35 fee applied when balance goes negative; account deactivates after 2 overdrafts and reactivates when balances are positive. |
| Transaction Log | All operations are recorded in `transactions.log`. |


## Challenges / Key Takeaways

- Learned how to safely read and write CSV files while preserving account data.
- Implemented banking rules such as overdraft fees and account deactivation/reactivation.
- Practiced object-oriented programming by using multiple classes to organize the code.
- Strengthened Git skills through frequent commits and pushes to GitHub.

## IceBox Features (Future Improvements)

- Build a web interface using Django or Flask to allow online banking through a browser.
- Integrate a database (e.g., PostgreSQL) instead of CSV for more scalable storage.
- Add password hashing for improved security.
- Implement automated unit tests for key banking operations.


