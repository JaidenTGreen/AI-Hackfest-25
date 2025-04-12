# AI-Hackfest-25
### My project for AI Hackfest 2025; a digital hackathon centered around Artificial Intelligence.

The idea behind my project is to have a website that users could upload their resume and preferred field in computer science
AI would respond with a few interview questions, and would give feedback on the responses.
I have a very limited grasp on AI (A few failed projects) so I would like to see what I can learn and implement this weekend!

# DevLog
## Friday April 11th
### 2:30pm:
Started the project at 10AM, spent a few hours getting comfortable and finding a path I wanted to fallow to develop my project.
I was going to use Gemini API, but I ran into too many bugs to continue.
I decided to pay for an OpenAI key to use ChatGPT4.
Recently, I got my python code to run ChatGPT4 through the API and included dotenv and venv to protect my API key.

![Image](https://github.com/user-attachments/assets/d4b4e8f8-a565-443f-8f85-c97494cc6f72)

### 11:00pm:
I included a PDF reader into the python file for OpenAI, where it works locally in the same file.
Also added a job choice input abd interview set-up queries. 
Chat logs are now saved in a text file to review past queries. 
Added a regenerative question and redo question option to inputs, and logs now store in a markdown file.
For the OpenAi model, I added a timer and implemented streaming feedback to the API. 
Converted the code to work in Gemini AI after some debugging. Implemeneted areas of improvement to the user based on their resume and job interest (potential projects, certifications, etc). 
I then started focusing on the frontend where I made an app.py file which implemented flask to better translate the API to my new html files (index and interview), I also addea a css file to add some style.

![Image](https://github.com/user-attachments/assets/e9e5f434-83de-4888-ba15-1e8fe183b1ca)

