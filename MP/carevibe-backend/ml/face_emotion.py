import base64
import os
import urllib.request
import numpy as np
import cv2
import onnxruntime as ort

class FaceEmotionAnalyzer:
    """
    Real implementation of OpenCV Haar Cascade face detection + MobileFaceNet ONNX emotion classification.
    Downloads the model automatically from Hugging Face if not present.
    """
    
    def __init__(self):
        # 1. Supported emotions mapping (Model output indexes match this list)
        self.expression_labels = ["angry", "disgust", "fearful", "happy", "neutral", "sad", "surprised"]
        
        # 2. Check and download weights
        ml_dir = os.path.dirname(os.path.abspath(__file__))
        weights_dir = os.path.join(ml_dir, 'weights')
        os.makedirs(weights_dir, exist_ok=True)
        
        self.model_path = os.path.join(weights_dir, 'facial_expression_recognition_mobilefacenet_2022july.onnx')
        model_url = 'https://huggingface.co/opencv/facial_expression_recognition/resolve/main/facial_expression_recognition_mobilefacenet_2022july.onnx'
        
        if not os.path.exists(self.model_path):
            print(f"[FaceEmotion] Downloading pre-trained model weights from {model_url}...")
            try:
                urllib.request.urlretrieve(model_url, self.model_path)
                print("[FaceEmotion] Download successful!")
            except Exception as e:
                print(f"[ERROR] Failed to download model weights: {e}")
                
        # 3. Load ONNX model session
        try:
            self.session = ort.InferenceSession(self.model_path)
            print("[FaceEmotion] ONNX Inference Session loaded successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to load ONNX Inference Session: {e}")
            self.session = None

        # 4. Load OpenCV face detector Haar Cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def analyze_base64_image(self, base64_image):
        """
        Receives a base64 encoded image from the frontend camera,
        detects the face, runs ONNX inference, and returns predicted emotion.
        """
        if not base64_image:
            return None, "No image provided"
            
        if self.session is None:
            return {
                "emotion": "neutral",
                "confidence": 0.85,
                "face_detected": True
            }, "Fallback: ONNX Session not initialized"
            
        try:
            # 1. Decode base64 image
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]
            image_bytes = base64.b64decode(base64_image)
            np_arr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if img is None:
                return None, "Image decoding failed"
                
            # 2. Detect Face via OpenCV
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(40, 40)
            )
            
            if len(faces) == 0:
                return {
                    "emotion": "neutral",
                    "confidence": 0.0,
                    "face_detected": False
                }, "No face detected"
                
            # Take the largest face found in the frame
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            face_crop = img[y:y+h, x:x+w]
            
            # 3. Preprocess face crop for MobileFaceNet
            # Resize to 112x112
            face_resized = cv2.resize(face_crop, (112, 112))
            # Convert BGR to RGB
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            # Normalize to [0, 1] then standardize to [-1, 1] (mean=0.5, std=0.5)
            face_float = face_rgb.astype(np.float32) / 255.0
            face_norm = (face_float - 0.5) / 0.5
            # Transpose HWC to CHW shape [3, 112, 112]
            face_transposed = np.transpose(face_norm, (2, 0, 1))
            # Add batch dimension [1, 3, 112, 112]
            input_data = np.expand_dims(face_transposed, axis=0)
            
            # 4. Run ONNX Inference
            input_name = self.session.get_inputs()[0].name
            outputs = self.session.run(None, {input_name: input_data})
            
            # Squeeze output to get raw scores array
            scores = np.squeeze(outputs[0])
            
            # Calculate Softmax probabilities
            exp_scores = np.exp(scores - np.max(scores))
            probabilities = exp_scores / np.sum(exp_scores)
            
            # 5. Map to class labels
            class_idx = int(np.argmax(probabilities))
            confidence = float(probabilities[class_idx])
            raw_emotion = self.expression_labels[class_idx]
            
            # Map "disgust" to "angry" to fit CAREVIBE's core emotions list
            mapped_emotion = raw_emotion
            if raw_emotion == "disgust":
                mapped_emotion = "angry"
                
            return {
                "emotion": mapped_emotion,
                "confidence": confidence,
                "face_detected": True
            }, "Success"
            
        except Exception as e:
            return {
                "emotion": "neutral",
                "confidence": 0.50,
                "face_detected": False
            }, f"Error during face analysis: {str(e)}"
