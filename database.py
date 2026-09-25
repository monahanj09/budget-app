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
            recurring_rule_id INTEGER,
            recurring_occurrence_date TEXT,
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

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER primary key AUTOINCREMENT,
                name TEXT NOT NULL,
                expected_amount REAL NOT NULL,
                type TEXT NOT NULL,
                category TEXT,
                shared INTEGER NOT NULL DEFAULT 0,
                notes TEXT,
                start_date TEXT NOT NULL,
                frequency TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
            )
        """)

    cursor.execute("PRAGMA table_info(transactions)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    if "recurring_rule_id" not in column_names:

        cursor.execute("ALTER TABLE transactions ADD COLUMN recurring_rule_id INTEGER")

    if "recurring_occurrence_date" not in column_names:

        cursor.execute("ALTER TABLE transactions ADD COLUMN recurring_occurrence_date TEXT")

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

def get_setting(key):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT value
        FROM settings
        WHERE key = ?
        """,
    (key,)
    )

    result = cursor.fetchone()
    connection.close()

    if result:
        return result[0]
    else:
        return None

def set_setting(key, value):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO settings
        (key, value)
        VALUES (?, ?)

        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
        """,
            (
                key,
                value
            )
    )

    connection.commit()
    connection.close()