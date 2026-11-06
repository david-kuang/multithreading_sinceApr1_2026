How to Run the Application
## Install Dependencies:
Bash
pip install -r requirements.txt

## Run Unit Tests:
Bash
pytest

## Start the Web Server:
Bash
uvicorn app.main:app --reload

## Access the App:
Open http://localhost:8000 in your web browser. (Set an OPENAI_API_KEY environment 
variable for real AI interaction; otherwise, it operates using built-in simulated responses).