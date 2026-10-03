import os
import google.generativeai as genai

class ChatbotService:
    """
    Adaptive chatbot that adjusts responses according to the user's emotional state.
    """
    
    def __init__(self):
        # Keep mock responses as a fallback
        self.mock_responses = {
            'happy': [
                "That's wonderful to hear! I'm glad you're feeling good.",
                "It sounds like you're having a great time. Let's keep this positive energy going!",
                "Amazing! Celebrate these good moments, they're important."
            ],
            'sad': [
                "I'm sorry you're feeling down. I'm here to listen if you want to talk about it.",
                "It's completely okay to feel sad sometimes. Be gentle with yourself today.",
                "I hear you. If things get too heavy, maybe try one of the breathing exercises in the suggestions pane?"
            ],
            'angry': [
                "It's understandable to feel frustrated. Take a deep breath.",
                "Anger can be an overwhelming emotion. Would you like to try writing down exactly what's bothering you?",
                "I sense your frustration. Sometimes a quick physical activity helps clear the mind."
            ],
            'fearful': [
                "It's perfectly natural to feel anxious. Try to focus on the present moment.",
                "You are safe here. Let's try to ground ourselves using the 5-4-3-2-1 technique.",
                "Fear can feel paralyzing. Take a slow, deep breath in... and exhale slowly."
            ],
            'surprised': [
                "Wow, that sounds unexpected! How are you processing that?",
                "Life is full of surprises. Are you feeling okay about it?"
            ],
            'neutral': [
                "I'm here whenever you need me. How can I help you today?",
                "Just checking in. What's on your mind?",
                "Sometimes a calm day is exactly what we need."
            ]
        }
        
        # Load API key from environment variable
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.has_gemini = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.has_gemini = True
                print("[Chatbot] Gemini API initialized successfully.")
            except Exception as e:
                print(f"[Chatbot] Gemini initialization failed: {e}. Falling back to mock responses.")

    def get_response(self, user_message, user_emotion='neutral', face_emotion='neutral', history=None):
        import random
        # We bind the 'emotion' variable to face_emotion so our context-aware heuristics
        # can adapt the text intent based explicitly on the user's facial expression.
        emotion = face_emotion.lower() if face_emotion else 'neutral'
        
        # Parse history to find previous emotions and context
        prev_emotions = []
        last_bot_reply = ""
        
        if history:
            for msg in reversed(history):
                # only consider user messages or system messages that explicitly define emotion
                if msg.get('role') == 'user' or '(System:' in msg.get('text', ''):
                    if msg.get('emotion'):
                        prev_emotions.append(msg.get('emotion').lower())
                elif msg.get('role') == 'assistant' or msg.get('role') == 'bot':
                    if not last_bot_reply:
                        last_bot_reply = msg.get('text', '').lower()
        
        last_emotion = prev_emotions[-1] if prev_emotions else None
        is_system = "(System:" in user_message
        
        if is_system:
            if emotion == 'happy':
                if last_emotion in ['sad', 'fearful', 'angry']:
                    reply = "I'm so glad to see a smile on your face now! It looks like you're feeling much better."
                else:
                    reply = "You look really happy right now! It's great to see you smiling. What's making you feel so good?"
            elif emotion == 'sad':
                if last_emotion == 'happy':
                    reply = "Your expression just shifted, and you seem a bit down now. Did something just happen to upset you?"
                else:
                    reply = "I can see from your face that you might be feeling sad or down. I'm here for you. Do you want to talk about it?"
            elif emotion == 'angry':
                reply = "You look quite tense or frustrated. Remember to take a deep breath. Is there something bothering you?"
            elif emotion == 'fearful':
                reply = "You seem a little anxious or scared. You're in a safe space here. Would you like to try a grounding exercise?"
            elif emotion == 'surprised':
                reply = "You look surprised! Did something unexpected just happen?"
            else:
                reply = "I'm analyzing your facial expression, and you seem quite calm and neutral. How is your day going so far?"
        else:
            # First attempt: Context-aware Gemini response
            if self.has_gemini:
                try:
                    history_text = ""
                    if history:
                        for msg in history:
                            role_label = "User" if msg.get('role') == 'user' else "Assistant"
                            history_text += f"{role_label}: {msg.get('text')}\n"
                    
                    system_prompt = f"""
You are CareVibe, an empathetic mental health assistant.
You must generate a short, conversational response to the user's latest message.

CONVERSATION HISTORY:
{history_text}

USER'S CURRENT FACIAL EMOTION: {emotion}
USER'S LATEST MESSAGE: {user_message}

Instructions:
1. Consider the conversation history to understand context.
2. If the user's topic changed (e.g., they already ate, they are full), adapt your response to the new context. DO NOT repeat old responses.
3. Use their facial emotion as additional context for your tone.
4. Keep the response concise, natural, and supportive.
"""
                    import time
                    response = None
                    for attempt in range(3):
                        try:
                            # Try flash first, then pro
                            model_to_use = self.model if attempt < 2 else genai.GenerativeModel('gemini-1.5-pro-latest')
                            response = model_to_use.generate_content(system_prompt)
                            if response and response.text:
                                return {
                                    "response": response.text.strip(),
                                    "detected_state_applied": emotion,
                                    "source": "gemini"
                                }
                        except Exception as e:
                            print(f"[Chatbot] Gemini attempt {attempt+1} failed: {e}")
                            if attempt < 2:
                                time.sleep(1)
                    
                    print("[Chatbot] All Gemini generation attempts failed. Falling back to heuristics.")
                except Exception as outer_e:
                    print(f"[Chatbot] Gemini integration error: {outer_e}. Falling back to heuristics.")

            text = user_message.lower()
            
            # 1. Greetings & Pleasantries
            if any(w in text for w in ['hi ', 'hello', 'hey', 'hii', 'good morning', 'good evening', 'good afternoon']) or text.strip() == 'hi':
                if emotion == 'sad':
                    reply = "Hello there. I notice you seem a bit down. How are you doing today?"
                elif emotion == 'happy':
                    reply = "Hello! You're looking cheerful today! How can I help you?"
                else:
                    reply = "Hello there! How are you doing today?"
            elif 'thank' in text:
                if emotion == 'happy':
                    reply = "You're very welcome! 😊"
                else:
                    reply = "You're welcome! I'm here whenever you need me."
            elif any(w in text for w in ['bye', 'goodnight', 'good night', 'goodbye', 'see you']):
                reply = "Take care! Remember I'm here whenever you need support."
                
            # 2. Specific Conversational Intents COMBINED with Emotion
            elif 'hungry' in text or 'food' in text or 'eat' in text:
                if 'ate' in text or 'full' in text or 'already' in text or 'just had' in text:
                    reply = "I'm glad you've eaten! A full stomach is always a good feeling. What are you up to now?"
                elif 'grab something to eat' in last_bot_reply or 'what are you in the mood for' in last_bot_reply:
                    reply = "Are you still deciding on what to eat, or did you find something good?"
                elif emotion in ['sad', 'fearful']:
                    reply = "I know you're feeling a bit low, but getting some of your favorite food might help you feel a little better. What are you in the mood for?"
                else:
                    reply = "Haha, then it's probably time to grab something to eat! What are you in the mood for?"
            elif 'selected' in text or 'got a job' in text or 'offer' in text or 'passed' in text:
                if emotion in ['sad', 'neutral', 'fearful']:
                    reply = "Congratulations on the achievement! Though I notice you don't seem super excited—are you feeling okay or anxious about it?"
                else:
                    reply = "That's great! Congratulations! How are you feeling about the next step?"
            elif 'interview' in text or 'exam' in text:
                if emotion in ['sad', 'fearful', 'angry'] or 'stressed' in text or 'anxious' in text:
                    reply = "It's completely normal to feel stressed about that. I can see you're worried. You've got this! Just take a deep breath. Want to practice or talk about it?"
                else:
                    reply = "An interview or exam is a big deal! You seem to be handling it well. How is your preparation going?"
            elif 'stressed' in text or 'anxious' in text:
                if emotion == 'happy':
                    reply = "You mentioned feeling stressed, but you're keeping a brave face! Remember it's okay to let it out. What's making you anxious?"
                else:
                    reply = "It's perfectly natural to feel stressed. I can see it's weighing on you. Remember to take a deep breath. Is there anything specific about it making you anxious?"
            elif 'bored' in text or 'boring' in text:
                if emotion == 'sad':
                    reply = "I know things feel dull and you're feeling down. Maybe try one of the wellness activities gently, or just take it easy today."
                else:
                    reply = "If you're feeling bored, maybe try one of the wellness activities or step outside for some fresh air! What do you usually like to do for fun?"
            elif 'movie' in text or 'watching' in text or 'playing' in text:
                if emotion == 'happy':
                    reply = "That sounds like a fun way to spend your time! It looks like you're really enjoying it!"
                else:
                    reply = "That sounds like a nice distraction. How is it so far?"
            elif any(w in text for w in ['mother', 'father', 'mom', 'dad', 'friend', 'sister', 'brother', 'mpther']):
                if any(w in text for w in ['talk', 'talked', 'met', 'saw', 'speak']):
                    reply = "That's wonderful that you reconnected with them! I'm sure that brings a lot of comfort. How did the conversation go?"

                elif emotion in ['sad', 'fearful']:
                    reply = "Relationships with loved ones can sometimes be heavy. I'm here if you want to talk more about them."
                else:
                    reply = "Family and friends are so important. Tell me more about your relationship with them."
            elif 'miss' in text or 'missed' in text:
                if emotion in ['sad', 'fearful']:
                    reply = "It's so hard to miss someone you care about, and I can see you're feeling it right now. It's completely okay to feel that way."
                else:
                    reply = "Missing someone just shows how much they mean to you. When is the next time you might see or speak to them?"
            
            # 3. Explicit Emotion Words in Text COMBINED with Facial Emotion
            elif any(w in text for w in ['sad', 'down', 'depressed', 'crying']):
                if emotion == 'happy':
                    reply = "You mentioned feeling down, but you're smiling. Sometimes we hide our pain. I'm here to listen if you want to talk about what's really bothering you."
                else:
                    reply = "I'm so sorry you're feeling this way, and I can see it in your expression. I'm here to listen."
            elif any(w in text for w in ['great', 'good', 'happy', 'amazing', 'excited', 'better', 'relieved']):
                if emotion in ['sad', 'fearful']:
                    reply = "You say you're feeling positive, but you look a bit worried or sad. If you're putting on a brave face, just know I'm here to support you."
                elif emotion == 'happy':
                    reply = "I'm so glad you're feeling happy and relieved, and your smile definitely shows it! It's important to cherish these good moments."
                else:
                    reply = "It's wonderful to hear that you're feeling good right now! What brought about this positive change?"
            
            # 4. Implicit Emotion Detection Fallback (Only applied if no specific intent is found)
            else:
                if emotion == 'happy':
                    reply = "You seem to be in a good mood. What's on your mind?"
                elif emotion == 'sad':
                    reply = "I'm sensing that you might be feeling a bit down. I'm here for you if you need to talk."
                elif emotion == 'angry':
                    reply = "You seem a bit tense or frustrated. Remember to take a deep breath. Is something bothering you?"
                elif emotion == 'fearful':
                    reply = "If you're feeling anxious, try to focus on the present moment. You are safe here."
                else:
                    reply = "I'm listening. Tell me more about what's going on."
                
        return {
            "response": reply,
            "detected_state_applied": emotion,
            "source": "local_heuristic"
        }
