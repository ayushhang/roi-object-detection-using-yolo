import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import random
import string
from detector.core.detector import YOLONDetector

class TestYOLOROIDetector(unittest.TestCase):
    
    def setUp(self):
        self.detector = YOLONDetector(model_path='yolov8n.pt', api_url='http://your-mongodb-api-url', api_key='your-api-key')

    # Test generate_unique_id method
    def test_generate_unique_id(self):
        # Test if the unique ID is always 16 characters long
        unique_id = self.detector.generate_unique_id()
        self.assertEqual(len(unique_id), 16)
        self.assertTrue(all(c in string.ascii_letters + string.digits for c in unique_id))
    
    # Test validate_roi method
    def test_validate_roi(self):
        # Test ROI validation for valid and invalid ROI coordinates
        x1, y1, x2, y2 = 100, 100, 50, 50  # ROI with invalid (too small) width and height
        validated_roi = self.detector.validate_roi(x1, y1, x2, y2)
        self.assertEqual(validated_roi, (50, 50, 60, 60))  # Ensure it adjusts to minimum size
        
        x1, y1, x2, y2 = 100, 100, 200, 200  # Valid ROI
        validated_roi = self.detector.validate_roi(x1, y1, x2, y2)
        self.assertEqual(validated_roi, (100, 100, 100, 100))  # Ensure it stays the same

    # Test get_location method (mocking geocoder response)
    @patch('geocoder.ip')
    def test_get_location(self, mock_geocoder):
        # Test if the location is fetched correctly
        mock_geocoder.return_value.ok = True
        mock_geocoder.return_value.lat = 40.7128
        mock_geocoder.return_value.lng = -74.0060
        
        location = self.detector.get_location()
        self.assertEqual(location, (40.7128, -74.0060))
        
        # Test if the location is cached and updated every 60 seconds
        self.detector.location_update_time = datetime.now().timestamp() - 30  # Pretend it's been 30 seconds
        location = self.detector.get_location()
        self.assertEqual(location, (40.7128, -74.0060))  # Should be the same as the mocked value
        
        # Test if location update is triggered after 60 seconds
        self.detector.location_update_time = datetime.now().timestamp() - 70  # Pretend it's been 70 seconds
        mock_geocoder.return_value.lat = 51.5074
        mock_geocoder.return_value.lng = -0.1278
        location = self.detector.get_location()
        self.assertEqual(location, (51.5074, -0.1278))  # Should update to new location

    # Test send_notification method (mocking the request.post)
    @patch('requests.post')
    def test_send_notification(self, mock_post):
        # Test if notification is sent correctly
        mock_post.return_value.status_code = 200
        detection_info = {"object": "person", "confidence": 0.85, "bbox": [100, 150, 200, 250]}
        
        # Mock successful location fetch
        self.detector.last_location = (40.7128, -74.0060)
        
        self.detector.send_notification(detection_info)
        mock_post.assert_called_once()  # Ensure requests.post is called
        
        # Validate payload structure in the request
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs['data'])
        
        # Check if the required fields are present in the payload
        self.assertIn('id', payload)
        self.assertIn('timestamp', payload)
        self.assertIn('detection', payload)
        self.assertIn('location', payload)
        self.assertEqual(payload['location']['coordinates'], {'latitude': 40.7128, 'longitude': -74.0060})
        
    # Test draw_roi method
    def test_draw_roi(self):
        # Since it's hard to test drawing via mouse events, you can test if ROI state changes
        self.detector.drawing = True
        self.detector.start_point = (100, 100)
        self.detector.end_point = (200, 200)
        self.detector.draw_roi(cv2.EVENT_LBUTTONUP, 200, 200, None, None)
        
        self.assertEqual(self.detector.roi, (100, 100, 100, 100))  # ROI should be updated
        self.assertFalse(self.detector.drawing)  # Drawing flag should be reset after mouse release
        
if __name__ == '__main__':
    unittest.main()
