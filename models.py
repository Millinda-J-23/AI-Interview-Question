from database import db
from flask_login import UserMixin
from datetime import datetime
from zoneinfo import ZoneInfo


# =====================================================
# Indian Time Function
# =====================================================

def indian_time():
    return datetime.now(ZoneInfo("Asia/Kolkata"))


# =====================================================
# User Model
# =====================================================

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )


# =====================================================
# Interview History Model
# =====================================================

class InterviewHistory(db.Model):

    __tablename__ = "interview_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    role = db.Column(
        db.String(100),
        nullable=False
    )

    experience = db.Column(
        db.String(100),
        nullable=False
    )

    skills = db.Column(
        db.Text,
        nullable=False
    )

    questions = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=indian_time,
        nullable=False
    )


# =====================================================
# Feedback Model
# =====================================================

class Feedback(db.Model):

    __tablename__ = "feedback"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    feedback = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=indian_time,
        nullable=False
    )