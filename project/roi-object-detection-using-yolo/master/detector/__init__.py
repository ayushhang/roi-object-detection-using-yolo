"""
YOLO ROI Detector Package

This package provides functionality for real-time object detection using YOLOv8,
with support for Region of Interest (ROI) selection and notification handling.

Modules:
--------
- `core`    : Contains the main detection logic, ROI handling, and frame processing.
- `utils`   : Utility functions for camera handling, geolocation, and ID generation.
- `api`     : Manages API interactions and data models.
- `config`  : Handles configuration settings.

Usage:
------
from yolo_detector import YOLONDetector

detector = YOLONDetector(model_path='yolov8n.pt')
detector.run()
"""

# Ensure correct relative imports
from .core.obj_detector import YOLONDetector
from .core.roi_handler import ROIHandler
from .core.frame_processor import FrameProcessor
from .utils.camera import Camera
from .utils.geocoding import Geocoder
from .utils.id_generator import IDGenerator
from .api.client import APIClient

__all__ = ["YOLONDetector","ROIHandler","FrameProcessor", "Camera", "Geocoder", "IDGenerator", "APIClient"]
