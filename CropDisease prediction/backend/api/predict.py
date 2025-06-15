from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import requests
from deep_translator import GoogleTranslator

app = FastAPI()

# Allow CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
MODEL_PATH = "./trained_plant_disease_model.keras"
model = tf.keras.models.load_model(MODEL_PATH)

# Class labels
class_names = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight', 'Potato___Late_blight',
    'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot', 'Tomato___Early_blight',
    'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).resize((128, 128))
    input_arr = np.array(image) / 255.0
    input_arr = np.expand_dims(input_arr, axis=0)

    predictions = model.predict(input_arr)
    result_index = np.argmax(predictions)
    predicted_disease = class_names[result_index]

    return {"predicted_disease": predicted_disease}

@app.get("/search/")
async def search(query: str):
    api_key = os.getenv("AIzaSyArEi1aGVDCju2zfSwgoS-1xxq-ozz7-t8")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={search_engine_id}"
    response = requests.get(url)
    data = response.json()

    if "items" in data and len(data["items"]) > 0:
        item = data["items"][0]
        return {"title": item["title"], "snippet": item["snippet"]}
    else:
        return {"title": "No Results", "snippet": "No information found."}

@app.get("/translate/")
async def translate(text: str):
    translated_text = GoogleTranslator(source='auto', target='hi').translate(text)
    return {"translated": translated_text}
