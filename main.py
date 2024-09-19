from flask import Flask, render_template, request, send_file, redirect, make_response
from gtts import gTTS
from PIL import Image
from io import BytesIO
import google.generativeai as palm
import requests
from IPython.display import Audio

app = Flask(__name__,template_folder='src')

# Preload model and language codes
palm.configure(api_key="AIzaSyBulnTRagspeZJ-acilW_UQCPn5mb3SAcQ")
mod = palm.GenerativeModel(model_name="gemini-1.5-flash")

language_codes = {
    "Afrikaans": "af",
    "Arabic": "ar",
    "Bengali": "bn",
    "Bulgarian": "bg",
    "Catalan": "ca",
    "Chinese (Mandarin)": "zh-CN",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "English (US)": "en-US",
    "English (UK)": "en-UK",
    "Esperanto": "eo",
    "Filipino": "tl",
    "Finnish": "fi",
    "French": "fr",
    "German": "de",
    "Greek": "el",
    "Gujarati": "gu",
    "Hebrew": "he",
    "Hindi": "hi",
    "Hungarian": "hu",
    "Icelandic": "is",
    "Indonesian": "id",
    "Irish": "ga",
    "Italian": "it",
    "Japanese": "ja",
    "Kannada": "kn",
    "Korean": "ko",
    "Latin": "la",
    "Latvian": "lv",
    "Lithuanian": "lt",
    "Malay": "ms",
    "Marathi": "mr",
    "Norwegian": "no",
    "Persian": "fa",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Serbian": "sr",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Spanish": "es",
    "Swahili": "sw",
    "Swedish": "sv",
    "Tamil": "ta",
    "Telugu": "te",
    "Thai": "th",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Vietnamese": "vi",
    "Welsh": "cy"
}

def generate_audio_description(img, lang, for_notebook=False):
    """Generates a description of the image in the specified language and converts it to audio."""
    language = language_codes.get(lang)
    if not language:
        raise ValueError("Unsupported language")

    # Generate content using PaLM model
    description_text = mod.generate_content([f"describe in {lang} articulately", img]).text

    # Convert description text to speech
    tts = gTTS(text=description_text, lang=language, slow=False)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    if for_notebook:
        return Audio(mp3_fp.read(), autoplay=True)

    return mp3_fp

@app.route('/')
def index():
    return render_template('index.html', language_codes=language_codes)

@app.route('/upload', methods=['POST'])
def upload():
    """Handles image upload or image URL and generates an audio description."""
    image_file = request.files.get('image')
    image_url = request.form.get('image_url')
    language = request.form.get('language')

    if not language:
        return redirect('/')

    try:
        # Check if an image file is uploaded
        if image_file: 
            img = Image.open(image_file.stream)
        # Else check if an image URL is provided
        elif image_url:
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
        else:
            return redirect('/')

        # Generate audio description
        audio_file = generate_audio_description(img, language)

        # Serve the audio file inline (not for download)
        response = make_response(audio_file.read())
        response.headers['Content-Type'] = 'audio/mpeg'
        response.headers['Content-Disposition'] = 'inline; filename=audio_description.mp3'
        return response

    except Exception as e:
        print(f"Error: {e}")
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
