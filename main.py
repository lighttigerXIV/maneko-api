from dotenv import load_dotenv
from flask import Flask

from responses import ok_response
from routes.categories import categories_blueprint
from routes.session import session_blueprint
from routes.user import user_blueprint

app = Flask(__name__)
app.register_blueprint(session_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(categories_blueprint)

"""
def categories(id):
    try:
        if request.method == "GET":
            pass
        if request.method == "PUT":
            pass
        if request.method == "POST":
            body = get_body()

        if request.method == "DELETE":
            pass

        return bad_request_response()
    except Exception as e:
        return internal_error_response(e)
"""


@app.route("/", methods=["GET"])
def root():
    return ok_response({"message": "API is running :P"})


app.debug = True

if __name__ == "__main__":
    load_dotenv()
    app.run()
