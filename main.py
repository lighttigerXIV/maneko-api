from dotenv import load_dotenv
from flask import Flask

from responses import ok_response
from routes.accounts import accounts_blueprint
from routes.categories import categories_blueprint
from routes.expenses import expenses_blueprint
from routes.incomes import incomes_blueprint
from routes.movements import movements_blueprint
from routes.reminders import reminders_blueprint
from routes.session import session_blueprint
from routes.subcategories import subcategories_blueprint
from routes.sync import sync_blueprint
from routes.transfers import transfers_blueprint
from routes.user import user_blueprint

app = Flask(__name__)
app.register_blueprint(accounts_blueprint)
app.register_blueprint(categories_blueprint)
app.register_blueprint(expenses_blueprint)
app.register_blueprint(incomes_blueprint)
app.register_blueprint(movements_blueprint)
app.register_blueprint(reminders_blueprint)
app.register_blueprint(session_blueprint)
app.register_blueprint(subcategories_blueprint)
app.register_blueprint(transfers_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(sync_blueprint)


@app.route("/", methods=["GET"])
def root():
    return ok_response({"message": "API is running :P"})


app.debug = True

if __name__ == "__main__":
    load_dotenv()
    app.run()
