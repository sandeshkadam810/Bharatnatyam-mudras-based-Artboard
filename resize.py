import cv2
import numpy as np
import os

# Create a directory to save the resized and cropped images
output_dir = r'C:\Users\SANDESH\Desktop\ipcv_cp\resized'  # Use raw string or double backslashes
os.makedirs(output_dir, exist_ok=True)

# Function to resize and crop images
def resize_and_crop(image, target_size=(224, 224)):
    h, w = image.shape[:2]
    # Resize while maintaining aspect ratio
    if h > w:
        new_height = target_size[0]
        new_width = int(w * (target_size[0] / h))
    else:
        new_width = target_size[1]
        new_height = int(h * (target_size[1] / w))
    
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Crop the center of the image
    start_x = (resized_image.shape[1] - target_size[1]) // 2
    start_y = (resized_image.shape[0] - target_size[0]) // 2

    cropped_image = resized_image[start_y:start_y + target_size[0], start_x:start_x + target_size[1]]
    return cropped_image

# Load and process the dataset
data_dir = r'C:\Users\SANDESH\Desktop\ipcv_cp\IPCV_CP_Images'  # Use raw string or double backslashes

# Iterate through each image file in the directory
for img_file in os.listdir(data_dir):
    img_path = os.path.join(data_dir, img_file)
    image = cv2.imread(img_path)

    if image is not None:
        # Resize and crop the image
        processed_image = resize_and_crop(image, target_size=(224, 224))
        
        # Save the processed image
        output_image_path = os.path.join(output_dir, img_file)
        cv2.imwrite(output_image_path, processed_image)

print("Resizing and cropping completed. Processed images are saved in:", output_dir)
