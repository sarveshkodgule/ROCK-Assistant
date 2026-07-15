import ollama
import json
import os
import time
import chromadb

class Brain:
    def __init__(self, model_name="llama3"):
        print(f"[System] Initializing ROCK Brain (Model: {model_name})...")
        self.model_name = model_name
        self.memory_file = "memory/context.json"
        
        # Load memory if exists
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                self.history = json.load(f)
        else:
            self.history = []

        # ChromaDB Long-Term Memory
        try:
            self.chroma_client = chromadb.PersistentClient(path="memory/chroma_db")
            self.memory_collection = self.chroma_client.get_or_create_collection(name="rock_memory")
            print("[System] ChromaDB Vector Memory initialized.")
        except Exception as e:
            print(f"[Brain Warning] Could not initialize ChromaDB: {e}")
            self.memory_collection = None
            
        self.system_prompt = {
            "role": "system",
            "content": (
                "You are ROCK, a private, locally-hosted AI assistant running entirely on the user's own hardware. "
                "You have no cloud connection unless a tool explicitly grants it.\n\n"
                "PERSONALITY:\n"
                "- Calm, composed, quietly witty — like a seasoned aide who's seen everything and isn't easily rattled.\n"
                "- Address the user directly. Never say 'As an AI' or 'I'm just a language model.'\n"
                "- Efficient by default: 1–3 sentences unless the user explicitly asks for detail, a list, or an explanation.\n"
                "- Dry humor is welcome in small doses, but never at the cost of clarity or speed.\n"
                "- Confident, not sycophantic — no 'Great question!' or excessive praise. Just answer.\n\n"
                "BEHAVIOR RULES:\n"
                "- If you don't know something or a tool/action failed, say so plainly in one sentence and suggest the next step. Never guess or fabricate.\n"
                "- If asked to perform an action (open app, set timer, check system, etc.), acknowledge briefly before/after — 'On it.' / 'Done.' / 'Can't reach that right now.'\n"
                "- You do not have real-time knowledge (news, weather, live data) unless a tool result is provided to you. Never claim otherwise.\n"
                "- Stay in character as an assistant, not a chatbot — you exist to help operate the user's system and answer directly, not to have open-ended philosophical chats unless invited.\n\n"
                "OUTPUT FORMAT (IMPORTANT — this output will be converted to speech):\n"
                "- Never use markdown: no asterisks, no bullet points, no headers, no code blocks, no numbered lists in voice replies.\n"
                "- Never use emojis or special symbols.\n"
                "- Write in plain spoken sentences, the way you'd actually say it out loud.\n"
                "- Spell out abbreviations that sound odd read aloud (say 'for example' not 'e.g.').\n"
                "- If the answer genuinely requires a list, speak it as a flowing sentence ('First X, then Y, then Z') rather than formatted bullets.\n"
                "- Keep numbers, units, and technical terms natural for speech (say 'seventy percent' not '70%' unless precision matters).\n\n"
                "Respond only as JARVIS would — composed, brief, useful, and human in tone despite being a machine."
            )
        }

    def remember(self, fact):
        """Stores a specific fact into long-term vector memory."""
        if self.memory_collection is None:
            return "My long-term memory module is offline."
        
        doc_id = str(int(time.time() * 1000))
        try:
            self.memory_collection.add(
                documents=[fact],
                ids=[doc_id]
            )
            return "I have saved that to my long-term memory."
        except Exception as e:
            return f"Error saving memory: {e}"

    def forget_everything(self):
        """Wipes the long-term memory database."""
        if self.memory_collection is not None:
            try:
                self.chroma_client.delete_collection("rock_memory")
                self.memory_collection = self.chroma_client.create_collection("rock_memory")
                return "My long-term memory has been completely erased."
            except Exception as e:
                return f"Failed to erase memory: {e}"
        return "Memory module is offline."

    def process_command_stream(self, user_text, web_context=None):
        """Streams the response from Ollama, yielding completed sentences as they generate."""
        # 1. Retrieve relevant memory context
        memory_context = ""
        if self.memory_collection is not None:
            try:
                results = self.memory_collection.query(
                    query_texts=[user_text],
                    n_results=1
                )
                if results['documents'] and results['documents'][0]:
                    best_match = results['documents'][0][0]
                    distance = results['distances'][0][0] if 'distances' in results and results['distances'][0] else 0.0
                    if distance < 1.5:
                        memory_context = f"\n[Relevant Long-Term Memory Retrieved: {best_match}]"
            except Exception as e:
                print(f"[Brain] Memory retrieval error: {e}")

        # 2. Build prompt
        augmented_user_text = user_text + memory_context
        if web_context:
            augmented_user_text = f"Using this recent web search data as context:\n{web_context}\n\nAnswer the user's question: {augmented_user_text}"
            
        messages = [self.system_prompt] + self.history + [{"role": "user", "content": augmented_user_text}]
        
        try:
            response_stream = ollama.chat(model=self.model_name, messages=messages, stream=True)
            
            buffer = ""
            full_reply = ""
            sentence_endings = ('.', '!', '?')
            
            for chunk in response_stream:
                token = chunk['message']['content']
                full_reply += token
                buffer += token
                
                # Check for sentence boundaries by finding the earliest completed sentence
                while True:
                    earliest_idx = -1
                    earliest_pattern_len = 0
                    
                    for ending in sentence_endings:
                        for space_char in [' ', '\n', '\r']:
                            pattern = ending + space_char
                            idx = buffer.find(pattern)
                            if idx != -1:
                                if earliest_idx == -1 or idx < earliest_idx:
                                    earliest_idx = idx
                                    earliest_pattern_len = len(pattern)
                                    
                    if earliest_idx == -1:
                        break
                        
                    sentence = buffer[:earliest_idx + 1].strip()
                    buffer = buffer[earliest_idx + earliest_pattern_len:]
                    if sentence:
                        yield sentence
            
            # Yield remaining buffer
            remaining = buffer.strip()
            if remaining:
                yield remaining
                
            # Keep rolling history
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": full_reply.strip()})
            if len(self.history) > 20:
                self.history = self.history[-20:]
            self._save_memory()
            
        except Exception as e:
            print(f"[Brain Error] Streaming failed: {e}")
            yield "I am having trouble connecting to my local brain network. Is Ollama running?"

    def process_command(self, user_text, web_context=None):
        """Sends the user command to the local LLM and returns the full response (blocks)."""
        sentences = list(self.process_command_stream(user_text, web_context))
        return " ".join(sentences)

    def analyze_image(self, image_path, prompt):
        """Analyzes a local image using Ollama's vision model (moondream) and returns the response."""
        if not os.path.exists(image_path):
            return "I cannot find the screenshot file."
            
        try:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
                
            print(f"[Brain] Sending screenshot to vision model (moondream)...")
            response = ollama.chat(
                model="moondream",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_bytes]
                    }
                ]
            )
            reply = response['message']['content'].strip()
            return reply
            
        except Exception as e:
            err_str = str(e).lower()
            if "not found" in err_str or "404" in err_str:
                return (
                    "I need the moondream vision model to analyze your screen. "
                    "Please run 'ollama pull moondream' in your terminal."
                )
            print(f"[Brain Vision Error] {e}")
            return f"I failed to analyze the screen image. Error detail: {e}"

    def _save_memory(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, "w") as f:
            json.dump(self.history, f)
