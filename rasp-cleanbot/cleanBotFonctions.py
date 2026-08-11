#effectuer les importation neccesaire
import serial
import time
import cv2

# Configurer le serial port
ser = serial.Serial('COM10', 9600, timeout=1)
ser.flush()


# fonction pour envoyer les commandes a arduino
def send_command(command):
    ser.write(command.encode())

# fonction pour recuperer la Distance actuelle
def get_distance():
    ser.write(b'D')  
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            try:
                # diviser la String et recuper la deuxieme partie(le nombre)
                distance_str = line.split(':')[1]
                #convertir la String en Int
                distance = int(distance_str)
                #retourner la distance
                return distance
            except (IndexError, ValueError):
                #afficher si il y a lieu une erreur
                print(f"Error parsing distance: {line}")
                return None

# Function to initialize the camera
def initialize_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None
    return cap

# Function to process a single frame and detect QR codes
def process_frame(cap, detector):
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image.")
        return None, None

    # Decode the QR Code
    data, bbox, _ = detector.detectAndDecode(frame)
    return frame, (data, bbox)

# Function to draw the bounding box around a detected QR code
def draw_box(img, bbox, data):
    if bbox is not None:
        points = [(int(bbox[0][i][0]), int(bbox[0][i][1])) for i in range(len(bbox[0]))]
        for i in range(len(points)):
            cv2.line(img, points[i - 1], points[i], (0, 255, 0), 2)
        cv2.putText(img, data, (points[0][0], points[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 1, cv2.LINE_AA)

# Function to display the camera feed
def display_camera_feed(cap, detector):
    frame, qr_data = process_frame(cap, detector)
    if frame is None:
        return  
    if qr_data and qr_data[0]:
        draw_box(frame, qr_data[1], qr_data[0])
        
        if qr_data[0] == "Avancer":
            send_command('F')
        elif qr_data[0] == "Reculer":
            send_command('B')
        elif qr_data[0] == "Droite":
            send_command('R')
        elif qr_data[0] == "Gauche":
            send_command('L')
        elif qr_data[0] == "STOP":
            send_command('S')

    cv2.imshow('Camera Feed', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return
