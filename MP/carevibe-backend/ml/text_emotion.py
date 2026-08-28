import os
import joblib

class TextEmotionAnalyzer:
    """
    True ML implementation of a TF-IDF with SVM text emotion classifier.
    Loads the trained Vectorizer and LinearSVC model.
    """
    
    def __init__(self):
        # We need to map the model's output labels to the standard expected emotions handled by the rest of the app.
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
        
        try:
            self.vectorizer = joblib.load(vectorizer_path)
            self.model = joblib.load(model_path)
            self.is_loaded = True
            print("Successfully loaded Text Emotion model.")
        except Exception as e:
            print(f"Error loading Text Emotion model: {e}")
            self.is_loaded = False

    def analyze(self, text):
        """
        Analyze text and return the primary emotion predicted by the SVM.
        """
        if not text or not getattr(self, 'is_loaded', False):
            return 'neutral'
            
        text_lower = text.lower()
        
        # Hybrid Approach: The baseline SVM struggles with short negations (like "not good") 
        # because the word "good" carries extreme joy-weight. We apply a heuristic safety net.
        negations_sad = ['not good', 'not great', 'not happy', 'not feeling well', 'day is bad', 'bad day']
        negations_happy = ['not bad', 'not sad', 'not terrible']
        
        if any(neg in text_lower for neg in negations_sad):
            return 'sad'
        if any(neg in text_lower for neg in negations_happy):
            return 'happy'
            
        try:
            # Vectorize the text
            x = self.vectorizer.transform([text])
            
            # Predict
            prediction = self.model.predict(x)[0]
            
            return self.label_map.get(prediction, prediction)
        except Exception as e:
            print(f"Prediction error: {e}")
            return 'neutral'
