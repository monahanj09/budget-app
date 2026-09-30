import html

import streamlit as st


def render_metric_card(label, value):
    """Render a metric inside a bordered dashboard card."""

    with st.container(border=True):
        st.metric(
            label,
            value
        )


def render_calendar_day(
    day,
    day_balance,
    day_transactions=None,
    max_transactions=3
):
    """Render a single cash-flow calendar day."""

    transaction_rows = ""
    hidden_count = 0

    if (
        day_transactions is not None
        and not day_transactions.empty
    ):

        transaction_priority = {
            "Income": 0,
            "Reimbursement": 1,
            "Expense": 2
        }

        sorted_transactions = day_transactions.copy()

        sorted_transactions["Display Priority"] = (
            sorted_transactions["Type"]
            .map(transaction_priority)
            .fillna(3)
        )

        sorted_transactions = sorted_transactions.sort_values(
            by="Display Priority",
            kind="stable"
        )

        visible_transactions = sorted_transactions.head(
            max_transactions
        )

        hidden_count = max(
            len(sorted_transactions) - max_transactions,
            0
        )

        for _, transaction in visible_transactions.iterrows():

            description = str(
                transaction["Description"]
            )

            if len(description) > 16:
                description = description[:14] + "..."

            description = html.escape(description)

            amount = float(
                transaction["Amount ($)"]
            )

            if transaction["Type"] == "Expense":

                formatted_amount = (
                    f"-${amount:,.2f}"
                )

                transaction_color = "red"

            else:

                formatted_amount = (
                    f"+${amount:,.2f}"
                )

                transaction_color = "green"

            transaction_rows += (
                '<div style="'
                'display:flex;'
                'justify-content:space-between;'
                'align-items:center;'
                'gap:6px;'
                'font-size:0.9rem;'
                'margin-bottom:5px;'
                '">'
                '<span style="'
                'overflow:hidden;'
                'white-space:nowrap;'
                'text-overflow:ellipsis;'
                'min-width:0;'
                '">'
                f'{description}'
                '</span>'
                '<span style="'
                f'color:{transaction_color};'
                'white-space:nowrap;'
                'flex-shrink:0;'
                '">'
                f'{formatted_amount}'
                '</span>'
                '</div>'
            )

    if hidden_count > 0:

        transaction_rows += (
            '<div style="'
            'font-size:0.85rem;'
            'color:gray;'
            'margin-top:4px;'
            '">'
            f'+{hidden_count} more'
            '</div>'
        )

    if day_balance < 0:

        formatted_balance = (
            f"-${abs(day_balance):,.2f}"
        )

        balance_color = "red"

    else:

        formatted_balance = (
            f"${day_balance:,.2f}"
        )

        balance_color = "inherit"

    day_html = (
        '<div style="'
        'height:230px;'
        'border:1px solid rgba(49,51,63,0.2);'
        'border-radius:0.5rem;'
        'padding:16px;'
        'box-sizing:border-box;'
        'display:flex;'
        'flex-direction:column;'
        '">'
        
        '<div style="'
        'font-weight:bold;'
        'margin-bottom:18px;'
        '">'
        f'{day}'
        '</div>'

        '<div>'
        f'{transaction_rows}'
        '</div>'

        '<div style="'
        'margin-top:auto;'
        '">'
        
        '<div style="'
        'border-top:1px solid rgba(49,51,63,0.2);'
        'margin-bottom:12px;'
        '"></div>'

        '<div style="'
        'display:flex;'
        'justify-content:space-between;'
        'gap:6px;'
        'font-weight:bold;'
        f'color:{balance_color};'
        '">'
        '<span>Balance</span>'
        '<span style="white-space:nowrap;">'
        f'{formatted_balance}'
        '</span>'
        '</div>'

        '</div>'
        '</div>'
    )

    st.markdown(
        day_html,
        unsafe_allow_html=True
    )