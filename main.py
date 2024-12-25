import requests
import streamlit as st
import tensorflow as tf
import numpy as np
from googletrans import Translator

def translate_to_hindi(text):
    translator = Translator()
    translated = translator.translate(text, dest='hi')
    return translated.text
# Page Background Style
page_bg_img = """
<style>
[data-testid="stAppViewContainer"]{
background-image: url(https://wallpapercave.com/w/uwp4441882);
background-size: cover;
}
</style>
"""
st.markdown(
    """
    <style>
    body {
        background-color: #ADD8E6; /* Light blue background */
        color: white; /* Black text color */
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(page_bg_img, unsafe_allow_html=True)

# TensorFlow Model Prediction
def model_prediction(test_image):
    model = tf.keras.models.load_model("trained_plant_disease_model.keras")
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=(128, 128))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr]) 
    predictions = model.predict(input_arr)
    return np.argmax(predictions)

# Google Custom Search API Call
def google_search(query, api_key, search_engine_id, num_results=3):
    search_url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,  # Your Google Custom Search API Key
        "cx": search_engine_id,  # Your Search Engine ID
        "num": num_results  # Get multiple results
    }
    response = requests.get(search_url, params=params)
    return response.json()


# Sidebar for Navigation
st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "Disease Recognition"])

# Main Page Logic
if app_mode == "Home":
    st.markdown(
        """
        <h1 style="
            color: black; 
            text-shadow: 0 0 10px rgba(173, 216, 230, 0.8), 
                         0 0 20px rgba(173, 216, 230, 0.6), 
                         0 0 30px rgba(173, 216, 230, 0.4);
        ">
            Krishi Kavach 
        </h1>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style="color: white;">
        Welcome to the Crop Disease Recognition System! 🌿🔍

        Our mission is to help in identifying crop diseases efficiently. Upload an image of a plant, and our system will analyze it to detect any signs of diseases. Together, let's protect our crops and ensure a healthier harvest!

        <h3 style="color: white;">How it works?</h3>
        <p>1. <b>Upload Image:</b> Go to the <b>Disease Recognition</b> page and upload an image of a plant with suspected diseases.<p>
        <p>2. <b>Analysis:</b> Our system will process the image using advanced algorithms to identify potential diseases.<p>
        <p>3. <b>Results:</b> View the results and recommendations for further action.<p>
        </div>
        """,
        unsafe_allow_html=True
    )


elif app_mode == "Disease Recognition":
    st.markdown(
        """
        <style>
        .header {
            color: white;
            font-size: 36px;
            font-weight: bold;
        }
        </style>
        <h1 class="header">Disease Recognition</h1>
        """,
        unsafe_allow_html=True
    )

    # Uploading the image
    test_image = st.file_uploader("Upload an image of a diseased plant")
    
    if st.button("Show Image"):
        if test_image is not None:
            st.image(test_image, width=400, use_column_width=True)
        else:
            st.write("Please upload an image to display")

    # Predict and Search Information about the Disease
    if st.button("Predict"):
        if test_image is not None:
            st.spinner()
            st.write("Analyzing the image...")

            # Predict disease using the model
            result_index = model_prediction(test_image)

            # List of disease names
            class_name = ['Apple_Apple_scab', 'Apple_Black_rot', 'Apple_Cedar_apple_rust', 'Apple_healthy',
                          'Blueberry__healthy', 'Cherry(including_sour)_Powdery_mildew', 
                          'Cherry_(including_sour)healthy', 'Corn(maize)_Cercospora_leaf_spot Gray_leaf_spot', 
                          'Corn_(maize)Common_rust', 'Corn_(maize)Northern_Leaf_Blight', 'Corn(maize)_healthy', 
                          'Grape_Black_rot', 'Grape_Esca(Black_Measles)', 'Grape_Leaf_blight(Isariopsis_Leaf_Spot)', 
                          'Grape_healthy', 'Orange_Haunglongbing(Citrus_greening)', 'Peach__Bacterial_spot',
                          'Peach_healthy', 'Pepper,_bell_Bacterial_spot', 'Pepper,_bell_healthy', 
                          'Potato_Early_blight', 'Potato_Late_blight', 'Potato_healthy', 
                          'Raspberry_healthy', 'Soybean_healthy', 'Squash_Powdery_mildew', 
                          'Not in Dataset', 'Strawberry_healthy', 'Tomato_Bacterial_spot', 
                          'Tomato_Early_blight', 'Tomato_Late_blight', 'Tomato_Leaf_Mold', 
                          'Tomato_Septoria_leaf_spot', 'Tomato_Spider_mites Two-spotted_spider_mite', 
                          'Tomato_Target_Spot', 'Tomato_Tomato_Yellow_Leaf_Curl_Virus', 'Tomato_Tomato_mosaic_virus',
                          'Tomato___healthy']

            # Get the disease name
            if result_index >= 0 and result_index < len(class_name):
                predicted_disease = class_name[result_index]
            else:
                st.error("The model predicted an invalid index. Please try again or check the model.")
                st.stop() 
            if predicted_disease != "Not in Dataset" :
                
            

                if "healthy" not in predicted_disease:  # Only proceed if not healthy
                    st.success(f"Model Prediction: {predicted_disease}")

                    # Google Custom Search API integration to fetch information
                    api_key = "AIzaSyArEi1aGVDCju2zfSwgoS-1xxq-ozz7-t8"  # Your API key
                    search_engine_id = "a2779f8bc3d1d4416"  # Your Search Engine ID
                    search_query = f"{result_index} disease remedy and information"
                    search_results = google_search(search_query, api_key, search_engine_id)

                    # Show the search result
                    if 'items' in search_results:
                        first_result = search_results['items'][0]
                        title = first_result.get('title', 'No Title Available')
                        snippet = first_result.get('snippet', 'No Description Available')
                        disease_name = first_result.get('title', 'Unknown Disease')
                        google_search_link = f"https://www.google.com/search?q={predicted_disease.replace(' ', '+')}+remedies"

                        # Remove the repetitive snippet concatenation
                        st.write(f"Disease Information : {snippet}")
                        st.write(f"Remedy Information : Visit this [link]({google_search_link}) for remedies")
                    

                    else:
                        st.write("No information available for this disease.")
                else:
                    st.success("The plant is healthy! No disease detected.")
            else:
                st.write("Please upload a valid image to make a prediction.")