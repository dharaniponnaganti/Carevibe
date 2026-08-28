import os
import time
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score

# Paths
DATA_DIR = r"C:\Users\dhara\OneDrive\Desktop\MP Data Sets"
TRAIN_FILE = os.path.join(DATA_DIR, "train.txt")
VAL_FILE = os.path.join(DATA_DIR, "val.txt")

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "weights")
os.makedirs(WEIGHTS_DIR, exist_ok=True)

def load_data(filepath):
    """Loads dataset from file with format: text;emotion"""
    texts = []
    labels = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(';')
            if len(parts) == 2:
                texts.append(parts[0])
                labels.append(parts[1])
    return texts, labels

def train_model():
    print("Loading training data...")
    start_time = time.time()
    train_texts, train_labels = load_data(TRAIN_FILE)
    val_texts, val_labels = load_data(VAL_FILE)
    print(f"Loaded {len(train_texts)} training samples and {len(val_texts)} validation samples in {time.time() - start_time:.2f}s")
    
    print("Vectorizing text with TF-IDF...")
    start_time = time.time()
    # Removed stop_words='english' and added ngram_range=(1,2) to capture negations like "not good"
    vectorizer = TfidfVectorizer(max_features=15000, lowercase=True, ngram_range=(1, 2))
    X_train = vectorizer.fit_transform(train_texts)
    X_val = vectorizer.transform(val_texts)
    print(f"Vectorization completed in {time.time() - start_time:.2f}s")
    
    print("Training Support Vector Machine (LinearSVC)...")
    start_time = time.time()
    model = LinearSVC(random_state=42, max_iter=2000)
    model.fit(X_train, train_labels)
    print(f"Model trained in {time.time() - start_time:.2f}s")
    
    print("Evaluating Model on Validation Set...")
    val_preds = model.predict(X_val)
    print(f"Accuracy: {accuracy_score(val_labels, val_preds)*100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(val_labels, val_preds))
    
    print("Saving model weights...")
    joblib.dump(vectorizer, os.path.join(WEIGHTS_DIR, "tfidf_vectorizer.pkl"))
    joblib.dump(model, os.path.join(WEIGHTS_DIR, "text_svm_model.pkl"))
    print(f"Weights saved successfully to {WEIGHTS_DIR}")

if __name__ == "__main__":
    train_model()
