import cv2
from detector.core.roi_handler import ROIHandler
from detector.utils.geocoding import Geocoder

class FrameProcessor:
    def __init__(self, roi_handler: ROIHandler, geocoder: Geocoder):
        self.roi_handler = roi_handler
        self.geocoder = geocoder

    def process_frame(self, frame):
        """
        Processes a frame by adding an overlay, drawing the ROI,
        and displaying location information if available.
        """
        display_frame = frame.copy()
        
        # Add a semi-transparent dark overlay
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
        display_frame = cv2.addWeighted(overlay, 0.4, display_frame, 0.6, 0)
        
        # Draw the ROI if it exists
        roi = self.roi_handler.get_roi()
        if roi:
            x, y, w, h = roi
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = f"ROI: x={x}, y={y}, w={w}, h={h}"
            cv2.putText(display_frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display location if available
            location = self.geocoder.get_location()
            if location:
                loc_text = f"Location: {location[0]:.6f}, {location[1]:.6f}"
                cv2.putText(display_frame, loc_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return display_frame
