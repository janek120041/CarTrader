# CarTrader

A Flask-based web application for buying and selling cars. Users can create accounts, list their cars for sale, browse listings, leave comments, and send inquiries to sellers.

## Features

### Authentication System
- Secure user registration with password strength validation
- User-friendly login interface with "Remember me" functionality
- Password reset capability (coming soon)
- Profile management with user details and listing history

### Car Management
- Create, edit, and delete car listings
- Upload multiple car images with preview
- Detailed car information including make, model, year, price, and mileage
- Advanced search and filter options by category

### User Interaction
- Comments and ratings system for cars
- Direct messaging between buyers and sellers
- Trade request system for vehicle exchanges
- Email notifications for new inquiries and responses

### UI/UX Features
- Responsive design using Bootstrap 5
- Modern and intuitive interface
- Real-time password strength indicator
- Form validation with helpful error messages
- Interactive image gallery for car photos

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)
- Git (for version control)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/janek120041/CarTrader.git
cd CarTrader
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

1. Set up environment variables:
```bash
# Windows
set FLASK_APP=run.py
set FLASK_ENV=development
set SECRET_KEY=your-secret-key
set DATABASE_URL=sqlite:///cartrader.db

# macOS/Linux
export FLASK_APP=run.py
export FLASK_ENV=development
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
│   │   ├── js/
│   │   │   └── main.js
│   │   └── car_images/
│   ├── templates/
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── profile.html
│   │   ├── cars/
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   ├── list.html
│   │   │   └── view.html
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

## Security Features

- Password hashing using bcrypt
- CSRF protection on all forms
- Secure session handling
- Input validation and sanitization
- Protected file uploads
- Rate limiting on authentication attempts

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Run tests if available
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/improvement`)
7. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bootstrap 5 for the UI components
- Flask-Login for authentication
- SQLAlchemy for database management
- Pillow for image processing
- Font Awesome for icons
