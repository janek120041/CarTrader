# CarTrader

A modern web application for trading cars, built with Flask and Bootstrap 5.

## Features

- User authentication and profiles
- Car listings with images
- Trade proposals system
- Private messaging between users
- Real-time notifications
- User ratings and reviews
- Responsive design

## Technology Stack

- Python 3.8+
- Flask 2.0+
- SQLAlchemy
- Bootstrap 5
- SQLite (development)
- Font Awesome 5

## Installation

1. Clone the repository:
```bash
git clone https://github.com/janek120041/CarTrader2.git
cd CarTrader2
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the development server:
```bash
flask run
```

## Project Structure

```
CarTrader/
├── app/
│   ├── auth/         # Authentication views and forms
│   ├── cars/         # Car listing views and forms
│   ├── messages/     # Messaging system
│   ├── profile/      # User profile views
│   ├── static/       # Static files (CSS, JS, images)
│   ├── templates/    # Jinja2 templates
│   └── models.py     # Database models
├── migrations/       # Database migrations
├── instance/        # Instance-specific files
├── config.py        # Configuration
└── requirements.txt # Project dependencies
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask documentation and community
- Bootstrap team for the excellent UI framework
- All contributors and users of the platform
