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

# Set the FACE_SUBSCRIPTION_KEY environment variable with your key as the value.
# This key will serve all examples in this document.
KEY = os.environ['FACE_SUBSCRIPTION_KEY']

# Set the FACE_ENDPOINT environment variable with the endpoint from your Face service in Azure.
# This endpoint will be used in all examples in this quickstart.
ENDPOINT = os.environ['FACE_ENDPOINT']
# FaceClient	This class represents your authorization to use the Face service, and you need it for all Face functionality. You instantiate it with your subscription information, and you use it to produce instances of other classes.
# FaceOperations	This class handles the basic detection and recognition tasks that you can do with human faces.
# DetectedFace	This class represents all of the data that was detected from a single face in an image. You can use it to retrieve detailed information about the face.
# FaceListOperations	This class manages the cloud-stored FaceList constructs, which store an assorted set of faces.
# PersonGroupPersonOperations	This class manages the cloud-stored Person constructs, which store a set of faces that belong to a single person.
# PersonGroupOperations	This class manages the cloud-stored PersonGroup constructs, which store a set of assorted Person objects.
# ShapshotOperations	This class manages the Snapshot functionality; you can use it to temporarily save all of your cloud-based face data and migrate that data to a new Azure subscription.

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

# Detect a face in an image that contains a single face
single_face_image_url = 'https://www.biography.com/.image/t_share/MTQ1MzAyNzYzOTgxNTE0NTEz/john-f-kennedy---mini-biography.jpg'
single_image_name = os.path.basename(single_face_image_url)
detected_faces = face_client.face.detect_with_url(url=single_face_image_url)
if not detected_faces:
    raise Exception('No face detected from image {}'.format(single_image_name))

# Display the detected face ID in the first single-face image.
# Face IDs are used for comparison to faces (their IDs) detected in other images.
print('Detected face ID from', single_image_name, ':')
for face in detected_faces: print (face.face_id)
print()

# Save this ID for use in Find Similar
first_image_face_ID = detected_faces[0].face_id

# Detect the faces in an image that contains multiple faces
# Each detected face gets assigned a new ID
multi_face_image_url = "http://www.historyplace.com/kennedy/president-family-portrait-closeup.jpg"
multi_image_name = os.path.basename(multi_face_image_url)
detected_faces2 = face_client.face.detect_with_url(url=multi_face_image_url)

# Search through faces detected in group image for the single face from first image.
# First, create a list of the face IDs found in the second image.
second_image_face_IDs = list(map(lambda x: x.face_id, detected_faces2))
# Next, find similar face IDs like the one detected in the first image.
similar_faces = face_client.face.find_similar(face_id=first_image_face_ID, face_ids=second_image_face_IDs)
if not similar_faces[0]:
    print('No similar faces found in', multi_image_name, '.')

# Print the details of the similar faces detected
print('Similar faces found in', multi_image_name + ':')
for face in similar_faces:
    first_image_face_ID = face.face_id
    # The similar face IDs of the single face image and the group image do not need to match, they are only used for identification purposes in each image.
    # The similar faces are matched using the Cognitive Services algorithm in find_similar().
    face_info = next(x for x in detected_faces2 if x.face_id == first_image_face_ID)
    if face_info:
        print('  Face ID: ', first_image_face_ID)
        print('  Face rectangle:')
        print('    Left: ', str(face_info.face_rectangle.left))
        print('    Top: ', str(face_info.face_rectangle.top))
        print('    Width: ', str(face_info.face_rectangle.width))
        print('    Height: ', str(face_info.face_rectangle.height))