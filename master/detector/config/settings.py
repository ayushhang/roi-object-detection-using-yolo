import os

class Settings:
    def __init__(self):
        # General configuration values
        self.api_url = os.getenv('API_URL', 'http://your-mongodb-api-url/notifications')
        self.api_key = os.getenv('API_KEY', 'your-api-key')
        
        # Camera settings
        self.camera_index = int(os.getenv('CAMERA_INDEX', 0))  # Default is 0 (first camera)
        self.frame_width = int(os.getenv('FRAME_WIDTH', 1280))
        self.frame_height = int(os.getenv('FRAME_HEIGHT', 720))

        # YOLO model configuration
        self.model_path = os.getenv('MODEL_PATH', 'yolov8n.pt')

        # Location update settings
        self.location_update_interval = int(os.getenv('LOCATION_UPDATE_INTERVAL', 60))  # in seconds

    def __repr__(self):
        return f"Settings(api_url={self.api_url}, api_key={self.api_key}, model_path={self.model_path})"
