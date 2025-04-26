import streamlit as st
import requests
import numpy as np
from PIL import Image
from model import get_caption_model, generate_caption
import streamlit.components.v1 as components


@st.cache(allow_output_mutation=True)
def get_model():
    try:
        return get_caption_model()
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None


caption_model = get_model()

img_url = st.text_input(label='Enter Image URL')

if img_url:
    try:
        img = Image.open(requests.get(img_url, stream=True).raw)
        st.image(img)

        img = np.array(img)
        if caption_model is not None:
            pred_caption = generate_caption(img, caption_model)
            st.write(pred_caption)
        else:
            st.write("Model not loaded, cannot generate caption.")
    except Exception as e:
        st.error(f"Error processing image URL: {e}")

# Embed the index.html content inside Streamlit app
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Image Captioning Frontend</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f9f9f9;
        }
        .container {
            max-width: 600px;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:disabled {
            background-color: #aaa;
            cursor: not-allowed;
        }
        img {
            max-width: 100%;
            margin-top: 20px;
            border-radius: 8px;
        }
        .caption {
            margin-top: 20px;
            font-size: 1.2em;
            color: #333;
        }
        .error {
            margin-top: 20px;
            color: red;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Image Captioning</h2>
        <label for="imageUrl">Enter Image URL:</label>
        <input type="text" id="imageUrl" placeholder="https://example.com/image.jpg" />
        <button id="generateBtn" disabled>Generate Caption</button>
        <div id="imageContainer"></div>
        <div id="caption" class="caption"></div>
        <div id="error" class="error"></div>
    </div>

    <script>
        const imageUrlInput = document.getElementById('imageUrl');
        const generateBtn = document.getElementById('generateBtn');
        const imageContainer = document.getElementById('imageContainer');
        const captionDiv = document.getElementById('caption');
        const errorDiv = document.getElementById('error');

        imageUrlInput.addEventListener('input', () => {
            generateBtn.disabled = !imageUrlInput.value.trim();
            captionDiv.textContent = '';
            errorDiv.textContent = '';
            imageContainer.innerHTML = '';
        });

        generateBtn.addEventListener('click', async () => {
            const url = imageUrlInput.value.trim();
            if (!url) return;

            captionDiv.textContent = '';
            errorDiv.textContent = '';
            imageContainer.innerHTML = '';

            // Show the image
            const img = document.createElement('img');
            img.src = url;
            img.alt = 'Input Image';
            imageContainer.appendChild(img);

            // Call backend API to get caption
            try {
                const response = await fetch('/api/generate_caption', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ image_url: url })
                });

                if (!response.ok) {
                    throw new Error('Failed to get caption from server');
                }

                const data = await response.json();
                if (data.caption) {
                    captionDiv.textContent = data.caption;
                } else {
                    captionDiv.textContent = 'No caption returned';
                }
            } catch (error) {
                errorDiv.textContent = error.message;
            }
        });
    </script>
</body>
</html>
"""

components.html(html_content, height=700)