from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    make_response
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
from models import User, InterviewHistory, Feedback


from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet

from xml.sax.saxutils import escape

import io
import time


# =====================================================
# Flask Configuration
# =====================================================

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print("Database initialization error:", e)


# =====================================================
# Login Manager
# =====================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

login_manager.login_message = "Please login first."

login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# =====================================================
# Home
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")

# =====================================================
# Health Check (Render)
# =====================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "running"
    })
# =====================================================
# Register
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password or not confirm:

            flash("Please fill all fields.", "danger")
            return redirect(url_for("register"))

        if password != confirm:

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


# =====================================================
# Login
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            flash("Login Successful!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password", "danger")

    return render_template("login.html")
    # =====================================================
# Dashboard
# =====================================================

@app.route("/dashboard")
@login_required
def dashboard():

    total_interviews = InterviewHistory.query.filter_by(
        username=current_user.username
    ).count()

    recent_history = (
        InterviewHistory.query.filter_by(
            username=current_user.username
        )
        .order_by(InterviewHistory.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        user=current_user,
        total_interviews=total_interviews,
        recent_history=recent_history
    )


# =====================================================
# Profile
# =====================================================

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


# =====================================================
# Interview
# =====================================================

@app.route("/interview", methods=["GET", "POST"])
@login_required
def interview():

    if request.method == "POST":

        company = request.form.get("company", "").strip()
        role = request.form.get("job_role", "").strip()
        experience = request.form.get("experience", "").strip()
        difficulty = request.form.get("difficulty", "").strip()
        skills = request.form.get("skills", "").strip()

        try:
            count = int(request.form.get("count", 5))
        except ValueError:
            count = 5

        if not role:
            flash("Please select a Job Role.", "danger")
            return redirect(url_for("interview"))

        if not skills:
            flash("Please enter Technical Skills.", "danger")
            return redirect(url_for("interview"))

        try:

            # No delay in production
            from ai_generator import generate_questions

            questions = generate_questions(
                company=company,
                role=role,
                experience=experience,
                difficulty=difficulty,
                skills=skills,
                count=count
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

            flash("Interview Questions Generated Successfully!", "success")

            return redirect(
                url_for(
                    "result",
                    history_id=history.id
                )
            )

        except Exception as e:

            flash(f"AI Error: {str(e)}", "danger")

            return redirect(url_for("interview"))

    return render_template("interview.html")


# =====================================================
# AJAX API
# =====================================================

@app.route("/generate_questions", methods=["POST"])
@login_required
def generate_questions_api():

    try:

        company = request.form.get("company", "")
        role = request.form.get("job_role", "")
        experience = request.form.get("experience", "")
        difficulty = request.form.get("difficulty", "")
        skills = request.form.get("skills", "")

        try:
            count = int(request.form.get("count", 5))
        except ValueError:
            count = 5

        from ai_generator import generate_questions
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

        return jsonify({
            "success": True,
            "history_id": history.id,
            "questions": questions
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
        # =====================================================
# Result Page
# =====================================================

@app.route("/result/<int:history_id>")
@login_required
def result(history_id):

    record = InterviewHistory.query.get_or_404(history_id)

    if record.username != current_user.username:
        flash("Access Denied.", "danger")
        return redirect(url_for("history"))

    # Create an empty feedback record if it doesn't exist
    existing = Feedback.query.filter_by(
        username=current_user.username,
        feedback=""
    ).first()

    if not existing:

        feedback = Feedback(
            username=current_user.username,
            rating=0,
            feedback=""
        )

        db.session.add(feedback)
        db.session.commit()

    return render_template(
        "result.html",
        questions=record.questions,
        role=record.role,
        experience=record.experience,
        skills=record.skills,
        history_id=record.id
    )
# =====================================================
# Submit Feedback
# =====================================================
@app.route("/feedback", methods=["POST"])
@login_required
def feedback():

    try:

        rating = request.form.get("rating")
        feedback_text = request.form.get("feedback")

        existing = Feedback.query.filter_by(
            username=current_user.username,
            feedback=""
        ).first()

        if existing:

            existing.rating = int(rating)
            existing.feedback = feedback_text

        else:

            new_feedback = Feedback(
                username=current_user.username,
                rating=int(rating),
                feedback=feedback_text
            )

            db.session.add(new_feedback)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Thank you for your feedback!"
        })

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
# =====================================================
# Interview History
# =====================================================

@app.route("/history")
@login_required
def history():

    records = (
        InterviewHistory.query
        .filter_by(username=current_user.username)
        .order_by(InterviewHistory.created_at.desc())
        .all()
    )

    return render_template(
        "history.html",
        records=records
    )

# =====================================================
# Admin Feedback
# =====================================================

@app.route("/admin/feedback")
@login_required
def admin_feedback():

    # Change this username to your admin username
    if current_user.username != "Millinda-J-23":
        flash("Access Denied.", "danger")
        return redirect(url_for("dashboard"))

    feedbacks = Feedback.query.order_by(
        Feedback.created_at.desc()
    ).all()

    return render_template(
        "admin_feedback.html",
        feedbacks=feedbacks
    )
# =====================================================
# View Questions
# =====================================================

@app.route("/view/<int:id>")
@login_required
def view(id):

    record = InterviewHistory.query.get_or_404(id)

    if record.username != current_user.username:

        flash("Access Denied.", "danger")

        return redirect(url_for("history"))

    return render_template(
        "view_questions.html",
        record=record
    )


# =====================================================
# Delete Interview
# =====================================================

@app.route("/delete/<int:id>")
@login_required
def delete(id):

    record = InterviewHistory.query.get_or_404(id)

    if record.username != current_user.username:

        flash("Access Denied.", "danger")

        return redirect(url_for("history"))

    db.session.delete(record)

    db.session.commit()

    flash("Interview deleted successfully.", "success")

    return redirect(url_for("history"))


# =====================================================
# Delete All Interviews
# =====================================================

@app.route("/delete_all")
@login_required
def delete_all():

    InterviewHistory.query.filter_by(
        username=current_user.username
    ).delete()

    db.session.commit()

    flash("All interview history deleted successfully.", "success")

    return redirect(url_for("history"))
    # =====================================================
# Download PDF
# =====================================================

@app.route("/download/<int:id>")
@login_required
def download(id):

    record = InterviewHistory.query.get_or_404(id)

    if record.username != current_user.username:
        flash("Access Denied.", "danger")
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

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"<b>User:</b> {escape(current_user.username)}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Role:</b> {escape(record.role)}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Experience:</b> {escape(record.experience)}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Skills:</b> {escape(record.skills)}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Generated Interview Questions",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 10))

    # Split questions line by line
    for line in record.questions.split("\n"):

        line = line.strip()

        if line:

            story.append(
                Paragraph(
                    escape(line),
                    styles["BodyText"]
                )
            )

            story.append(Spacer(1, 8))

    doc.build(story)

    pdf = buffer.getvalue()

    buffer.close()

    response = make_response(pdf)

    response.headers["Content-Type"] = "application/pdf"

    response.headers["Content-Disposition"] = (
        f'attachment; filename="Interview_{record.id}.pdf"'
    )

    return response
    
# =====================================================
# Logout
# =====================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "success")

    return redirect(url_for("home"))


# =====================================================
# 404 Error
# =====================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


# =====================================================
# 500 Error
# =====================================================

@app.errorhandler(500)
def internal_server_error(error):

    db.session.rollback()

    return render_template(
        "500.html"
    ), 500


# =====================================================
# Run Flask App
# =====================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )