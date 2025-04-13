'''
Author: Jaiden Green
School: University of Kansas
Created: Friday, April 11, 2025 6:45 PM
Last Updated: Friday, April 12, 2025 11:00 PM
Program Description:
Python file that interacts with OpenAI's API to conduct a mock interview based on a user's resume.
Inputs and reads either txt or pdf files for the resume.
Outputs a series of technical interview questions based on the resume and the target job title.
Collaborators: None
Sources: OpenAI, ChatGPT
'''
from flask import Flask, render_template, request, redirect, session, url_for
from flask_session import Session
import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import markdown

# === Setup ===
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
app.secret_key = "supersecretkey"

# === Enable server-side session storage ===
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["UPLOAD_FOLDER"] = "uploads"
Session(app)

ALLOWED_EXTENSIONS = {"pdf", "txt"}
model = genai.GenerativeModel("gemini-2.0-flash")


# === Utils ===
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath):
    if filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    elif filepath.endswith(".pdf"):
        reader = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return ""

def generate_questions(resume_text, job_title):
    prompt = f"""
You are a professional interviewer. Based on the resume below, generate 3 to 5 **numbered** and realistic **technical** interview questions for the position of **{job_title}**.

Only output the questions in this format:
1. ...
2. ...
3. ...

Resume:
{resume_text}
"""
    response = model.generate_content(prompt)
    lines = response.text.strip().split("\n")
    return [line.strip() for line in lines if line.strip() and line.strip()[0].isdigit()]

def analyze_resume(resume_text, job_title):
    prompt = f"""
You are a senior technical career coach.

The candidate has applied for the role: "{job_title}". Below is their resume.

Your job is to always offer helpful feedback — even if the resume is strong. If the candidate looks qualified, say so, but ALWAYS include concrete suggestions for improvement.

Do NOT return "None", "N/A", or say there is nothing to improve.

Format your response like this:
1. Missing or Weak Technical Skills
2. Areas to Improve Based on Current Experience
3. Suggested Next Steps
4. Optional: Project or Course Recommendations

Resume:
{resume_text}
"""
    response = model.generate_content(prompt)
    return markdown.markdown(response.text.strip())

def get_feedback(question, answer):
    prompt = f"""
Question: {question}
Answer: {answer}

Provide helpful, constructive feedback on this interview answer.
"""
    response = model.generate_content(prompt)
    return markdown.markdown(response.text.strip())


# === Routes ===
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        job_title = request.form.get("job_title")
        resume_file = request.files.get("resume")

        if not resume_file or not allowed_file(resume_file.filename):
            return "❌ Please upload a valid .txt or .pdf resume."

        filename = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
        resume_file.save(filename)

        resume_text = extract_text_from_file(filename)
        print("📄 DEBUG: Resume Text Snippet:", resume_text[:500])

        gap_analysis = analyze_resume(resume_text, job_title)
        print("📊 GAP ANALYSIS RAW RESPONSE:", repr(gap_analysis))
        if not gap_analysis.strip() or gap_analysis.strip().lower() == "none":
            gap_analysis = (
                "✅ Your resume looks strong overall. That said, here are some areas to consider improving:\n"
                "- Add more metrics and impact to your project descriptions\n"
                "- Explore open-source contributions in your domain\n"
                "- Expand skills in adjacent technologies (e.g., system design, cloud deployment)\n"
                "- Consider polishing formatting for scannability\n"
            )

        questions = generate_questions(resume_text, job_title)

        session["job_title"] = job_title
        session["resume_text"] = resume_text
        session["gap_analysis"] = gap_analysis
        session["questions"] = questions
        session["answers"] = []
        session["feedbacks"] = []
        session["index"] = 0

        return redirect(url_for("interview"))

    return render_template("index.html")

@app.route("/interview", methods=["GET", "POST"])
def interview():
    if request.method == "POST":
        if "regenerate" in request.form:
            resume_text = session.get("resume_text")
            job_title = session.get("job_title")
            questions = generate_questions(resume_text, job_title)
            session["questions"] = questions
            return redirect(url_for("interview"))

        elif "start" in request.form:
            session["index"] = 0
            session["answers"] = []
            session["feedbacks"] = []
            return redirect(url_for("question"))

    return render_template("interview.html",
                           job_title=session.get("job_title"),
                           gap_analysis=session.get("gap_analysis"),
                           questions=session.get("questions"))

@app.route("/question", methods=["GET", "POST"])
def question():
    index = session.get("index", 0)
    questions = session.get("questions", [])

    if index >= len(questions):
        return redirect(url_for("results"))
    
    current_question = questions[index]
    feedback = None
    answer = ""

    if request.method == "POST":
        if "redo" in request.form:
            # Go back to this question with previous answer
            answer_list = session.get("answers", [])
            answer = answer_list[index] if index < len(answer_list) else ""
            return render_template("question.html", question=current_question, index=index,
                                   answer=answer, feedback=None, timer=90)

        elif "continue" in request.form:
            # Move to next question
            session["index"] = index + 1
            return redirect(url_for("question"))

        elif "submit" in request.form:
            # First submission of answer
            user_answer = request.form.get("answer", "").strip()

            if not user_answer:
                return render_template("question.html", question=current_question, index=index,
                                       answer="", feedback=None, timer=90)

            feedback = get_feedback(current_question, user_answer)

            # Save answer + feedback
            answers = session.get("answers", [])
            feedbacks = session.get("feedbacks", [])

            if len(answers) > index:
                answers[index] = user_answer
                feedbacks[index] = feedback
            else:
                answers.append(user_answer)
                feedbacks.append(feedback)

            session["answers"] = answers
            session["feedbacks"] = feedbacks

            return render_template("question.html", question=current_question, index=index,
                                   answer=user_answer, feedback=feedback, timer=90)

    # Initial load
    return render_template("question.html", question=current_question, index=index,
                           answer=answer, feedback=None, timer=90)

@app.route("/results")
def results():
    return render_template("results.html",
                           job_title=session.get("job_title"),
                           questions=session.get("questions"),
                           answers=session.get("answers"),
                           feedbacks=session.get("feedbacks"),
                           zip=zip)

os.makedirs("uploads", exist_ok=True)

