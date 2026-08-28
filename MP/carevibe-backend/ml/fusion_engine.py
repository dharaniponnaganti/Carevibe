class FusionEngine:
    """
    Decision-level fusion engine that combines textual and facial emotional outputs.
    Detects emotional conflicts (e.g., Happy text but Sad face)
    """
    
    def __init__(self):
        # Define high-conflict pairs
        self.conflict_matrix = {
            'happy': ['sad', 'angry', 'fearful'],
            'sad': ['happy', 'surprised'],
            'angry': ['happy'],
            'fearful': ['happy'],
            'surprised': ['sad']
        }

    def fuse_emotions(self, text_emotion, face_emotion):
        """
        Takes the detected emotions from both modes and determines the final state.
        Returns the final emotion and whether a conflict is detected.
        """
        conflict = False
        final_emotion = text_emotion  # Default to text emotion if no conflict
        
        # Handle cases where one mode is missing
        if not text_emotion and face_emotion:
            return face_emotion, False, "Based purely on facial expression."
        if text_emotion and not face_emotion:
            return text_emotion, False, "Based purely on text analysis."
        if not text_emotion and not face_emotion:
            return "neutral", False, "No data provided."
            
        text_emotion = text_emotion.lower()
        face_emotion = face_emotion.lower()
        
        # Check for conflict
        if face_emotion in self.conflict_matrix.get(text_emotion, []):
            conflict = True
            # In cases of conflict, usually facial expression (non-verbal) is a more 
            # accurate indicator of true emotional state than written text.
            final_emotion = face_emotion
            reasoning = f"Conflict detected (Text: {text_emotion}, Face: {face_emotion}). Prioritizing facial expression as it often reveals underlying states."
        
        # If no conflict but they are different, let's just use a weighted pseudo-logic
        # In a generic situation, maybe default to the face emotion.
        elif text_emotion != face_emotion and text_emotion == 'neutral':
            final_emotion = face_emotion
            reasoning = f"Text is neutral, but face shows {face_emotion}. Using facial emotion."
        elif text_emotion != face_emotion and face_emotion == 'neutral':
            final_emotion = text_emotion
            reasoning = f"Face is neutral, but text shows {text_emotion}. Using text emotion."
        elif text_emotion == face_emotion:
            final_emotion = text_emotion
            reasoning = f"Congruent emotions. Both modes show {text_emotion}."
        else:
            final_emotion = face_emotion
            reasoning = f"Slight difference ({text_emotion} vs {face_emotion}). Defaulting to facial expression."
            
        return final_emotion, conflict, reasoning
