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
                self.model = genai.GenerativeModel('gemini-3.6-flash')
                self.has_gemini = True
                print("[Chatbot] Gemini API initialized successfully.")
            except Exception as e:
                print(f"[Chatbot] Gemini initialization failed: {e}. Falling back to mock responses.")

    def get_response(self, user_message, user_emotion='neutral'):
        """
        Generate a conversational response that considers the user's emotional state.
        If Gemini API key is configured, calls Gemini to get a dynamic response.
        Otherwise, falls back to pre-written mock responses.
        """
        emotion = user_emotion.lower()
        if emotion not in self.mock_responses:
            emotion = 'neutral'
            
        if self.has_gemini:
            try:
                # System prompt guiding the behavior of the agent based on emotion context
                prompt = f"""
                You are CAREVIBE, a compassionate, supportive, and empathetic mental health assistant.
                The user is currently feeling {emotion}. 
                Respond to their message in a warm, friendly, and non-judgmental way.
                Keep your response relatively concise (1-3 sentences) to maintain a natural chat interface.
                If they express high distress, remind them gently of coping techniques (like breathing exercises) or resources.
                
                User Message: "{user_message}"
                """
                response = self.model.generate_content(prompt)
                ai_text = response.text.strip()
                if ai_text:
                    return {
                        "response": ai_text,
                        "detected_state_applied": emotion
                    }
            except Exception as e:
                print(f"[Chatbot] Gemini generation failed: {e}. Falling back to mock.")
                
        # Mock fallback
        import random
        selected_response = random.choice(self.mock_responses[emotion])
        return {
            "response": selected_response,
            "detected_state_applied": emotion
        }
