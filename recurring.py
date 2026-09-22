import calendar
from datetime import date, timedelta

from database import get_connection
from transactions import add_transaction

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