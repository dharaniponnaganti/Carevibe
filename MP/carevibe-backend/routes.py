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
    
    # 1. Text Analysis
    text_emotion = text_analyzer.analyze(text) if text else None
    
    # 2. Face Analysis
    face_emotion = None
    if image:
        face_result, _ = face_analyzer.analyze_base64_image(image)
        if face_result:
            face_emotion = face_result['emotion']
            
    # 3. Fusion
    final_emotion, conflict, reasoning = fusion_engine.fuse_emotions(text_emotion, face_emotion)
    
    # 4. Risk Analysis & Suggestions
    risk_info = suggestion_engine.determine_risk_level(final_emotion, text)
    suggestions = suggestion_engine.generate_suggestions(final_emotion)
    
    return jsonify({
        'text_emotion': text_emotion,
        'face_emotion': face_emotion,
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

@api.route('/dashboard/stability', methods=['GET'])
@token_required
def get_stability(user_id):
    checkins = CheckIn.get_user_checkins(user_id, limit=14) # Last 14 checkins
    chat_history = ChatMessage.get_history(user_id, limit=20) # Recent chat emotion inferences
    score = StabilityService.calculate_stability(checkins, chat_messages=chat_history)
    
    # Get latest emotion from checkin or chat
    latest_emotion = "Neutral"
    if checkins and chat_history:
        if checkins[0]['created_at'].isoformat() > chat_history[-1]['timestamp']:
            latest_emotion = checkins[0].get('emotion', 'Neutral')
        else:
            latest_emotion = chat_history[-1].get('emotion', 'Neutral')
    elif checkins:
        latest_emotion = checkins[0].get('emotion', 'Neutral')
    elif chat_history:
        latest_emotion = chat_history[-1].get('emotion', 'Neutral')
        
    return jsonify({'stability_score': score, 'latest_emotion': latest_emotion}), 200

# ===== HEALTH CHECK =====

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'CAREVIBE Backend'
    }), 200
