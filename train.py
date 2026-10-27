"""
Fake News Detection - Model Training Pipeline
=====================================================
This script trains a Machine Learning model to detect Fake News vs Real News.
Steps:
1. Try downloading Kaggle Fake & Real News Dataset (with automatic fallback to local benchmark data).
2. Load Fake.csv (label 0) and True.csv (label 1), merge and shuffle.
3. Preprocess text: lowercase, remove URLs, punctuation, numbers, and stopwords.
4. Extract features using TfidfVectorizer(stop_words='english', max_df=0.7).
5. Split data (80% train, 20% test).
6. Train LogisticRegression and PassiveAggressiveClassifier.
7. Print Accuracy, Classification Report, and Confusion Matrix.
8. Save best model as models/model.pkl and vectorizer as models/tfidf.pkl (Accuracy > 92%).
"""

import os
import re
import pickle
import string
import urllib.request
import zipfile
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Import dataset generator fallback
try:
    from data_generator import build_datasets
except ImportError:
    from fake_news_detector.data_generator import build_datasets

# Import and ensure NLTK stopwords
import nltk
try:
    from nltk.corpus import stopwords
    _ = stopwords.words('english')
except (LookupError, AttributeError):
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words('english'))

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
FAKE_CSV = os.path.join(DATA_DIR, "Fake.csv")
TRUE_CSV = os.path.join(DATA_DIR, "True.csv")
MODEL_PATH = os.path.join(MODELS_DIR, "model.pkl")
TFIDF_PATH = os.path.join(MODELS_DIR, "tfidf.pkl")


def download_or_prepare_dataset():
    """
    Attempts to download Kaggle Fake and Real News dataset.
    If Kaggle API / network download fails, verifies data/Fake.csv & data/True.csv
    or automatically builds a benchmark dataset.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    print("\n" + "="*60)
    print("STEP 1: Checking and Preparing Dataset...")
    print("="*60)
    
    # Check if files already exist
    if os.path.exists(FAKE_CSV) and os.path.exists(TRUE_CSV):
        print(f"[*] Found existing datasets:\n    - {FAKE_CSV}\n    - {TRUE_CSV}")
        return

    # Attempt download from Kaggle using kagglehub if available
    download_success = False
    try:
        print("[*] Attempting to download from Kaggle (clmentbisaillon/fake-and-real-news-dataset)...")
        import kagglehub
        path = kagglehub.dataset_download("clmentbisaillon/fake-and-real-news-dataset")
        print(f"[+] Downloaded dataset from Kaggle to: {path}")
        
        # Copy or link files into data/
        for fname in ["Fake.csv", "True.csv"]:
            src = os.path.join(path, fname)
            dst = os.path.join(DATA_DIR, fname)
            if os.path.exists(src):
                import shutil
                shutil.copyfile(src, dst)
                print(f"[+] Loaded {fname} into data directory.")
        download_success = True
    except Exception as e:
        print(f"[-] Kaggle automatic download not available: {e}")
        print("[*] Using built-in local sample data loading logic...")

    # If Kaggle download was not performed, generate rich benchmark datasets
    if not (os.path.exists(FAKE_CSV) and os.path.exists(TRUE_CSV)):
        print("[*] Generating comprehensive Fake.csv and True.csv benchmark datasets...")
        build_datasets(output_dir=DATA_DIR, count_per_class=300)
        print("[+] Benchmark dataset generated successfully!")


def clean_text(text: str) -> str:
    """
    Cleans raw text for machine learning:
    - Converts to lowercase
    - Removes URLs & web links
    - Removes HTML tags
    - Removes punctuation
    - Removes digits and numbers
    - Removes English stopwords
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Lowercase
    text = text.lower()
    
    # 2. Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # 3. Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # 4. Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 5. Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # 6. Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 7. Remove stopwords
    words = [word for word in text.split() if word not in STOPWORDS and len(word) > 2]
    return " ".join(words)


def train_and_evaluate():
    """
    Loads data, preprocesses text, trains models, evaluates performance,
    and saves the best model and vectorizer.
    """
    # 1. Prepare data
    download_or_prepare_dataset()
    
    # 2. Load Fake.csv and True.csv
    print("\n" + "="*60)
    print("STEP 2: Loading and Merging Datasets...")
    print("="*60)
    
    df_fake = pd.read_csv(FAKE_CSV)
    df_true = pd.read_csv(TRUE_CSV)
    
    # Assign labels: 0 for FAKE, 1 for REAL
    df_fake['label'] = 0
    df_true['label'] = 1
    
    print(f"[+] Loaded Fake news records: {len(df_fake)} (Label: 0)")
    print(f"[+] Loaded True news records: {len(df_true)} (Label: 1)")
    
    # Merge both into one dataframe
    df = pd.concat([df_fake, df_true], ignore_index=True)
    
    # Combine title and text for richer feature context
    title_col = 'title' if 'title' in df.columns else None
    text_col = 'text' if 'text' in df.columns else df.columns[0]
    
    if title_col:
        df['combined_text'] = df[title_col].fillna('') + " " + df[text_col].fillna('')
    else:
        df['combined_text'] = df[text_col].fillna('')
        
    # Shuffle dataframe
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    print(f"[+] Total merged dataset size: {len(df)} samples")
    
    # 3. Preprocessing
    print("\n" + "="*60)
    print("STEP 3: Cleaning & Preprocessing Text (Lowercase, URLs, Stopwords)...")
    print("="*60)
    
    df['cleaned_text'] = df['combined_text'].apply(clean_text)
    
    # Filter empty rows if any
    df = df[df['cleaned_text'].str.strip() != ''].reset_index(drop=True)
    print(f"[+] Text cleaned successfully. Retained {len(df)} valid samples.")
    
    X = df['cleaned_text']
    y = df['label']
    
    # 4. Train-Test Split (80% train, 20% test)
    print("\n" + "="*60)
    print("STEP 4: Splitting Data (80% Train, 20% Test)...")
    print("="*60)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"[+] Training samples: {len(X_train)} | Testing samples: {len(X_test)}")
    
    # 5. TF-IDF Vectorization
    print("\n" + "="*60)
    print("STEP 5: Vectorizing Text with TfidfVectorizer(stop_words='english', max_df=0.7)...")
    print("="*60)
    
    tfidf = TfidfVectorizer(stop_words='english', max_df=0.7, ngram_range=(1, 2), max_features=10000)
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)
    print(f"[+] TF-IDF vocabulary size: {len(tfidf.vocabulary_)} features")
    
    # 6. Train Models
    print("\n" + "="*60)
    print("STEP 6: Training Machine Learning Classifiers...")
    print("="*60)
    
    # Model A: Logistic Regression
    print("[*] Training Model 1: Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    lr_model.fit(X_train_tfidf, y_train)
    y_pred_lr = lr_model.predict(X_test_tfidf)
    acc_lr = accuracy_score(y_test, y_pred_lr)
    
    # Model B: Passive-Aggressive Classifier
    print("[*] Training Model 2: Passive-Aggressive Classifier...")
    pac_model = PassiveAggressiveClassifier(max_iter=1000, random_state=42, C=0.5)
    pac_model.fit(X_train_tfidf, y_train)
    y_pred_pac = pac_model.predict(X_test_tfidf)
    acc_pac = accuracy_score(y_test, y_pred_pac)
    
    # 7. Print Metrics & Comparison
    print("\n" + "="*60)
    print("STEP 7: Model Evaluation & Comparison")
    print("="*60)
    
    print(f"\n--- Model 1: Logistic Regression ---")
    print(f"Accuracy: {acc_lr * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_lr, target_names=["FAKE (0)", "REAL (1)"]))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred_lr))
    
    print(f"\n--- Model 2: Passive-Aggressive Classifier ---")
    print(f"Accuracy: {acc_pac * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_pac, target_names=["FAKE (0)", "REAL (1)"]))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred_pac))
    
    # 8. Select Best Model and Save
    print("\n" + "="*60)
    print("STEP 8: Saving Best Model and TF-IDF Vectorizer")
    print("="*60)
    
    # Choose model with higher accuracy (prefer Logistic Regression if tied for calibrated probabilities)
    if acc_pac > acc_lr:
        best_name = "Passive-Aggressive Classifier"
        best_model = pac_model
        best_acc = acc_pac
    else:
        best_name = "Logistic Regression"
        best_model = lr_model
        best_acc = acc_lr
        
    print(f"[+] Selected Best Model: {best_name} with Accuracy: {best_acc * 100:.2f}%")
    
    # Check accuracy requirement (> 92%)
    if best_acc >= 0.92:
        print(f"[SUCCESS] Accuracy benchmark met (>92%): {best_acc * 100:.2f}%")
    else:
        print(f"[WARNING] Accuracy is {best_acc * 100:.2f}%. (Benchmark: >92%)")
        
    # Save model and vectorizer with pickle
    with open(MODEL_PATH, "wb") as f_model:
        pickle.dump(best_model, f_model)
    print(f"[+] Model saved to: {MODEL_PATH}")
    
    with open(TFIDF_PATH, "wb") as f_tfidf:
        pickle.dump(tfidf, f_tfidf)
    print(f"[+] TF-IDF Vectorizer saved to: {TFIDF_PATH}")
    
    print("\n" + "="*60)
    print("TRAINING PIPELINE COMPLETE! Ready to run: streamlit run app.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    train_and_evaluate()
