import sys

# Force stdout UTF-8 encoding for Windows terminal output
sys.stdout.reconfigure(encoding='utf-8')

from services.chatbot import ChatbotService

bot = ChatbotService()
test_cases = [
    ('I am feeling sad', 'emotional_support'),
    ('I feel lonely', 'emotional_support'),
    ('I am stressed', 'emotional_support'),
    ('I am angry', 'emotional_support'),
    ('I am happy', 'emotional_support'),
    ('Suggest me some songs', 'music_recommendation'),
    ('I want relaxing music', 'music_recommendation'),
    ('Suggest me a game', 'game_recommendation'),
    ('I am bored', 'game_recommendation'),
    ('Give me something fun', 'game_recommendation'),
    ('I want to relax', 'relaxation_activity'),
    ('I need a breathing exercise', 'relaxation_activity'),
    ('Hello', 'greeting'),
    ('What can you do?', 'general_conversation'),
    ('', 'general_conversation')
]

print("| Prompt | Expected Intent | Detected Intent | Status |")
print("| --- | --- | --- | --- |")
for prompt, expected in test_cases:
    detected = bot.detect_intent(prompt)
    res = bot.get_response(prompt, 'neutral')
    status = "PASS" if detected == expected else "FAIL"
    print(f'| "{prompt}" | `{expected}` | `{detected}` | `{status}` |')
