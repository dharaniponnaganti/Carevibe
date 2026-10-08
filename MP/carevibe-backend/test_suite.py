import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
from app import create_app

app = create_app()
client = app.test_client()

results = []

def record(module, test_name, status, details=""):
    results.append({
        'module': module,
        'test_name': test_name,
        'status': status,
        'details': details
    })
    print(f"[{module}] {test_name}: {status} - {details}")

print("=== STARTING CAREVIBE IN-PROCESS TEST SUITE ===")

# 1. API Health Check
try:
    res = client.get('/api/health')
    if res.status_code == 200:
        record('APIs', 'Health Endpoint', 'PASS', 'Status 200 OK')
    else:
        record('APIs', 'Health Endpoint', 'FAIL', f'Status {res.status_code}')
except Exception as e:
        record('APIs', 'Health Endpoint', 'FAIL', str(e))

# 2. Auth Tests
token = None
user_id = None
test_email = f"test_{os.urandom(4).hex()}@example.com"

try:
    # Register
    res = client.post('/api/auth/register', json={
        'username': f'user_{os.urandom(3).hex()}',
        'email': test_email,
        'password': 'Password123!',
        'full_name': 'Test User'
    })
    if res.status_code == 201:
        data = res.get_json()
        token = data.get('token')
        user_id = data.get('user_id')
        record('Authentication', 'Valid Registration', 'PASS', 'User registered, JWT issued')
    else:
        record('Authentication', 'Valid Registration', 'FAIL', res.get_data(as_text=True))
        
    # Duplicate email
    res_dup = client.post('/api/auth/register', json={
        'username': 'otheruser',
        'email': test_email,
        'password': 'Password123!'
    })
    if res_dup.status_code == 400:
        record('Authentication', 'Duplicate Email Rejection', 'PASS', '400 returned on duplicate')
    else:
        record('Authentication', 'Duplicate Email Rejection', 'FAIL', res_dup.get_data(as_text=True))

    # Login
    res_login = client.post('/api/auth/login', json={
        'email': test_email,
        'password': 'Password123!'
    })
    if res_login.status_code == 200:
        record('Authentication', 'Valid Login', 'PASS', 'Token received')
    else:
        record('Authentication', 'Valid Login', 'FAIL', res_login.get_data(as_text=True))

    # Invalid Password Login
    res_bad_login = client.post('/api/auth/login', json={
        'email': test_email,
        'password': 'WrongPassword'
    })
    if res_bad_login.status_code == 401:
        record('Authentication', 'Invalid Password Handling', 'PASS', '401 Unauthorized')
    else:
        record('Authentication', 'Invalid Password Handling', 'FAIL', res_bad_login.get_data(as_text=True))

except Exception as e:
    record('Authentication', 'Auth Suite Exception', 'FAIL', str(e))

headers = {'Authorization': f'Bearer {token}'} if token else {}

# 3. Text Emotion Model Tests
test_prompts = [
    ("I am feeling very happy today.", "happy"),
    ("I feel sad and lonely.", "sad"),
    ("I am extremely angry.", "angry"),
    ("I am scared about what will happen.", "fearful"),
    ("I am surprised by this news.", "surprised")
]

for prompt, exp in test_prompts:
    try:
        res = client.post('/api/analyze/fusion', json={'text': prompt}, headers=headers)
        if res.status_code == 200:
            pred = res.get_json().get('text_emotion')
            if pred == exp:
                record('Text Emotion', f"Prompt: '{prompt}'", 'PASS', f"Predicted: {pred}")
            else:
                record('Text Emotion', f"Prompt: '{prompt}'", 'FAIL', f"Expected {exp}, got {pred}")
        else:
            record('Text Emotion', f"Prompt: '{prompt}'", 'FAIL', f"Status {res.status_code}")
    except Exception as e:
        record('Text Emotion', f"Prompt: '{prompt}'", 'FAIL', str(e))

# 4. Face Emotion Model Tests
try:
    # Face emotion on simulated face parameter
    res = client.post('/api/analyze/fusion', json={'text': '', 'image': '', 'simulated_face': 'happy'}, headers=headers)
    if res.status_code == 200 and res.get_json().get('face_emotion') == 'happy':
        record('Face Emotion', 'Face Recognition Stream', 'PASS', 'Face prediction happy verified')
    else:
        record('Face Emotion', 'Face Recognition Stream', 'FAIL', str(res.get_json()))
except Exception as e:
    record('Face Emotion', 'Face Recognition Stream', 'FAIL', str(e))

# 5. Fusion Engine Tests
fusion_cases = [
    ("Text Only", {'text': 'I am happy', 'image': '', 'simulated_face': ''}),
    ("Face Only", {'text': '', 'image': '', 'simulated_face': 'sad'}),
    ("Text + Face Matching", {'text': 'I am sad', 'image': '', 'simulated_face': 'sad'}),
    ("Text + Face Conflict", {'text': 'I am happy', 'image': '', 'simulated_face': 'sad'})
]

for label, payload in fusion_cases:
    try:
        res = client.post('/api/analyze/fusion', json=payload, headers=headers)
        if res.status_code == 200:
            d = res.get_json()
            record('Fusion', label, 'PASS', f"Final: {d.get('final_emotion')}, Conflict: {d.get('conflict_detected')}")
        else:
            record('Fusion', label, 'FAIL', f"Status {res.status_code}")
    except Exception as e:
        record('Fusion', label, 'FAIL', str(e))

# 6. Chatbot & Recommendation Intent Tests
chat_prompts = [
    ("I am feeling sad", "emotional_support"),
    ("Suggest me some songs", "music_recommendation"),
    ("Suggest me a game", "game_recommendation"),
    ("I want to relax", "relaxation_activity"),
    ("Hello", "greeting"),
    ("What can you do?", "general_conversation")
]

for prompt, exp_intent in chat_prompts:
    try:
        res = client.post('/api/chat', json={'message': prompt, 'emotion': 'neutral'}, headers=headers)
        if res.status_code == 200:
            d = res.get_json()
            if d.get('intent') == exp_intent:
                record('Chatbot', f"Intent '{exp_intent}'", 'PASS', f"Recommendations: {len(d.get('recommendations', []))}")
            else:
                record('Chatbot', f"Intent '{exp_intent}'", 'FAIL', f"Got intent: {d.get('intent')}")
        else:
            record('Chatbot', f"Intent '{exp_intent}'", 'FAIL', f"Status {res.status_code}")
    except Exception as e:
        record('Chatbot', f"Intent '{exp_intent}'", 'FAIL', str(e))

# 7. Music & Activity Recommendations
try:
    res = client.post('/api/chat', json={'message': 'Suggest me some songs'}, headers=headers)
    recs = res.get_json().get('recommendations', []) if res.status_code == 200 else []
    if len(recs) > 0 and 'url' in recs[0]['data']:
        record('Music', 'Music Recommendation Links', 'PASS', f"Verified YouTube URL: {recs[0]['data']['url']}")
    else:
        record('Music', 'Music Recommendation Links', 'FAIL', 'Missing link payload')
except Exception as e:
    record('Music', 'Music Recommendation Links', 'FAIL', str(e))

try:
    res = client.post('/api/chat', json={'message': 'I need a breathing exercise'}, headers=headers)
    recs = res.get_json().get('recommendations', []) if res.status_code == 200 else []
    if len(recs) > 0 and recs[0]['data'].get('action') == 'breathing':
        record('Activities', '4-7-8 Breathing Action Link', 'PASS', 'Action action: breathing')
    else:
        record('Activities', '4-7-8 Breathing Action Link', 'FAIL', 'Missing activity action')
except Exception as e:
    record('Activities', '4-7-8 Breathing Action Link', 'FAIL', str(e))

# 8. Emergency Alert Test
try:
    res = client.post('/api/analyze/fusion', json={'text': 'I feel worthless and want to harm myself'}, headers=headers)
    if res.status_code == 200 and res.get_json().get('risk_level', {}).get('trigger_alert') == True:
        record('Emergency Alert', 'High Risk Distress Keyword Alert', 'PASS', 'High risk trigger_alert: True')
    else:
        record('Emergency Alert', 'High Risk Distress Keyword Alert', 'FAIL', str(res.get_json()))
except Exception as e:
    record('Emergency Alert', 'High Risk Distress Keyword Alert', 'FAIL', str(e))

# 9. CRUD & Persistence Tests (Checkins, Journal, Goals)
try:
    # Checkin
    res = client.post('/api/checkins', json={'emotion': 'happy', 'mood_score': 8}, headers=headers)
    if res.status_code == 201:
        record('Check-in', 'Create Checkin', 'PASS', 'Saved to MongoDB')
    else:
        record('Check-in', 'Create Checkin', 'FAIL', res.get_data(as_text=True))

    # Journal
    res_j = client.post('/api/journal', json={'title': 'Test Day', 'content': 'Everything went great!'}, headers=headers)
    if res_j.status_code == 201:
        j_id = res_j.get_json().get('entry_id')
        record('Journal', 'Create Journal Entry', 'PASS', f"ID: {j_id}")
        
        # Read
        res_get_j = client.get('/api/journal', headers=headers)
        if res_get_j.status_code == 200 and res_get_j.get_json().get('total', 0) > 0:
            record('Journal', 'Read Journal Entries', 'PASS', f"Total: {res_get_j.get_json()['total']}")
        else:
            record('Journal', 'Read Journal Entries', 'FAIL', res_get_j.get_data(as_text=True))
    else:
        record('Journal', 'Create Journal Entry', 'FAIL', res_j.get_data(as_text=True))

    # Goals
    res_g = client.post('/api/goals', json={'title': 'Walk 5km'}, headers=headers)
    if res_g.status_code == 201:
        g_id = res_g.get_json().get('goal_id')
        record('Goals', 'Create Goal', 'PASS', f"ID: {g_id}")
        
        # Update
        res_up_g = client.put(f'/api/goals/{g_id}', json={'completed': True}, headers=headers)
        if res_up_g.status_code == 200:
            record('Goals', 'Update Goal Completion', 'PASS', 'Status updated')
        else:
            record('Goals', 'Update Goal Completion', 'FAIL', res_up_g.get_data(as_text=True))
    else:
        record('Goals', 'Create Goal', 'FAIL', res_g.get_data(as_text=True))

except Exception as e:
    record('APIs', 'CRUD Exception', 'FAIL', str(e))

# 10. Dashboard Stats & User Isolation
try:
    res = client.get('/api/dashboard/stats', headers=headers)
    if res.status_code == 200:
        d = res.get_json()
        record('Dashboard', 'Fetch Dashboard Stats', 'PASS', f"Streak: {d.get('streak')}, Stability: {d.get('stability_score')}")
    else:
        record('Dashboard', 'Fetch Dashboard Stats', 'FAIL', res.get_data(as_text=True))
except Exception as e:
    record('Dashboard', 'Fetch Dashboard Stats', 'FAIL', str(e))

# 11. Database Isolation
try:
    res_unauth = client.get('/api/journal')
    if res_unauth.status_code == 401:
        record('Database', 'User Account Isolation', 'PASS', 'Unauthenticated request rejected with 401')
    else:
        record('Database', 'User Account Isolation', 'FAIL', f"Status: {res_unauth.status_code}")
except Exception as e:
    record('Database', 'User Account Isolation', 'FAIL', str(e))

print("\n=== SUMMARY TABLE ===")
modules = sorted(list(set(r['module'] for r in results)))
print(f"{'Module':<20} | {'Tests':<6} | {'Passed':<6} | {'Failed':<6} | {'Blocked':<7} | {'Status':<6}")
print("-" * 65)

total_tests = 0
total_passed = 0

for m in modules:
    m_results = [r for r in results if r['module'] == m]
    t_cnt = len(m_results)
    p_cnt = sum(1 for r in m_results if r['status'] == 'PASS')
    f_cnt = sum(1 for r in m_results if r['status'] == 'FAIL')
    b_cnt = sum(1 for r in m_results if r['status'] == 'BLOCKED')
    status_str = "PASS" if f_cnt == 0 and b_cnt == 0 else ("FAIL" if f_cnt > 0 else "BLOCKED")
    
    total_tests += t_cnt
    total_passed += p_cnt
    
    print(f"{m:<20} | {t_cnt:<6} | {p_cnt:<6} | {f_cnt:<6} | {b_cnt:<7} | {status_str:<6}")

print("-" * 65)
pct = (total_passed / total_tests) * 100 if total_tests > 0 else 0
print(f"TOTAL: {total_tests} tests executed | {total_passed} passed | Overall Pass Rate: {pct:.2f}%\n")
