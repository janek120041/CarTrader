# CarTrader

A Flask-based web application for buying and selling cars. Users can create accounts, list their cars for sale, browse listings, leave comments, and send inquiries to sellers.

## Features

- User authentication (register, login, profile management)
- Car listings with images and detailed information
- Search and filter cars by category
- Comments and ratings system
- Inquiry system for buyer-seller communication
- Responsive design using Bootstrap 5

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CarTraderAPP
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create necessary directories:
```bash
mkdir -p app/static/car_images
```

## Configuration

1. Set up environment variables (optional):
```bash
# Windows
set SECRET_KEY=your-secret-key
set DATABASE_URL=sqlite:///cartrader.db

# macOS/Linux
export SECRET_KEY=your-secret-key
export DATABASE_URL=sqlite:///cartrader.db
```

2. Initialize the database:
```python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
```

## Running the Application

1. Start the development server:
```bash
python run.py
```

2. Open a web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
CarTraderAPP/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── core.css
│   │   └── car_images/
│   ├── templates/
│   │   ├── auth/
│   │   ├── cars/
│   │   └── base.html
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── cars.py
│   │   └── main.py
│   ├── __init__.py
│   └── models.py
├── venv/
├── config.py
├── requirements.txt
├── run.py
└── README.md
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
