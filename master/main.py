import cv2
import logging
from detector.core.obj_detector import YOLONDetector
from detector.config.settings import Settings
import platform

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def main():
    try:
        # Initialize the settings
        config = Settings()
        logging.info("Configuration loaded successfully.")
        
        # Print platform-specific info
        logging.info(f"Running on {platform.system()} system")
        
        # Initialize the detector with settings from the configuration
        detector = YOLONDetector(
            model_path=config.model_path,
            api_url=config.api_url,
            api_key=config.api_key
        )
        
        logging.info("Starting the object detection loop...")
        
        # Run the detector (starts the camera feed and detection loop)
        detector.run()

    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        logging.exception("Exception occurred")

if __name__ == "__main__":
    main()
