# Real-Time Fall Detection System using YOLOv11 and ESP32-CAM

This project implements a real-time fall detection system that utilizes an ESP32-CAM module to stream live video to a server for processing. The system is designed to be particularly beneficial for assisting the elderly and individuals with disabilities who are at increased risk of falls, enabling rapid response times in critical situations.

## Features

* **Real-time Fall Detection:**  Continuously monitors live video streams from an ESP32-CAM to detect falls as they occur.
* **YOLOv11 Object Detection:**  Uses a pre-trained YOLOv11 object detection model to accurately identify falls in video frames.
* **Geolocation-Based Alerts:**  Upon detecting a fall that lasts for a specified duration, the system sends SMS alerts containing location coordinates (using geolocation APIs) to designated contacts. 
* **Twilio Integration:**  Leverages the Twilio API for sending SMS notifications. 

## How it Works

1. **Video Streaming:** The ESP32-CAM module captures video and continuously streams it to a server using a network connection (Wi-Fi). 
2. **Fall Detection:** The server runs the YOLOv11 model, which analyzes each video frame in real-time to detect if a person has fallen. 
3. **Alert Trigger:**  If a fall is detected and persists for a predetermined time threshold (to minimize false alarms), the system triggers an alert.
4. **Notification with Geolocation:** An SMS message is sent to designated emergency contacts (caregivers, family members) containing information about the fall and the estimated location of the individual. 

## Project Structure

```
├── main.py             # Main Python script for video processing and alerts
├── fall.pt            # YOLOv11 model weights file
└── requirements.txt    # List of Python dependencies
```

## Getting Started

1. **Prerequisites:**
   * **ESP32-CAM Setup:** You'll need an ESP32-CAM module set up to stream video to your server. There are many online tutorials available for this setup. 
   * **Twilio Account:** Create a Twilio account ([https://www.twilio.com/](https://www.twilio.com/)) and get your Account SID, Auth Token, and a Twilio phone number. 
   * **Geolocation API (Optional):**  Choose a geolocation API and obtain the necessary API keys (if required). You can use IP-based geolocation or services like Nominatim.

2. **Clone the Repository:**
   ```bash
   git clone git@github.com:Red-54/Fall_Detection.git
   cd Fall_Detection
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration:**
   * **`main.py`:** 
      * Update the URL to your ESP32-CAM's video stream. 
      * Configure your Twilio credentials (Account SID, Auth Token, Twilio phone number).
      * Set the recipient's phone number for SMS alerts. 
      * Adjust the `fall_detection_threshold` (in seconds) to control how long a fall must be detected before an alert is sent. 
   * **Geolocation:**  Implement the geolocation logic in `main.py` using your chosen API. 

5. **Run the System:**
   ```bash
   python main.py
   ```

## Accuracy

The YOLOv11 model used in this project has achieved an 88\% mAP50 accuracy on a custom dataset of fall detection scenarios. Further improvements in accuracy can be achieved through:

* **Dataset Enhancement:** Training the model on a larger and more diverse dataset. 
* **Hyperparameter Tuning:** Experimenting with different model parameters.
* **Environmental Considerations:**  Optimizing for specific lighting conditions and environments. 

## Future Improvements

* **Web Interface/Dashboard:** Create a user-friendly web interface to visualize real-time video, fall events, and location data.
* **Fall Severity Estimation:**  Implement algorithms to estimate the severity of falls (e.g., based on impact or duration).
* **Cloud Integration:** Deploy the system on a cloud platform for scalability and reliability. 

## Contributing

Contributions to this project are welcome! Please feel free to fork the repository and submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 


**Remember to:**

* **Replace Placeholders:**  Update the README with your actual GitHub username, project name, and any other relevant details.
* **Add a License File:** Create a `LICENSE` file in your repository (e.g., choose the MIT License). 
* **Clear Documentation:** Provide clear instructions on how to set up and run the project. 
* **Screenshots/GIFs:** Consider adding screenshots or GIFs to your README to visually showcase how the project works. 


