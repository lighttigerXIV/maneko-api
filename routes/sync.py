from flask import Blueprint, g, request

from db import get_db
from responses import bad_request_response, database_error_reponse, internal_error_response, ok_response
from token_utils import authenticated
from validation_utils import get_body

sync_blueprint = Blueprint("sync_blueprint", __name__)


def get_sync_response():
    conn, cursor = get_db()

    cursor.execute(
        """
        WITH categories_query AS (
            SELECT id, name, color, icon, deleted, last_modified 
            FROM category
            WHERE user_id = '756b5af3-2b24-4613-aec7-59f6bb3a7f86'
        ),
        sub_categories_query AS (
            SELECT sc.id, sc.name, sc.category_id, sc.icon, sc.deleted, sc.last_modified
            FROM sub_category sc
            LEFT JOIN category c ON c.id = sc.category_id
            WHERE c.user_id = '756b5af3-2b24-4613-aec7-59f6bb3a7f86'
        ),
        accounts_query AS (
            SELECT id, name, icon, balance, deleted, last_modified  
            FROM account
            WHERE user_id = '756b5af3-2b24-4613-aec7-59f6bb3a7f86'
        ),
        movements_query AS (
            SELECT id, amount, movement_date, description, expense_id, income_id, transfer_id, deleted, last_modified 
            FROM movement
            WHERE user_id = '756b5af3-2b24-4613-aec7-59f6bb3a7f86'
        ),
        expenses_query AS (
            SELECT e.id, e.account_id, e.category_id, e.sub_category_id, e.info, e.last_modified 
            FROM expense e
            LEFT JOIN account a ON a.id = e.account_id
            WHERE a.user_id = '756b5af3-2b24-4613-aec7-59f6bb3a7f86'
        ),
        incomes_query AS (
            SELECT i.id, i.account_id, i.category_id, i.sub_category_id, i.info, i.last_modified 
            FROM income i
            LEFT JOIN account a ON a.id = i.account_id
            WHERE a.user_id = '756b5af3-2b24-4613-aec7-59f6bb3a7f86'
        ),
        transfers_query AS (
            SELECT t.id, t.from_account_id, t.to_account_id, t.last_modified 
            FROM transfer t
            LEFT JOIN account a ON a.id = t.from_account_id
            WHERE a.user_id = '756b5af3-2b24-4613-aec7-59f6bb3a7f86'
        ),
        reminders_query AS (
            SELECT id, name, hour, minute, deleted, last_modified
            FROM reminder
            WHERE user_id = '756b5af3-2b24-4613-aec7-59f6bb3a7f86'
        )

        SELECT json_build_object(
            'categories', coalesce((SELECT json_agg(categories_query) FROM categories_query), json_build_array()),
            'sub_categories', coalesce((SELECT json_agg(sub_categories_query) FROM sub_categories_query), json_build_array()),
            'accounts', coalesce((SELECT json_agg(accounts_query) FROM accounts_query), json_build_array()),
            'movements', coalesce((SELECT json_agg(movements_query) FROM movements_query), json_build_array()),
            'expenses', coalesce((SELECT json_agg(expenses_query) FROM expenses_query), json_build_array()),
            'incomes', coalesce((SELECT json_agg(incomes_query) FROM incomes_query), json_build_array()),
            'transfers', coalesce((SELECT json_agg(transfers_query) FROM transfers_query), json_build_array()),
            'reminders', coalesce((SELECT json_agg(reminders_query) FROM reminders_query), json_build_array())
        ) AS response
        """
    )

    row = cursor.fetchone()

    if not row:
        return None

    conn.close()
    cursor.close()

    return row["response"]


@sync_blueprint.route("/sync", methods=["GET", "PUT"])
@authenticated
def sync():
    try:
        if request.method == "GET":
            response = get_sync_response()

            if not response:
                return database_error_reponse()

            return ok_response(response)

        if request.method == "PUT":
            body = get_body()

            user_id = g.user_id

            conn, cursor = get_db()

            for account in body["accounts"]:
                cursor.execute(
                    """
                    INSERT INTO account (id, user_id, name, icon, balance, deleted, last_modified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT(id)
                    DO UPDATE SET 
                        name = EXCLUDED.name,
                        icon = EXCLUDED.icon,
                        balance = EXCLUDED.balance,
                        deleted = EXCLUDED.deleted,
                        last_modified = EXCLUDED.last_modified
                    WHERE EXCLUDED.last_modified > account.last_modified
                    """,
                    [
                        account["id"],
                        user_id,
                        account["name"],
                        account["icon"],
                        account["balance"],
                        account["deleted"],
                        account["last_modified"],
                    ],
                )

            for category in body["categories"]:
                cursor.execute(
                    """
                    INSERT INTO category (id, user_id, name, icon, color, deleted, last_modified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT(id)
                    DO UPDATE SET 
                        name = EXCLUDED.name, 
                        icon = EXCLUDED.icon, 
                        color = EXCLUDED.color, 
                        deleted = EXCLUDED.deleted, 
                        last_modified = EXCLUDED.last_modified
                    WHERE EXCLUDED.last_modified > category.last_modified
                    """,
                    [
                        category["id"],
                        user_id,
                        category["name"],
                        category["icon"],
                        category["color"],
                        category["deleted"],
                        category["last_modified"],
                    ],
                )

            for sub_cat in body["sub_categories"]:
                cursor.execute(
                    """
                    INSERT INTO sub_category (id, category_id, name, icon, deleted, last_modified)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT(id)
                    DO UPDATE SET 
                        category_id = EXCLUDED.category_id,
                        name = EXCLUDED.name, 
                        icon = EXCLUDED.icon, 
                        deleted = EXCLUDED.deleted, 
                        last_modified = EXCLUDED.last_modified
                    WHERE EXCLUDED.last_modified > sub_category.last_modified
                    """,
                    [
                        sub_cat["id"],
                        sub_cat["category_id"],
                        sub_cat["name"],
                        sub_cat["icon"],
                        sub_cat["deleted"],
                        sub_cat["last_modified"],
                    ],
                )

            for expense in body["expenses"]:
                cursor.execute(
                    """
                    INSERT INTO expense (id, account_id, category_id, sub_category_id, info, last_modified)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT(id)
                    DO UPDATE SET 
                        account_id = EXCLUDED.account_id,
                        category_id = EXCLUDED.category_id,
                        sub_category_id = EXCLUDED.sub_category_id,
                        info = EXCLUDED.info, 
                        last_modified = EXCLUDED.last_modified
                    WHERE EXCLUDED.last_modified > expense.last_modified
                    """,
                    [
                        expense["id"],
                        expense["account_id"],
                        expense["category_id"],
                        expense["sub_category_id"],
                        expense["info"],
                        expense["last_modified"],
                    ],
                )

            for income in body["incomes"]:
                cursor.execute(
                    """
                    INSERT INTO income (id, account_id, category_id, sub_category_id, info, last_modified)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT(id)
                    DO UPDATE SET 
                        account_id = EXCLUDED.account_id,
                        category_id = EXCLUDED.category_id,
                        sub_category_id = EXCLUDED.sub_category_id,
                        info = EXCLUDED.info, 
                        last_modified = EXCLUDED.last_modified
                    WHERE EXCLUDED.last_modified > income.last_modified
                    """,
                    [
                        income["id"],
                        income["account_id"],
                        income["category_id"],
                        income["sub_category_id"],
                        income["info"],
                        income["last_modified"],
                    ],
                )

            for transfer in body["transfers"]:
                cursor.execute(
                    """
                    INSERT INTO transfer (id, from_account_id, to_account_id, last_modified)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT(id)
                    DO UPDATE SET 
                        from_account_id = EXCLUDED.from_account_id,
                        to_account_id = EXCLUDED.to_account_id,
                        last_modified = EXCLUDED.last_modified
                    WHERE EXCLUDED.last_modified >= transfer.last_modified
                    """,
                    [
                        transfer["id"],
                        transfer["from_account_id"],
                        transfer["to_account_id"],
                        transfer["last_modified"],
                    ],
                )

            for movement in body["movements"]:
                cursor.execute(
                    """
                    INSERT INTO movement (id, user_id, amount, movement_date, description, expense_id, income_id, transfer_id, deleted, last_modified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT(id)
                    DO UPDATE SET 
                        amount = EXCLUDED.amount,
                        movement_date = EXCLUDED.movement_date,
                        description = EXCLUDED.description,
                        expense_id = EXCLUDED.expense_id,
                        income_id = EXCLUDED.income_id,
                        transfer_id = EXCLUDED.transfer_id,
                        deleted = EXCLUDED.deleted,
                        last_modified = EXCLUDED.last_modified
                    WHERE EXCLUDED.last_modified > movement.last_modified
                    """,
                    [
                        movement["id"],
                        user_id,
                        movement["amount"],
                        movement["movement_date"],
                        movement["description"],
                        movement.get("expense_id"),
                        movement.get("income_id"),
                        movement.get("transfer_id"),
                        movement["deleted"],
                        movement["last_modified"],
                    ],
                )

            for reminder in body["reminders"]:
                cursor.execute(
                    """
                    INSERT INTO reminder (id, user_id, name, hour, minute, deleted, last_modified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT(id)
                    DO UPDATE SET 
                        name = EXCLUDED.name,
                        hour = EXCLUDED.hour,
                        minute = EXCLUDED.minute,
                        deleted = EXCLUDED.deleted,
                        last_modified = EXCLUDED.last_modified
                    WHERE EXCLUDED.last_modified > reminder.last_modified
                    """,
                    [
                        reminder["id"],
                        user_id,
                        reminder["name"],
                        reminder["hour"],
                        reminder["minute"],
                        reminder["deleted"],
                        reminder["last_modified"],
                    ],
                )

            conn.commit()
            conn.close()
            cursor.close()

            return ok_response({"message": "Sync successfull"})

        return bad_request_response()
    except Exception as e:
        return internal_error_response(e)
