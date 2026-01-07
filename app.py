import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=API_KEY)


model = genai.GenerativeModel("models/gemini-2.5-flash")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        try:
            # Read image into bytes
            img_bytes = file.read()

            # Prepare content for Gemini API
            image_parts = [
                {
                    "mime_type": file.mimetype,
                    "data": img_bytes
                },
            ]
            
            # Craft the prompt for cattle breed identification
            prompt_parts = [
                "Identify the breed of this cattle. Provide a concise answer, e.g., 'Holstein', 'Angus', 'Jersey'. If unsure, state 'Unsure'.",
                image_parts[0] # The image itself
            ]

            # Make the API call
            response = model.generate_content(prompt_parts)
            
            # Extract and clean the response
            breed_identification = response.text.strip()
            return jsonify({"breed": breed_identification})

        except Exception as e:
            app.logger.error(f"Error processing image: {e}")
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
