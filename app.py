from flask import Flask, render_template, request
import pandas as pd
import os
import re

app = Flask(__name__)

# 🔒 Secret key
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key")

# Google Sheet CSV Link
DATA_URL = "https://docs.google.com/spreadsheets/d/1bmPVm-Ur4mqK9l-TJ7Za3vEd6b9wNVkeUo8-n7LHUKI/export?format=csv"

def load_data():
    try:
        df = pd.read_csv(DATA_URL)
        df["certificate_id"] = df["certificate_id"].astype(str).str.upper().str.strip()
        return df
    except Exception as e:
        print("Error loading data:", e)
        return pd.DataFrame()

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        user_input = request.form.get("certificate_id", "").strip()

        # ✅ Allow only numbers
        numbers_only = re.sub(r'[^0-9]', '', user_input)

        if numbers_only:
            # ✅ Add LCF prefix automatically
            cert_id = "LCF" + numbers_only

            df = load_data()

            if not df.empty:
                record = df[df["certificate_id"] == cert_id]

                if not record.empty:
                    result = record.iloc[0].to_dict()
                else:
                    result = "NOT FOUND"
            else:
                result = "ERROR"
        else:
            result = "NOT FOUND"

    return render_template("index.html", result=result)


# ✅ Production run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
