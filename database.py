import sqlite3
import calendar
from datetime import date, timedelta
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


def add_transaction(
    date,
    name,
    amount,
    transaction_type,
    category,
    shared,
    notes,
    recurring_rule_id=None,
    recurring_occurrence_date=None
):
    """Add a transaction to the database."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (date, name, amount, type, category, shared, notes, recurring_rule_id, recurring_occurrence_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        date,
        name,
        amount,
        transaction_type,
        category,
        shared,
        notes,
        recurring_rule_id,
        recurring_occurrence_date
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
            notes,
            recurring_rule_id
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

def add_recurring_transaction(
        name,
        expected_amount,
        type,
        category,
        shared,
        notes,
        start_date,
        frequency
):
    """Add a recurring transaction to the database."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO recurring_transactions
        (name, expected_amount, type, category, shared, notes, start_date, frequency)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        expected_amount,
        type,
        category,
        shared,
        notes,
        start_date,
        frequency
    ))

    connection.commit()
    connection.close()

def get_recurring_transactions():
    """Return all recurring transaction rules."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            expected_amount,
            type,
            category,
            shared,
            notes,
            start_date,
            frequency,
            active
        FROM recurring_transactions
        ORDER BY start_date, id
    """)

    recurring_transactions = cursor.fetchall()

    connection.close()

    return recurring_transactions

def delete_recurring_transaction(rule_id):
    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute("""
        DELETE FROM transactions
        WHERE recurring_rule_id = ?
        """, (rule_id,))
    cursor.execute(

    """
        DELETE FROM recurring_transactions
        WHERE id = ?
        """,
        (rule_id,)
    )

    connection.commit()
    connection.close()

def set_recurring_transaction_active(rule_id, active):
    """Set recurring transactions as active or inactive"""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE recurring_transactions
        SET active = ?
        WHERE id = ?
        """,
        (active, rule_id)
    )
    connection.commit()
    connection.close()

def recurring_occurrence_exists(rule_id, occurrence_date):
    """Check whether a recurring transaction occurrence has already been generated"""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 1
        FROM transactions
        WHERE recurring_rule_id = ?
        AND recurring_occurrence_date = ?
        LIMIT 1
        """, (rule_id, occurrence_date)
    )

    result = cursor.fetchone()
    connection.close()

    return result is not None

def get_occurrences_for_month(start_date, frequency, year, month):
    """Return recurring occurrence dates for a specified month."""

    occurrences = []

    start_date = date.fromisoformat(start_date)

    month_start = date(year, month, 1)

    month_end = date(
        year,
        month,
        calendar.monthrange(year, month)[1]
    )

    current_date = start_date

    if frequency == "Weekly":
        interval_days = 7
    elif frequency == "Biweekly":
        interval_days = 14
    else:
        interval_days=None

    if interval_days is not None:

        while current_date <= month_end:

            if current_date >= month_start:

                occurrences.append(current_date)

            current_date += timedelta(days=interval_days)


    if frequency == "Monthly":

        intended_day = start_date.day

        days_in_month = calendar.monthrange(year, month)[1]

        occurrence_day = min(intended_day, days_in_month)

        occurrence_date = date(year, month, occurrence_day)

        if occurrence_date >= start_date:

            occurrences.append(occurrence_date)

    return occurrences

def generate_recurring_transactions(year, month):

    """Generate missing recurring transactions for a specified month."""

    recurring_rules = get_recurring_transactions()

    for rule in recurring_rules:

        if rule[9] == 1:

            occurrences = get_occurrences_for_month(rule[7], rule[8], year, month)

            for occurrence in occurrences:

                if not recurring_occurrence_exists(rule[0], occurrence.isoformat()):

                    add_transaction(
                        date = occurrence.isoformat(),
                        name = rule[1],
                        amount = rule[2],
                        transaction_type = rule[3],
                        category = rule[4],
                        shared = rule[5],
                        notes = rule[6],
                        recurring_rule_id = rule[0],
                        recurring_occurrence_date = occurrence.isoformat()
                    )