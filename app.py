"""
Smart Campus Connect - Python Flask Backend (Firestore Version)
Team: Link Loopers
Cloud Storage: Firebase Firestore (Permanent Storage)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# ==================== FIREBASE SETUP ====================

import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

firebase_json = os.environ.get("FIREBASE_KEY")

if not firebase_json:
    raise Exception("FIREBASE_KEY environment variable is missing")

cred = credentials.Certificate(json.loads(firebase_json))
firebase_admin.initialize_app(cred)
db = firestore.client()
   # your file name
firebase_admin.initialize_app(cred)
db = firestore.client()

# ==================== FLASK SETUP ====================

app = Flask(__name__)
CORS(app)

# =======================================================
# ROOT CHECK
# =======================================================
@app.route('/')
def index():
    return jsonify({
        'message': 'Smart Campus Connect API (Firestore)',
        'team': 'Link Loopers',
        'status': 'running'
    })

# =======================================================
# ANNOUNCEMENTS (Firestore Collection: announcements)
# =======================================================

@app.route('/api/announcements', methods=['GET'])
def get_announcements():
    docs = db.collection("announcements").order_by("timestamp").stream()
    ann = [doc.to_dict() for doc in docs]
    return jsonify(ann)

@app.route('/api/announcements', methods=['POST'])
def add_announcement():
    data = request.json
    db.collection("announcements").add({
        "message": data.get("message"),
        "postedBy": data.get("postedBy"),
        "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    })
    return jsonify({"status": "success", "message": "Announcement added"})

# =======================================================
# EVENTS (Firestore Collection: events)
# =======================================================

@app.route('/api/events', methods=['GET'])
def get_events():
    docs = db.collection("events").order_by("created", direction=firestore.Query.DESCENDING).stream()
    events = [doc.to_dict() for doc in docs]
    return jsonify(events)

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    db.collection("events").add({
        "event": data.get("event"),
        "date": data.get("date"),
        "time": data.get("time"),
        "created": datetime.now().timestamp()
    })
    return jsonify({"status": "success", "message": "Event added"})

# =======================================================
# STUDENTS (Firestore Collection: students)
# =======================================================

@app.route('/api/students', methods=['GET'])
def get_students():
    docs = db.collection("students").stream()
    students = [doc.to_dict() for doc in docs]
    return jsonify(students)

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    student_id = str(data.get("id"))
    db.collection("students").document(student_id).set(data)
    return jsonify({"status": "success", "message": "Student added"})

@app.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    doc = db.collection("students").document(str(student_id)).get()
    if doc.exists:
        return jsonify(doc.to_dict())
    return jsonify({"status": "error", "message": "Student not found"}), 404

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    db.collection("students").document(str(student_id)).delete()
    return jsonify({"status": "success", "message": "Student deleted"})

# =======================================================
# POLLS (Firestore Collection: polls)
# =======================================================

@app.route('/api/polls', methods=['GET'])
def get_polls():
    docs = db.collection("polls").stream()
    polls = [{**doc.to_dict(), "id": doc.id} for doc in docs]
    return jsonify(polls)

@app.route('/api/polls', methods=['POST'])
def create_poll():
    data = request.json
    db.collection("polls").add({
        "question": data.get("question"),
        "options": data.get("options"),
        "votes": [0] * len(data.get("options")),
        "totalVotes": 0
    })
    return jsonify({"status": "success", "message": "Poll created"})

@app.route('/api/polls/<poll_id>/vote', methods=['POST'])
def vote_poll(poll_id):
    data = request.json
    doc_ref = db.collection("polls").document(poll_id)
    poll = doc_ref.get().to_dict()

    index = data.get("optionIndex")
    poll["votes"][index] += 1
    poll["totalVotes"] += 1

    doc_ref.update(poll)
    return jsonify({"status": "success", "message": "Vote recorded"})

# =======================================================
# AUTH (Firestore Collection: users)
# =======================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json

    # Check if email exists
    existing = db.collection("users").where("email", "==", data["email"]).get()
    if existing:
        return jsonify({"status": "error", "message": "Email already exists"}), 400

    db.collection("users").add(data)
    return jsonify({"status": "success", "message": "Registration successful"})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    users_ref = db.collection("users") \
                  .where("email", "==", data["email"]) \
                  .where("password", "==", data["password"]) \
                  .get()

    if not users_ref:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    user = users_ref[0].to_dict()
    return jsonify({"status": "success", "user": user})

# =======================================================
# RUN SERVER
# =======================================================

if __name__ == '__main__':
    print("="*50)
    print(" Smart Campus Connect (Firestore Enabled Backend)")
    print(" Team: Link Loopers")
    print("="*50)
    print("Server running on http://localhost:8080")
    print()

    import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)


