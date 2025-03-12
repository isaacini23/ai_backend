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
from .serializers import TranscriptionSerializer

@api_view(['POST'])
def transcribe_audio(request):
    if 'audio' not in request.FILES:
        return Response({'error': 'No audio file uploaded'}, status=400)

    audio_file = request.FILES['audio']
    file_path = default_storage.save(audio_file.name, audio_file)

    # Convert FLAC to WAV if needed
    wav_path = file_path.rsplit(".", 1)[0] + ".wav"
    subprocess.run(["ffmpeg", "-i", file_path, "-ar", "16000", "-ac", "1", "-sample_fmt", "s16", wav_path], check=True)

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        return Response({"transcription": text})
    except sr.UnknownValueError:
        return Response({"error": "Could not understand audio"})
    except sr.RequestError:
        return Response({"error": "Speech recognition service unavailable"})

# ✅ Improved OCR with OpenCV
def preprocess_image(image_path):
    """Enhance image quality using OpenCV for better OCR results."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)  # Resize to improve OCR accuracy
    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Apply thresholding
    return Image.fromarray(thresh)

@api_view(['POST'])
def ocr_image(request):
    if 'image' not in request.FILES:
        return Response({'error': 'No image file uploaded'}, status=400)

    image_file = request.FILES['image']
    file_path = default_storage.save(image_file.name, image_file)

    # Process image with OpenCV
    processed_image = preprocess_image(file_path)

    # Perform OCR
    text = pytesseract.image_to_string(processed_image, lang="eng")

    # Save transcription
    transcription = Transcription.objects.create(image_file=file_path, text=text)
    serializer = TranscriptionSerializer(transcription)

    return Response(serializer.data)

@api_view(['GET'])
def get_transcriptions(request):
    transcriptions = Transcription.objects.all()
    serializer = TranscriptionSerializer(transcriptions, many=True)
    return Response(serializer.data)
