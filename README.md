# CarTrader

CarTrader is a web platform for users to trade cars with each other. Built with Flask, SQLAlchemy, and Flask-Login.

## Features
- User registration and authentication
- Browse and filter cars
- Propose and manage car trades
- User dashboard with car and trade management

## Setup

1. Clone the repository and navigate to the project directory.
2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python run.py
   ```
5. Visit `http://127.0.0.1:5000` in your browser.

## Project Structure
- `run.py` - App entry point
- `car_trader/` - Main app package
  - `__init__.py` - App factory and extension setup
  - `models.py` - Database models
  - `routes.py` - Main routes
  - `auth.py` - Authentication routes
  - `templates/` - Jinja2 HTML templates
  - `static/` - CSS and static files

## Notes
- Replace `car_logo.png` in `static/` with your own logo for best results.
- This is a starter scaffold; you can expand features and logic as needed. 