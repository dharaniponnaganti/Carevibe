import os
import random
import google.generativeai as genai

class ChatbotService:
    """
    Emotion-aware & Intent-driven Chatbot Service.
    Supports 6 intents:
      - emotional_support
      - music_recommendation
      - game_recommendation
      - relaxation_activity
      - greeting
      - general_conversation
    Integrates Gemini AI with robust local fallback logic.
    """
    
    def __init__(self):
        # Curated music dataset with verified links and mood categories
        self.music_database = {
            'happy': [
                {"song": "Happy", "artist": "Pharrell Williams", "mood": "Upbeat / Happy", "url": "https://www.youtube.com/results?search_query=Happy+Pharrell+Williams+Official"},
                {"song": "Can't Stop the Feeling!", "artist": "Justin Timberlake", "mood": "Energetic", "url": "https://www.youtube.com/results?search_query=Can't+Stop+the+Feeling+Justin+Timberlake"},
                {"song": "Good as Hell", "artist": "Lizzo", "mood": "Uplifting", "url": "https://www.youtube.com/results?search_query=Good+as+Hell+Lizzo"}
            ],
            'sad': [
                {"song": "Weightless", "artist": "Marconi Union", "mood": "Calming / Anti-Anxiety", "url": "https://www.youtube.com/results?search_query=Weightless+Marconi+Union"},
                {"song": "Someone Like You", "artist": "Adele", "mood": "Soothing", "url": "https://www.youtube.com/results?search_query=Someone+Like+You+Adele"},
                {"song": "Fix You", "artist": "Coldplay", "mood": "Comforting", "url": "https://www.youtube.com/results?search_query=Fix+You+Coldplay"}
            ],
            'angry': [
                {"song": "Breathe", "artist": "The Prodigy", "mood": "Release / Cathartic", "url": "https://www.youtube.com/results?search_query=Breathe+The+Prodigy"},
                {"song": "Peaceful Piano Mix", "artist": "Spotify / Relaxing", "mood": "De-stress", "url": "https://www.youtube.com/results?search_query=Peaceful+Piano+Relaxing+Music"}
            ],
            'fearful': [
                {"song": "Ocean Waves & Soft Piano", "artist": "Nature Sounds", "mood": "Grounding", "url": "https://www.youtube.com/results?search_query=Ocean+Waves+Soft+Piano+Meditation"},
                {"song": "432Hz Miracle Tone", "artist": "Meditation Ambient", "mood": "Deep Relaxation", "url": "https://www.youtube.com/results?search_query=432Hz+Miracle+Tone+Meditation"}
            ],
            'relaxing': [
                {"song": "Weightless Ambient", "artist": "Marconi Union", "mood": "Relaxing", "url": "https://www.youtube.com/results?search_query=Weightless+Marconi+Union"},
                {"song": "Rain Sounds for Sleep & Focus", "artist": "Ambient Nature", "mood": "Peaceful", "url": "https://www.youtube.com/results?search_query=Rain+Sounds+for+Sleep+and+Focus"}
            ],
            'general': [
                {"song": "Sunshine & Good Vibes", "artist": "Chillout Beats", "mood": "General Mix", "url": "https://www.youtube.com/results?search_query=Chillout+Beats+Positive+Vibes"},
                {"song": "Lofi Hip Hop Radio - Beats to Relax/Study", "artist": "Lofi Girl", "mood": "Chill", "url": "https://www.youtube.com/results?search_query=Lofi+Girl+Radio"}
            ]
        }

        # Activity & Games Database
        self.games_database = [
            {"title": "Guided 4-7-8 Breathing", "type": "relaxation_activity", "desc": "Inhale 4s, hold 7s, exhale 8s. Resets your nervous system.", "action": "breathing"},
            {"title": "Mindfulness Zen Bubble Pop", "type": "mindfulness_game", "desc": "Focus on popping soothing floating bubbles to quiet your thoughts.", "action": "zen_bubbles"},
            {"title": "5-4-3-2-1 Sensory Grounding", "type": "relaxation_activity", "desc": "Identify 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste.", "action": "grounding"},
            {"title": "Quick Reaction & Focus Trainer", "type": "reaction_game", "desc": "Test your mental focus and clear distractions.", "action": "reaction"}
        ]

        # Emotion-specific supportive suggestions (non-diagnostic)
        self.emotion_responses = {
            'sad': [
                "I hear you, and it is completely okay to feel sad sometimes. Be gentle with yourself today.",
                "I'm sorry you're feeling down. Would you like to try a soothing 4-7-8 breathing exercise or listen to relaxing music?",
                "It's valid to feel this way. Remember to take things one small step at a time."
            ],
            'fearful': [
                "It sounds like you're feeling anxious or worried. Let's take a slow, deep breath together.",
                "Anxiety can feel overwhelming, but you are safe right now. Try the 5-4-3-2-1 grounding technique.",
                "Take a pause. Focus on your breath and let your shoulders drop."
            ],
            'angry': [
                "It is understandable to feel frustrated or angry. Taking a brief break can help cool things down.",
                "Anger is a natural emotion. Try writing down what's on your mind or doing a quick physical stretch.",
                "Let's channel that energy out. Deep breaths or a short walk can help reset your focus."
            ],
            'happy': [
                "I'm so glad to hear you're feeling good! Celebrate these positive moments.",
                "That's wonderful energy! What made your day so special?",
                "Awesome! Keep that momentum going."
            ],
            'surprised': [
                "Life is full of unexpected turns! Take a moment to process what happened.",
                "Wow, that sounds surprising! How are you feeling about it?"
            ],
            'neutral': [
                "I'm here whenever you need me. How can I support you today?",
                "Checking in with yourself is a great habit. What's on your mind?",
                "A calm, steady day is a great space to relax."
            ]
        }

        # Initialize Gemini API if key exists
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.has_gemini = False
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-3.6-flash')
                self.has_gemini = True
                print("[Chatbot] Gemini API initialized successfully.")
            except Exception as e:
                print(f"[Chatbot] Gemini initialization failed: {e}. Using local intent fallback.")

    def detect_intent(self, text):
        """
        Classifies user prompt into 1 of 6 intent categories:
          - music_recommendation
          - game_recommendation
          - relaxation_activity
          - greeting
          - general_conversation
          - emotional_support
        """
        if not text:
            return 'general_conversation'
            
        t = text.lower().strip()
        
        # 1. Greetings
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening', 'greetings', 'sup', 'yo']
        if any(t == g or t.startswith(g + ' ') for g in greetings):
            return 'greeting'
            
        # 2. Music requests
        music_keywords = ['song', 'songs', 'music', 'playlist', 'track', 'listen', 'audio', 'tune', 'tunes', 'sing']
        if any(k in t for k in music_keywords):
            return 'music_recommendation'
            
        # 3. Game requests
        game_keywords = ['game', 'games', 'play', 'bored', 'fun activity', 'fun', 'distract', 'distraction', 'fun to do']
        if any(k in t for k in game_keywords):
            return 'game_recommendation'
            
        # 4. Relaxation & Breathing requests
        relax_keywords = ['relax', 'relaxation', 'breathing', 'breathe', 'calm', 'meditate', 'meditation', 'stretch', 'unwind']
        if any(k in t for k in relax_keywords):
            return 'relaxation_activity'
            
        # 5. General conversation queries
        general_keywords = ['what can you do', 'who are you', 'how are you', 'help me', 'features', 'what are you']
        if any(k in t for k in general_keywords):
            return 'general_conversation'
            
        # 6. Default to emotional support
        return 'emotional_support'

    def get_music_recommendations(self, prompt, emotion):
        """Returns relevant music cards based on prompt or detected emotion state."""
        prompt_lower = prompt.lower()
        if 'happy' in prompt_lower or emotion == 'happy':
            cat = 'happy'
        elif 'sad' in prompt_lower or emotion == 'sad':
            cat = 'sad'
        elif 'relax' in prompt_lower or 'calm' in prompt_lower:
            cat = 'relaxing'
        elif emotion in self.music_database:
            cat = emotion
        else:
            cat = 'general'
            
        return self.music_database.get(cat, self.music_database['general'])

    def get_response(self, user_message, user_emotion='neutral'):
        """
        Processes prompt, detects intent, considers detected text/face emotion,
        and generates response with supportive recommendations.
        """
        emotion = user_emotion.lower() if user_emotion else 'neutral'
        intent = self.detect_intent(user_message)
        
        cards = []
        response_text = ""

        # --- INTENT HANDLING LOGIC ---
        if intent == 'greeting':
            response_text = f"Hello! 👋 I'm CAREVIBE, your emotional wellness assistant. How are you feeling today?"
            
        elif intent == 'general_conversation':
            response_text = ("I am CAREVIBE! I can help you track your emotions, provide empathetic support, "
                             "suggest relaxing music, guide you through 4-7-8 breathing exercises, or offer mindfulness activities.")
            
        elif intent == 'music_recommendation':
            recs = self.get_music_recommendations(user_message, emotion)
            cards = [{"type": "music", "data": m} for m in recs]
            response_text = f"Here are some curated song recommendations for you based on your request:"
            
        elif intent == 'game_recommendation':
            cards = [{"type": "game", "data": g} for g in self.games_database]
            response_text = "Here are some fun games and mindfulness activities to help you pass the time and refocus:"
            
        elif intent == 'relaxation_activity':
            cards = [
                {"type": "game", "data": self.games_database[0]}, # 4-7-8 Breathing
                {"type": "game", "data": self.games_database[2]}, # 5-4-3-2-1 Grounding
                {"type": "music", "data": self.music_database['relaxing'][0]}
            ]
            response_text = "Taking time to unwind is essential. I recommend trying our guided 4-7-8 breathing exercise:"
            
        else: # intent == 'emotional_support'
            # If Gemini is available, use dynamic LLM response with system prompt
            if self.has_gemini:
                try:
                    prompt_str = f"""
                    You are CAREVIBE, a warm, empathetic, and supportive mental health companion.
                    The user's current detected emotional state is: {emotion}.
                    User message: "{user_message}"
                    
                    Guidelines:
                    - Respond in 1-3 sentences with high empathy and care.
                    - Do NOT diagnose any medical or mental health condition.
                    - Do NOT claim to be a doctor or therapist.
                    - Gently suggest a healthy coping mechanism (like breathing, relaxing music, or journaling).
                    """
                    gen_res = self.model.generate_content(prompt_str)
                    if gen_res and gen_res.text:
                        response_text = gen_res.text.strip()
                except Exception as e:
                    print(f"[Chatbot] Gemini call failed: {e}. Using local fallback.")
                    
            if not response_text:
                pool = self.emotion_responses.get(emotion, self.emotion_responses['neutral'])
                response_text = random.choice(pool)
                
            # Attach relevant activity cards based on detected emotion
            if emotion in ['sad', 'fearful', 'angry']:
                cards.append({"type": "game", "data": self.games_database[0]}) # Breathing
                cards.append({"type": "music", "data": self.music_database[emotion if emotion in self.music_database else 'sad'][0]})

        return {
            "response": response_text,
            "intent": intent,
            "detected_state_applied": emotion,
            "recommendations": cards
        }
