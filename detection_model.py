# import pyttsx3
import cv2
import numpy as np
import urllib.request
import time
from datetime import datetime
import os
from playsound import playsound 
# import cloudinary
# from cloudinary.uploader import upload

# cloudinary.config(
#     cloud_name="",
#     api_key="",
#     api_secret=""
# )

# def upload_to_cloudinary(image_path):
#     filename = os.path.basename(image_path)
#     folder_name = 'alert'
#     public_id = f"{folder_name}/{filename}"
#     result = upload(image_path, public_id=public_id)
#     return result['secure_url']


# engine = pyttsx3.init()
# engine.setProperty('rate', 180) 
# engine.setProperty('volume', 0.9)


stream_url = 'http://192.168.1.41/cam-mid.jpg'
print("Starting: ", stream_url)

# YOLOv3 parameters
whT = 320  
confThreshold = 0.3  
nmsThreshold = 0.3 
classesfile = 'coco.names'
classNames = []

# Load class names
with open(classesfile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

# YOLOv3 model configuration and weights
modelConfig = 'yolov3.cfg'
modelWeights = 'yolov3.weights'
net = cv2.dnn.readNetFromDarknet(modelConfig, modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Function to find and process objects
def findObject(outputs, img, timestamp):  
    hT, wT, cT = img.shape
    bbox = [] 
    classIds = []
    confs = []
    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold: 
                w, h = int(det[2]*wT), int(det[3]*hT)
                x, y = int((det[0]*wT)-w/2), int((det[1]*hT)-h/2)
                bbox.append([x, y, w, h])
                classIds.append(classId)
                confs.append(float(confidence))

    indices = cv2.dnn.NMSBoxes(bbox, confs, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]

        object_name = classNames[classIds[i]]
        if object_name == 'person':
            print("Detected Object:", object_name)
            playsound("alert_sound.mp3")
            # engine.say(object_name + " Ahead")
            # engine.runAndWait()
            
            
            alert_folder = 'static/alert'
            if not os.path.exists(alert_folder):
                os.makedirs(alert_folder)
            timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
            file_path = os.path.join(alert_folder, f"person_detected_{timestamp_str}.jpg")
            cv2.imwrite(file_path, img)
            # cloudinary_url = upload_to_cloudinary(file_path)


        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 255), 2)
        cv2.putText(img, f'{classNames[classIds[i]].upper()} {int(confs[i]*100)}%', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

# Main loop
while True:
    stream = None
    while stream is None:
        try:
            stream = urllib.request.urlopen(stream_url)
        except:
            print("Failed to open stream. Retrying in 5 seconds...")
            time.sleep(5)
            continue
    
    data = bytes()
    while True:
        data += stream.read(1024)
        a = data.find(b'\xff\xd8')
        b = data.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = data[a:b+2]
            data = data[b+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            break
    
    blob = cv2.dnn.blobFromImage(img, 1/255, (whT, whT), [0, 0, 0], 1, crop=False)
    net.setInput(blob)
    outputNames = net.getUnconnectedOutLayersNames()
    outputs = net.forward(outputNames)
    findObject(outputs, img, datetime.now())  
    cv2.imshow('Image', img)  
    
    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
