"""
Encapsulation Example: Bank Account
Demonstrates data hiding and controlled access through methods
"""

class BankAccount:
    def __init__(self, account_number, owner_name, initial_balance=0):
        # Private attributes (name mangling with __)
        self.__account_number = account_number
        self.__owner_name = owner_name
        self.__balance = initial_balance
        self.__transaction_history = []

    # Public method to deposit money
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            self.__transaction_history.append(f"Deposited: ${amount}")
            return True
        return False

    # Public method to withdraw money
    def withdraw(self, amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            self.__transaction_history.append(f"Withdrawn: ${amount}")
            return True
        return False

    # Getter method for balance (read-only access)
    def get_balance(self):
        return self.__balance

    # Getter for account number
    def get_account_number(self):
        return self.__account_number

    # Method to view transaction history
    def get_transaction_history(self):
        return self.__transaction_history.copy()  # Return copy to prevent modification

    def __str__(self):
        return f"Account: {self.__account_number}, Owner: {self.__owner_name}, Balance: ${self.__balance}"


# Usage Example
if __name__ == "__main__":
    # Create a bank account
    account = BankAccount("ACC001", "John Doe", 1000)

    print(account)  # Account: ACC001, Owner: John Doe, Balance: $1000

    # Deposit money
    account.deposit(500)
    print(f"Balance after deposit: ${account.get_balance()}")  # $1500

    # Withdraw money
    account.withdraw(200)
    print(f"Balance after withdrawal: ${account.get_balance()}")  # $1300

    # Try to access private attribute (will fail)
    # print(account.__balance)  # AttributeError

    # Correct way to access balance
    print(f"Current balance: ${account.get_balance()}")

    # View transaction history
    print("\nTransaction History:")
    for transaction in account.get_transaction_history():
        print(f"  - {transaction}")

    """
    Output:
    Account: ACC001, Owner: John Doe, Balance: $1000
    Balance after deposit: $1500
    Balance after withdrawal: $1300
    Current balance: $1300

    Transaction History:
      - Deposited: $500
      - Withdrawn: $200
    """
