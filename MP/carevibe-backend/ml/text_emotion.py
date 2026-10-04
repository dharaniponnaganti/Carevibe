import os
import joblib

class TextEmotionAnalyzer:
    """
    True ML implementation of a TF-IDF with SVM text emotion classifier.
    Loads the trained Vectorizer and LinearSVC model.
    """
    
    def __init__(self):
        # Map original dataset emotion labels to CAREVIBE standardized emotions
        self.label_map = {
            'joy': 'happy',
            'sadness': 'sad',
            'anger': 'angry',
            'fear': 'fearful',
            'surprise': 'surprised',
            'love': 'happy', # map love to happy
            'neutral': 'neutral'
        }
        
        # Load the models
        weights_dir = os.path.join(os.path.dirname(__file__), "weights")
        vectorizer_path = os.path.join(weights_dir, "tfidf_vectorizer.pkl")
        model_path = os.path.join(weights_dir, "text_svm_model.pkl")
        
        self.is_loaded = False
        try:
            if not os.path.exists(vectorizer_path) or not os.path.exists(model_path):
                raise FileNotFoundError(f"Model or vectorizer file missing in {weights_dir}")
                
            self.vectorizer = joblib.load(vectorizer_path)
            self.model = joblib.load(model_path)
            
            # Verify that vectorizer is fitted
            if not hasattr(self.vectorizer, 'vocabulary_') or not hasattr(self.vectorizer, 'idf_'):
                raise ValueError("Loaded TF-IDF Vectorizer is not fitted!")
                
            self.is_loaded = True
            print("[TextEmotionAnalyzer] Successfully loaded fitted TF-IDF Vectorizer and LinearSVC model.")
        except Exception as e:
            print(f"[ERROR] Text Emotion model initialization failed: {e}")
            self.is_loaded = False

    def analyze(self, text):
        """
        Analyze text and return the primary emotion predicted by the SVM.
        """
        if not text:
            return 'neutral'
            
        if not getattr(self, 'is_loaded', False):
            print("[WARN] Text model is not loaded. Returning neutral fallback.")
            return 'neutral'
            
        text_lower = text.lower()
        
        # Hybrid Approach: Heuristic safety net for clear negation phrases
        negations_sad = ['not good', 'not great', 'not happy', 'not feeling well', 'day is bad', 'bad day']
        negations_happy = ['not bad', 'not sad', 'not terrible']
        
        if any(neg in text_lower for neg in negations_sad):
            return 'sad'
        if any(neg in text_lower for neg in negations_happy):
            return 'happy'
            
        try:
            # Vectorize the text
            x = self.vectorizer.transform([text])
            
            # Predict using LinearSVC
            prediction = self.model.predict(x)[0]
            
            return self.label_map.get(prediction, prediction)
        except Exception as e:
            print(f"[ERROR] Text prediction failed for input '{text}': {e}")
            return 'neutral'
