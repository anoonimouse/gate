from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)
data = pd.read_csv("gate_ece_obc_cutoffs.csv")

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        try:
            score = float(request.form['score'])
            category = request.form['category'].strip().upper()
            discipline = request.form['discipline'].strip().upper()

            filtered = data[
                (data['Category'].str.upper() == category) &
                (data['Discipline'].str.upper() == discipline) &
                (data['Closing Score'] <= score)
            ]

            results = {}
            for year in sorted(filtered['Year'].unique()):
                yearly = filtered[filtered['Year'] == year]
                results[year] = yearly.sort_values("Closing Score", ascending=False).to_dict("records")
        except Exception as e:
            results = {"error": str(e)}

    return render_template("index.html", results=results)

if __name__ == '__main__':
    app.run(debug=True)