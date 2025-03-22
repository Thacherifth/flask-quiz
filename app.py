from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import pandas as pd
import qrcode
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
db = SQLAlchemy(app)


# Database model
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    choice = db.Column(db.String(1), nullable=False)


# Generate a QR code
def generate_qr():
    url = "https://flask-quiz-9pjm.onrender.com/"  # Change this to your hosted URL when deploying
    qr = qrcode.make(url)
    qr.save("static/quiz_qr.png")


# Create DB
with app.app_context():
    db.create_all()


# Route to display quiz
@app.route("/", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        choice = request.form.get("choice")
        if choice in ["A", "B", "C", "D"]:
            new_answer = Answer(choice=choice)
            db.session.add(new_answer)
            db.session.commit()
            return redirect(url_for("results"))
    return render_template("index.html")


# Route to display results
@app.route("/results")
def results():
    data = pd.read_sql(Answer.query.statement, db.session.bind)
    answer_counts = data["choice"].value_counts()

    # Create the bar chart
    plt.figure(figsize=(6, 4))
    answer_counts.sort_index().plot(kind="bar", color=["blue", "green", "red", "purple"])
    plt.xlabel("Answers (A, B, C, D)")
    plt.ylabel("Number of Votes")
    plt.title("Quiz Answer Distribution")
    plt.xticks(rotation=0)

    # Save the figure
    plt.savefig("static/results.png")
    plt.close()

    return render_template("results.html")


# Run the app
if __name__ == "__main__":
    generate_qr()
    app.run(debug=True)
