import cv2
import numpy as np
from ultralytics import YOLO
from detector.utils.camera import Camera
from detector.utils.geocoding import Geocoder
from detector.utils.id_generator import IDGenerator
from detector.api.client import APIClient
from detector.core.roi_handler import ROIHandler
from datetime import datetime
from typing import Set
import platform

class YOLONDetector:
    def __init__(self, model_path='yolov8n.pt', api_url='http://your-mongodb-api-url', api_key='your-api-key'):
        self.camera = Camera()
        self.roi_handler = ROIHandler()
        self.geocoder = Geocoder()
        self.api_client = APIClient(api_url, api_key)
        self.model = YOLO(model_path)
        self.last_detections: Set[str] = set()
        self.location_update_time = 0
        self.LOCATION_UPDATE_INTERVAL = 60
        
    def get_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    def detect_objects(self, frame):
        display_frame = frame.copy()
        current_detections = set()
        
        roi = self.roi_handler.get_roi()
        if roi:
            x, y, w, h = roi
            roi_frame = frame[y:y+h, x:x+w]
            if roi_frame.size > 0:
                results = self.model(roi_frame, verbose=False)
                for result in results:
                    for box in result.boxes:
                        conf = float(box.conf)
                        cls = int(box.cls)
                        label = f'{self.model.names[cls]}'
                        if label.lower() == 'person' and conf > 0.5:
                            current_detections.add(label)
                            bbox = box.xyxy[0].cpu().numpy()
                            x1, y1, x2, y2 = map(int, bbox)
                            x1, x2 = x1 + x, x2 + x
                            y1, y2 = y1 + y, y2 + y
                            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                            cv2.putText(display_frame, f'{label} {conf:.2f}', (x1, y1 - 10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            if 'person' not in self.last_detections:
                                location = self.geocoder.get_location()
                                detection_info = {
                                    "id": IDGenerator.generate_id(),
                                    "timestamp": self.get_timestamp(),
                                    "detection": {
                                        "object": "person",
                                        "confidence": conf,
                                        "bbox": [x1, y1, x2, y2]
                                    },
                                    "location": {
                                        "roi": roi,
                                        "camera_id": "camera_1",
                                        "coordinates": location
                                    }
                                }
                                self.api_client.send_notification(detection_info)
        
        self.last_detections = current_detections
        return display_frame
