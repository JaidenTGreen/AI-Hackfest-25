'''
Author: Jaiden Green
School: University of Kansas
Created: Friday, April 11, 2025 5:00 PM
Last Updated: Friday, April 11, 2025
Program Description:
Python file that interacts with OpenAI's API to conduct a mock interview based on a user's resume.
Inputs and reads either txt or pdf files for the resume.
Outputs a series of technical interview questions based on the resume and the target job title.
Collaborators: None
Sources: OpenAI, ChatGPT
Version: 2.0
'''

import google.generativeai as genai
import os
import time
import threading
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

# --- Load resume from .txt or .pdf ---
def load_resume(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Resume file not found.")

    if file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    else:
        raise ValueError("Unsupported file type. Use .txt or .pdf")

# --- Prompt user for resume path and job title ---
resume_path = input("Enter the path to your resume (.txt or .pdf): ").strip()
try:
    resume = load_resume(resume_path)
    print("✅ Resume loaded successfully.")
except Exception as e:
    print(f"❌ Error loading resume: {e}")
    exit()

target_job = input("Enter the target job title: ").strip()

# --- Generate Gemini questions ---
def get_questions_gemini(resume, target_job):
    prompt = f"""
You are a professional interviewer. Based on the resume below, generate 3 to 5 **numbered** and realistic **technical** interview questions for the position of **{target_job}**.

Only output the questions in this format:
1. ...
2. ...
3. ...

Resume:
{resume}
"""
    response = model.generate_content(prompt)
    lines = response.text.strip().split("\n")
    return [line.strip() for line in lines if line.strip() and line.strip()[0].isdigit()]

questions = get_questions_gemini(resume, target_job)
print("\n🧠 Here are your generated interview questions:\n")
for q in questions:
    print(q)

while True:
    regenerate = input("\n🔄 Would you like to regenerate the questions? (yes/no): ").lower().strip()
    if regenerate == "yes":
        questions = get_questions_gemini(resume, target_job)
        print("\n♻️ New Questions:\n")
        for q in questions:
            print(q)
    elif regenerate == "no":
        break
    else:
        print("Please enter 'yes' or 'no'.")

# --- Markdown log setup ---
log_path = "interview_log_gemini.md"
with open(log_path, "a", encoding="utf-8") as log_file:
    log_file.write(f"\n# Interview Simulation\n**Target Job:** {target_job}\n\n")

    for idx, q in enumerate(questions, 1):
        print(f"\n📝 Question {idx}: {q}")
        
        print("\n⏱️ You have 90 seconds to answer. Start typing:")
        answer = ""
        start_time = time.time()
        def timeout():
            print("\n⏰ Time's up! Press enter to submit your answer.")
        timer = threading.Timer(90, timeout)
        timer.start()

        try:
            answer = input()
        finally:
            timer.cancel()

        while True:
            feedback_prompt = f"""
Resume:
{resume}

Question: {q}
Answer: {answer}

Give helpful, constructive feedback on this interview answer.
"""
            print("\n💡 Feedback:")
            try:
                feedback_response = model.generate_content(feedback_prompt)
                feedback = feedback_response.text.strip()
                print(feedback)
            except Exception as e:
                print(f"❌ Error: {e}")
                break

            retry = input("🔁 Would you like to retry this answer? (yes/no): ").lower().strip()
            if retry == "no":
                break
            elif retry == "yes":
                print("\n⏱️ You have 90 seconds to answer. Start typing:")
                timer = threading.Timer(90, timeout)
                timer.start()
                try:
                    answer = input()
                finally:
                    timer.cancel()
            else:
                print("Please enter 'yes' or 'no'.")

        # Save to markdown log
        log_file.write(f"## Question {idx}\n")
        log_file.write(f"**Q:** {q}\n\n")
        log_file.write(f"**A:** {answer}\n\n")
        log_file.write(f"**💡 Feedback:** {feedback}\n\n---\n")

print(f"\n📁 Gemini session saved to: {log_path}")
