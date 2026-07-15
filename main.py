import time
import os
from core.audio import AudioCore
from core.brain import Brain
from actions.system import SystemActions
from actions.apps import AppActions
from actions.web import WebActions
from actions.media import MediaActions
from datetime import datetime

class RockAssistant:
    def __init__(self, text_mode=False):
        print("=========================================")
        print(" ROCK SYSTEM INITIALIZATION ")
        print("=========================================")
        self.text_mode = text_mode
        self.audio = AudioCore()
        # Initialize the Brain using the lightweight Microsoft phi3 model
        self.brain = Brain(model_name="phi3")
        
        self.audio.speak("System initialized. ROCK is online and ready.")
        self.audio.wait_for_speech()

    def run(self):
        while True:
            try:
                if self.text_mode:
                    command = input("\nUser: ").strip()
                    if not command:
                        continue
                    print(f"[User] {command}")
                    cmd_lower = command.lower()
                    
                    # 4. Action Routing (Hardcoded fast-paths for OS actions)
                    response = ""
                    is_stream = False
                    
                    if "battery" in cmd_lower:
                        response = SystemActions.get_battery_status()
                    elif "cpu" in cmd_lower:
                        response = SystemActions.get_cpu_status()
                    elif "memory" in cmd_lower or "ram" in cmd_lower:
                        response = SystemActions.get_memory_status()
                    elif "code" in cmd_lower or "vs code" in cmd_lower:
                        response = AppActions.open_vscode()
                    elif "notepad" in cmd_lower or "notes" in cmd_lower:
                        response = AppActions.open_notepad()
                    elif "spotify" in cmd_lower or "music" in cmd_lower:
                        response = AppActions.open_spotify()
                    elif "discord" in cmd_lower:
                        response = AppActions.open_discord()
                    elif "time" in cmd_lower:
                        current_time = datetime.now().strftime("%I:%M %p")
                        response = f"The current time is {current_time}."
                    elif "date" in cmd_lower:
                        current_date = datetime.now().strftime("%B %d, %Y")
                        response = f"Today's date is {current_date}."
                    elif "browser" in cmd_lower or "chrome" in cmd_lower:
                        response = AppActions.open_browser()
                    
                    # Media Control Actions
                    elif "play music" in cmd_lower or "pause music" in cmd_lower or "resume music" in cmd_lower or "toggle music" in cmd_lower:
                        response = MediaActions.play_pause()
                    elif "next song" in cmd_lower or "skip song" in cmd_lower or "next track" in cmd_lower or "skip" in cmd_lower:
                        response = MediaActions.next_track()
                    elif "previous song" in cmd_lower or "prev song" in cmd_lower or "previous track" in cmd_lower:
                        response = MediaActions.prev_track()
                    elif "volume up" in cmd_lower or "louder" in cmd_lower or "increase volume" in cmd_lower:
                        response = MediaActions.volume_up()
                    elif "volume down" in cmd_lower or "quieter" in cmd_lower or "decrease volume" in cmd_lower:
                        response = MediaActions.volume_down()
                        
                    elif "stop listening" in cmd_lower or "sleep" in cmd_lower:
                        self.audio.speak("Going offline. Wake me if you need anything.")
                        break
                    elif "remember this" in cmd_lower or "memorize this" in cmd_lower:
                        # Extract the fact to remember
                        fact = command.split("this:", 1)[-1].strip() if ":" in command else command.replace("remember this", "").strip()
                        if fact:
                            response = self.brain.remember(fact)
                        else:
                            response = "What would you like me to remember? Please say 'remember this' followed by the fact."
                    elif "forget everything" in cmd_lower or "erase your memory" in cmd_lower:
                        response = self.brain.forget_everything()
                    
                    # Screen Awareness Action
                    elif any(kw in cmd_lower for kw in ["on my screen", "read this", "what does this say", "look at this error", "look at my screen", "read my screen", "what's on the screen"]):
                        from actions.screen import ScreenActions
                        image_path = ScreenActions.capture_screen()
                        
                        if image_path:
                            # Refine prompt based on command
                            prompt = "Analyze this screenshot and answer the user's request. Keep it to 1-3 sentences."
                            if "error" in cmd_lower:
                                prompt = "Identify the error in this screenshot and briefly state how to fix it in 1-3 sentences."
                            elif "read" in cmd_lower or "say" in cmd_lower:
                                prompt = "Read the visible text in this screenshot in 1-3 sentences."
                                
                            response = self.brain.analyze_image(image_path, prompt)
                            try:
                                if os.path.exists(image_path):
                                    os.remove(image_path)
                            except Exception as e:
                                print(f"[Warning] Failed to delete temp screenshot: {e}")
                        else:
                            response = "Failed to capture your screen."
                            
                    elif any(kw in cmd_lower for kw in ["search", "look up", "what is", "who is", "tell me about", "how to"]):
                        web_context = WebActions.search_web(command)
                        response = self.brain.process_command_stream(command, web_context=web_context)
                        is_stream = True
                    else:
                        response = self.brain.process_command_stream(command)
                        is_stream = True
                    
                    if is_stream:
                        print("ROCK: ", end="", flush=True)
                        for sentence in response:
                            print(sentence, end=" ", flush=True)
                            self.audio.speak(sentence)
                        print()  # Add final newline
                    else:
                        self.audio.speak(response)
                        
                    self.audio.wait_for_speech()

                else:
                    # Voice Mode (Standard)
                    # 1. Wait for wake word
                    self.audio.wait_for_wake_word()
                    
                    # Mute system volume so ROCK can hear the user clearly
                    self.audio.mute_system()
                    
                    try:
                        # 2. Acknowledge
                        self.audio.speak("Yes Sarvesh?")
                        self.audio.wait_for_speech() # Ensure ROCK finishes speaking before listening
                        
                        # 3. Listen for command
                        command = self.audio.listen_for_command()
                        
                        if not command:
                            # Timeout or unverified voice
                            continue
                            
                        print(f"[User] {command}")
                        cmd_lower = command.lower()
                        
                        # 4. Action Routing (Hardcoded fast-paths for OS actions)
                        response = ""
                        is_stream = False
                        
                        if "battery" in cmd_lower:
                            response = SystemActions.get_battery_status()
                        elif "cpu" in cmd_lower:
                            response = SystemActions.get_cpu_status()
                        elif "memory" in cmd_lower or "ram" in cmd_lower:
                            response = SystemActions.get_memory_status()
                        elif "code" in cmd_lower or "vs code" in cmd_lower:
                            response = AppActions.open_vscode()
                        elif "notepad" in cmd_lower or "notes" in cmd_lower:
                            response = AppActions.open_notepad()
                        elif "spotify" in cmd_lower or "music" in cmd_lower:
                            response = AppActions.open_spotify()
                        elif "discord" in cmd_lower:
                            response = AppActions.open_discord()
                        elif "time" in cmd_lower:
                            current_time = datetime.now().strftime("%I:%M %p")
                            response = f"The current time is {current_time}."
                        elif "date" in cmd_lower:
                            current_date = datetime.now().strftime("%B %d, %Y")
                            response = f"Today's date is {current_date}."
                        elif "browser" in cmd_lower or "chrome" in cmd_lower:
                            response = AppActions.open_browser()
                        
                        # Media Control Actions
                        elif "play music" in cmd_lower or "pause music" in cmd_lower or "resume music" in cmd_lower or "toggle music" in cmd_lower:
                            response = MediaActions.play_pause()
                        elif "next song" in cmd_lower or "skip song" in cmd_lower or "next track" in cmd_lower or "skip" in cmd_lower:
                            response = MediaActions.next_track()
                        elif "previous song" in cmd_lower or "prev song" in cmd_lower or "previous track" in cmd_lower:
                            response = MediaActions.prev_track()
                        elif "volume up" in cmd_lower or "louder" in cmd_lower or "increase volume" in cmd_lower:
                            response = MediaActions.volume_up()
                        elif "volume down" in cmd_lower or "quieter" in cmd_lower or "decrease volume" in cmd_lower:
                            response = MediaActions.volume_down()
                            
                        elif "stop listening" in cmd_lower or "sleep" in cmd_lower:
                            self.audio.speak("Going offline. Wake me if you need anything.")
                            break
                        elif "remember this" in cmd_lower or "memorize this" in cmd_lower:
                            # Extract the fact to remember
                            fact = command.split("this:", 1)[-1].strip() if ":" in command else command.replace("remember this", "").strip()
                            if fact:
                                response = self.brain.remember(fact)
                            else:
                                response = "What would you like me to remember? Please say 'remember this' followed by the fact."
                        elif "forget everything" in cmd_lower or "erase your memory" in cmd_lower:
                            response = self.brain.forget_everything()
                        
                        # Screen Awareness Action
                        elif any(kw in cmd_lower for kw in ["on my screen", "read this", "what does this say", "look at this error", "look at my screen", "read my screen", "what's on the screen"]):
                            self.audio.speak("Taking a screenshot.")
                            self.audio.wait_for_speech()
                            
                            from actions.screen import ScreenActions
                            image_path = ScreenActions.capture_screen()
                            
                            if image_path:
                                # Refine prompt based on command
                                prompt = "Analyze this screenshot and answer the user's request. Keep it to 1-3 sentences."
                                if "error" in cmd_lower:
                                    prompt = "Identify the error in this screenshot and briefly state how to fix it in 1-3 sentences."
                                elif "read" in cmd_lower or "say" in cmd_lower:
                                    prompt = "Read the visible text in this screenshot in 1-3 sentences."
                                    
                                response = self.brain.analyze_image(image_path, prompt)
                                
                                # Clean up file (privacy first!)
                                try:
                                    if os.path.exists(image_path):
                                        os.remove(image_path)
                                except Exception as e:
                                    print(f"[Warning] Failed to delete temp screenshot: {e}")
                            else:
                                response = "Failed to capture your screen."
                                
                        elif any(kw in cmd_lower for kw in ["search", "look up", "what is", "who is", "tell me about", "how to"]):
                            # Gather context from the web
                            self.audio.speak("Searching the web for you.")
                            self.audio.wait_for_speech()
                            web_context = WebActions.search_web(command)
                            response = self.brain.process_command_stream(command, web_context=web_context)
                            is_stream = True
                        else:
                            # 5. Pass to LLM Brain stream if no hardcoded action matches
                            response = self.brain.process_command_stream(command)
                            is_stream = True
                        
                        # 6. Speak the response (stream sentences or speak static text)
                        if is_stream:
                            print("ROCK: ", end="", flush=True)
                            for sentence in response:
                                print(sentence, end=" ", flush=True)
                                self.audio.speak(sentence)
                            print()  # Add final newline
                        else:
                            self.audio.speak(response)
                        
                    finally:
                        # Wait for ROCK to finish speaking completely before unmuting system audio
                        self.audio.wait_for_speech()
                        self.audio.unmute_system()
                
            except KeyboardInterrupt:
                print("\n[System] ROCK shutting down.")
                break
            except Exception as e:
                print(f"[System Error] {e}")

if __name__ == "__main__":
    import sys
    text_mode = "--text" in sys.argv or "-t" in sys.argv
    rock = RockAssistant(text_mode=text_mode)
    rock.run()

