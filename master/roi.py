import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime
import requests
import json
from typing import Set, Tuple, Optional, List
import random
import string
import geocoder
import platform

class YOLOROIDetector:
    def __init__(self, model_path='yolov8n.pt', api_url='http://your-mongodb-api-url', api_key='your-api-key'):
        # Windows-specific camera initialization
        if platform.system() == 'Windows':
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # DirectShow API for Windows
        else:
            self.cap = cv2.VideoCapture(0)
            
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.roi = None
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.last_detections: Set[str] = set()
        self.min_roi_size = 10  # Minimum ROI size in pixels
        
        # API configuration
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        # Initialize YOLO model
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"Error loading YOLO model: {str(e)}")
            raise
        
        # Create window and set mouse callback
        cv2.namedWindow('Video')
        cv2.setMouseCallback('Video', self.draw_roi)
        
        # Initialize location
        self.last_location = None
        self.location_update_time = 0
        self.LOCATION_UPDATE_INTERVAL = 60

    def validate_roi(self, x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int, int, int]:
        """
        Validate and adjust ROI coordinates to prevent zero-size regions
        """
        # Ensure minimum width and height
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        if width < self.min_roi_size:
            x2 = x1 + self.min_roi_size if x2 > x1 else x1 - self.min_roi_size
            
        if height < self.min_roi_size:
            y2 = y1 + self.min_roi_size if y2 > y1 else y1 - self.min_roi_size
        
        return (x1, y1, x2, y2)

    def get_location(self) -> Optional[Tuple[float, float]]:
        current_time = datetime.now().timestamp()
        
        if (self.last_location is None or 
            current_time - self.location_update_time > self.LOCATION_UPDATE_INTERVAL):
            try:
                g = geocoder.ip('me')
                if g.ok:
                    self.last_location = (g.lat, g.lng)
                    self.location_update_time = current_time
                    print(f"Location updated: {self.last_location}")
                else:
                    print("Failed to get location")
                    return None
            except Exception as e:
                print(f"Error getting location: {str(e)}")
                return None
                
        return self.last_location

    def generate_unique_id(self) -> str:
        characters = string.ascii_letters + string.digits
        unique_id = ''.join(random.choice(characters) for _ in range(16))
        return unique_id
    
    def send_notification(self, detection_info: dict) -> None:
        try:
            location = self.get_location()
            
            payload = {
                "id": self.generate_unique_id(),
                "timestamp": self.get_timestamp(),
                "detection": detection_info,
                "location": {
                    "roi": self.roi,
                    "camera_id": "camera_1",
                    "coordinates": {
                        "latitude": location[0] if location else None,
                        "longitude": location[1] if location else None
                    }
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                print(f"Notification sent successfully - ID: {payload['id']}")
                print(f"Location: {payload['location']['coordinates']}")
                print(f"Detection info: {detection_info}")
            else:
                print(f"Failed to send notification. Status code: {response.status_code}")
                
        except Exception as e:
            print(f"Error sending notification: {str(e)}")

    def draw_roi(self, event, x, y, flags, param):
        try:
            if event == cv2.EVENT_LBUTTONDOWN:
                self.drawing = True
                self.start_point = (x, y)
                
            elif event == cv2.EVENT_MOUSEMOVE:
                if self.drawing:
                    self.end_point = (x, y)
                    
            elif event == cv2.EVENT_LBUTTONUP:
                self.drawing = False
                if self.start_point and (x, y):
                    # Validate and adjust ROI points
                    x1, y1, x2, y2 = self.validate_roi(
                        self.start_point[0],
                        self.start_point[1],
                        x,
                        y
                    )
                    
                    # Calculate width and height
                    width = abs(x2 - x1)
                    height = abs(y2 - y1)
                    
                    # Set ROI with validated coordinates
                    self.roi = (min(x1, x2), min(y1, y2), width, height)
                    print(f"ROI set: {self.roi}")
        except Exception as e:
            print(f"Error in draw_roi: {str(e)}")
            self.roi = None
    
    def get_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    def process_frame(self, frame):
        try:
            display_frame = frame.copy()
            current_detections = set()
            
            # Add semi-transparent dark overlay
            overlay = display_frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
            display_frame = cv2.addWeighted(overlay, 0.4, display_frame, 0.6, 0)
            
            if self.drawing and self.start_point and self.end_point:
                # Draw temporary ROI while dragging
                x1, y1, x2, y2 = self.validate_roi(
                    self.start_point[0],
                    self.start_point[1],
                    self.end_point[0],
                    self.end_point[1]
                )
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
            elif self.roi:
                x, y, w, h = self.roi
                
                # Ensure ROI is within frame boundaries
                x = max(0, min(x, frame.shape[1] - self.min_roi_size))
                y = max(0, min(y, frame.shape[0] - self.min_roi_size))
                w = min(w, frame.shape[1] - x)
                h = min(h, frame.shape[0] - y)
                
                # Draw ROI rectangle
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                try:
                    # Extract and process ROI
                    if w > 0 and h > 0:  # Additional check before slicing
                        roi_frame = frame[y:y+h, x:x+w]
                        if roi_frame.size > 0:  # Verify ROI is not empty
                            results = self.model(roi_frame, verbose=False)
                            
                            for result in results:
                                boxes = result.boxes
                                for box in boxes:
                                    conf = float(box.conf)
                                    cls = int(box.cls)
                                    label = f'{self.model.names[cls]}'
                                    
                                    if label.lower() == 'person' and conf > 0.5:
                                        current_detections.add(label)
                                        
                                        b = box.xyxy[0].cpu().numpy()
                                        x1, y1, x2, y2 = map(int, b)
                                        x1, x2 = x1 + x, x2 + x
                                        y1, y2 = y1 + y, y2 + y
                                        
                                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                                        cv2.putText(display_frame, f'{label} {conf:.2f}', (x1, y1 - 10), 
                                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                                        
                                        if 'person' not in self.last_detections:
                                            detection_info = {
                                                "object": "person",
                                                "confidence": float(conf),
                                                "bbox": [int(coord) for coord in [x1, y1, x2, y2]]
                                            }
                                            self.send_notification(detection_info)
                except Exception as e:
                    print(f"Error processing ROI: {str(e)}")
                
                # Update detections
                self.last_detections = current_detections
                
                # Display ROI info
                text = f"ROI: x={x}, y={y}, w={w}, h={h}"
                cv2.putText(display_frame, text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Display location if available
                location = self.last_location
                if location:
                    loc_text = f"Location: {location[0]:.6f}, {location[1]:.6f}"
                    cv2.putText(display_frame, loc_text, (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            return display_frame
            
        except Exception as e:
            print(f"Error in process_frame: {str(e)}")
            return frame  # Return original frame if processing fails
    
    def run(self):
        print(f"Running on {platform.system()} system")
        print("Press 'q' to quit or 'c' to clear ROI")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    print("Error capturing frame")
                    break
                    
                display_frame = self.process_frame(frame)
                cv2.imshow('Video', display_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    self.roi = None
                    self.start_point = None
                    self.end_point = None
                    self.last_detections.clear()
                    print("ROI cleared")
            
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
        finally:
            print("Cleaning up...")
            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        detector = YOLOROIDetector(
            api_url='http://your-mongodb-api-url/notifications',
            api_key='your-api-key'
        )
        detector.run()
    except Exception as e:
        print(f"Application error: {str(e)}")