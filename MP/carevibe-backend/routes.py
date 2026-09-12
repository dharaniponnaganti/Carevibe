from flask import Blueprint, request, jsonify
from database import User, CheckIn, JournalEntry, Goal, ChatMessage
import jwt
import os
from functools import wraps

api = Blueprint('api', __name__, url_prefix='/api')

# ML & Services Integration
from ml import TextEmotionAnalyzer, FaceEmotionAnalyzer, FusionEngine
from services import StabilityService, SuggestionEngine, ChatbotService

text_analyzer = TextEmotionAnalyzer()
face_analyzer = FaceEmotionAnalyzer()
fusion_engine = FusionEngine()
suggestion_engine = SuggestionEngine()
chatbot = ChatbotService()

# Secret key for JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

def token_required(f):
    """Decorator to verify JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(user_id, *args, **kwargs)
    
    return decorated

# ===== AUTH ROUTES =====

@api.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    user_id, message = User.create(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        full_name=data.get('full_name')
    )
    
    if not user_id:
        return jsonify({'message': message}), 400
    
    # Generate JWT token
    token = jwt.encode({'user_id': user_id}, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'message': message,
        'user_id': user_id,
        'token': token
    }), 201

@api.route('/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    user_id, message = User.authenticate(
        email=data['email'],
        password=data['password']
    )
    
    if not user_id:
        return jsonify({'message': message}), 401
    
    # Generate JWT token
    token = jwt.encode({'user_id': user_id}, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'message': message,
        'user_id': user_id,
        'token': token
    }), 200

# ===== USER ROUTES =====

@api.route('/user/profile', methods=['GET'])
@token_required
def get_profile(user_id):
    """Get user profile"""
    user = User.get_by_id(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(user), 200

@api.route('/user/profile', methods=['PUT'])
@token_required
def update_profile(user_id):
    """Update user profile"""
    data = request.get_json()
    
    User.update(user_id, **data)
    
    user = User.get_by_id(user_id)
    return jsonify({
        'message': 'Profile updated',
        'user': user
    }), 200

# ===== CHECK-IN ROUTES =====

@api.route('/checkins', methods=['POST'])
@token_required
def create_checkin(user_id):
    """Create a new check-in"""
    data = request.get_json()
    
    if not data.get('emotion') or data.get('mood_score') is None:
        return jsonify({'message': 'Missing emotion or mood_score'}), 400
    
    checkin_id, message = CheckIn.create(
        user_id=user_id,
        emotion=data['emotion'],
        mood_score=data['mood_score'],
        notes=data.get('notes'),
        activities=data.get('activities', [])
    )
    
    return jsonify({
        'message': message,
        'checkin_id': checkin_id
    }), 201

@api.route('/checkins', methods=['GET'])
@token_required
def get_checkins(user_id):
    """Get user's check-ins"""
    limit = request.args.get('limit', 30, type=int)
    checkins = CheckIn.get_user_checkins(user_id, limit)
    
    return jsonify({
        'checkins': checkins,
        'total': len(checkins)
    }), 200

@api.route('/checkins/<checkin_id>', methods=['DELETE'])
@token_required
def delete_checkin(user_id, checkin_id):
    """Delete a check-in"""
    if CheckIn.delete(checkin_id):
        return jsonify({'message': 'Check-in deleted'}), 200
    
    return jsonify({'message': 'Check-in not found'}), 404

# ===== JOURNAL ROUTES =====

@api.route('/journal', methods=['POST'])
@token_required
def create_journal(user_id):
    """Create a new journal entry"""
    data = request.get_json()
    
    if not data.get('title') or not data.get('content'):
        return jsonify({'message': 'Missing title or content'}), 400
    
    entry_id, message = JournalEntry.create(
        user_id=user_id,
        title=data['title'],
        content=data['content'],
        mood=data.get('mood')
    )
    
    return jsonify({
        'message': message,
        'entry_id': entry_id
    }), 201

@api.route('/journal', methods=['GET'])
@token_required
def get_journal_entries(user_id):
    """Get user's journal entries"""
    limit = request.args.get('limit', 30, type=int)
    entries = JournalEntry.get_user_entries(user_id, limit)
    
    return jsonify({
        'entries': entries,
        'total': len(entries)
    }), 200

@api.route('/journal/<entry_id>', methods=['PUT'])
@token_required
def update_journal(user_id, entry_id):
    """Update journal entry"""
    data = request.get_json()
    
    if JournalEntry.update(entry_id, **data):
        return jsonify({'message': 'Journal entry updated'}), 200
    
    return jsonify({'message': 'Journal entry not found'}), 404

@api.route('/journal/<entry_id>', methods=['DELETE'])
@token_required
def delete_journal(user_id, entry_id):
    """Delete journal entry"""
    if JournalEntry.delete(entry_id):
        return jsonify({'message': 'Journal entry deleted'}), 200
    
    return jsonify({'message': 'Journal entry not found'}), 404

# ===== GOAL ROUTES =====

@api.route('/goals', methods=['POST'])
@token_required
def create_goal(user_id):
    """Create a new goal"""
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({'message': 'Missing title'}), 400
    
    goal_id, message = Goal.create(
        user_id=user_id,
        title=data['title'],
        description=data.get('description'),
        category=data.get('category'),
        deadline=data.get('deadline')
    )
    
    return jsonify({
        'message': message,
        'goal_id': goal_id
    }), 201

@api.route('/goals', methods=['GET'])
@token_required
def get_goals(user_id):
    """Get user's goals"""
    completed = request.args.get('completed', None)
    if completed is not None:
        completed = completed.lower() == 'true'
    
    goals = Goal.get_user_goals(user_id, completed)
    
    return jsonify({
        'goals': goals,
        'total': len(goals)
    }), 200

@api.route('/goals/<goal_id>', methods=['PUT'])
@token_required
def update_goal(user_id, goal_id):
    """Update goal"""
    data = request.get_json()
    
    if Goal.update(goal_id, **data):
        return jsonify({'message': 'Goal updated'}), 200
    
    return jsonify({'message': 'Goal not found'}), 404

@api.route('/goals/<goal_id>', methods=['DELETE'])
@token_required
def delete_goal(user_id, goal_id):
    """Delete goal"""
    if Goal.delete(goal_id):
        return jsonify({'message': 'Goal deleted'}), 200
    
    return jsonify({'message': 'Goal not found'}), 404

# ===== ANALYSIS & ML ROUTES =====

@api.route('/analyze/fusion', methods=['POST'])
@token_required
def analyze_fusion(user_id):
    data = request.get_json()
    text = data.get('text', '')
    image = data.get('image', '')
    simulated_face = data.get('simulated_face', '')
    
    # 1. Text Analysis
    text_emotion = text_analyzer.analyze(text) if text else None
    
    # 2. Face Analysis
    face_emotion = None
    face_confidence = 0.0
    if simulated_face and simulated_face != 'camera':
        face_emotion = simulated_face
        face_confidence = 0.92
    elif image:
        face_result, _ = face_analyzer.analyze_base64_image(image)
        if face_result and face_result.get('face_detected'):
            face_emotion = face_result['emotion']
            face_confidence = face_result.get('confidence', 0.85)
            
    # 3. Fusion
    final_emotion, conflict, reasoning = fusion_engine.fuse_emotions(text_emotion, face_emotion)
    
    # 4. Risk Analysis & Suggestions
    risk_info = suggestion_engine.determine_risk_level(final_emotion, text)
    suggestions = suggestion_engine.generate_suggestions(final_emotion)
    
    return jsonify({
        'text_emotion': text_emotion,
        'face_emotion': face_emotion,
        'face_confidence': face_confidence,
        'final_emotion': final_emotion,
        'conflict_detected': conflict,
        'fusion_reasoning': reasoning,
        'risk_level': risk_info,
        'suggestions': suggestions
    }), 200

@api.route('/chat', methods=['POST'])
@token_required
def chat_endpoint(user_id):
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'message': 'Missing message'}), 400
        
    user_emotion = data.get('emotion', 'neutral')
    user_message = data['message']
    
    # Save the user's message to MongoDB
    ChatMessage.create(user_id, role='user', text=user_message, emotion=user_emotion)
    
    # Get Chatbot Response
    response_data = chatbot.get_response(user_message, user_emotion)
    
    # Save the chatbot's response to MongoDB
    ChatMessage.create(user_id, role='bot', text=response_data['response'], emotion=None)
    
    return jsonify(response_data), 200

@api.route('/chat/history', methods=['GET'])
@token_required
def get_chat_history(user_id):
    """Retrieve chat history for the user."""
    limit = request.args.get('limit', 50, type=int)
    messages = ChatMessage.get_history(user_id, limit=limit)
    return jsonify({'messages': messages}), 200

@api.route('/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(user_id):
    """Single Source of Truth Dashboard Statistics API"""
    try:
        from database import get_db
        db = get_db()
        from bson.objectid import ObjectId
        from datetime import datetime, timedelta
        
        # Safe ObjectId conversion for user query matching
        obj_user_id = None
        try:
            obj_user_id = ObjectId(user_id)
        except:
            pass
            
        user_query = {'$or': [{'user_id': obj_user_id}, {'user_id': str(user_id)}]} if obj_user_id else {'user_id': str(user_id)}
        
        checkins = CheckIn.get_user_checkins(user_id, limit=100)
        chat_history = ChatMessage.get_history(user_id, limit=100)
        
        total_checkins = db.checkins.count_documents(user_query)
        journal_entries = db.journals.count_documents(user_query)
        chat_messages_count = db.chat_messages.count_documents({'$and': [user_query, {'role': 'user'}]})
        
        # Goals count
        user_goals = Goal.get_user_goals(user_id)
        total_goals = len(user_goals)
        goals_completed = sum(1 for g in user_goals if g.get('completed'))
        
        # Stability score calculation
        score = StabilityService.calculate_stability(checkins, chat_messages=chat_history)
        
        # Calculate improvement percentage
        improvement_pct = 0
        if len(checkins) >= 2:
            recent_avg = sum(c.get('mood_score', 5) for c in checkins[:len(checkins)//2]) / (len(checkins)//2)
            older_avg = sum(c.get('mood_score', 5) for c in checkins[len(checkins)//2:]) / (len(checkins) - len(checkins)//2)
            if older_avg > 0:
                improvement_pct = round(((recent_avg - older_avg) / older_avg) * 100)
        
        # Get latest emotion from checkin or chat
        latest_emotion = "Neutral"
        if checkins:
            latest_emotion = checkins[0].get('emotion', 'Neutral')
        elif chat_history:
            latest_emotion = chat_history[-1].get('emotion', 'Neutral')
            
        # ----------------------------------------------------
        # CALENDAR DATE STREAK CALCULATION (YYYY-MM-DD)
        # ----------------------------------------------------
        tz_offset_min = 0
        try:
            tz_header = request.headers.get('X-Client-Offset')
            if tz_header is not None:
                tz_offset_min = int(tz_header)
        except:
            pass

        activity_dates = set()
        
        def add_date(d_val):
            if not d_val:
                return
            dt_obj = None
            if isinstance(d_val, datetime):
                dt_obj = d_val - timedelta(minutes=tz_offset_min)
            elif isinstance(d_val, str):
                try:
                    clean_str = d_val.replace('Z', '').split('.')[0]
                    dt_obj = datetime.fromisoformat(clean_str) - timedelta(minutes=tz_offset_min)
                except:
                    if len(d_val) >= 10 and d_val[4] == '-' and d_val[7] == '-':
                        activity_dates.add(d_val[:10])
                        return
            if dt_obj:
                activity_dates.add(dt_obj.strftime('%Y-%m-%d'))

        for c in checkins:
            add_date(c.get('created_at'))
        for msg in chat_history:
            add_date(msg.get('timestamp') or msg.get('created_at'))
            
        try:
            journal_docs = list(db.journals.find(user_query))
            for j in journal_docs:
                add_date(j.get('created_at'))
        except:
            pass

        try:
            goal_docs = list(db.goals.find(user_query))
            for g in goal_docs:
                add_date(g.get('created_at'))
        except:
            pass

        # Sort dates in descending order (most recent first)
        sorted_dates = sorted([datetime.strptime(d, '%Y-%m-%d').date() for d in activity_dates], reverse=True)
        
        streak = 0
        if sorted_dates:
            # Client date header or default to UTC date
            client_date_str = request.headers.get('X-Client-Date')
            today = None
            if client_date_str:
                try:
                    today = datetime.strptime(client_date_str[:10], '%Y-%m-%d').date()
                except:
                    pass
            if not today:
                today = datetime.utcnow().date()
                
            yesterday = today - timedelta(days=1)
            
            # If latest activity is today or yesterday, streak is active
            if sorted_dates[0] in (today, yesterday):
                streak = 1
                curr = sorted_dates[0]
                for d in sorted_dates[1:]:
                    diff = (curr - d).days
                    if diff == 1:
                        streak += 1
                        curr = d
                    elif diff == 0:
                        continue # Same calendar date activity -> skip without double counting
                    else:
                        break # Gap in consecutive days -> stop counting
            else:
                streak = 0
            
        # Avg Mood calculation
        avg_mood = "--"
        if checkins:
            moods = [c.get('mood_score') for c in checkins if c.get('mood_score') is not None]
            if moods:
                avg_mood = round(sum(moods) / len(moods), 1)

        # Emotion Frequency calculation (Last 30 Days)
        emotion_counts = {'happy': 0, 'calm': 0, 'neutral': 0, 'fearful': 0, 'sad': 0, 'angry': 0, 'surprised': 0}
        total_emotions = 0
        for c in checkins:
            em = (c.get('emotion') or '').lower()
            if em in emotion_counts:
                emotion_counts[em] += 1
                total_emotions += 1
        for msg in chat_history:
            em = (msg.get('emotion') or '').lower()
            if em in emotion_counts:
                emotion_counts[em] += 1
                total_emotions += 1

        emotion_freq = {}
        for em, cnt in emotion_counts.items():
            pct = round((cnt / total_emotions) * 100) if total_emotions > 0 else 0
            emotion_freq[em] = pct
            
        return jsonify({
            'streak': streak,
            'streak_count': streak,
            'total_checkins': total_checkins,
            'journal_entries': journal_entries,
            'activities_count': journal_entries,
            'goals_completed': goals_completed,
            'total_goals': total_goals,
            'chat_sessions_count': chat_messages_count,
            'latest_emotion': latest_emotion,
            'stability_score': score,
            'improvement_pct': improvement_pct,
            'avg_mood': avg_mood,
            'emotion_freq': emotion_freq
        }), 200
    except Exception as e:
        print(f"Error in get_dashboard_stats: {e}")
        return jsonify({
            'streak': 0,
            'streak_count': 0,
            'total_checkins': 0,
            'journal_entries': 0,
            'activities_count': 0,
            'goals_completed': 0,
            'total_goals': 0,
            'chat_sessions_count': 0,
            'latest_emotion': 'Neutral',
            'stability_score': 50,
            'improvement_pct': 0,
            'avg_mood': '--',
            'emotion_freq': {'happy': 0, 'calm': 0, 'neutral': 0, 'fearful': 0, 'sad': 0}
        }), 200

@api.route('/dashboard/stability', methods=['GET'])
@token_required
def get_stability(user_id):
    return get_dashboard_stats(user_id)

# ===== HEALTH CHECK =====

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'CAREVIBE Backend'
    }), 200
