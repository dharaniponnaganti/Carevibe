import time
import os
import json
import base64
import numpy as np
import cv2
from app import create_app
from ml import TextEmotionAnalyzer, FaceEmotionAnalyzer, FusionEngine
from services import ChatbotService, StabilityService, SuggestionEngine
from database import get_db

app = create_app()
client = app.test_client()

print("==================================================")
print("       RUNNING COMPREHENSIVE CAREVIBE AUDIT       ")
print("==================================================")

# --- STEP 3: TEXT EMOTION MODEL ---
text_analyzer = TextEmotionAnalyzer()
prompts = [
    "I am feeling very happy today",
    "I feel sad and lonely",
    "I am extremely angry",
    "I am scared",
    "I am surprised",
    "I really love this",
    "", # empty
    "   ", # whitespace
    "a", # short
    "I feel completely overwhelming joy and unbelievable happiness and extreme delight after receiving this incredible news!", # long
    "@#$%^&*()!", # special chars
    "1234567890", # numbers
    "i AM FeeLiNG VERY haPPy ToDAY!" # mixed case
]

print("\n--- STEP 3: TEXT EMOTION TEST RESULTS ---")
for p in prompts:
    t0 = time.perf_counter()
    pred = text_analyzer.analyze(p)
    t1 = time.perf_counter()
    print(f"Input: '{p}' => Prediction: '{pred}' (Time: {(t1-t0)*1000:.2f} ms)")

# --- STEP 4: FACE EMOTION MODEL ---
face_analyzer = FaceEmotionAnalyzer()
print("\n--- STEP 4: FACE EMOTION TEST RESULTS ---")

# Test empty/invalid
res_empty, msg_empty = face_analyzer.analyze_base64_image("")
print(f"Empty Base64 => Result: {res_empty}, Message: '{msg_empty}'")

# Test synthetic no-face image (blank white image)
blank_img = np.ones((200, 200, 3), dtype=np.uint8) * 255
_, buffer = cv2.imencode('.jpg', blank_img)
blank_b64 = base64.b64encode(buffer).decode('utf-8')
res_noface, msg_noface = face_analyzer.analyze_base64_image(blank_b64)
print(f"Blank Image (No Face) => Result: {res_noface}, Message: '{msg_noface}'")

# --- STEP 5: FUSION ENGINE ---
fusion = FusionEngine()
print("\n--- STEP 5: FUSION ENGINE TEST RESULTS ---")
fusion_cases = [
    ("Case 1: Happy + Happy", "happy", "happy"),
    ("Case 2: Happy Text + Sad Face", "happy", "sad"),
    ("Case 3: Sad Text + Sad Face", "sad", "sad"),
    ("Case 4: Text Only (Happy)", "happy", None),
    ("Case 5: Face Only (Sad)", None, "sad"),
    ("Case 6: No modality", None, None),
]

for label, text_em, face_em in fusion_cases:
    t0 = time.perf_counter()
    final_em, conflict, reasoning = fusion.fuse_emotions(text_em, face_em)
    t1 = time.perf_counter()
    print(f"{label} => Final: '{final_em}', Conflict: {conflict}, Reasoning: '{reasoning}' ({(t1-t0)*1000:.2f} ms)")

# --- STEP 6: CHATBOT INTENTS ---
chatbot = ChatbotService()
print("\n--- STEP 6: CHATBOT TEST RESULTS ---")
chat_tests = [
    ("Hello there", "greeting"),
    ("I feel so depressed and hopeless today", "emotional_support"),
    ("Can you suggest some soothing songs?", "music_recommendation"),
    ("I am bored, recommend a fun game", "game_recommendation"),
    ("Help me do a breathing exercise to relax", "relaxation_activity"),
    ("Who are you and what features do you have?", "general_conversation"),
    ("xyz123 random nonsense query", "unknown/fallback")
]

for msg, exp_intent in chat_tests:
    t0 = time.perf_counter()
    resp = chatbot.get_response(msg, user_emotion="sad")
    t1 = time.perf_counter()
    print(f"Msg: '{msg}' => Intent: '{resp['intent']}', Recs Count: {len(resp['recommendations'])} ({(t1-t0)*1000:.2f} ms)")

# --- STEP 7 & 8: API PERFORMANCE & DASHBOARD AUDIT ---
print("\n--- STEP 10 & 12: API BENCHMARKS ---")

# Benchmark endpoints
endpoints = [
    ("GET /", 'get', '/'),
    ("GET /api/health", 'get', '/api/health'),
    ("POST /api/auth/register", 'post', '/api/auth/register', {'username': f'test_{time.time()}', 'email': f'test_{time.time()}@test.com', 'password': 'Pass'}),
    ("POST /api/analyze/fusion", 'post', '/api/analyze/fusion', {'text': 'I am feeling wonderful'}),
    ("POST /api/chat", 'post', '/api/chat', {'message': 'Suggest songs'}),
]

for name, method, path, *payload in endpoints:
    t0 = time.perf_counter()
    if method == 'get':
        res = client.get(path)
    else:
        body = payload[0] if payload else {}
        res = client.post(path, json=body)
    t1 = time.perf_counter()
    print(f"{name} => Status: {res.status_code}, Response Time: {(t1-t0)*1000:.2f} ms")

print("\n--- CAREVIBE AUDIT RUN COMPLETE ---")
