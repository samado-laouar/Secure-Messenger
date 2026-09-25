import face_recognition
import cv2
import numpy as np
import pickle
import os
from pathlib import Path

FACE_DATA_DIR = "face_data"
Path(FACE_DATA_DIR).mkdir(exist_ok=True)

def get_face_encoding_path(username):
    """Get the path to store face encoding for a user"""
    return os.path.join(FACE_DATA_DIR, f"{username}_face.pkl")

def capture_face_for_registration(username):
    """
    Capture face from webcam for registration
    Returns: (success, message, encoding)
    """
    video_capture = cv2.VideoCapture(0)
    
    if not video_capture.isOpened():
        return False, "Cannot access webcam", None
    
    print("Position your face in the frame and press SPACE to capture")
    print("Press ESC to cancel")
    
    face_encoding = None
    success = False
    message = ""
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        
        # Find faces in the frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        # Draw rectangles around detected faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected", (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Display instructions
        cv2.putText(frame, "Press SPACE to capture, ESC to cancel", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Face Registration', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            message = "Registration cancelled"
            break
        elif key == 32:  # SPACE
            if len(face_locations) == 0:
                message = "No face detected. Please try again."
                continue
            elif len(face_locations) > 1:
                message = "Multiple faces detected. Please ensure only one person is visible."
                continue
            else:
                # Encode the face
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                if face_encodings:
                    face_encoding = face_encodings[0]
                    success = True
                    message = "Face captured successfully!"
                    break
                else:
                    message = "Failed to encode face. Please try again."
    
    video_capture.release()
    cv2.destroyAllWindows()
    
    return success, message, face_encoding

def save_face_encoding(username, encoding):
    """Save face encoding to file"""
    try:
        filepath = get_face_encoding_path(username)
        with open(filepath, 'wb') as f:
            pickle.dump(encoding, f)
        return True, "Face encoding saved successfully"
    except Exception as e:
        return False, f"Error saving face encoding: {str(e)}"

def load_face_encoding(username):
    """Load face encoding from file"""
    try:
        filepath = get_face_encoding_path(username)
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading face encoding: {e}")
        return None

def has_face_recognition(username):
    """Check if user has face recognition enabled"""
    return os.path.exists(get_face_encoding_path(username))

def verify_face_for_user(username):
    """
    Verify user's face for password recovery
    Returns: (success, message)
    """
    # Load the user's registered face encoding
    known_encoding = load_face_encoding(username)
    
    if known_encoding is None:
        return False, "No face recognition data found for this user"
    
    video_capture = cv2.VideoCapture(0)
    
    if not video_capture.isOpened():
        return False, "Cannot access webcam"
    
    print("Position your face in the frame...")
    print("Press ESC to cancel")
    
    authenticated = False
    message = ""
    frame_count = 0
    max_frames = 100  # Try for ~3 seconds at 30fps
    
    while frame_count < max_frames:
        ret, frame = video_capture.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Process every 3rd frame for performance
        if frame_count % 3 != 0:
            cv2.imshow('Face Verification', frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                message = "Verification cancelled"
                break
            continue
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Draw rectangle
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Compare with known face
            matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.6)
            
            if matches[0]:
                # Calculate face distance (lower is better)
                face_distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                confidence = (1 - face_distance) * 100
                
                cv2.putText(frame, f"Match: {confidence:.1f}%", 
                           (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (0, 255, 0), 2)
                
                authenticated = True
                message = f"Face verified successfully"
                break
        
        if authenticated:
            break
        
        # Display instructions
        cv2.putText(frame, "Look at the camera... ESC to cancel", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Face Verification', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            message = "Verification cancelled"
            break
    
    if not authenticated and not message:
        message = "Face not recognized"
    
    video_capture.release()
    cv2.destroyAllWindows()
    
    return authenticated, message

def delete_face_encoding(username):
    """Delete face encoding for a user"""
    try:
        filepath = get_face_encoding_path(username)
        if os.path.exists(filepath):
            os.remove(filepath)
        return True, "Face encoding deleted"
    except Exception as e:
        return False, f"Error deleting face encoding: {str(e)}"