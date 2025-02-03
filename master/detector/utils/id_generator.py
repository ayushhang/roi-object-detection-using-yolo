import random
import string

class IDGenerator:
    def __init__(self, length: int = 16):
        """
        Initializes the ID generator with the specified ID length.
        :param length: Length of the generated unique ID (default is 16 characters).
        """
        self.length = length

    def generate_unique_id(self) -> str:
        """
        Generates a unique ID consisting of random alphanumeric characters.
        :return: A string representing the unique ID.
        """
        characters = string.ascii_letters + string.digits  # Alphanumeric characters (uppercase, lowercase, digits)
        unique_id = ''.join(random.choice(characters) for _ in range(self.length))
        return unique_id
