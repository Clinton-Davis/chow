from flask import Flask
import os

app = Flask(__name__)





@app.route('/')
def hello():
    return "Howyow!"

if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
            port=(os.environ.get('PORT')),
            debug=True)