"""
Hardware Shop Credit Tracker
----------------------------
A small Flask web app for a hardware shop in Eldoret that sells on credit.
Type a customer's name and see how much they owe - instead of flipping
through the credit notebook.

Routes:
    /              HTML page with the shop name and a search form
    /api/balance   JSON API: /api/balance?name=Kiprop  -> customer's balance

Usage:
    pip install -r requirements.txt
    python app.py
    Then open http://127.0.0.1:5000 in your browser.
"""

import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

SHOP_NAME = "Kimutai Hardware & Building Supplies"
SHOP_LOCATION = "Uganda Road, Eldoret"

# Sample data - in a real shop this would come from a database or spreadsheet.
CUSTOMERS = {
    "joseph kiprop":   {"balance_kes": 12450, "last_payment": "2026-10-28", "credit_limit_kes": 30000},
    "mary chebet":     {"balance_kes": 0,     "last_payment": "2026-11-02", "credit_limit_kes": 20000},
    "daniel otieno":   {"balance_kes": 38900, "last_payment": "2026-09-15", "credit_limit_kes": 40000},
    "faith jepkosgei": {"balance_kes": 6200,  "last_payment": "2026-11-05", "credit_limit_kes": 15000},
    "peter wafula":    {"balance_kes": 21750, "last_payment": "2026-10-10", "credit_limit_kes": 25000},
    "grace njoroge":   {"balance_kes": 3300,  "last_payment": "2026-11-08", "credit_limit_kes": 10000},
}


def find_customers(query):
    """Exact full-name match first; otherwise every customer whose name contains the query."""
    q = " ".join(query.lower().split())
    if q in CUSTOMERS:
        return [q]
    return [name for name in CUSTOMERS if q in name]


def customer_json(name):
    data = CUSTOMERS[name]
    return {
        "name": name.title(),
        "balance_kes": data["balance_kes"],
        "credit_limit_kes": data["credit_limit_kes"],
        "available_credit_kes": max(data["credit_limit_kes"] - data["balance_kes"], 0),
        "last_payment": data["last_payment"],
        "status": "cleared" if data["balance_kes"] == 0
                  else "near limit" if data["balance_kes"] >= 0.8 * data["credit_limit_kes"]
                  else "owing",
    }


@app.route("/")
def home():
    return render_template("index.html", shop_name=SHOP_NAME, shop_location=SHOP_LOCATION)


@app.route("/api/balance")
def balance():
    query = request.args.get("name", "").strip()
    if not query:
        return jsonify({"error": "Missing customer name. Use /api/balance?name=Kiprop"}), 400
    if len(query) < 2:
        return jsonify({"error": "Type at least 2 letters of the customer's name."}), 400

    matches = find_customers(query)
    if not matches:
        return jsonify({"error": f"No customer found matching '{query}'."}), 404
    if len(matches) > 1:
        return jsonify({
            "error": f"More than one customer matches '{query}'. Please be more specific.",
            "matches": [m.title() for m in matches],
        }), 400
    return jsonify(customer_json(matches[0])), 200


@app.errorhandler(404)
def not_found(_err):
    return jsonify({"error": "Page not found. Try / or /api/balance?name=..."}), 404


if __name__ == "__main__":
    # Debug mode only when FLASK_DEBUG=1 - never run debug mode on a public server.
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
