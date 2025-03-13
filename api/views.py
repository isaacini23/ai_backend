import os
import subprocess
import cv2
import numpy as np
from rest_framework.response import Response
from rest_framework.decorators import api_view
import speech_recognition as sr
import pytesseract
from PIL import Image
from django.core.files.storage import default_storage
from .models import Transcription
from paddleocr import PaddleOCR

from .serializers import TranscriptionSerializer

# Define storage path
AUDIO_UPLOAD_FOLDER = "media/uploads/audio/"

# Ensure the folder exists
os.makedirs(AUDIO_UPLOAD_FOLDER, exist_ok=True)

@api_view(['POST'])
def transcribe_audio(request):
    """Convert uploaded audio file to text and save it to a folder."""
    print("✅ Received speech-to-text request")

    if 'audio' not in request.FILES:
        print("❌ No audio file uploaded")
        return Response({'error': 'No audio file uploaded'}, status=400)

    audio_file = request.FILES['audio']
    file_name = audio_file.name
    file_path = os.path.join(AUDIO_UPLOAD_FOLDER, file_name)

    # Save file manually to the folder
    with open(file_path, 'wb') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)

    print(f"🔍 Saved audio file: {file_path}")

    # Convert to WAV if needed
    wav_path = file_path.rsplit(".", 1)[0] + ".wav"
    
    try:
        print("🎵 Converting audio to WAV...")
        subprocess.run(
            ["ffmpeg", "-i", file_path, "-ar", "16000", "-ac", "1", "-sample_fmt", "s16", wav_path],
            check=True,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )

        if not os.path.exists(wav_path):
            print("❌ WAV conversion failed")
            return Response({'error': 'Failed to convert audio to WAV'}, status=500)

        print("✅ Audio converted successfully")

        # Process audio with speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            print("🎤 Listening to audio...")
            audio = recognizer.record(source)

        try:
            print("🧠 Performing speech recognition...")
            text = recognizer.recognize_google(audio)
            print(f"📜 Transcription: {text}")

            return Response({"transcription": text, "file_path": wav_path})

        except sr.UnknownValueError:
            return Response({"error": "Could not understand audio"}, status=400)
        except sr.RequestError:
            return Response({"error": "Speech recognition service unavailable"}, status=503)

    except subprocess.CalledProcessError:
        return Response({'error': 'ffmpeg failed to convert audio'}, status=500)






# Define storage path
IMAGE_UPLOAD_FOLDER = "media/uploads/images/"

# Initialize PaddleOCR (supports multiple languages)
ocr = PaddleOCR(lang='en')

@api_view(['POST'])
def ocr_image(request):
    """Extract text from an uploaded image using PaddleOCR."""
    print("✅ Received OCR request")

    if 'image' not in request.FILES:
        return Response({'error': 'No image file uploaded'}, status=400)

    # Save the uploaded file
    image_file = request.FILES['image']
    file_name = image_file.name
    file_path = os.path.join(IMAGE_UPLOAD_FOLDER, file_name)

    with open(file_path, 'wb') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)

    print(f"🔍 Saved image file: {file_path}")

    # Perform OCR with PaddleOCR
    try:
        result = ocr.ocr(file_path, cls=True)

        # Extract text from result
        extracted_text = "\n".join([word[1][0] for line in result for word in line])

        print(f"📜 Extracted Text:\n{extracted_text}")

        return Response({"text": extracted_text, "file_path": file_path})

    except Exception as e:
        print(f"❌ OCR Error: {e}")
        return Response({"error": "OCR failed", "details": str(e)}, status=500)
def get_transcriptions(request):
    transcriptions = Transcription.objects.all()
    serializer = TranscriptionSerializer(transcriptions, many=True)
    return Response(serializer.data)