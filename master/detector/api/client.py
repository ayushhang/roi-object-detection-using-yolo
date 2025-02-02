import requests
import json
from typing import Dict, Optional

class APIClient:
    def __init__(self, api_url: str, api_key: str):
        """
        Initializes the API client with the provided API URL and API key.
        :param api_url: The URL of the API to send notifications to.
        :param api_key: The API key used for authentication.
        """
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    def send_notification(self, data: Dict) -> bool:
        """
        Sends a notification to the API with the provided data.
        :param data: A dictionary containing the notification data.
        :return: True if the notification was successfully sent, False otherwise.
        """
        try:
            # Send a POST request to the API with the notification data
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(data))

            # Check if the response status code indicates success (200 OK)
            if response.status_code == 200:
                print(f"Notification sent successfully: {data}")
                return True
            else:
                print(f"Failed to send notification. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            # Handle any request exceptions (e.g., network issues, timeout)
            print(f"Error sending notification: {str(e)}")
            return False
