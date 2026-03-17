from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# 🔒 Secret key (set in environment for production)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# 🌐 Google Sheet CSV URL
DATA_URL = "https://docs.google.com/spreadsheets/d/1bmPVm-Ur4mqK9l-TJ7Za3vEd6b9wNVkeUo8-n7LHUKI/export?format=csv"

# 📦 Global cache
data_cache = None


# ✅ Load and cache data
def load_data():
    global data_cache

    if data_cache is None:
        try:
            df = pd.read_csv(DATA_URL)

            # Normalize column names (important)
            df.columns = df.columns.str.strip().str.lower()

            if "certificate_id" not in df.columns:
                raise Exception("Missing 'certificate_id' column in sheet")

            # Clean certificate_id
            df["certificate_id"] = (
                df["certificate_id"]
                .astype(str)
                .str.upper()
                .str.strip()
            )

            data_cache = df

        except Exception as e:
            print("❌ Error loading data:", e)
            data_cache = pd.DataFrame()

    return data_cache


# 🏠 Main route
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        cert_id = request.form.get("certificate_id", "").upper().strip()

        if not cert_id:
            error = "Please enter a Certificate ID"
        else:
            df = load_data()

            if df.empty:
                error = "System error: Unable to load certificate data"
            else:
                record = df[df["certificate_id"] == cert_id]

                if not record.empty:
                    result = record.iloc[0].to_dict()
                else:
                    result = "NOT FOUND"

    return render_template("index.html", result=result, error=error)


# 🔄 Optional: Refresh data manually (for admin use)
@app.route("/refresh")
def refresh_data():
    global data_cache
    data_cache = None
    load_data()
    return "✅ Data refreshed successfully!"


# 🚀 Production entry
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
