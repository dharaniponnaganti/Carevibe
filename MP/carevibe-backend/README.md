# CAREVIBE Backend

A Flask-based REST API backend for the CAREVIBE mental health assistant application with MongoDB integration.

## Features

- User authentication (registration & login) with JWT tokens
- User profile management
- Check-in tracking (emotions, mood scores, activities)
- Journal entry management
- Goal tracking and progress monitoring
- MongoDB database integration
- CORS support for frontend integration
- Secure password hashing with bcrypt

## Project Structure

```
carevibe-backend/
├── app.py              # Flask application factory
├── config.py           # Configuration management
├── database.py         # MongoDB connection manager
├── models.py           # Database models (User, CheckIn, Journal, Goal)
├── routes.py           # API endpoints
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Requirements

- Python 3.8+
- MongoDB 4.0+
- pip (Python package manager)

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create .env file:**
```bash
cp .env.example .env
```

3. **Update .env with your configuration:**
```
FLASK_APP=app.py
FLASK_ENV=development
MONGODB_URI=mongodb://localhost:27017/carevibe
SECRET_KEY=your_secret_key_here
DEBUG=True
```

## Running the Backend

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user

### User
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile

### Check-ins
- `POST /api/checkins` - Create a new check-in
- `GET /api/checkins` - Get user's check-ins
- `DELETE /api/checkins/<id>` - Delete a check-in

### Journal
- `POST /api/journal` - Create journal entry
- `GET /api/journal` - Get journal entries
- `PUT /api/journal/<id>` - Update journal entry
- `DELETE /api/journal/<id>` - Delete journal entry

### Goals
- `POST /api/goals` - Create a new goal
- `GET /api/goals` - Get user's goals
- `PUT /api/goals/<id>` - Update goal
- `DELETE /api/goals/<id>` - Delete goal

### Health
- `GET /api/health` - Health check

## Authentication

Include JWT token in request headers:
```
Authorization: Bearer <token>
```

## Database Models

### User
- username (unique)
- email (unique)
- password (hashed)
- full_name
- profile_picture
- bio
- theme
- created_at
- updated_at

### CheckIn
- user_id
- emotion
- mood_score
- notes
- activities
- created_at
- updated_at

### JournalEntry
- user_id
- title
- content
- mood
- created_at
- updated_at

### Goal
- user_id
- title
- description
- category
- deadline
- completed
- progress
- created_at
- updated_at

## CORS Configuration

The API is configured to accept requests from all origins. Update CORS settings in `app.py` for production:

```python
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

## Development

### Using Flask Debug Mode
The application automatically enables debug mode in development:
```bash
FLASK_ENV=development python app.py
```

### Testing
Create test files and run:
```bash
python -m pytest tests/
```

## Deployment

For production deployment:

1. Set `FLASK_ENV=production`
2. Use a production WSGI server (e.g., Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Update SECRET_KEY in .env
4. Configure MongoDB for production
5. Restrict CORS origins

## License

MIT License
