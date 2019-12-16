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
single_face_image_url = 'https://www.biography.com/.image/t_share/MTQ1MzAyNzYzOTgxNTE0NTEz/john-f-kennedy---mini-biography.jpg'
single_image_name = os.path.basename(single_face_image_url)
detected_faces = face_client.face.detect_with_url(url=single_face_image_url)
#Controla la excepción en el caso de que no detecte caras en la imagen
if not detected_faces:
    raise Exception('No face detected from image {}'.format(single_image_name))

# Muestra la identificación de la cara detectada en la primera image.
# Los Face ID se utilizan para comparar las caras en otras imágenes.
print('Detected face ID from', single_image_name, ':')
for face in detected_faces: print (face.face_id)
print()

# Se guarda el ID con el fin de busca una cara similar.
first_image_face_ID = detected_faces[0].face_id

# Detecta las caras en una imagen que contiene varias caras
# A cada cara detectada se le asigna una nueva ID
multi_face_image_url = "http://www.historyplace.com/kennedy/president-family-portrait-closeup.jpg"
multi_image_name = os.path.basename(multi_face_image_url)
detected_faces2 = face_client.face.detect_with_url(url=multi_face_image_url)

# Busca en las caras detectadas en la imagen del grupo para determinar si esta el ID de la primera imagen.
# Primero, se cree una lista de los Face ID que se encuentran en la segunda imagen.
second_image_face_IDs = list(map(lambda x: x.face_id, detected_faces2))
# A continuación, se buscan los Face ID similares a las detectadas en la primera imagen.
similar_faces = face_client.face.find_similar(face_id=first_image_face_ID, face_ids=second_image_face_IDs)
if not similar_faces[0]:
    print('No similar faces found in', multi_image_name, '.')


# Convierte los puntos en un rectangulo
def getRectangle(faceDictionary):
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top
    right = left + rect.width
    bottom = top + rect.height
    
    return ((left, top), (right, bottom))

# Imprime los detalles de las caras similares detectadas
print('Similar faces found in', multi_image_name + ':')
for face in similar_faces:
    first_image_face_ID = face.face_id
    # No necesariamente los Face ID de la misma cara son iguale, solo se utilizan con fines de identificación en cada imagen.
    # Las caras similares se combinan utilizando el algoritmo de servicios cognitivos en find_similar ().
    face_info = next(x for x in detected_faces2 if x.face_id == first_image_face_ID)
    if face_info:
        print('  Face ID: ', first_image_face_ID)
        print('  Face rectangle:')
        print('    Left: ', str(face_info.face_rectangle.left))
        print('    Top: ', str(face_info.face_rectangle.top))
        print('    Width: ', str(face_info.face_rectangle.width))
        print('    Height: ', str(face_info.face_rectangle.height))
        # Descarga la imagen de la url
        response = requests.get(multi_face_image_url)
        img = Image.open(BytesIO(response.content))

        # Para cada cara dibuja un rectangulo rojo
        print('Drawing rectangle around face... see popup for results.')
        draw = ImageDraw.Draw(img)
        draw.rectangle(getRectangle(face_info), outline='red')

        # Muestra la imagen en un pop-up
        img.show()