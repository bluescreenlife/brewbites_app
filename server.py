from flask import Flask, render_template
from datetime import datetime
import requests

app = Flask(__name__)

@app.route("/")
def msp():
    date = datetime.now().strftime("%m/%d/%Y")
    response = requests.get("https://api.npoint.io/5ef993025244afcd13cd")
    if response.status_code == 200:
        trucks = response.json()
        return render_template("index.html", date=date, trucks=trucks)
    else:
        print(response.status_code, response.text)
        return render_template("maintenance.html")
    

if __name__ == "__main__":
    app.run(debug=True)