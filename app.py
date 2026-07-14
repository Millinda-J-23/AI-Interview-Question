from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    make_response,
    jsonify
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from config import Config
from database import db
from models import User, InterviewHistory
from ai_generator import generate_questions

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph
)
from reportlab.lib.styles import getSampleStyleSheet

import io
import time

# =====================================
# Flask Configuration
# =====================================

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# =====================================
# Login Manager
# =====================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


# =====================================
# Home
# =====================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================
# Register
# =====================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password or not confirm_password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash("Registration Successful!", "success")

        return redirect(url_for("dashboard"))

    return render_template("register.html")


# =====================================
# Login
# =====================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            flash("Login Successful!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password", "danger")

    return render_template("login.html")
# =====================================
# Dashboard
# =====================================

@app.route("/dashboard")
@login_required
def dashboard():

    total_interviews = InterviewHistory.query.filter_by(
        username=current_user.username
    ).count()

    return render_template(
        "dashboard.html",
        user=current_user,
        total_interviews=total_interviews,
        questions=[]
    )


# =====================================
# Profile
# =====================================

@app.route("/profile")
@login_required
def profile():

    total_interviews = InterviewHistory.query.filter_by(
        username=current_user.username
    ).count()

    return render_template(
        "profile.html",
        current_user=current_user,
        total_interviews=total_interviews
    )


# =====================================
# Interview
# =====================================
@app.route("/interview", methods=["GET", "POST"])
@login_required
def interview():

    if request.method == "POST":

        company = request.form.get("company")
        role = request.form.get("job_role")
        experience = request.form.get("experience")
        difficulty = request.form.get("difficulty")
        skills = request.form.get("skills")
        count = request.form.get("count", "3")

        if not role:
            flash("Please select a Job Role.", "danger")
            return redirect(url_for("interview"))

        if not skills:
            flash("Please enter your technical skills.", "danger")
            return redirect(url_for("interview"))

        try:

            time.sleep(5)

            company = request.form.get("company")
            role = request.form.get("job_role")
            experience = request.form.get("experience")
            difficulty = request.form.get("difficulty")
            skills = request.form.get("skills")
            count = request.form.get("count", "3")

            questions = generate_questions(
                company,
                role,
                experience,
                difficulty,
                skills,
                count
            )

            history = InterviewHistory(
                username=current_user.username,
                role=role,
                experience=experience,
                skills=skills,
                questions=questions
            )

            db.session.add(history)
            db.session.commit()

            return render_template(
                "result.html",
                questions=questions,
                role=role,
                experience=experience,
                skills=skills,
                history_id=history.id
            )

        except Exception as e:
            flash(f"AI Error: {e}", "danger")
            return redirect(url_for("interview"))

    return render_template("interview.html")
# =====================================
# API (Future AJAX Support)
# =====================================
# =====================================
# AJAX Generate Questions
# =====================================

@app.route("/generate_questions", methods=["POST"])
@login_required
def generate_questions_api():

    try:

        company = request.form.get("company", "")
        role = request.form.get("job_role", "")
        experience = request.form.get("experience", "")
        difficulty = request.form.get("difficulty", "")
        skills = request.form.get("skills", "")
        count = request.form.get("count", "3")

        questions = generate_questions(
            company,
            role,
            experience,
            difficulty,
            skills,
            int(count)
        )

        history = InterviewHistory(
            username=current_user.username,
            role=role,
            experience=experience,
            skills=skills,
            questions=questions
        )

        db.session.add(history)
        db.session.commit()

        return jsonify({
            "success": True,
            "history_id": history.id
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =====================================
# Result Page
# =====================================

@app.route("/result/<int:history_id>")
@login_required
def result(history_id):

    record = InterviewHistory.query.get_or_404(history_id)

    if record.username != current_user.username:
        flash("Access Denied", "danger")
        return redirect(url_for("history"))

    return render_template(
        "result.html",
        questions=record.questions,
        role=record.role,
        experience=record.experience,
        skills=record.skills,
        history_id=record.id
    )
# =====================================
# Interview History
# =====================================

@app.route("/history")
@login_required
def history():

    records = InterviewHistory.query.filter_by(
        username=current_user.username
    ).order_by(
        InterviewHistory.created_at.desc()
    ).all()

    return render_template(
        "history.html",
        records=records
    )


# =====================================
# View Interview
# =====================================

@app.route("/view/<int:id>")
@login_required
def view(id):

    record = InterviewHistory.query.get_or_404(id)

    if record.username != current_user.username:

        flash("Access Denied", "danger")
        return redirect(url_for("history"))

    return render_template(
        "view_questions.html",
        record=record
    )


# =====================================
# Delete Interview
# =====================================

@app.route("/delete/<int:id>")
@login_required
def delete(id):

    record = InterviewHistory.query.get_or_404(id)

    if record.username != current_user.username:

        flash("Access Denied", "danger")
        return redirect(url_for("history"))

    db.session.delete(record)
    db.session.commit()

    flash("Interview deleted successfully.", "success")

    return redirect(url_for("history"))


# =====================================
# Download PDF
# =====================================

@app.route("/download/<int:id>")
@login_required
def download(id):

    record = InterviewHistory.query.get_or_404(id)

    if record.username != current_user.username:

        flash("Access Denied", "danger")
        return redirect(url_for("history"))

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "AI Interview Question Generator",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Username:</b> {current_user.username}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Role:</b> {record.role}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Experience:</b> {record.experience}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Skills:</b> {record.skills}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            "<br/><b>Generated Questions</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            record.questions.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    )

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)

    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f'attachment; filename="Interview_{record.id}.pdf"'
    )

    return response
# =====================================
# Logout
# =====================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "success")

    return redirect(url_for("home"))


# =====================================
# Error Handlers
# =====================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):

    db.session.rollback()

    return render_template("500.html"), 500


# =====================================
# Run Application
# =====================================

if __name__ == "__main__":

    app.run(
        debug=True
    )