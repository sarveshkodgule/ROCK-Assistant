import os
from PIL import ImageGrab

class ScreenActions:
    @staticmethod
    def capture_screen():
        """Captures a screenshot of the primary display and saves it to a temporary file.
        
        Returns:
            str: Path to the saved image file, or None if the capture failed.
        """
        try:
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)
            image_path = os.path.join(temp_dir, "screen_capture.png")
            
            # Grab the screenshot of the primary monitor
            screenshot = ImageGrab.grab()
            screenshot.save(image_path, "PNG")
            return image_path
        except Exception as e:
            print(f"[Screen Capture Error] {e}")
            return None
