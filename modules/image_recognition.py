import tensorflow as tf
import numpy as np
from PIL import Image

# Path to the saved model (adjust the path as needed)
model_path = 'data/moroccan_monuments_model.h5'  # Replace with the actual model path

# Load the model
model = tf.keras.models.load_model(model_path)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Class labels as per your model's training
class_labels = {
    0: 'Jemaa el fna', 1: 'Medersa Attarine', 2: 'Medersa Ben Youssef', 3: 'Volubilis', 
    4: 'La Citerne portugaise El Jadida', 5: 'Palais Bahia', 6: 'Le Palais El Badi', 7: 'Tannerie Chouara',
    8: 'Cap Spartel', 9: 'Ait Ben Haddou', 10: 'Tombeaux saadiens', 11: 'Mosquee Hassan 2', 
    12: 'La mosquee Koutoubia', 13: 'Bab Boujloud', 14: 'Mausolee Mohammed V'
}

# Function to preprocess the image
def preprocess_image(img_path):
    img = Image.open(img_path)
    img = img.resize((224, 224))  # Resize the image to match the input size during training
    img_array = np.array(img) / 255.0  # Normalize the image by scaling pixel values to [0, 1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

def predict_monument(img_path):
    try:
        # Extract the filename from the path
        filename = img_path.split('/')[-1]
        # Preprocess the image
        img_array = preprocess_image(img_path)

        # Make predictions
        predictions = model.predict(img_array)

        # Get the predicted class
        predicted_class = np.argmax(predictions, axis=1)
        predicted_label = class_labels[predicted_class[0]]

        return f"Il s'agit en effet de {predicted_label}"
    except Exception as e:
        return f"Erreur avec {filename}: {e}"
