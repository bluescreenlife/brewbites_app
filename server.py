from flask import Flask, render_template
from main import truck_dict
from datetime import datetime

app = Flask(__name__)

@app.route("/msp")
def msp():
    date = datetime.now().strftime("%m/%d/%Y")
    trucks = truck_dict()
    return render_template("index.html", date=date, trucks=trucks)

if __name__ == "__main__":
    app.run(debug=True)