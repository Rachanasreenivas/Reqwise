from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import datetime
import os

# Create Flask app
app = Flask(__name__, template_folder=os.path.abspath("templates"))

# ----- Database Setup -----
def init_db():
    conn = sqlite3.connect('reqwise.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_name TEXT,
                    resource_type TEXT,
                    amount INTEGER,
                    status TEXT,
                    request_time TEXT,
                    cost_estimate REAL
                )''')
    conn.commit()
    conn.close()

# ----- Routes -----

# Home/Dashboard: Show all requests
@app.route('/')
def index():
    conn = sqlite3.connect('reqwise.db')
    c = conn.cursor()
    c.execute("SELECT * FROM requests")
    data = c.fetchall()
    conn.close()
    return render_template('index.html', data=data)

# User request form
@app.route('/request', methods=['GET', 'POST'])
def request_resource():
    if request.method == 'POST':
        team_name = request.form['team_name']
        resource_type = request.form['resource_type']
        amount = int(request.form['amount'])
        cost_estimate = estimate_cost(resource_type, amount)

        conn = sqlite3.connect('reqwise.db')
        c = conn.cursor()
        c.execute("INSERT INTO requests (team_name, resource_type, amount, status, request_time, cost_estimate) VALUES (?, ?, ?, ?, ?, ?)",
                  (team_name, resource_type, amount, 'Pending', datetime.datetime.now().isoformat(), cost_estimate))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('request.html')

# Approve a request
@app.route('/approve/<int:req_id>')
def approve(req_id):
    update_status(req_id, 'Approved')
    return redirect(url_for('index'))

# Reject a request
@app.route('/reject/<int:req_id>')
def reject(req_id):
    update_status(req_id, 'Rejected')
    return redirect(url_for('index'))

# Provide a JSON template
@app.route('/template')
def get_template():
    template = {
        "team_name": "Example Team",
        "resource_type": "storage",
        "amount": 100
    }
    return jsonify(template)

# ----- Helper Functions -----
def update_status(req_id, status):
    conn = sqlite3.connect('reqwise.db')
    c = conn.cursor()
    c.execute("UPDATE requests SET status = ? WHERE id = ?", (status, req_id))
    conn.commit()
    conn.close()

def estimate_cost(resource_type, amount):
    prices = {
        'storage': 0.10,   # $0.10 per GB
        'vm': 0.50,        # $0.50 per VM
        'database': 0.30   # $0.30 per DB unit
    }
    return round(prices.get(resource_type, 0.10) * amount, 2)

# ----- Main -----
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
