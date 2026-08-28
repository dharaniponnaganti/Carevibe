class StabilityService:
    """
    Calculates the Emotional Stability Score based on recent emotional trends.
    """
    
    @staticmethod
    def calculate_stability(checkins, chat_messages=None):
        """
        Takes a list of recent check-ins and chat messages, and calculates a score from 0-100.
        """
        emotion_to_score = {
            'happy': 85,
            'surprised': 70,
            'neutral': 55,
            'fearful': 35,
            'sad': 25,
            'angry': 20
        }
        
        mood_scores = []
        
        # Pull scores from manual check-ins
        if checkins:
            mood_scores.extend([c.get('mood_score', 50) for c in checkins])
            
        # Pull pseudo-scores from recent chat inferences
        if chat_messages:
            for msg in chat_messages:
                emo = msg.get('emotion')
                if emo and emo in emotion_to_score:
                    mood_scores.append(emotion_to_score[emo])
                    
        if not mood_scores:
            return 100  # Default to stable if no data
        
        # Calculate average
        avg_mood = sum(mood_scores) / len(mood_scores)
        
        # Calculate variance/volatility
        if len(mood_scores) > 1:
            variance = sum((x - avg_mood) ** 2 for x in mood_scores) / len(mood_scores)
            volatility = min(100, variance ** 0.5 * 2)  # Scale standard deviation to a max penalty of 100
        else:
            volatility = 0
            
        base_stability = avg_mood
        stability_score = base_stability - (volatility * 0.5)
        
        return max(0, min(100, round(stability_score)))
