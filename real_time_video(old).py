#!/usr/bin/env python3

from keras.preprocessing.image import img_to_array
import imutils
import cv2
from keras.models import load_model
import numpy as np
import keras.backend
import time
# from models.cnn import resize
import tensorflow

# parameters for loading data and images
detection_model_path = 'haarcascade_files/haarcascade_frontalface_default.xml'
# emotion_model_path = 'models/best_model/MUL_KSIZE_MobileNet_v2_best_bottleneck_prelu_0.5_16-0.68-0.69.hdf5'
emotion_model_path = 'models/best_model/MUL_KSIZE_MobileNet_v2_best.hdf5'
# emotion_model_path = 'models/MobileNet-0.34-0.34.hdf5'
# hyper-parameters for bounding boxes shape
EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised",
            "neutral"]

def main():
    # loading models
    keras.backend.clear_session()
    face_detection = cv2.CascadeClassifier(detection_model_path)
    emotion_classifier = load_model(emotion_model_path, compile=False, custom_objects={'tf': tensorflow})

    # feelings_faces = []
    # for index, emotion in enumerate(EMOTIONS):
    #     feelings_faces.append(cv2.imread('emojis/' + emotion + '.png', -1))

    # starting video streaming
    cv2.namedWindow('cam')
    camera = cv2.VideoCapture(2)
    # camera = cv2.VideoCapture("2018010301.mp4")

    while True:
        start = time.time()
        ret, frame = camera.read()
        # frame = camera.read()[1]
        # reading the frame
        frame = imutils.resize(frame, width=300)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detection.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
                                                flags=cv2.CASCADE_SCALE_IMAGE)

        canvas = np.zeros((250, 300, 3), dtype="uint8")
        frameClone = frame.copy()
        if len(faces) > 0:
            faces = sorted(faces, reverse=True, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = faces
            # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare
            # the ROI for classification via the CNN
            roi = gray[fY:fY + fH, fX:fX + fW]
            roi = cv2.resize(roi, (48, 48))
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)

            preds = emotion_classifier.predict(roi)[0]
            emotion_probability = np.max(preds)
            label = EMOTIONS[preds.argmax()]

            for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
                # construct the label text
                text = "{}: {:.2f}%".format(emotion, prob * 100)

                # draw the label + probability bar on the canvas
                # emoji_face = feelings_faces[np.argmax(preds)]

                w = int(prob * 300)
                cv2.rectangle(canvas, (7, (i * 35) + 5),
                              (w, (i * 35) + 35), (0, 0, 255), -1)
                cv2.putText(canvas, text, (10, (i * 35) + 23),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                            (255, 255, 255), 2)
                cv2.putText(frameClone, label, (fX, fY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH),
                              (0, 0, 255), 2)
        #    for c in range(0, 3):
        #        frame[200:320, 10:130, c] = emoji_face[:, :, c] * \
        #        (emoji_face[:, :, 3] / 255.0) + frame[200:320,
        #        10:130, c] * (1.0 - emoji_face[:, :, 3] / 255.0)
        end = time.time()
        seconds = end - start
        if seconds == 0:
            fps = 0
        else:
            fps = 1 / seconds
        # fps=1
        cv2.putText(frameClone, "FPS: " + str('%.0f' % fps), (5, 15), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255),
                    1, 0)

        cv2.imshow('cam', frameClone)
        cv2.imshow("Probabilities", canvas)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()