import csv
from datetime import datetime



def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def to_bool(value):
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    return s in ("true", "1", "yes", "y")


def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return int(float(value))
        except Exception:
            return 0



class Account:
    def __init__(self, balance: float = 0.0):
        self.balance = float(balance)

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount

    def withdraw_raw(self, amount: float):
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive.")
        self.balance -= amount


class CheckingAccount(Account):
    pass


class SavingsAccount(Account):
    pass


class Customer:
    def __init__(
        self,
        cid: str,
        first_name: str,
        last_name: str,
        password: str,
        active: bool = True,
        overdraft_count: int = 0,
    ):
        self.id = str(cid).strip()
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.password = password
        self.active = bool(active)
        self.overdraft_count = int(overdraft_count)
        self.accounts = {
            "checking": CheckingAccount(0.0),
            "savings": SavingsAccount(0.0),
        }


class Bank:
    OVERDRAFT_FEE = 35.0
    MAX_WITHDRAW_PER_TX = 100.0

    def __init__(self, csv_file="Pybank.csv"):
        self.csv_file = csv_file
        self.customers: dict[str, Customer] = {}
        self.current_user: Customer | None = None
        self.tx_log: list[dict] = []

    def add_customer(self):
        print("\n=== Add New Customer ===")
        cid = input("Enter new customer ID: ").strip()
        if cid in self.customers:
            print("⚠️ ID already exists.")
            return
        first = input("First name: ").strip()
        last  = input("Last name: ").strip()
        password = input("Password: ").strip()

        cust = Customer(cid, first, last, password, active=True, overdraft_count=0)
        self.customers[cid] = cust
        self.save_customers()
        print(f"✅ Customer {first} {last} added successfully.")


  
    def _log(self, kind, detail: dict):
        row = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "type": kind,
            **detail,
        }
        self.tx_log.append(row)
        with open("transactions.log", "a", encoding="utf-8") as f:
            f.write(str(row) + "\n")

    
    def load_customers(self):
        with open(self.csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                cust = Customer(
                    row["id"],
                    row["first_name"],
                    row["last_name"],
                    row["password"],
                    active=to_bool(row.get("active", True)),
                    overdraft_count=to_int(row.get("overdraft_count", 0)),
                )
                cust.accounts["checking"].balance = to_float(row.get("checking", 0))
                cust.accounts["savings"].balance = to_float(row.get("savings", 0))
                self.customers[cust.id] = cust
        self._log("system", {"action": "load_customers", "count": len(self.customers)})

    def save_customers(self):
        fieldnames = [
            "id", "first_name", "last_name", "password",
            "checking", "savings", "active", "overdraft_count"
        ]
        with open(self.csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for c in self.customers.values():
                writer.writerow({
                    "id": c.id,
                    "first_name": c.first_name,
                    "last_name": c.last_name,
                    "password": c.password,
                    "checking": f"{c.accounts['checking'].balance:.2f}",
                    "savings": f"{c.accounts['savings'].balance:.2f}",
                    "active": str(c.active),
                    "overdraft_count": c.overdraft_count,
                })
        self._log("system", {"action": "save_customers", "count": len(self.customers)})

   
    def login(self, cid: str, password: str) -> bool:
        user = self.customers.get(str(cid))
        if not user:
            return False
        if user.password != password:
            return False
        self.current_user = user
        self._log("auth", {"action": "login", "cid": user.id})
        return True

    def logout(self):
        if self.current_user:
            self._log("auth", {"action": "logout", "cid": self.current_user.id})
        self.current_user = None

    def _require_login(self):
        if not self.current_user:
            raise PermissionError("Login required.")

    def _require_owner(self, cid: str):
        self._require_login()
        if self.current_user.id != str(cid):
            raise PermissionError("Access denied: you can only access your own info.")

    
    def _apply_overdraft_policy_after_withdraw(self, customer: Customer, acct_key: str):
        acct = customer.accounts[acct_key]
        if acct.balance < 0:
            acct.balance -= self.OVERDRAFT_FEE
            customer.overdraft_count += 1
            if customer.overdraft_count > 2:
                customer.active = False

    def _try_reactivate_if_funded(self, customer: Customer):
        if (customer.accounts["checking"].balance >= 0 and
            customer.accounts["savings"].balance >= 0):
            customer.active = True


    def withdraw(self, cid: str, acct_key: str, amount: float):
        self._require_owner(cid)
        customer = self.customers[cid]
        if acct_key not in customer.accounts:
            raise ValueError("Invalid account type.")
        if not customer.active:
            raise PermissionError("Account is deactivated.")
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if amount > self.MAX_WITHDRAW_PER_TX:
            raise ValueError("Cannot withdraw more than $100 in one transaction.")
        if customer.accounts[acct_key].balance < 0 and amount > 100:
            raise ValueError("Cannot withdraw more than $100 while account is negative.")
        before = customer.accounts[acct_key].balance
        customer.accounts[acct_key].withdraw_raw(amount)
        self._apply_overdraft_policy_after_withdraw(customer, acct_key)
        self._log("withdraw", {
            "cid": cid, "acct": acct_key, "amount": amount,
            "before": before, "after": customer.accounts[acct_key].balance,
            "overdraft_count": customer.overdraft_count, "active": customer.active
        })

    def deposit(self, cid: str, acct_key: str, amount: float):
        self._require_owner(cid)
        customer = self.customers[cid]
        if acct_key not in customer.accounts:
            raise ValueError("Invalid account type.")
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        before = customer.accounts[acct_key].balance
        customer.accounts[acct_key].deposit(amount)
        self._try_reactivate_if_funded(customer)
        self._log("deposit", {
            "cid": cid, "acct": acct_key, "amount": amount,
            "before": before, "after": customer.accounts[acct_key].balance,
            "overdraft_count": customer.overdraft_count, "active": customer.active
        })

    def transfer_self(self, cid: str, from_acct: str, to_acct: str, amount: float):
        if from_acct == to_acct:
            raise ValueError("Source and destination accounts must differ.")
        self.withdraw(cid, from_acct, amount)
        self.deposit(cid, to_acct, amount)
        self._log("transfer_self", {
            "cid": cid, "from": from_acct, "to": to_acct, "amount": float(amount)
        })

    def transfer_to_other(self, from_cid: str, from_acct: str,
                          to_cid: str, to_acct: str, amount: float):
        self._require_owner(from_cid)
        if to_cid not in self.customers:
            raise ValueError("Destination customer not found.")
        if to_acct not in self.customers[to_cid].accounts:
            raise ValueError("Invalid destination account.")
        self.withdraw(from_cid, from_acct, amount)
        before = self.customers[to_cid].accounts[to_acct].balance
        self.customers[to_cid].accounts[to_acct].deposit(float(amount))
        self._try_reactivate_if_funded(self.customers[to_cid])
        self._log("transfer_other", {
            "from_cid": from_cid, "from_acct": from_acct,
            "to_cid": to_cid, "to_acct": to_acct,
            "amount": float(amount), "dest_before": before,
            "dest_after": self.customers[to_cid].accounts[to_acct].balance
        })



if __name__ == "__main__":
    print("=== Welcome to the Bank ===")
    bank = Bank("Pybank.csv")
    bank.load_customers()

    while True:
        print("\n1) Login  2) Add Customer  3) Deposit  4) Withdraw  5) Transfer  6) Logout  7) Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            cid = input("Customer ID: ")
            pwd = input("Password: ")
            if bank.login(cid, pwd):
                print("Login successful.")
            else:
                print("Login failed.")

        elif choice == "2":
            bank.add_customer()

        elif choice == "3":
            if not bank.current_user:
                print("Please login first.")
            else:
                acct = input("Account (checking/savings): ")
                amt  = float(input("Amount: "))
                bank.deposit(bank.current_user.id, acct, amt)
                bank.save_customers()
                print("Deposit complete.")

        elif choice == "4":
            if not bank.current_user:
                print("Please login first.")
            else:
                acct = input("Account (checking/savings): ")
                amt  = float(input("Amount: "))
                bank.withdraw(bank.current_user.id, acct, amt)
                bank.save_customers()
                print("Withdrawal complete.")

        elif choice == "5":
            if not bank.current_user:
                print("Please login first.")
            else:
                to_cid = input("Destination customer ID: ")
                acct   = input("Destination account (checking/savings): ")
                amt    = float(input("Amount: "))
                bank.transfer_to_other(bank.current_user.id, "checking", to_cid, acct, amt)
                bank.save_customers()
                print("Transfer complete.")

        elif choice == "6":
            bank.logout()
            print("Logged out.")

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid option, please try again.")

    if bank.login("10002", "serf"):
        bank.deposit("10002", "checking", 50)
        bank.withdraw("10002", "checking", 20)
        bank.transfer_self("10002", "checking", "savings", 10)
        bank.logout()
    bank.save_customers()

