from flask import Flask, render_template, request
from tracker import check_price  # Import your functions from tracker.py

app = Flask(__name__)

@app.route("/")
def home():
    # Renders the main page with the form
    return render_template("index.html")

@app.route("/track", methods=["POST"])
def track():
    url = request.form["url"]
    target_price = float(request.form["price"])
    email = request.form["email"]

    # Update check_price to return a message string
    message = check_price(url, target_price, email)

    return render_template("track.html", message=message, product_url=url)


if __name__ == "__main__":
    app.run(debug=True)
