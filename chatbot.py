'''
Author: Jaiden Green
School: University of Kansas
Created: Friday, April 11, 2025 11:30 AM
Last Updated: Friday, April 11, 2025 5:00 PM
Program Description:
Python file that interacts with OpenAI's API to conduct a mock interview based on a user's resume.
Inputs and reads either txt or pdf files for the resume.
Outputs a series of technical interview questions based on the resume and the target job title.
Collaborators: None
Sources: OpenAI, ChatGPT
Version: 1.0.3
'''
import openai
import os
import time
import threading
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        raise ValueError("Unsupported file type. Use a .txt or .pdf file.")

# --- Prompt user for resume path and job title ---
resume_path = input("Enter the path to your resume (.txt or .pdf): ").strip()
try:
    resume = load_resume(resume_path)
    print("✅ Resume loaded successfully.")
except Exception as e:
    print(f"❌ Error loading resume: {e}")
    exit()

target_job = input("Enter the target job title: ").strip()

# --- Generate questions with retry option ---
def get_interview_questions(resume, target_job):
    question_prompt = f"""
You are a professional interviewer. Based on the resume below, generate 3 to 5 **numbered** and realistic **technical** interview questions for the position of **{target_job}**.

Only output the questions in this format:
1. ...
2. ...
3. ...

Resume:
{resume}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question_prompt}
        ]
    )
    raw = response.choices[0].message.content.strip().split("\n")
    questions = [line.strip() for line in raw if line.strip() and any(char.isdigit() for char in line[:3])]
    return questions

questions = get_interview_questions(resume, target_job)
print("\n🧠 Here are your generated interview questions:\n")
for q in questions:
    print(q)

while True:
    regenerate = input("\n🔄 Would you like to regenerate the questions? (yes/no): ").lower().strip()
    if regenerate == "yes":
        questions = get_interview_questions(resume, target_job)
        print("\n♻️ New Questions:\n")
        for q in questions:
            print(q)
    elif regenerate == "no":
        break
    else:
        print("Please enter 'yes' or 'no'.")

# --- Markdown log setup ---
log_path = "interview_log.md"
with open(log_path, "a", encoding="utf-8") as log_file:
    log_file.write(f"\n# Interview Simulation\n**Target Job:** {target_job}\n\n")

    for idx, q in enumerate(questions, 1):
        print(f"\n📝 Question {idx}: {q}")
        
        # Timer logic: 90 seconds to answer
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
            print("\n💡 Generating feedback (streaming)...")
            print("Feedback:", end=" ", flush=True)
            feedback = ""
            try:
                stream = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "user", "content": f"""
Resume:
{resume}

Question: {q}
Answer: {answer}

Give helpful, constructive feedback on this interview answer.
"""}
                    ],
                    stream=True
                )

                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        print(delta.content, end="", flush=True)
                        feedback += delta.content
            except Exception as e:
                print(f"\n❌ Error streaming feedback: {e}")
                break

            print("\n")
            retry = input("🔁 Would you like to retry this answer? (yes/no): ").lower().strip()
            if retry == "no":
                break
            elif retry == "yes":
                print("\n⏱️ You have 90 seconds to answer. Start typing:")
                answer = ""
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

print(f"\n📁 Session saved to: {log_path}")
print("✅ All done! Good luck with your interview preparation!")

# --- End of File ---
