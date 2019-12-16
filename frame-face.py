import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType

#API Key del servicio de Azure, se puede obtener en el portal de Azure
KEY = 'API_KEY'

# Endpoint de la conexión, se puede obtener en el portal de Azure
ENDPOINT = 'FACE_ENDPOINT'

# Crea un cliente usando los datos suministrados para el FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

# Detecta una cara en una imagen que contiene una sola cara
single_face_image_url = 'https://pbs.twimg.com/profile_images/1019274579540430848/F1TZagiu.jpg'
single_image_name = os.path.basename(single_face_image_url)
detected_faces = face_client.face.detect_with_url(url=single_face_image_url)
if not detected_faces:
    raise Exception('No face detected from image {}'.format(single_image_name))

# Convierte los puntos en un rectangulo
def getRectangle(faceDictionary):
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top
    right = left + rect.width
    bottom = top + rect.height
    
    return ((left, top), (right, bottom))


# Descarga la imagen de la url
response = requests.get(single_face_image_url)
img = Image.open(BytesIO(response.content))

# Para cada cara dibuja un rectangulo rojo
print('Drawing rectangle around face... see popup for results.')
draw = ImageDraw.Draw(img)
for face in detected_faces:
    draw.rectangle(getRectangle(face), outline='red')

# Muestra la imagen en un pop-up
img.show()