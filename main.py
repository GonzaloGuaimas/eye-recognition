import cv2
import numpy as np
import dlib
from math import hypot

#font
font = cv2.FONT_HERSHEY_SIMPLEX

#video capture
cap = cv2.VideoCapture(0)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

def get_gaze_ratio(eye_points, facial_landmarks):
    # Gaze detection
    left_eye_region = np.array([(facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),
                        (facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),
                        (facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),
                        (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),
                        (facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),
                        (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)], np.int32)

    height, width, _ = frame.shape
    mask = np.zeros((height, width), np.uint8)
    cv2.polylines(mask, [left_eye_region], True, 255, 2)
    cv2.fillPoly(mask, [left_eye_region], 255)
    eye = cv2.bitwise_and(gray, gray, mask=mask)

    min_x = np.min(left_eye_region[:, 0])
    max_x = np.max(left_eye_region[:, 0])
    min_y = np.min(left_eye_region[:, 1])
    max_y = np.max(left_eye_region[:, 1])
    gray_eye = eye[min_y: max_y, min_x: max_x]
    _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
    # four part
    height, width = threshold_eye.shape
    left_side_threshold = threshold_eye[0: height, 0: int(width / 2)]
    left_side_white = cv2.countNonZero(left_side_threshold)
    right_side_threshold = threshold_eye[0: height, int(width / 2): width]
    right_side_white = cv2.countNonZero(right_side_threshold)

    threshold_eye = cv2.resize(threshold_eye, None, fx=5, fy=5)
    eye = cv2.resize(gray_eye, None, fx=5, fy=5)
    cv2.imshow("Eye", eye)
    cv2.imshow("Threshold", threshold_eye)
    # cv2.imshow("Left eye", left_eye)
    cv2.imshow("Left", left_side_threshold) #eye left
    cv2.imshow("Right", right_side_threshold) #eye right

    if left_side_white == 0:
        gaze_ratio = 1
    elif right_side_white == 0:
        gaze_ratio = 5
    else:
        gaze_ratio = left_side_white / right_side_white

    
    return gaze_ratio

def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))
    hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
    ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)
    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))
    ratio = hor_line_lenght / ver_line_lenght
    return ratio

while True:
    _, frame = cap.read()
    new_frame = np.zeros((500, 500, 3), np.uint8)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        cv2.putText(frame, "anyone there???", (50, 150), font, 3, (255, 0, 0))

    for face in faces:
        landmarks = predictor(gray, face)
        #Detect Blinking
        left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2
        if blinking_ratio > 5.7:
            cv2.putText(frame, "BLINKING", (50, 150), font, 7, (255, 0, 0))

        #Show Lines
        left_point = (landmarks.part(36).x, landmarks.part(36).y)
        right_point = (landmarks.part(39).x, landmarks.part(39).y)

        center_top = midpoint(landmarks.part(37), landmarks.part(38))
        center_bottom = midpoint(landmarks.part(41), landmarks.part(40))

        hor_line = cv2.line(frame, left_point, right_point, (0,255,0), 2)
        ver_line = cv2.line(frame, center_top, center_bottom, (0,255,0), 2)
        
        # Gaze detection
        # left_eye_region = np.array([(landmarks.part(36).x, landmarks.part(36).y),
        #                     (landmarks.part(37).x, landmarks.part(37).y),
        #                     (landmarks.part(38).x, landmarks.part(38).y),
        #                     (landmarks.part(39).x, landmarks.part(39).y),
        #                     (landmarks.part(40).x, landmarks.part(40).y),
        #                     (landmarks.part(41).x, landmarks.part(41).y)], np.int32)

        # height, width, _ = frame.shape
        # mask = np.zeros((height, width), np.uint8)
        # cv2.polylines(mask, [left_eye_region], True, 255, 2)
        # cv2.fillPoly(mask, [left_eye_region], 255)
        # left_eye = cv2.bitwise_and(gray, gray, mask=mask)

        # min_x = np.min(left_eye_region[:, 0])
        # max_x = np.max(left_eye_region[:, 0])
        # min_y = np.min(left_eye_region[:, 1])
        # max_y = np.max(left_eye_region[:, 1])
        # gray_eye = left_eye[min_y: max_y, min_x: max_x]
        # _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
        # # four part
        # height, width = threshold_eye.shape
        # left_side_threshold = threshold_eye[0: height, 0: int(width / 2)]
        # left_side_white = cv2.countNonZero(left_side_threshold)
        # right_side_threshold = threshold_eye[0: height, int(width / 2): width]
        # right_side_white = cv2.countNonZero(right_side_threshold)

        # gaze_ratio = left_side_white / right_side_white

        #Gaze Detection
        gaze_ratio_left_eye = get_gaze_ratio([36, 37, 38, 39, 40, 41], landmarks)
        gaze_ratio_right_eye = get_gaze_ratio([42, 43, 44, 45, 46, 47], landmarks)
        gaze_ratio = (gaze_ratio_right_eye + gaze_ratio_left_eye) / 2

        cv2.putText(frame, str(gaze_ratio), (10, 300), font, 2, (0,0,255), 3)


        #text of Direction top right left bottom
        # if gaze_ratio <= 1:
        if gaze_ratio <= 0.5:
            cv2.putText(frame, "RIGHT", (50, 100), font, 2, (0, 0, 255), 3)
            new_frame[:] = (0, 0, 255)
        # esto es as lo normal
        # elif 1 < gaze_ratio < 1.7:
        elif 0.5 < gaze_ratio < 2.7:
            cv2.putText(frame, "CENTER", (50, 100), font, 2, (0, 0, 255), 3)
        else:
            new_frame[:] = (255, 0, 0)
            cv2.putText(frame, "LEFT", (50, 100), font, 2, (0, 0, 255), 3)



        #Images... it was there before create the function...
        # threshold_eye = cv2.resize(threshold_eye, None, fx=5, fy=5)
        # eye = cv2.resize(gray_eye, None, fx=5, fy=5)
        # cv2.imshow("Eye", eye)
        # cv2.imshow("Threshold", threshold_eye)
        # cv2.imshow("Left eye", left_eye)
        # cv2.imshow("Left", left_side_threshold) #eye left
        # cv2.imshow("Right", right_side_threshold) #eye right

    cv2.imshow("Frame", frame)
    cv2.imshow("New Frame", new_frame)
    key = cv2.waitKey(1)
    if (key) == 27: #ESC to exit
        break


cap.release()
cv2.destroyAllWindows()