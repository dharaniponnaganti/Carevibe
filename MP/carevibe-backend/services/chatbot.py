import os
import google.generativeai as genai

class ChatbotService:
    """
    Adaptive chatbot that adjusts responses according to the user's emotional state.
    """
    
    def __init__(self):
        # Keep mock responses as a fallback
        self.mock_responses = {
            'happy': [
                "That's wonderful to hear! I'm glad you're feeling good.",
                "It sounds like you're having a great time. Let's keep this positive energy going!",
                "Amazing! Celebrate these good moments, they're important."
            ],
            'sad': [
                "I'm sorry you're feeling down. I'm here to listen if you want to talk about it.",
                "It's completely okay to feel sad sometimes. Be gentle with yourself today.",
                "I hear you. If things get too heavy, maybe try one of the breathing exercises in the suggestions pane?"
            ],
            'angry': [
                "It's understandable to feel frustrated. Take a deep breath.",
                "Anger can be an overwhelming emotion. Would you like to try writing down exactly what's bothering you?",
                "I sense your frustration. Sometimes a quick physical activity helps clear the mind."
            ],
            'fearful': [
                "It's perfectly natural to feel anxious. Try to focus on the present moment.",
                "You are safe here. Let's try to ground ourselves using the 5-4-3-2-1 technique.",
                "Fear can feel paralyzing. Take a slow, deep breath in... and exhale slowly."
            ],
            'surprised': [
                "Wow, that sounds unexpected! How are you processing that?",
                "Life is full of surprises. Are you feeling okay about it?"
            ],
            'neutral': [
                "I'm here whenever you need me. How can I help you today?",
                "Just checking in. What's on your mind?",
                "Sometimes a calm day is exactly what we need."
            ]
        }
        
        # Load API key from environment variable
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.has_gemini = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.has_gemini = True
                print("[Chatbot] Gemini API initialized successfully.")
            except Exception as e:
                print(f"[Chatbot] Gemini initialization failed: {e}. Falling back to mock responses.")

    def get_response(self, user_message, user_emotion='neutral', history=None):
        import random
        emotion = user_emotion.lower() if user_emotion else 'neutral'
        
        # Parse history to find previous emotions
        prev_emotions = []
        if history:
            for msg in reversed(history):
                # only consider user messages or system messages that explicitly define emotion
                if msg.get('role') == 'user' or '(System:' in msg.get('text', ''):
                    if msg.get('emotion'):
                        prev_emotions.append(msg.get('emotion').lower())
        
        last_emotion = prev_emotions[-1] if prev_emotions else None
        is_system = "(System:" in user_message
        
        if is_system:
            if emotion == 'happy':
                if last_emotion in ['sad', 'fearful', 'angry']:
                    reply = "I'm so glad to see a smile on your face now! It looks like you're feeling much better."
                else:
                    reply = "You look really happy right now! It's great to see you smiling. What's making you feel so good?"
            elif emotion == 'sad':
                if last_emotion == 'happy':
                    reply = "Your expression just shifted, and you seem a bit down now. Did something just happen to upset you?"
                else:
                    reply = "I can see from your face that you might be feeling sad or down. I'm here for you. Do you want to talk about it?"
            elif emotion == 'angry':
                reply = "You look quite tense or frustrated. Remember to take a deep breath. Is there something bothering you?"
            elif emotion == 'fearful':
                reply = "You seem a little anxious or scared. You're in a safe space here. Would you like to try a grounding exercise?"
            elif emotion == 'surprised':
                reply = "You look surprised! Did something unexpected just happen?"
            else:
                reply = "I'm analyzing your facial expression, and you seem quite calm and neutral. How is your day going so far?"
        else:
            text = user_message.lower()
            if 'thank' in text:
                reply = "You're very welcome! I'm always here to help."
            elif 'bye' in text or 'goodnight' in text:
                reply = "Take care! Remember I'm here whenever you need support."
            elif emotion == 'sad' or any(w in text for w in ['sad', 'down', 'depressed']):
                if last_emotion == 'happy':
                    reply = "You were feeling good earlier, but it sounds like you're down now. I'm sorry you're feeling this way. Would you like some suggestions for self-care?"
                else:
                    reply = random.choice(self.mock_responses.get('sad', self.mock_responses['neutral']))
            elif emotion == 'happy' or any(w in text for w in ['great', 'good', 'happy']):
                reply = random.choice(self.mock_responses.get('happy', self.mock_responses['neutral']))
            elif emotion == 'angry':
                reply = random.choice(self.mock_responses.get('angry', self.mock_responses['neutral']))
            elif emotion == 'fearful':
                reply = random.choice(self.mock_responses.get('fearful', self.mock_responses['neutral']))
            else:
                reply = random.choice(self.mock_responses.get(emotion, self.mock_responses['neutral']))
                
        return {
            "response": reply,
            "detected_state_applied": emotion,
            "source": "local_heuristic"
        }
