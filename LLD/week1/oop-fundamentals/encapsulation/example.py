"""
Encapsulation Example: Bank Account
Demonstrates data hiding and controlled access through methods
"""

class BankAccount:
    """
    A bank account that protects its internal state through encapsulation.
    External code cannot directly access balance or transaction history.
    """

    def __init__(self, account_number, owner_name, initial_balance=0):
        # Private attributes (name mangling with __)
        # These cannot be accessed directly from outside the class
        self.__account_number = account_number
        self.__owner_name = owner_name
        self.__balance = initial_balance
        self.__transaction_history = []

    def deposit(self, amount):
        """
        Deposit money into the account.
        Validates amount before modifying balance.

        Args:
            amount: Amount to deposit

        Returns:
            True if successful, False otherwise
        """
        if amount <= 0:
            print(f"Error: Deposit amount must be positive (got ${amount})")
            return False

        self.__balance += amount
        self.__transaction_history.append(f"Deposited: ${amount}")
        print(f"Successfully deposited ${amount}")
        return True

    def withdraw(self, amount):
        """
        Withdraw money from the account.
        Validates amount and checks sufficient balance.

        Args:
            amount: Amount to withdraw

        Returns:
            True if successful, False otherwise
        """
        if amount <= 0:
            print(f"Error: Withdrawal amount must be positive (got ${amount})")
            return False

        if amount > self.__balance:
            print(f"Error: Insufficient funds (balance: ${self.__balance}, requested: ${amount})")
            return False

        self.__balance -= amount
        self.__transaction_history.append(f"Withdrawn: ${amount}")
        print(f"Successfully withdrew ${amount}")
        return True

    def get_balance(self):
        """
        Get current balance (read-only access).

        Returns:
            Current account balance
        """
        return self.__balance

    def get_account_number(self):
        """Get account number (read-only)."""
        return self.__account_number

    def get_transaction_history(self):
        """
        Get transaction history.
        Returns a copy to prevent external modification.
        """
        return self.__transaction_history.copy()

    def transfer(self, target_account, amount):
        """
        Transfer money to another account.

        Args:
            target_account: BankAccount instance to transfer to
            amount: Amount to transfer

        Returns:
            True if successful, False otherwise
        """
        if amount <= 0:
            print(f"Error: Transfer amount must be positive")
            return False

        if amount > self.__balance:
            print(f"Error: Insufficient funds for transfer")
            return False

        # Withdraw from this account
        self.__balance -= amount
        self.__transaction_history.append(f"Transfer out to {target_account.get_account_number()}: ${amount}")

        # Deposit to target account
        target_account.deposit(amount)

        print(f"Successfully transferred ${amount} to account {target_account.get_account_number()}")
        return True

    def __str__(self):
        """String representation of the account."""
        return f"Account {self.__account_number} ({self.__owner_name}): ${self.__balance}"


# Demonstration
if __name__ == "__main__":
    print("=== Bank Account Encapsulation Demo ===\n")

    # Create accounts
    account1 = BankAccount("ACC001", "Alice Johnson", 1000)
    account2 = BankAccount("ACC002", "Bob Smith", 500)

    print(f"Initial state:")
    print(f"  {account1}")
    print(f"  {account2}")

    print("\n--- Deposit Operations ---")
    account1.deposit(500)
    account1.deposit(-100)  # Invalid: negative amount

    print("\n--- Withdrawal Operations ---")
    account1.withdraw(200)
    account1.withdraw(2000)  # Invalid: insufficient funds

    print("\n--- Transfer Operations ---")
    account1.transfer(account2, 300)

    print(f"\n--- Final State ---")
    print(f"  {account1}")
    print(f"  {account2}")

    print(f"\n--- Transaction History ---")
    print(f"Account {account1.get_account_number()} transactions:")
    for transaction in account1.get_transaction_history():
        print(f"  - {transaction}")

    print(f"\nAccount {account2.get_account_number()} transactions:")
    for transaction in account2.get_transaction_history():
        print(f"  - {transaction}")

    print("\n--- Attempting Direct Access (Demonstrates Protection) ---")
    try:
        # This will fail - private attribute is not accessible
        print(account1.__balance)
    except AttributeError as e:
        print(f"Error accessing __balance directly: {e}")

    # Correct way to access balance
    print(f"Correct way - using getter: ${account1.get_balance()}")
