from flask import Flask , session, request , render_template , redirect , url_for
from flask_session import Session 
from cs50 import SQL
import os
import requests

ALPHAVANTAGE_API_KEY = "H6Q79RY0HTKO9Q5G"
ALPHAVANTAGE_BASE = "https://www.alphavantage.co/query"

def lookup(symbol):
    """Look up stock price for given symbol."""
    try:
        # 1️⃣ Build the query parameters
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHAVANTAGE_API_KEY
        }

        # 2️⃣ Send the request
        response = requests.get(ALPHAVANTAGE_BASE, params=params)
        response.raise_for_status()  # raise error if something went wrong

        # 3️⃣ Parse the data
        data = response.json()

        # 4️⃣ Extract the price
        quote = data.get("Global Quote")
        if not quote or "05. price" not in quote:
            return None  # invalid symbol or bad response

        return float(quote["05. price"])
    except Exception as e:
        print("Error fetching data:", e)
        return None


app = Flask(__name__)

user_db = SQL("sqlite:///users.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    user_name = session.get("name")
    return render_template("access.html" , user_name=user_name)


@app.route("/login" , methods=["GET" , "POST"])
def login():
    if request.method == "POST":  
        user_name = request.form.get("user_name")
        password_typed = request.form.get("password")
        rows = user_db.execute("SELECT * FROM users WHERE name = ?" , user_name)
        if not rows:
            return render_template("invalid.html")
        user = rows[0]
        stored_password = user["password"]
        if password_typed == stored_password:
            session["name"] = user["name"]
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register" , methods=["GET" , "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("user_name")
        password = request.form.get("password")
        user_db.execute("INSERT INTO users (name, password) VALUES(?, ?)" , name , password)
        return redirect("/")
    return render_template("register.html")

@app.route("/buy")
def buy():
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    items = []
    for sym in symbols:
        price = lookup(sym)
        items.append({"symbol": sym, "price": price})
    return render_template("buy.html", items=items)  

@app.route("/cart", methods=["POST"])
def cart_add():
    symbol = request.form.get("symbol")
    if not symbol:
        return redirect(url_for("buy"))

    price = lookup(symbol)  # re-check price server-side
    if price is None:
        return redirect(url_for("buy"))

    cart = session.get("cart", [])
    cart.append({"symbol": symbol, "price": price, "qty": 1})
    session["cart"] = cart
    return redirect(url_for("view_cart"))

@app.route("/cart")
def view_cart():
    cart = session.get("cart", [])
    total = sum(item["price"] * item["qty"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)