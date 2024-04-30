import cv2
import os


def blur_faces_or_eyes(image_path, blur_type='faces'):
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_eye.xml')

    img = cv2.imread(image_path)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if blur_type == 'faces':
        targets = face_cascade.detectMultiScale(
            gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    elif blur_type == 'eyes':
        targets = eye_cascade.detectMultiScale(
            gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))
    else:
        print("Invalid blur type. Please choose 'faces' or 'eyes'.")
        return

    for (x, y, w, h) in targets:
        if blur_type == 'faces':
            blur_region = img[y:y+h, x:x+w]
            cv2.rectangle(img, (x-5, y-5), (x+w+5, y+h+5), (0, 165, 255), 2)
        elif blur_type == 'eyes':
            blur_region = img[y:y+h, x:x+w]
            cv2.rectangle(img, (x-5, y-5), (x+w+5, y+h+5), (0, 165, 255), 2)

        blurred = cv2.medianBlur(blur_region, 35)

        if blur_type == 'faces':
            img[y:y+h, x:x+w] = blurred
        elif blur_type == 'eyes':
            img[y:y+h, x:x+w] = blurred

    output_path = f"blurred_{os.path.basename(image_path)}"
    cv2.imwrite(output_path, img)
    return output_path
