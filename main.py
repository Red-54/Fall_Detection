import cv2
import urllib.request
import numpy as np
import time
from ultralytics import YOLO
import os
from geopy.geocoders import Nominatim
from twilio.rest import Client
import geocoder

model = YOLO(f"{os.getcwd()}/weed.pt")

# Twilio credentials (replace with your actual credentials)
account_sid = 'xxxxxx  # Your Twilio Account SID
auth_token = 'xxxxxxx'                # Your Twilio Auth Token
FROM_NUMBER = '+xxxxxxx'                        # Your Twilio phone number
TO_NUMBER = '+xxxxxxxx'                         # Recipient's phone number

# Initialize Twilio client
client = Client(account_sid, auth_token)

url = "http://x.x.x.x/cam-lo.jpg" # Replace with your feed


# Function to get geolocation (latitude, longitude, address)
# def get_geolocation():
#     # geolocator = Nominatim(user_agent="geoapiExercises")
#     # location = geolocator.geocode("Pune Maharashtra")  # Change the location if necessary
    
#     # if location:
#     #     return location.latitude, location.longitude, location.address
#     # else:
#     #     return None, None, None

#     return "834.60", "764.23", "Pune Maharashtra"

# # Function to send an SMS alert using Twilio
# def send_sms_alert(latitude, longitude, address):
#     message = f"Fall detected! Location: {address} (Lat: {latitude}, Lon: {longitude})"
    
#     try:
#         message_created = client.messages.create(
#             body=message,
#             from_=FROM_NUMBER,
#             to=TO_NUMBER
#         )
#         print(f"SMS sent with SID: {message_created.sid}")
#     except Exception as e:
#         print(f"Error sending SMS: {e}")

def send_sms(body):
    message = body
    try:
        message_created = client.messages.create(
            body=message,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        print(f"SMS sent with SID: {message_created.sid}")
    except Exception as e:
        print(f"Error sending SMS: {e}")
    print(f"SMS sent: {message.sid}")

# Function to get geolocation based on IP
def get_geolocation():
    ip_info = geocoder.ip("me")  # Gets the geolocation of the public IP
    if ip_info.latlng:
        return f"Weed DETECTED! Location: {ip_info.city}, Coordinates: {ip_info.latlng[0]}, {ip_info.latlng[1]}"
    return "Unable to obtain geolocation."

def capture_images(url):
    fall_detected_time = None  # To track when the fall was first detected
    fall_detection_threshold = -1
    while True:
        try:
            # Download image from the URL
            with urllib.request.urlopen(url) as response:
                img_np = np.array(bytearray(response.read()), dtype=np.uint8)
                img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

                if img is not None:
                    # Fall detection
                    results = model(img, conf=0.8)
                    
                    fall_detected = False
                    # Draw bounding boxes
                    for result in results:
                        boxes = result.boxes
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy.tolist()[0]
                            c = box.cls
                            x1, y1, x2, y2 = int(x1), int(y1), int(y2), int(y2)
                            label = model.names[int(c)]
                            print(label)
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
                            # Get geolocation
                            alert = get_geolocation()
                            send_sms(alert)
                            fall_detected_time = None  # Reset after sending alert
                    else:
                        fall_detected_time = None  # Reset if no fall detected               

                    cv2.imshow("ESP32-CAM Image", img)

                # Exit the loop when 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    capture_images(url)
