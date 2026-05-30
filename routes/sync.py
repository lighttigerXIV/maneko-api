from flask import Blueprint, request

from db import get_db
from responses import bad_request_response, database_error_reponse, internal_error_response, ok_response
from token_utils import authenticated

sync_blueprint = Blueprint("sync_blueprint", __name__)


@sync_blueprint.route("/sync", methods=["GET", "POST"])
@authenticated
def sync():
    try:
        if request.method == "GET":
            conn, cursor = get_db()

            cursor.execute(
                """
                WITH categories_query AS (
                    SELECT id, name, color, icon, deleted, last_modified 
                    FROM category
                    WHERE user_id = '756b5af3-2b24-4613-aec7-59f6bb3a7f86'
                ),
                sub_categories_query AS (
                    SELECT sc.id, sc.name, sc.icon, sc.deleted, sc.last_modified
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
                    SELECT e.account_id, e.category_id, e.sub_category_id, e.info, e.last_modified 
                    FROM expense e
                    LEFT JOIN account a ON a.id = e.account_id
                    WHERE a.user_id = '756b5af3-2b24-4613-aec7-59f6bb3a7f86'
                ),
                incomes_query AS (
                    SELECT i.account_id, i.category_id, i.sub_category_id, i.info, i.last_modified 
                    FROM income i
                    LEFT JOIN account a ON a.id = i.account_id
                    WHERE a.user_id = '756b5af3-2b24-4613-aec7-59f6bb3a7f86'
                ),
                transfers_query AS (
                    SELECT t.from_account_id, t.to_account_id, t.last_modified 
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
                return database_error_reponse()

            return ok_response(row["response"])

        if request.method == "PUT":
            return ok_response("meow")

        return bad_request_response()
    except Exception as e:
        return internal_error_response(e)
