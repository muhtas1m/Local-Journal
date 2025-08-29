
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "local-only-secret"
DATA_FILE = "journal.xlsx"
COLUMNS = ["Date", "Time", "Location", "Daily Summary", "Thoughts & Feelings", "Reflection", "Gratitude", "Next Steps / Intentions"]

def ensure_file():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        try:
            df.to_excel(DATA_FILE, index=False, engine="openpyxl")
        except Exception:
            # If openpyxl not available, create a CSV and later convert on next save
            df.to_csv(DATA_FILE.replace(".xlsx",".csv"), index=False)

def to_ddmmyyyy(dt):
    return dt.strftime("%d/%m/%Y")

def normalize_date(raw):
    # Accepts various inputs; returns dd/mm/yyyy
    if not raw:
        return to_ddmmyyyy(datetime.now())
    # Try HTML date input (yyyy-mm-dd)
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return to_ddmmyyyy(datetime.strptime(raw, fmt))
        except ValueError:
            continue
    # Fallback: now
    return to_ddmmyyyy(datetime.now())

def read_df():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_excel(DATA_FILE, engine="openpyxl")
        except Exception:
            pass
    csv_fallback = DATA_FILE.replace(".xlsx",".csv")
    if os.path.exists(csv_fallback):
        try:
            return pd.read_csv(csv_fallback)
        except Exception:
            pass
    return pd.DataFrame(columns=COLUMNS)

def save_df(df):
    try:
        df.to_excel(DATA_FILE, index=False, engine="openpyxl")
    except Exception:
        # Fallback to CSV if excel engine missing
        df.to_csv(DATA_FILE.replace(".xlsx",".csv"), index=False)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = {
        "Date": normalize_date(request.form.get("date")),
        "Time": request.form.get("time", ""),
        "Location": request.form.get("location", ""),
        "Daily Summary": request.form.get("summary", ""),
        "Thoughts & Feelings": request.form.get("thoughts", ""),
        "Reflection": request.form.get("reflection", ""),
        "Gratitude": request.form.get("gratitude", ""),
        "Next Steps / Intentions": request.form.get("nextsteps", ""),
    }
    ensure_file()
    df = read_df()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    save_df(df)
    flash("Entry saved. Stored locally in this folder.")
    return redirect(url_for("index"))

@app.route("/entries")
def entries():
    ensure_file()
    df = read_df()
    records = df.to_dict(orient="records")
    return render_template("entries.html", records=records, columns=COLUMNS)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
