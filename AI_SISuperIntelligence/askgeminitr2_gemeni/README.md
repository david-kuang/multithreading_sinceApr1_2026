try3viaGEMINI/
│
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_app.py
│
├── requirements.txt
└── README.md

Setup Instructions
Clone or create the project folder with the exact structure shown above.
Create and activate a virtual environment:
Bash
python -m venv .venv

# On Windows (Command Prompt):
.venv\Scripts\activate.bat
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt
Starting the Server
Run the FastAPI development server using uvicorn:
Bash
uvicorn app.main:app --reload
Once started, the application will run locally at [http://127.0.0.1:8000](http://127.0.0.1:8000).

How to Browse & Test API Endpoints
Interactive Swagger UI: Open your browser and navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test registration, session creation, and query submission interactively.

Alternative Redoc Documentation: Visit [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

Running Unit Tests
Execute the entire test suite using pytest as a module:
Bash
python -m pytest -v