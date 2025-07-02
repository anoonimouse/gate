from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

REQUIRED_COLUMNS = ['Year', 'Round', 'Paper', 'Score', 'Rank', 'Category', 'Offers']

# Load and validate CSV
def load_and_clean_data(csv_file):
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file '{csv_file}' not found.")

    df = pd.read_csv(csv_file)

    # Check required columns
    if not all(col in df.columns for col in REQUIRED_COLUMNS):
        raise ValueError(f"CSV must contain columns: {', '.join(REQUIRED_COLUMNS)}")

    # Sanitize and clean
    df['Paper'] = df['Paper'].astype(str).str.strip().str.upper()
    df['Category'] = df['Category'].astype(str).str.strip().str.upper()
    df['Offers'] = df['Offers'].astype(str).str.strip()

    # Convert score to numeric and drop bad rows
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
    df = df.dropna(subset=['Score'])

    return df

# Try loading the data at startup
try:
    df = load_and_clean_data('coap_data.csv')
except Exception as e:
    print(f"❌ Failed to load CSV: {e}")
    df = pd.DataFrame()  # Use empty DF to prevent crash
    load_error = str(e)
else:
    load_error = None


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    score_input = None
    error_msg = None

    if load_error:
        error_msg = f"Error loading data: {load_error}"
    elif request.method == 'POST':
        try:
            score_input = float(request.form['score'])
            paper = request.form['paper'].strip().upper()
            category = request.form['category'].strip().upper()

            # Validate score range
            if not (100 <= score_input <= 1000):
                raise ValueError("Score must be between 100 and 1000")

            # Filter matching data
            filtered = df[
                (df['Paper'] == paper) &
                (df['Score'] <= score_input)
            ]

            if category != 'ALL':
                filtered = filtered[filtered['Category'] == category]

            results = filtered[['Year', 'Round', 'Paper', 'Score', 'Rank', 'Category', 'Offers']] \
                .sort_values(by=['Year', 'Round', 'Score'], ascending=[False, True, False]) \
                .to_dict(orient='records')

        except Exception as e:
            error_msg = str(e)

    return render_template('index.html', results=results, score=score_input, error_msg=error_msg)

if __name__ == '__main__':
    app.run(debug=True)
