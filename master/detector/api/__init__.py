# Initialize the API package for notifications and related services.

from .client import APIClient
from .models import Detection, Location, Notification
__all__ = [
    "APIClient",
    "ROIHandler",
    "FrameProcessor"
]