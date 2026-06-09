import ctypes

# Win32 Virtual Key Codes
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002

def _press_key(vk_code):
    """Simulates a key press and release event for media/volume keys."""
    try:
        # Press key
        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
        # Release key
        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
    except Exception as e:
        print(f"[Error] Failed to send media keypress {vk_code}: {e}")

class MediaActions:
    @staticmethod
    def play_pause():
        _press_key(VK_MEDIA_PLAY_PAUSE)
        return "Toggled playback."

    @staticmethod
    def next_track():
        _press_key(VK_MEDIA_NEXT_TRACK)
        return "Skipped to next track."

    @staticmethod
    def prev_track():
        _press_key(VK_MEDIA_PREV_TRACK)
        return "Went to previous track."

    @staticmethod
    def volume_up():
        # Press volume up key 3 times to raise system volume by ~6%
        for _ in range(3):
            _press_key(VK_VOLUME_UP)
        return "Volume increased."

    @staticmethod
    def volume_down():
        # Press volume down key 3 times to lower system volume by ~6%
        for _ in range(3):
            _press_key(VK_VOLUME_DOWN)
        return "Volume decreased."
