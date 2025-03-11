from rest_framework.response import Response
from rest_framework.decorators import api_view
import speech_recognition as sr
import pytesseract
from PIL import Image

@api_view(['POST'])
def transcribe_audio(request):
    recognizer = sr.Recognizer()
    audio_file = request.FILES['audio']
    
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    
    return Response({"transcription": text})

@api_view(['POST'])
def ocr_image(request):
    image_file = request.FILES['image']
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    
    return Response({"recognized_text": text})
