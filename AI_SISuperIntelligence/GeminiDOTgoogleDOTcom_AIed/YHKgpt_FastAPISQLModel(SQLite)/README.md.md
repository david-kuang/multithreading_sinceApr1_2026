# Production-Ready ChatGPT-like Web App

A complete, lightweight, production-ready full-stack ChatGPT clone built with **FastAPI**, **SQLModel (SQLite)**, and a vanilla JavaScript frontend styled similarly to ChatGPT.

## Project Structure

- `database.py`: Database configuration, SQLite engine, and SQLModel schemas (`Conversation`, `Message`).
- `main.py`: FastAPI application endpoints, dependency injection, and complete error handling.
- `static/index.html`: Modern, responsive single-page chat interface.
- `requirements.txt`: Python package dependencies.
- `test_main.py`: Comprehensive test suite using `pytest`.

## Setup and Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   
## Run the application using Uvicon and Browse

1. Run the application using Uvicon:
   ```Bash
   uvicon main:app --reload
   
2. Open your browser and navigate to http://127.0.0.1:8000

## Bash pytest
pytest test_main.py -v