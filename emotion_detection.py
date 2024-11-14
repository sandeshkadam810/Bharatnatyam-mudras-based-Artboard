from fer import FER 
import cv2

# Emotion dictionary mapping for Bharatanatyam mudras
mudra_dict = {
    'angry': "(Roudra)",  # Keep Angry
    'fear': "(Bhayanaka)",  # Keep Fearful
    'happy': "(Hasya)",  # Keep Happy
    'neutral': "(Shanta)",  # Keep Neutral
    'sad': "(Karuna)",  # Keep Sad
    'surprise': "(Adbhuta)"  # Surprised
}

# Initialize the FER detector
detector = FER()

# Function to detect emotion
def detect_emotion(frame):
    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get the top emotion detected
    result = detector.top_emotion(rgb_frame)

    # Return the mapped emotion if available
    if result and result[0] in mudra_dict:
        return mudra_dict[result[0]]
    return "(Shanta)"  # Default to Neutral if no emotion detected