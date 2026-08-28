# CAREVIBE - Frontend & Backend Integration Guide

## ✅ Integration Complete!

Your CAREVIBE frontend and Flask backend are now fully connected!

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│          CAREVIBE Frontend (HTML/CSS/JS)           │
│     (smart_mha_ui_draft.html)                       │
├─────────────────────────────────────────────────────┤
│         API Calls via Fetch (localhost:5000)        │
├─────────────────────────────────────────────────────┤
│      Flask Backend (Python) - Running on Port 5000  │
│     (carevibe-backend/app.py)                       │
├─────────────────────────────────────────────────────┤
│            MongoDB Database                         │
│     (Collections: users, checkins, journals, goals) │
└─────────────────────────────────────────────────────┘
```

## Integrated Features

### 1. **Authentication** ✅
- **Register**: Create new user account
  - Endpoint: `POST /api/auth/register`
  - Fields: username, email, password, full_name
  - Returns: JWT token + user_id

- **Login**: Sign in with email/password
  - Endpoint: `POST /api/auth/login`
  - Fields: email, password
  - Returns: JWT token + user_id

- **Logout**: Clear local auth data
  - Function: `handleLogout()`
  - Clears: authToken, userId from localStorage

### 2. **Check-ins** ✅
- **Create Check-in**: Record daily mood and emotions
  - Endpoint: `POST /api/checkins`
  - Fields: emotion, mood_score, notes, activities
  - Function: `handleCheckInSubmit()`

- **Get Check-ins**: Retrieve user's check-in history
  - Endpoint: `GET /api/checkins`
  - Requires: Valid JWT token

### 3. **Journal Entries** ✅
- **Create Entry**: Write and save journal entries
  - Endpoint: `POST /api/journal`
  - Fields: title, content, mood
  - Function: `handleJournalSave()`

- **Get Entries**: Retrieve all journal entries
  - Endpoint: `GET /api/journal`

- **Update Entry**: Edit existing journal entry
  - Endpoint: `PUT /api/journal/<id>`

- **Delete Entry**: Remove a journal entry
  - Endpoint: `DELETE /api/journal/<id>`

### 4. **Goals** ✅
- **Create Goal**: Set wellness goals
  - Endpoint: `POST /api/goals`
  - Fields: title, description, category, deadline
  - Function: `handleGoalCreate()`

- **Get Goals**: Retrieve user's goals
  - Endpoint: `GET /api/goals`

- **Update Goal**: Track progress
  - Endpoint: `PUT /api/goals/<id>`

- **Delete Goal**: Remove a goal
  - Endpoint: `DELETE /api/goals/<id>`

### 5. **User Profile** ✅
- **Get Profile**: Retrieve user information
  - Endpoint: `GET /api/user/profile`

- **Update Profile**: Modify user details
  - Endpoint: `PUT /api/user/profile`

## Frontend Integration Code

### API Configuration
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
let authToken = null;
let currentUserId = null;
```

### API Call Helper
```javascript
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (authToken) {
        options.headers['Authorization'] = `Bearer ${authToken}`;
    }

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    return await response.json();
}
```

### Authentication Flow
1. User enters email and password
2. Frontend sends POST to `/api/auth/login`
3. Backend validates credentials and returns JWT token
4. Frontend stores token in localStorage
5. Token automatically included in all future requests

## Data Flow Examples

### Login Flow
```
User Input (email, password)
    ↓
handleLogin() function
    ↓
apiCall('/auth/login', 'POST', {email, password})
    ↓
Backend validates in MongoDB
    ↓
Returns JWT token
    ↓
Store in localStorage
    ↓
Access granted to other screens
```

### Check-in Flow
```
User selects emotion & mood score
    ↓
Clicks "Save Check-in & Continue"
    ↓
handleCheckInSubmit() extracts data
    ↓
apiCall('/checkins', 'POST', {...})
    ↓
Backend creates document in MongoDB
    ↓
Returns confirmation
    ↓
Switch to Chat screen
```

### Journal Entry Flow
```
User writes journal content
    ↓
Clicks "Save Entry"
    ↓
handleJournalSave() gathers data
    ↓
apiCall('/journal', 'POST', {...})
    ↓
MongoDB stores entry
    ↓
Confirmation message
```

## Running the System

### Start Backend
```bash
cd carevibe-backend
python app.py
```
Backend will run on: `http://localhost:5000`

### Open Frontend
```
Open smart_mha_ui_draft.html in a web browser
```

### Test the Integration
1. **Register**: Click "Create one" link in login screen
2. **Login**: Enter credentials to access app
3. **Check-in**: Add daily mood and emotion
4. **Journal**: Write and save entries
5. **Goals**: Create and track wellness goals
6. **Logout**: Settings → Logout button

## Storage Details

### Frontend Storage
- **localStorage Keys**:
  - `authToken`: JWT token for API authentication
  - `userId`: User's MongoDB ID
  - `darkMode`: Dark mode preference

### Backend Storage (MongoDB)
- **Collections**:
  - `users`: User accounts, profiles, passwords (hashed)
  - `checkins`: Daily mood and emotion records
  - `journals`: Journal entries with timestamps
  - `goals`: Wellness goals with progress tracking

## Security Features

✅ **Passwords**: Hashed with bcrypt (not stored in plain text)
✅ **Authentication**: JWT tokens required for protected endpoints
✅ **Authorization**: Tokens checked on every API call
✅ **CORS**: Enabled to allow frontend-backend communication
✅ **Data Validation**: Backend validates all input data

## Troubleshooting

### "Cannot reach backend" Error
- Ensure Flask backend is running: `python app.py`
- Check backend is on localhost:5000
- Verify no firewall blocking port 5000

### "Invalid token" Error
- Clear localStorage in browser dev tools
- Logout and login again
- Token may have expired (regenerate by logging in)

### "User not found" Error
- Register first before logging in
- Check email spelling
- Verify user exists in MongoDB

### MongoDB Connection Error
- Ensure MongoDB is running on localhost:27017
- Update MONGODB_URI in .env if using different host
- Check .env file has correct connection string

## API Response Format

### Success Response
```json
{
    "message": "Operation successful",
    "data": {...}
}
```

### Error Response
```json
{
    "error": true,
    "message": "Error description"
}
```

## Frontend Functions Reference

### Authentication
- `handleLogin()` - Process login form
- `handleRegister()` - Process registration
- `handleLogout()` - Clear auth and logout
- `toggleAuthMode()` - Switch between login/register forms

### Data Management
- `handleCheckInSubmit()` - Save check-in data
- `handleJournalSave()` - Save journal entry
- `handleGoalCreate()` - Create new goal

### Utilities
- `apiCall(endpoint, method, data)` - Make API requests
- `switchScreen(screenId)` - Navigate between screens
- `selectMood(element)` - Select mood emoji
- `updateMoodValue(value)` - Update mood slider display

## Next Steps

1. ✅ Test all authentication flows
2. ✅ Verify data persists in MongoDB
3. ✅ Test all CRUD operations (Create, Read, Update, Delete)
4. ✅ Add loading states to improve UX
5. ✅ Add error handling and validation
6. ✅ Deploy to production (AWS, Heroku, etc.)

## Additional Resources

- **Backend Docs**: See `carevibe-backend/README.md`
- **API Routes**: Check `carevibe-backend/routes.py`
- **Database Models**: Review `carevibe-backend/models.py`
- **Configuration**: Update `carevibe-backend/.env`

---

**Status**: ✅ Integration Complete and Ready for Testing

**Backend Running**: http://localhost:5000
**Frontend Ready**: Open smart_mha_ui_draft.html in browser
