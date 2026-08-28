class ChatbotService:
    """
    Adaptive chatbot that adjusts responses according to the user's emotional state.
    """
    
    def __init__(self):
        # MOCK Implementation replacing an LLM call
        self.responses = {
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

    def get_response(self, user_message, user_emotion='neutral'):
        """
        Generate a conversational response that considers the user's emotional state.
        In a real app, this would wrap an API call to Gemini/OpenAI passing the emotion as context.
        """
        import random
        
        emotion = user_emotion.lower()
        if emotion not in self.responses:
            emotion = 'neutral'
            
        # Simple mock: pick a random response mapped to the emotional state
        selected_response = random.choice(self.responses[emotion])
        
        return {
            "response": selected_response,
            "detected_state_applied": emotion
        }
