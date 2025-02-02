import cv2
import platform

class Camera:
    def __init__(self, camera_index=0, width=1280, height=720):
        """
        Initialize the camera with the specified index and resolution.
        :param camera_index: Index of the camera (default is 0).
        :param width: Width of the captured frames (default is 1280).
        :param height: Height of the captured frames (default is 720).
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        
        self._initialize_camera()

    def _initialize_camera(self):
        """
        Initializes the camera based on the operating system.
        Uses DirectShow on Windows and default API on other systems.
        """
        try:
            if platform.system() == 'Windows':
                # Use DirectShow for better compatibility on Windows
                self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            else:
                self.cap = cv2.VideoCapture(self.camera_index)

            # Set camera resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

            if not self.cap.isOpened():
                raise Exception("Camera initialization failed")

            print(f"Camera initialized with resolution {self.width}x{self.height}")

        except Exception as e:
            print(f"Error initializing camera: {str(e)}")
            self.cap = None

    def capture_frame(self):
        """
        Captures a frame from the camera.
        :return: Captured frame or None if capturing fails.
        """
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                print("Failed to capture frame")
                return None
        return None

    def release(self):
        """
        Releases the camera resource.
        """
        if self.cap:
            self.cap.release()
            print("Camera released")

    def is_opened(self):
        """
        Check if the camera is properly opened.
        :return: True if camera is open, False otherwise.
        """
        return self.cap is not None and self.cap.isOpened()
