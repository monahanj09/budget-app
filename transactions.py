from database import get_connection

def add_transaction(
    date,
    name,
    amount,
    transaction_type,
    category,
    shared,
    notes,
    recurring_rule_id=None,
    recurring_occurrence_date=None,
    shared_members=None
):
    """Add a transaction to the database."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (date, name, amount, type, category, shared, shared_members, notes, recurring_rule_id, recurring_occurrence_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        date,
        name,
        amount,
        transaction_type,
        category,
        shared,
        shared_members,
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
            shared_members,
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
        shared_members,
        notes
):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
        UPDATE transactions
        SET date = ?, name = ?, amount = ?, type = ?, category = ?, shared = ?, shared_members = ?, notes = ?
        WHERE id = ?
    """, (
        date,
        name,
        amount,
        transaction_type,
        category,
        shared,
        shared_members,
        notes,
        transaction_id
    ))

        connection.commit()
        connection.close()