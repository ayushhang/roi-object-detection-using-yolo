import cv2

class ROIHandler:
    def __init__(self):
        self.roi = None
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.min_roi_size = 10

    def validate_roi(self, x1, y1, x2, y2):
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        if width < self.min_roi_size:
            x2 = x1 + self.min_roi_size if x2 > x1 else x1 - self.min_roi_size
        if height < self.min_roi_size:
            y2 = y1 + self.min_roi_size if y2 > y1 else y1 - self.min_roi_size
        return x1, y1, x2, y2

    def draw_roi(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.end_point = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            if self.start_point and self.end_point:
                x1, y1, x2, y2 = self.validate_roi(
                    self.start_point[0], self.start_point[1], x, y
                )
                self.roi = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                print(f"ROI set: {self.roi}")

    def get_roi(self):
        return self.roi

    def clear_roi(self):
        self.roi = None
        self.start_point = None
        self.end_point = None
        print("ROI cleared")
