import tkinter as tk
from tkinter import messagebox
import threading
from typing import Self
import cv2
import logging
from PIL import Image, ImageTk
from detector.core.obj_detector import YOLONDetector
from detector.config.settings import Settings
from detector.utils.camera import Camera
from detector.utils.geocoding import Geocoder
from detector.utils.id_generator import IDGenerator
from detector.api.client import APIClient
from detector.core.roi_handler import ROIHandler
from detector.core.frame_processor import FrameProcessor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Global variables
detector = None
detection_thread = None
is_running = False
roi = None  # Store the ROI coordinates (x, y, width, height)
drawing = False  # Flag to check if the user is currently drawing the ROI
start_point = None  # Starting point of the ROI (click)
end_point = None  # Ending point of the ROI (release)

def start_detection():
    """Function to start the object detection in a separate thread."""
    global detector, is_running
    if not is_running:
        config = Settings()

        # Initialize the detector with the configuration
        detector = YOLONDetector(
            model_path=config.model_path,
            api_url=config.api_url,
            api_key=config.api_key
        )
        
        logging.info("Starting the object detection loop...")
        YOLONDetector.run(Self)  # Start detection loop
        is_running = True
        update_status("Detection is running...")

def stop_detection():
    """Stop the object detection."""
    global detector, is_running
    if is_running:
        logging.info("Stopping the detection...")
        YOLONDetector.cap.release()  # Stop the camera capture
        cv2.destroyAllWindows()  # Close any OpenCV windows
        is_running = False
        update_status("Detection stopped.")
    else:
        update_status("Detection is not running.")

def update_status(status: str):
    """Update the status label in the GUI."""
    status_label.config(text=status)

def show_error(message: str):
    """Display an error message in the GUI."""
    messagebox.showerror("Error", message)

def run_detection_in_thread():
    """Run the detection in a separate thread to keep the GUI responsive."""
    try:
        start_detection()
    except Exception as e:
        show_error(f"Error during detection: {str(e)}")
        stop_detection()

def open_camera_feed():
    """Start the camera feed in the GUI window."""
    global detector, is_running, roi, drawing, start_point, end_point
    try:
        if not is_running:
            update_status("Starting camera feed...")
            threading.Thread(target=run_detection_in_thread, daemon=True).start()
        
        while is_running:
            # Capture frame from the camera
            ret, frame = YOLONDetector.cap.read()
            if not ret:
                break
            
            # Process the frame
            processed_frame = FrameProcessor.process_frame(frame)

            # Draw ROI if it exists
            if roi is not None:
                x, y, w, h = roi
                cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Convert the frame to RGB (Tkinter uses RGB)
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            img_tk = ImageTk.PhotoImage(img)
            
            # Update the canvas with the new frame
            video_canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            video_canvas.image = img_tk

    except Exception as e:
        show_error(f"Error with camera feed: {str(e)}")
        stop_detection()

def start_button_click():
    """Handle the start button click event."""
    if not is_running:
        open_camera_feed()
    else:
        show_error("Detection is already running.")

def stop_button_click():
    """Handle the stop button click event."""
    stop_detection()

def on_mouse_click(event):
    """Handle mouse click to start drawing the ROI."""
    global start_point, drawing
    start_point = (event.x, event.y)
    drawing = True

def on_mouse_move(event):
    """Handle mouse move to update the ROI while dragging."""
    global end_point, drawing
    if drawing:
        end_point = (event.x, event.y)
        video_canvas.delete("ROI")  # Remove previous ROI rectangle
        video_canvas.create_rectangle(start_point[0], start_point[1], end_point[0], end_point[1], outline="green", width=2, tags="ROI")

def on_mouse_release(event):
    """Handle mouse release to finalize the ROI."""
    global roi, drawing, start_point, end_point
    if drawing:
        drawing = False
        end_point = (event.x, event.y)
        roi = (start_point[0], start_point[1], abs(end_point[0] - start_point[0]), abs(end_point[1] - start_point[1]))
        video_canvas.delete("ROI")  # Remove temporary ROI rectangle
        video_canvas.create_rectangle(start_point[0], start_point[1], end_point[0], end_point[1], outline="green", width=2, tags="ROI")
        update_status(f"ROI set: {roi}")

# Create the main window
root = tk.Tk()
root.title("Object Detection Application")

# Set up the window size
root.geometry("800x600")

# Create a canvas to display the video feed
video_canvas = tk.Canvas(root, width=640, height=480)
video_canvas.pack(pady=20)

# Create buttons to control the detection
start_button = tk.Button(root, text="Start Detection", command=start_button_click)
start_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(root, text="Stop Detection", command=stop_button_click)
stop_button.pack(side=tk.LEFT, padx=10)

# Create a label to display the status
status_label = tk.Label(root, text="Detection not started", font=("Arial", 14))
status_label.pack(pady=20)

# Bind mouse events for drawing ROI
video_canvas.bind("<ButtonPress-1>", on_mouse_click)
video_canvas.bind("<B1-Motion>", on_mouse_move)
video_canvas.bind("<ButtonRelease-1>", on_mouse_release)

# Start the main loop for the application
root.mainloop()
