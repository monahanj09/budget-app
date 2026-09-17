import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "budget.db"


def get_connection():
    """Create and return a connection to the budget database."""
    return sqlite3.connect(DB_PATH)


def create_tables():
    """Create the transactions table if it does not already exist."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            category TEXT,
            shared INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_balances (
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                starting_balance REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (year, month)
            )
        """)

    connection.commit()
    connection.close()

# EXPERIMENTAL/CURRENTLY UNUSED
# Prototype from v0.3 for assigning transactions to a budget period
# separate from their cashflow date.
# Retained in case this concept is revisited in a future version
def add_budget_period_columns():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(transactions)")
    columns = [column[1] for column in cursor.fetchall()]

    if "budget_year" not in columns:
        cursor.execute(
            "ALTER TABLE transactions ADD COLUMN budget_year INTEGER"
        )

    if "budget_month" not in columns:
        cursor.execute(
            "ALTER TABLE transactions ADD COLUMN budget_month INTEGER"
        )

    cursor.execute("""
    UPDATE transactions
    SET budget_year = CAST(strftime('%Y', date) AS INTEGER),
        budget_month = CAST(strftime('%m', date) AS INTEGER)
    WHERE budget_year IS NULL
    OR budget_month IS NULL
    """)

    connection.commit()
    connection.close()


def add_transaction(
    date,
    name,
    amount,
    transaction_type,
    category,
    shared,
    notes
):
    """Add a transaction to the database."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (date, name, amount, type, category, shared, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        date,
        name,
        amount,
        transaction_type,
        category,
        shared,
        notes
    ))

    connection.commit()
    connection.close()


def get_transactions(year, month):
    """Return all transactions for a given month."""

    connection = get_connection()
    cursor = connection.cursor()

    month_string = f"{year}-{month:02d}"

    cursor.execute("""
        SELECT
            id,
            date,
            name,
            amount,
            type,
            category,
            shared,
            notes
        FROM transactions
        WHERE substr(date, 1, 7) = ?
        ORDER BY date, id
    """, (month_string,))

    transactions = cursor.fetchall()

    connection.close()

    return transactions

def delete_transaction(transaction_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(

    """
        DELETE FROM transactions
        WHERE id = ?
        """,
        (transaction_id,)
    )

    connection.commit()
    connection.close()

def update_transaction(
        transaction_id,
        date,
        name,
        amount,
        transaction_type,
        category,
        shared,
        notes
):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
        UPDATE transactions
        SET date = ?, name = ?, amount = ?, type = ?, category = ?, shared = ?, notes = ?
        WHERE id = ?
    """, (
        date,
        name,
        amount,
        transaction_type,
        category,
        shared,
        notes,
        transaction_id
    ))

        connection.commit()
        connection.close()

def set_starting_balance(year, month, starting_balance):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
    """
    INSERT INTO monthly_balances
    (year, month, starting_balance)
    VALUES (?, ?, ?)

    ON CONFLICT(year, month)
    DO UPDATE SET starting_balance = excluded.starting_balance
    """,
    (
        year,
        month,
        starting_balance
    )
    )
    connection.commit()
    connection.close()

def get_starting_balance(year, month):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
         """SELECT starting_balance
         FROM monthly_balances
         WHERE year = ? AND month = ?""",
        (year, month)
    )
    result = cursor.fetchone()
    connection.close()

    if result:
        return result[0]
    else:
        return 0.00