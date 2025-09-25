# ==============================================================================
# ### --- Final Phase: Creating an API for our Model --- ###
# ==============================================================================

# Step 1: Import necessary libraries
# Flask: The main tool for building our API (our 'waiter')
# joblib: To load our saved AI brain ('blur_detector_model.joblib')
# cv2 (OpenCV), numpy: To process the images that users send to us
from flask import Flask, request, jsonify
import joblib
import cv2
import numpy as np
import os

# Step 2: Initialize the Flask App
# This creates the foundation of our web service.
app = Flask(__name__)

# Step 3: Load the trained model
# We load the 'AI brain' into memory as soon as the API starts.
# This makes it ready to make predictions instantly.
print("Loading model...")
model_path = 'blur_detector_model.joblib'
model = joblib.load(model_path)
print("Model loaded successfully!")

# Step 4: Create a function to calculate blurriness
# This is the exact same function we used in Google Colab.
def calculate_laplacian_variance(image_bytes):
    # The image comes in as a stream of bytes, so we need to decode it first
    image_np = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    if img is None:
        return 0 # Return 0 if image is invalid

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance

# Step 5: Define the API endpoint for prediction
# This is the 'door' that n8n will knock on.
# We're telling Flask: "If someone sends a POST request to '/predict', run this function."
@app.route('/predict', methods=['POST'])
def predict():
    # Check if a file was sent in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    if file:
        # Read the image file from the request
        image_bytes = file.read()

        # Calculate the blurriness score using our function
        score = calculate_laplacian_variance(image_bytes)

        # Use our loaded model to predict based on the score
        # The model needs the score in a 2D array format, e.g., [[123.45]]
        prediction = model.predict([[score]])

        # Send the result back as a clean JSON response
        # The result from prediction is an array (e.g., ['clear']), so we take the first element.
        return jsonify({
            'prediction': prediction[0],
            'blur_score': score
        })

# Step 6: Define a root endpoint for health check
# This is a simple 'door' to check if our API is running.
@app.route('/', methods=['GET'])
def health_check():
    return "Blur Detector API is running!"


# This part allows the app to be run by a production server like Gunicorn
if __name__ == '__main__':
    # This block is not typically used in production on Render,
    # but it's useful for testing on your own computer.
    # Render uses the 'Start Command' (gunicorn app:app) instead.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

