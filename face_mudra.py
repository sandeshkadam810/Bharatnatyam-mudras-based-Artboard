import numpy as np
import cv2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import MaxPooling2D
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Create the model structure (same as used in training)
model = Sequential()

model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48,48,1)))
model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(1024, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(7, activation='softmax'))  # Keep it at 7 to match the original model

# Load the pre-trained model weights
model.load_weights('facemudra.h5')

# Dictionary for Bharatanatyam facial mudras (mapping 7 categories to 5)
mudra_dict = {
    0: "(Roudra)",  # Keep Angry
    2: "(Bhayanaka)",  # Keep Fearful
    3: "(Hasya)",  # Keep Happy
    4: "(Shanta)",  # Keep Neutral
    5: "(Karuna)",  # Keep Sad
    6: "(Adbhuta)",  # surprised
    1: None  # Ignore Disgusted
}

# Start the webcam feed
cap = cv2.VideoCapture(0)
cv2.ocl.setUseOpenCL(False)

while True:
    # Find haar cascade to draw bounding box around face
    ret, frame = cap.read()
    if not ret:
        break
    facecasc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facecasc.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
        prediction = model.predict(cropped_img)
        maxindex = int(np.argmax(prediction))

        # Map the prediction to Bharatanatyam mudras, ignoring Disgusted and Surprised
        mudra = mudra_dict[maxindex]
        if mudra:  # Only display if it's one of the 5 valid mudras
            cv2.putText(frame, mudra, (x+20, y-60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Resize the video window to smaller size (800x480)
    cv2.imshow('Video', cv2.resize(frame, (800, 480), interpolation=cv2.INTER_CUBIC))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
