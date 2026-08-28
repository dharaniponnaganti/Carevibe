from datetime import datetime
from bson.objectid import ObjectId
import bcrypt
from database import Database

class User:
    """User model"""
    
    @staticmethod
    def create(username, email, password, full_name=None):
        """Create a new user"""
        db = Database.get_db()
        
        # Check if user already exists
        if db.users.find_one({'email': email}):
            return None, "Email already exists"
        
        if db.users.find_one({'username': username}):
            return None, "Username already exists"
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'full_name': full_name or username,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'profile_picture': None,
            'bio': '',
            'theme': 'light'
        }
        
        result = db.users.insert_one(user_data)
        return str(result.inserted_id), "User created successfully"
    
    @staticmethod
    def authenticate(email, password):
        """Authenticate user"""
        db = Database.get_db()
        user = db.users.find_one({'email': email})
        
        if not user:
            return None, "User not found"
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return str(user['_id']), "Authentication successful"
        
        return None, "Invalid password"
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        db = Database.get_db()
        try:
            user = db.users.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                user.pop('password', None)  # Don't return password
                return user
        except:
            pass
        return None
    
    @staticmethod
    def update(user_id, **kwargs):
        """Update user information"""
        db = Database.get_db()
        try:
            update_data = {k: v for k, v in kwargs.items() if k != '_id'}
            update_data['updated_at'] = datetime.utcnow()
            
            db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return True
        except:
            return False

class CheckIn:
    """Check-in model"""
    
    @staticmethod
    def create(user_id, emotion, mood_score, notes=None, activities=None):
        """Create a new check-in"""
        db = Database.get_db()
        
        checkin_data = {
            'user_id': ObjectId(user_id),
            'emotion': emotion,
            'mood_score': mood_score,
            'notes': notes or '',
            'activities': activities or [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.checkins.insert_one(checkin_data)
        return str(result.inserted_id), "Check-in saved"
    
    @staticmethod
    def get_user_checkins(user_id, limit=30):
        """Get user's check-ins"""
        db = Database.get_db()
        try:
            checkins = list(db.checkins.find(
                {'user_id': ObjectId(user_id)}
            ).sort('created_at', -1).limit(limit))
            
            for checkin in checkins:
                checkin['_id'] = str(checkin['_id'])
                checkin['user_id'] = str(checkin['user_id'])
            
            return checkins
        except:
            return []
    
    @staticmethod
    def delete(checkin_id):
        """Delete a check-in"""
        db = Database.get_db()
        try:
            db.checkins.delete_one({'_id': ObjectId(checkin_id)})
            return True
        except:
            return False

class JournalEntry:
    """Journal entry model"""
    
    @staticmethod
    def create(user_id, title, content, mood=None):
        """Create a new journal entry"""
        db = Database.get_db()
        
        journal_data = {
            'user_id': ObjectId(user_id),
            'title': title,
            'content': content,
            'mood': mood or 'neutral',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.journals.insert_one(journal_data)
        return str(result.inserted_id), "Journal entry saved"
    
    @staticmethod
    def get_user_entries(user_id, limit=30):
        """Get user's journal entries"""
        db = Database.get_db()
        try:
            entries = list(db.journals.find(
                {'user_id': ObjectId(user_id)}
            ).sort('created_at', -1).limit(limit))
            
            for entry in entries:
                entry['_id'] = str(entry['_id'])
                entry['user_id'] = str(entry['user_id'])
            
            return entries
        except:
            return []
    
    @staticmethod
    def update(entry_id, title=None, content=None, mood=None):
        """Update journal entry"""
        db = Database.get_db()
        try:
            update_data = {'updated_at': datetime.utcnow()}
            if title:
                update_data['title'] = title
            if content:
                update_data['content'] = content
            if mood:
                update_data['mood'] = mood
            
            db.journals.update_one(
                {'_id': ObjectId(entry_id)},
                {'$set': update_data}
            )
            return True
        except:
            return False
    
    @staticmethod
    def delete(entry_id):
        """Delete journal entry"""
        db = Database.get_db()
        try:
            db.journals.delete_one({'_id': ObjectId(entry_id)})
            return True
        except:
            return False

class Goal:
    """Goal model"""
    
    @staticmethod
    def create(user_id, title, description=None, category=None, deadline=None):
        """Create a new goal"""
        db = Database.get_db()
        
        goal_data = {
            'user_id': ObjectId(user_id),
            'title': title,
            'description': description or '',
            'category': category or 'general',
            'deadline': deadline,
            'completed': False,
            'progress': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.goals.insert_one(goal_data)
        return str(result.inserted_id), "Goal created"
    
    @staticmethod
    def get_user_goals(user_id, completed=None):
        """Get user's goals"""
        db = Database.get_db()
        try:
            query = {'user_id': ObjectId(user_id)}
            if completed is not None:
                query['completed'] = completed
            
            goals = list(db.goals.find(query).sort('created_at', -1))
            
            for goal in goals:
                goal['_id'] = str(goal['_id'])
                goal['user_id'] = str(goal['user_id'])
            
            return goals
        except:
            return []
    
    @staticmethod
    def update(goal_id, progress=None, completed=None, title=None):
        """Update goal"""
        db = Database.get_db()
        try:
            update_data = {'updated_at': datetime.utcnow()}
            if progress is not None:
                update_data['progress'] = progress
            if completed is not None:
                update_data['completed'] = completed
            if title:
                update_data['title'] = title
            
            db.goals.update_one(
                {'_id': ObjectId(goal_id)},
                {'$set': update_data}
            )
            return True
        except:
            return False
    
    @staticmethod
    def delete(goal_id):
        """Delete goal"""
        db = Database.get_db()
        try:
            db.goals.delete_one({'_id': ObjectId(goal_id)})
            return True
        except:
            return False
