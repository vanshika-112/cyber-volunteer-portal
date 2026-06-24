from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.secret_key = "cyberportal123"

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Report Table
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    threat_type = db.Column(db.String(100))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    evidence = db.Column(db.String(500))
    screenshot = db.Column(db.String(300))
    status = db.Column(db.String(50), default="Pending")


# Routes

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/report", methods=["GET", "POST"])
def report():

    if request.method == "POST":

        threat_type = request.form["threat_type"]
        title = request.form["title"]
        description = request.form["description"]
        evidence = request.form["evidence"]
        screenshot_file = request.files.get("screenshot")
        filename = ""

        if screenshot_file and screenshot_file.filename:
            filename = screenshot_file.filename
            screenshot_file.save(
                os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
                )
            )

        new_report = Report(
            threat_type=threat_type,
            title=title,
            description=description,
            evidence=evidence,
            screenshot=filename
        )

        db.session.add(new_report)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("report.html")


@app.route("/awareness")
def awareness():
    return render_template("awareness.html")


@app.route("/dashboard")
def dashboard():

    reports = Report.query.all()

    total_reports = Report.query.count()

    pending_reports = Report.query.filter_by(
        status="Pending"
    ).count()

    verified_reports = Report.query.filter_by(
        status="Verified"
    ).count()

    return render_template(
        "dashboard.html",
        reports=reports,
        total_reports=total_reports,
        pending_reports=pending_reports,
        verified_reports=verified_reports
    )

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        if (
            role == "admin"
            and username == "admin"
            and password == "admin123"
        ):
            session["role"] = "admin"
            session["username"] = username

            return redirect("/admin/dashboard")

        if (
            role == "volunteer"
            and username == "volunteer"
            and password == "vol123"
        ):
            session["role"] = "volunteer"
            session["username"] = username

            return redirect("/volunteer/dashboard")

    return render_template("login.html")

@app.route("/admin/dashboard")
def admin_dashboard():

    if session.get("role") != "admin":
        return redirect("/login")

    return render_template("admin_dashboard.html")

@app.route("/volunteer/dashboard")
def volunteer_dashboard():

    if session.get("role") != "volunteer":
        return redirect("/login")

    return render_template("volunteer_dashboard.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# Main

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)