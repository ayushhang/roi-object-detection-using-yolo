from pydantic import BaseModel
from typing import List, Optional, Tuple

class Detection(BaseModel):
    """
    Represents the detection data, such as object type, confidence score, and bounding box.
    """
    object: str  # e.g., 'person'
    confidence: float  # Confidence score for the detection
    bbox: List[int]  # Bounding box [x1, y1, x2, y2]

class Location(BaseModel):
    """
    Represents the location data including coordinates and ROI.
    """
    roi: Tuple[int, int, int, int]  # (x, y, width, height)
    camera_id: str  # Camera ID, e.g., "camera_1"
    coordinates: Optional[Tuple[float, float]] = None  # Latitude, Longitude (Optional)

class Notification(BaseModel):
    """
    Represents the full notification structure, including detection and location data.
    """
    id: str  # Unique identifier for the notification
    timestamp: str  # Timestamp of when the detection was made
    detection: Detection  # Detection details
    location: Location  # Location details
