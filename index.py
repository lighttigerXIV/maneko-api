from dotenv import load_dotenv
from flask import Flask
from routes.user import user_blueprint


app = Flask(__name__)
app.register_blueprint(user_blueprint)


app.debug = True

if __name__ == "__main__":
    load_dotenv()
    app.run()
