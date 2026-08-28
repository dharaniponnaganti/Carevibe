class SuggestionEngine:
    """
    Smart suggestion engine that provides context-aware support and monitors for emergency risk.
    """
    
    def __init__(self):
        self.suggestions = {
            'happy': [
                {"title": "Keep the Momentum", "desc": "Write down 3 things you're grateful for today."},
                {"title": "Upbeat Playlist", "desc": "Listen to our energized curated mix."}
            ],
            'sad': [
                {"title": "Guided Breathing", "desc": "Try the 4-7-8 breathing technique to center yourself."},
                {"title": "Gentle Walk", "desc": "A 10-minute walk outside can help shift your perspective."},
                {"title": "Soothing Sounds", "desc": "Listen to ambient nature or piano sounds."}
            ],
            'angry': [
                {"title": "Box Breathing", "desc": "Inhale for 4s, hold for 4s, exhale 4s, hold 4s."},
                {"title": "Physical Release", "desc": "Try a short, intense workout or brisk walk."},
                {"title": "Journaling", "desc": "Write down what's frustrating you to externalize it."}
            ],
            'fearful': [
                {"title": "Grounding Exercise", "desc": "5-4-3-2-1 technique: identify 5 things you can see, 4 you can touch..."},
                {"title": "Progressive Muscle Relaxation", "desc": "Tense and relax your muscles starting from your toes."},
                {"title": "Safe Space Visualization", "desc": "Close your eyes and visualize a calming, secure environment."}
            ],
            'surprised': [
                {"title": "Take a Moment", "desc": "Pause and process what you just experienced."},
                {"title": "Deep Breath", "desc": "Inhale deeply and sigh it out."}
            ],
            'neutral': [
                {"title": "Mindful Moment", "desc": "Take 2 minutes to just be present with your surroundings."},
                {"title": "Stretch", "desc": "Do a quick full-body stretch to release any hidden tension."}
            ]
        }

    def generate_suggestions(self, emotion):
        """Return a list of suggestions based on emotion."""
        emotion = emotion.lower()
        return self.suggestions.get(emotion, self.suggestions['neutral'])

    def determine_risk_level(self, emotion, text_content=""):
        """
        Determines the risk level (low, medium, high) based on emotion and text content.
        Triggers emergency alert states.
        """
        text_lower = text_content.lower()
        high_risk_words = ['harm', 'suicide', 'kill', 'end it all', 'worthless', 'giving up', 'cut myself']
        
        # Check explicit high risk keywords
        for word in high_risk_words:
            if word in text_lower:
                return {
                    "level": "high",
                    "trigger_alert": True,
                    "message": "We've detected you might be in distress. Please reach out to emergency services or a crisis lifeline immediately."
                }
                
        if emotion in ['sad', 'fearful', 'angry']:
            return {
                "level": "medium",
                "trigger_alert": False,
                "message": "You're experiencing some difficult emotions. Remember to use your coping strategies."
            }
            
        return {
            "level": "low",
            "trigger_alert": False,
            "message": "Your emotional state appears stable."
        }
