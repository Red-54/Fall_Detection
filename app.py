import streamlit as st
import cv2
import urllib.request
import numpy as np
import time
from ultralytics import YOLO
import os
from twilio.rest import Client
import geocoder

# Load YOLO model
model = YOLO(f"fall.pt")

# Load credentials from Streamlit secrets
account_sid = st.secrets["twilio_account_sid"]
auth_token = st.secrets["twilio_auth_token"]
FROM_NUMBER = st.secrets["twilio_from_number"]
TO_NUMBER = st.secrets["twilio_to_number"]

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Streamlit page configuration
st.set_page_config(page_title="Fall Detection System", layout="wide")
st.title("Fall Detection and Alert System")

# Input for camera source
camera_source = st.selectbox("Select Camera Source", ("ESP32-CAM", "Webcam"))
url = ""
if camera_source == "ESP32-CAM":
    url = st.text_input("Enter ESP32-CAM Stream URL", "http://x.x.x.x/cam-lo.jpg")

# Input for fall detection threshold
fall_detection_threshold = st.slider("Set Fall Detection Threshold (seconds)", min_value=1, max_value=30, value=5)

# Function to send SMS
@st.cache_data
def send_sms(body):
    try:
        message_created = client.messages.create(
            body=body,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        st.success(f"SMS sent with SID: {message_created.sid}")
    except Exception as e:
        st.error(f"Error sending SMS: {e}")

# Function to get geolocation
@st.cache_data
def get_geolocation():
    if camera_source == "ESP32-CAM" and url:
        ip = url.split("//")[-1].split("/")[0]  # Extract IP from ESP32-CAM URL
        ip_info = geocoder.ip(ip)
    else:
        ip_info = geocoder.ip("me")  # Gets the geolocation of the laptop's public IP

    if ip_info.latlng:
        return f"Fall DETECTED! Location: {ip_info.city}, Coordinates: {ip_info.latlng[0]}, {ip_info.latlng[1]}"
    return "Unable to obtain geolocation."

# Function to process the video stream
def process_stream():
    fall_detected_time = None  # To track when the fall was first detected

    cap = None
    if camera_source == "Webcam":
        cap = cv2.VideoCapture(0)

    while True:
        try:
            if camera_source == "ESP32-CAM":
                # Download image from the URL
                with urllib.request.urlopen(url) as response:
                    img_np = np.array(bytearray(response.read()), dtype=np.uint8)
                    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            else:
                # Capture frame from webcam
                if cap is None or not cap.isOpened():
                    cap = cv2.VideoCapture(0)
                ret, img = cap.read()
                if not ret:
                    st.error("Failed to access webcam")
                    break

            if img is not None:
                # Object detection
                results = model(img, conf=0.8)

                fall_detected = False

                # Draw bounding boxes
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy.tolist()[0]
                        c = box.cls
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        label = model.names[int(c)]

                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(
                            img,
                            label,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 255, 0),
                            2,
                        )

                        if label == 'Fall-Detected':
                            fall_detected = True
                            if fall_detected_time is None:
                                fall_detected_time = time.time()  # Start timer

                if fall_detected:
                    elapsed_time = time.time() - fall_detected_time
                    if elapsed_time > fall_detection_threshold:
                        alert = get_geolocation()
                        send_sms(alert)
                        fall_detected_time = None  # Reset after sending alert
                else:
                    fall_detected_time = None  # Reset if no fall detected

                # Display the image in Streamlit
                st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), channels="RGB", caption="Camera Feed")

        except urllib.error.HTTPError as e:
            st.error(f"HTTP Error: {e.code} - {e.reason}")
            time.sleep(1)
        except Exception as e:
            st.error(f"Error: {e}")
            time.sleep(1)

    if cap:
        cap.release()

# Start processing the stream if the user clicks the button
if st.button("Start Fall Detection"):
    if camera_source == "ESP32-CAM" and not url:
        st.error("Please enter a valid ESP32-CAM stream URL.")
    else:
        process_stream()

