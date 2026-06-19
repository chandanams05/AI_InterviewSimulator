from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import random
import re
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# ================= MongoDB =================
client = MongoClient("mongodb+srv://chandana05:mongoDB26@cluster0.isrnuwh.mongodb.net/?retryWrites=true&w=majority")
db = client["ai_interview"]
users = db["users"]
questions_collection = db["questions"]

# ================= Gemini =================
genai.configure(api_key="AIzaSyCh5cF07a_Dnep6zPjch_KgRT1-d6Rj5YU")
model = genai.GenerativeModel("gemini-2.0-flash")

# ================= DEFAULT ROLES =================
DEFAULT_ROLES = [
    "Python Developer", "Java Developer", "Frontend Developer",
    "Backend Developer", "Full Stack Developer", "Data Analyst",
    "Data Scientist", "Machine Learning Engineer", "DevOps Engineer",
    "Cloud Engineer", "Cyber Security", "Android Developer",
    "iOS Developer", "Software Tester", "UI/UX Designer",
    "System Design", "Database Engineer", "Network Engineer",
    "Embedded Systems", "HR"
]

# ================= CLEAN TEXT =================
def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

# ================= FALLBACK =================
def fallback(answer):
    if len(answer.strip()) < 5:
        return 0, "Too short / invalid answer."
    return 5, "Basic answer."

# ================= HOME =================
@app.route("/")
def home():
    return redirect(url_for("login"))

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        user = users.find_one({"username": u, "password": p})

        if user:
            session["username"] = u
            return redirect(url_for("index"))

        return "Invalid credentials"

    return render_template("login.html")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if users.find_one({"username": u}):
            return "Username exists"

        users.insert_one({"username": u, "password": p})
        return redirect(url_for("login"))

    return render_template("register.html")

# ================= ROLE PAGE =================
@app.route("/index", methods=["GET", "POST"])
def index():

    if "username" not in session:
        return redirect(url_for("login"))

    # if DB empty → use default roles
    db_roles = list(questions_collection.distinct("role"))
    roles = db_roles if db_roles else DEFAULT_ROLES

    if request.method == "POST":
        session["role"] = request.form["role"]
        return redirect(url_for("new_interview"))

    return render_template("index.html", roles=roles)

# ================= NEW INTERVIEW =================
@app.route("/new_interview")
def new_interview():

    if "username" not in session:
        return redirect(url_for("login"))

    role = session.get("role")

    questions = list(questions_collection.find({"role": role}))

    cleaned = []
    seen = set()

    for q in questions:
        text = str(q.get("question", ""))

        key = normalize(text)

        if key not in seen:
            seen.add(key)

            cleaned.append({
                "question": text,
                "difficulty": str(q.get("difficulty", "Medium"))
            })

    random.shuffle(cleaned)

    # if no questions → fallback message
    if not cleaned:
        cleaned = [{
            "question": "No questions available for this role yet. Please add dataset.",
            "difficulty": "NA"
        }]

    session["questions"] = cleaned[:5]

    return redirect(url_for("interview"))

# ================= INTERVIEW =================
@app.route("/interview")
def interview():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template(
        "interview.html",
        questions=session.get("questions", []),
        role=session.get("role")
    )

# ================= RESULT =================
@app.route("/result", methods=["POST"])
def result():

    questions = session.get("questions", [])
    answers = request.form

    results = []
    total = 0

    for i, q in enumerate(questions):

        ans = answers.get(f"answer{i+1}", "").strip()

        if len(ans) < 5:
            score = 0
            feedback = "Invalid answer"

        else:
            try:
                res = model.generate_content(f"""
Question: {q['question']}
Answer: {ans}

Score out of 10 + feedback
""")

                text = res.text

                match = re.search(r'(\d+)/10', text)
                score = int(match.group(1)) if match else 5
                feedback = text

            except:
                score, feedback = fallback(ans)

        total += score

        results.append({
            "question": q["question"],
            "answer": ans,
            "score": score,
            "feedback": feedback
        })

    avg = round(total / len(questions), 2) if questions else 0

    return render_template("result.html", results=results, average=avg)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)