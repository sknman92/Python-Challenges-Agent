# **Challenge: Budget Transaction Validator with Custom Context Manager**

# You're building a lightweight budget tracker. Your job is to implement a custom
# context manager class and custom exceptions to safely process a series of
# financial transactions against a running balance.

# ---

# **The Data**

starting_balance = 500.00

transactions = [
    {"id": "T001", "type": "debit",  "amount": 120.00},
    {"id": "T002", "type": "credit", "amount": 200.00},
    {"id": "T003", "type": "debit",  "amount": 650.00},
    {"id": "T004", "type": "credit", "amount": 100.00},
    {"id": "T005", "type": "debit",  "amount": -50.00},
    {"id": "T006", "type": "debit",  "amount": 80.00},
]

# **Your Tasks:**

# **Task 1 — Custom Exceptions**

# Define two custom exception classes:
# - `InsufficientFundsError`: raised when a debit would push the balance below
#   zero. It should store and display the transaction ID and the shortfall
#   amount (how much over budget the transaction was).
# - `InvalidTransactionError`: raised when a transaction has a negative amount.
#   It should store and display the transaction ID and the invalid amount.

# ---

# **Task 2 — `TransactionSession` Context Manager**

# Implement a context manager class called `TransactionSession`:
# - On `__enter__`, it should print `"[Session Open] Starting balance: $X"` and
#   return itself.
# - It should expose an `apply(transaction, balance)` method that:
#   - Raises `InvalidTransactionError` if the amount is negative.
#   - Raises `InsufficientFundsError` if a debit would cause the balance to go
#     below zero.
#   - Otherwise, updates and returns the new balance (credit adds, debit
#     subtracts).
# - On `__exit__`, it should print `"[Session Closed] Ending balance: $X"` using
#   whatever the final balance was.
#   - It should **suppress** `InvalidTransactionError` (log a warning and
#     continue) but **not suppress** `InsufficientFundsError` (let it
#     propagate).
#   - Hint: think carefully about what `__exit__` receives and what it should
#     return.

# ---

# **Task 3 — Processing Loop**

# Write a loop that processes all transactions using the `TransactionSession`
# context manager:
# - Use a `with` block and call `session.apply(...)` for each transaction
#   inside a `try/except`.
# - Catch `InvalidTransactionError` per-transaction and print a warning, then
#   continue to the next transaction.
# - If `InsufficientFundsError` is raised, print the error details and stop
#   processing (let it exit the `with` block).
# - Track the running balance across transactions.

# ---

# **Expected behavior to reason through:**
# - T001: valid debit -> balance becomes 380.00
# - T002: valid credit -> balance becomes 580.00
# - T003: debit of 650 on a balance of 580 -> `InsufficientFundsError`
#   (shortfall: 70.00), processing stops
# - T004, T005, T006 are never reached
# - T005 would have triggered `InvalidTransactionError` if reached (negative
#   amount)

# ---

# **Bonus (optional):**
# Refactor `TransactionSession` using `contextlib.contextmanager` as a
# generator-based context manager instead of a class. Keep the same behavior.

# ---

#-----------------------------------------------------------------------
# SOLUTION

# Task 1
class InsufficientFundsError(Exception):
    """
    Raised when a debit would push the balance below.
    Stores and displays the transaction ID and the shortfall.
    """
    def __init__(self, transaction_id, shortfall):
        self.tranaction_id = transaction_id
        self.shortfall = shortfall
        super().__init__(f"[{transaction_id}] Insufficient funds - short by ${shortfall:.2f}")
        
    pass

class InvalidTransactionError(Exception):
    """"
    Raised when a transaction has a negative amount.
    Stores and displays the transaction ID and the invalid amount.
    """
    def __init__(self, transaction_id, invalid_amount):
        self.transaction_id = transaction_id
        self.invalid_amount = invalid_amount
        super().__init__(f"[{transaction_id}] invalid amount: {invalid_amount}")
        
    pass


# Task 2
class TransactionSession:
    def __init__(self, starting_balance):
        self.balance = starting_balance

    def __enter__(self):
        print(f"[Session Open] Staring balance: ${self.balance}")
        return self

    def apply(self, transaction, balance):
        amount = transaction["amount"]

        new_balance = balance + amount if transaction['type'] == 'credit'\
            else balance - amount

        if amount < 0:
            raise InvalidTransactionError(transaction['id'], amount)

        if new_balance < 0:
            raise InsufficientFundsError(transaction['id'], -new_balance)

        self.balance = new_balance

        return self.balance

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"[Session Closed] Ending balance: {self.balance}")
        if exc_type is InvalidTransactionError:
            print(f"Warning: {exc_value}")
            return True
        return False
    
# Task 3
starting_balance = 500
with TransactionSession(starting_balance) as s:
    for transaction in transactions:
        try:
            s.apply(transaction, s.balance)
            print(f'{s.balance}')
        except InvalidTransactionError as e:
            print(e)
            continue
        except InsufficientFundsError as e:
            print(e)
            raise e
            