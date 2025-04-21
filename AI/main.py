import requests
import streamlit as st
import tensorflow as tf
from deep_translator import GoogleTranslator
import numpy as np

# Page Background Style - Dark Mode
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #000000;
    color: white;
}
[data-testid="stHeader"] {
    background: transparent;
}
[data-testid="stSidebar"] {
    background-color: #111111;
}
h1, h2, h3, h4, h5, h6, p {
    color: white !important;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# TensorFlow Model Prediction
def model_prediction(test_image):
    model = tf.keras.models.load_model("C:/Users/shukl/Documents/Projects/Plant_classification/trained_plant_disease_model.keras")
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=(128, 128))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    predictions = model.predict(input_arr)
    return np.argmax(predictions)

# Google Custom Search API Call
def google_search(query, api_key, search_engine_id):
    search_url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": search_engine_id,
        "num": 1
    }
    response = requests.get(search_url, params=params)
    return response.json()

# New Hindi Translator using deep_translator
def translate_to_hindi(text):
    try:
        return GoogleTranslator(source='en', target='hi').translate(text)
    except Exception as e:
        return "Translation failed."

# Sidebar Navigation
st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "Disease Recognition"])

# Home Page
if app_mode == "Home":
    st.markdown("""
        <h1 style="text-shadow: 0 0 10px rgba(255,255,255,0.8);">
            Krishi Kavach 🌾
        </h1>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div>
        Welcome to the Crop Disease Recognition System! 🌿🔍

        Our mission is to help identify crop diseases efficiently. Upload an image of a plant, and our system will analyze it for signs of disease. Let’s ensure a healthier harvest together.

        <h3>How it works?</h3>
        <p>1. <b>Upload Image:</b> Go to the <b>Disease Recognition</b> page and upload an image.</p>
        <p>2. <b>Analysis:</b> Our model identifies possible plant diseases.</p>
        <p>3. <b>Results:</b> View diagnosis and treatment suggestions.</p>
        </div>
        """, unsafe_allow_html=True)

# Disease Recognition Page
elif app_mode == "Disease Recognition":
    st.markdown("""<h1 style="color: white;">Disease Recognition</h1>""", unsafe_allow_html=True)

    test_image = st.file_uploader("Upload an image of a diseased plant")

    if st.button("Show Image"):
        if test_image is not None:
            st.image(test_image, width=400, use_column_width=True)
        else:
            st.warning("Please upload an image to display")

    if st.button("Predict"):
        if test_image is not None:
            with st.spinner("Analyzing the image..."):
                result_index = model_prediction(test_image)

                class_name = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
                              'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew',
                              'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                              'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy',
                              'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                              'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot',
                              'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
                              'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
                              'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew',
                              'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot',
                              'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold',
                              'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
                              'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
                              'Tomato___healthy']

                if 0 <= result_index < len(class_name):
                    predicted_disease = class_name[result_index]
                else:
                    st.error("Invalid model prediction index.")
                    st.stop()

                if "healthy" not in predicted_disease:
                    st.success(f"Model Prediction: {predicted_disease}")

                    api_key = "AIzaSyArEi1aGVDCju2zfSwgoS-1xxq-ozz7-t8"
                    search_engine_id = "a2779f8bc3d1d4416"
                    search_query = f"{predicted_disease} disease remedy and information"
                    search_results = google_search(search_query, api_key, search_engine_id)

                    if 'items' in search_results:
                        first_result = search_results['items'][0]
                        title = first_result.get('title', 'No Title')
                        snippet = first_result.get('snippet', 'No Description')
                        link = first_result.get('link', '#')
                        expanded_snippet = "\n".join([snippet] * 4) if len(snippet.split()) < 30 else snippet

                        st.markdown(f"**Disease Info (English):** {expanded_snippet}")
                        st.markdown(f"**Remedy (English):** [Read more]({link})")

                        translated_text = translate_to_hindi(expanded_snippet)
                        st.markdown(f"**Disease Info (Hindi):** {translated_text}")
                    else:
                        st.info("No additional information found.")
                else:
                    st.success("The plant appears healthy! 🌱")
        else:
            st.warning("Please upload an image first.")
