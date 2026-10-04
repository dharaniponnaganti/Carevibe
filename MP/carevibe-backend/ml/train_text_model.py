import os
import time
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, confusion_matrix

# Paths (Configurable via DATASET_DIR environment variable)
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset")
DATA_DIR = os.getenv("DATASET_DIR", DEFAULT_DATA_DIR)
TRAIN_FILE = os.path.join(DATA_DIR, "train.txt")
VAL_FILE = os.path.join(DATA_DIR, "val.txt")
TEST_FILE = os.path.join(DATA_DIR, "test.txt")

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "weights")
os.makedirs(WEIGHTS_DIR, exist_ok=True)

def load_data(filepath):
    """Loads dataset from file with format: text;emotion"""
    texts = []
    labels = []
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found: {filepath}")
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

def evaluate_split(split_name, y_true, y_pred, labels):
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')
    print(f"\n================ {split_name.upper()} EVALUATION METRICS ================")
    print(f"Accuracy:           {acc * 100:.2f}%")
    print(f"Weighted Precision: {prec * 100:.2f}%")
    print(f"Weighted Recall:    {rec * 100:.2f}%")
    print(f"Weighted F1-Score:  {f1 * 100:.2f}%")
    print("\nDetailed Per-Class Classification Report:")
    print(classification_report(y_true, y_pred, target_names=labels, digits=4))
    
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=[f"True_{l}" for l in labels], columns=[f"Pred_{l}" for l in labels])
    print(f"\nConfusion Matrix ({split_name}):")
    print(cm_df)
    return acc, prec, rec, f1

def train_model():
    print("Loading datasets...")
    start_time = time.time()
    train_texts, train_labels = load_data(TRAIN_FILE)
    val_texts, val_labels = load_data(VAL_FILE)
    test_texts, test_labels = load_data(TEST_FILE)
    print(f"Loaded {len(train_texts)} train, {len(val_texts)} val, and {len(test_texts)} test samples in {time.time() - start_time:.2f}s")
    
    print("Vectorizing text with TF-IDF (fitting ONLY on training set)...")
    start_time = time.time()
    vectorizer = TfidfVectorizer(max_features=15000, lowercase=True, ngram_range=(1, 2))
    X_train = vectorizer.fit_transform(train_texts)
    X_val = vectorizer.transform(val_texts)
    X_test = vectorizer.transform(test_texts)
    print(f"Vectorization completed in {time.time() - start_time:.2f}s")
    
    print("Training LinearSVC model...")
    start_time = time.time()
    model = LinearSVC(random_state=42, max_iter=2000)
    model.fit(X_train, train_labels)
    print(f"Model trained in {time.time() - start_time:.2f}s")
    
    # Preserve class order
    class_labels = sorted(list(set(train_labels)))
    
    # 1. Validation Evaluation
    val_preds = model.predict(X_val)
    evaluate_split("Validation Set", val_labels, val_preds, class_labels)
    
    # 2. Test Evaluation
    test_preds = model.predict(X_test)
    evaluate_split("Test Set", test_labels, test_preds, class_labels)
    
    print("\nSaving trained model weights...")
    joblib.dump(vectorizer, os.path.join(WEIGHTS_DIR, "tfidf_vectorizer.pkl"))
    joblib.dump(model, os.path.join(WEIGHTS_DIR, "text_svm_model.pkl"))
    print(f"Weights saved successfully to {WEIGHTS_DIR}")

if __name__ == "__main__":
    train_model()
