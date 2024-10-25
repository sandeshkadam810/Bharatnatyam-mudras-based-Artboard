import cv2
import mediapipe as mp
import tensorflow as tf
import numpy as np
import keras

mudra_names = [
    'Alapadmam(1)', 'Anjali(1)', 'Aralam(1)', 'Ardhachandran(1)', 'Ardhapathaka(1)',
    'Berunda(1)', 'Bramaram(1)', 'Chakra(1)', 'Chandrakala(1)', 'Chaturam(1)', 'Garuda(1)',
    'Hamsapaksha(1)', 'Hamsasyam(1)', 'Kangulam(1)', 'Kapith(1)', 'Kapotham(1)',
    'Karkatta(1)', 'Kartariswastika(1)', 'Katakamukha_1', 'Katakamukha_2', 'Katakamukha_3',
    'Katakavardhana(1)', 'Katrimukha(1)', 'Khatva(1)', 'Kilaka(1)', 'Kurma(1)',
    'Matsya(1)', 'Mayura(1)', 'Mrigasirsha(1)', 'Mukulam(1)', 'Mushti(1)',
    'Nagabandha(1)', 'Padmakosha(1)', 'Pasha(1)', 'Pathaka(1)', 'Pushpaputa(1)',
    'Sakata(1)', 'Samputa(1)', 'Sarpasirsha(1)', 'Shanka(1)', 'Shivalinga(1)',
    'Shukatundam(1)', 'Sikharam(1)', 'Simhamukham(1)', 'Suchi(1)', 'Swastikam(1)',
    'Tamarachudam(1)', 'Tripathaka(1)', 'Trishulam(1)', 'Varaha(1)', 'extra', 'none'
]

num_classes = len(mudra_names)
input_shape = (224, 224, 3)  # Define the input shape including channels
keras.config.enable_unsafe_deserialization()
# Load the trained model
model = tf.keras.models.load_model(r'C:\Users\SANDESH\Desktop\ipcv-cp\handmudra.h5')
print("Model loaded successfully!")

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect hands in the frame
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get bounding box of the hand
            x_min, y_min, x_max, y_max = 1.0, 1.0, 0.0, 0.0
            for landmark in hand_landmarks.landmark:
                x_min = min(x_min, landmark.x)
                x_max = max(x_max, landmark.x)
                y_min = min(y_min, landmark.y)
                y_max = max(y_max, landmark.y)

            # Convert normalized coordinates to pixel coordinates
            height, width, _ = frame.shape
            x_min = int(x_min * width) - 30
            x_max = int(x_max * width) + 20
            y_min = int(y_min * height) - 30
            y_max = int(y_max * height) + 20  

            # Crop and preprocess the hand region
            hand_image = frame[y_min:y_max, x_min:x_max]
            if hand_image.size == 0:
                print("Hand image is empty!")
                continue

            try: 
                resized_hand = cv2.resize(hand_image, (224, 224))  # Ensure resizing
                preprocessed_hand = np.expand_dims(resized_hand, axis=0) / 255.0
                
                # Make predictions only if hand is detected
                predictions = model.predict(preprocessed_hand)
                print("Predictions:", predictions)  # Check raw predictions
                
                predicted_index = np.argmax(predictions)
                confidence = predictions[0][predicted_index]
                
                if confidence > 0.5:  # Only display predictions above 50% confidence
                    predicted_mudra = mudra_names[predicted_index]
                else:
                    predicted_mudra = "Unknown"
                    
                # Display the predicted mudra on the frame
                cv2.putText(frame, f'Mudra: {predicted_mudra} ({confidence:.2f})', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                print("Predicted Mudra:", predicted_mudra)
            except Exception as e:
                print("Error during prediction:", e)

    # Display the frame with predictions
    cv2.imshow("Gesture Recognition", frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
