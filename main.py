from dotenv import load_dotenv
from flask import Flask

from responses import ok_response
from routes.session import session_blueprint
from routes.user import user_blueprint

app = Flask(__name__)
app.register_blueprint(session_blueprint)
app.register_blueprint(user_blueprint)


@app.route("/", methods=["GET"])
def root():
    return ok_response({"message": "API is running :P"})


app.debug = True

if __name__ == "__main__":
    load_dotenv()
    app.run()
