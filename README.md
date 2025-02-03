# **YOLO ROI Object Detection with Notification System**

This project implements a **real-time object detection system** using **YOLOv8** and **OpenCV**. It allows users to **select a Region of Interest (ROI)** for detecting objects (specifically persons) and sends **detection notifications** to a specified API, including **geolocation data**.

## **Features**
- 📌 **Real-time Object Detection**  
  - Uses **YOLOv8** to detect objects inside a user-defined ROI.  
  - Displays bounding boxes and labels for detected objects.  

- 🖱️ **Dynamic ROI Selection**  
  - Users can select an **ROI using the mouse**.  
  - Ensures a **minimum ROI size** for accurate detection.  

- 🔔 **Notification System**  
  - Sends **detection alerts** to an external API (e.g., MongoDB-based).  
  - Includes:
    - Timestamp ⏳  
    - Object details (label, confidence, bounding box)  
    - Camera ID 📷  
    - **Geolocation data (latitude & longitude)** 🌍  

- 📍 **Geolocation Integration**  
  - Uses **IP-based geolocation** (`geocoder.ip('me')`).  
  - Updates location at regular intervals.  

- 🎥 **Optimized Video Processing**  
  - Applies **semi-transparent overlays** for better visualization.  
  - Supports **Windows and Linux**, using DirectShow API on Windows for better camera performance.  

- ⚡ **Logging & Error Handling**  
  - Ensures smooth execution with proper error handling.  

---
## **Packages Required**
- opencv-python - Computer Vision Library
- numpy - Matrix Operations
- ultralytics - YOLOv8 Object Detection
- requests - API Communication
- geocoder - Geolocation Lookup

**Execute these lines on the terminal**
```bash
pip install opencv-python numpy ultralytics requests geocoder pydantic
```

---
## **Configuration**
You can configure the API endpoint and API key inside the script:
```python
detector = YOLONDetector(
    api_url="http://your-mongodb-api-url/notifications",
    api_key="your-api-key"
)
```
Replace ```your-mongodb-api-url/notifications``` and ```your-api-key``` with your actual API details.

---
## **Installation**
### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/ayushhang/roi-object-detection-using-yolo.git
cd roi-object-detection-using-yolo
```

