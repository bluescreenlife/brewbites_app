from flask import Flask, render_template
from datetime import datetime
import requests

app = Flask(__name__)

@app.route("/")
def msp():
    date = datetime.now().strftime("%m/%d/%Y")

    json_bin = "https://api.jsonbin.io/v3/b/659b6e0a1f5677401f18ffe1"

    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': '$2a$10$iTnNq06UFXSRHIYKj1EoCuNZEjdkvpZLt9rWEJva7c08HOEdwVDJq'
    }

    response = requests.get(json_bin, headers=headers)
    
    if response.status_code == 200:
        trucks = response.json()["record"]
        return render_template("index.html", date=date, trucks=trucks)
    else:
        print(response.status_code, response.text)
        return render_template("maintenance.html")
    

if __name__ == "__main__":
    app.run(debug=True)