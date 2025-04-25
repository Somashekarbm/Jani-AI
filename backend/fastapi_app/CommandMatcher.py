import numpy as np
from sentence_transformers import SentenceTransformer
import re
import spacy
from datetime import datetime, timedelta
import json
import nltk
from nltk.corpus import wordnet
import subprocess
import platform
import webbrowser
import os

# Download required NLTK data
nltk.download('wordnet', quiet=True)

# Load NLP models
model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load("en_core_web_sm")

def preprocess_query(query):
    # Normalize, remove filler words
    query = re.sub(r'\b(um|uh|like|you know|please|can you|could you|hey)\b', '', query.lower())
    return query.strip()

class CommandMatcher:
    def __init__(self):
        # Initialize as before
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Default model
        self.commands = self.initialize_commands()
        self.preprocess = preprocess_query
        self.command_embeddings = self.generate_embeddings()
        
        # Add conversation context
        self.context = {
            "last_command": None,
            "last_parameters": {},
            "session_apps": set(),  # Track apps opened in this session
            "conversation_history": [],
            "notes": []  # Store user notes
        }
        
        # OS detection for app execution
        self.os_name = platform.system()
        
    def improve_semantic_matching(self):
        # Use a more powerful embedding model
        self.model = SentenceTransformer('paraphrase-mpnet-base-v2')  # Better semantic understanding
        # Re-generate embeddings with new model
        self.command_embeddings = self.generate_embeddings()
           
    def initialize_commands(self):
        """Define all supported commands with variations and parameter extraction patterns"""
        commands = [
            {
                "id": "wikipedia_search",
                "patterns": [
                    "wikipedia {query}",
                    "search wikipedia for {query}",
                    "look up {query} on wikipedia",
                    "what does wikipedia say about {query}",
                    "find {query} on wikipedia",
                    "check wikipedia for {query}",
                    "wikipedia article on {query}",
                    "tell me about {query} from wikipedia",
                    "can you search wikipedia for {query}"
                ],
                "examples": [
                    "wikipedia artificial intelligence",
                    "search wikipedia for quantum computing",
                    "look up mount everest on wikipedia",
                    "what does wikipedia say about climate change",
                    "find black holes on wikipedia",
                    "check wikipedia for world war 2",
                    "wikipedia article on Albert Einstein",
                    "tell me about pandas from wikipedia"
                ],
                "template": "wikipedia {query}",
                "params": ["query"],
                "param_extractors": {
                    "query": self._extract_wikipedia_query
                },
            },
            {
                "id": "open_youtube",
                "patterns": [
                    "open youtube",
                    "launch youtube",
                    "start youtube",
                    "go to youtube",
                    "browse youtube",
                    "youtube please",
                    "can you open youtube",
                    "i want to watch youtube",
                    "take me to youtube",
                    "show me youtube"
                ],
                "examples": [
                    "open youtube",
                    "can you open youtube",
                    "launch youtube please",
                    "i want to watch some videos",
                    "go to youtube",
                    "browse youtube",
                    "youtube please",
                    "take me to youtube"
                ],
                "template": "open youtube",
                "params": [],
            },
            {
                "id": "youtube_search",
                "patterns": [
                    "search youtube for {query}",
                    "find {query} on youtube",
                    "look up {query} videos",
                    "youtube {query}",
                    "search for {query} videos",
                    "watch {query} on youtube",
                    "find videos about {query}",
                    "search videos of {query}",
                    "look for {query} on youtube"
                ],
                "examples": [
                    "search youtube for cooking tutorials",
                    "find latest music videos on youtube",
                    "look up python programming tutorials",
                    "youtube cat videos",
                    "search for guitar lessons videos",
                    "watch documentary on youtube",
                    "find videos about space exploration",
                    "search videos of dance performances",
                    "look for hiking tips on youtube"
                ],
                "template": "search youtube for {query}",
                "params": ["query"],
                "param_extractors": {
                    "query": self._extract_search_query
                },
                
            },
            {
                "id": "open_google",
                "patterns": [
                    "open google",
                    "launch google",
                    "start google",
                    "go to google",
                    "browse google",
                    "google homepage",
                    "navigate to google",
                    "take me to google",
                    "show google"
                ],
                "examples": [
                    "open google",
                    "launch google browser",
                    "i need to search something online",
                    "go to google",
                    "browse google",
                    "google homepage please",
                    "navigate to google",
                    "take me to google"
                ],
                "template": "open google",
                "params": [],
                
            },
            {
                "id": "google_search",
                "patterns": [
                    "search google for {query}",
                    "google {query}",
                    "look up {query} online",
                    "search for {query}",
                    "search {query}",
                    "find {query} on google",
                    "search the web for {query}",
                    "look for {query} online",
                    "find information about {query}"
                ],
                "examples": [
                    "search google for best restaurants near me",
                    "google weather forecast",
                    "look up the height of eiffel tower",
                    "search for new movies",
                    "search covid statistics",
                    "find recipe for chocolate cake on google",
                    "search the web for cheap flights",
                    "look for used cars online",
                    "find information about solar panels"
                ],
                "template": "search google for {query}",
                "params": ["query"],
                "param_extractors": {
                    "query": self._extract_search_query
                },
                
            },
            {
                "id": "set_reminder",
                "patterns": [
                    "remind me to {task} in {time} minutes",
                    "remind me in {time} minutes to {task}",
                    "set a reminder for {task} in {time} minutes",
                    "create reminder to {task} in {time} minutes",
                    "set an alarm to {task} in {time} minutes",
                    "remind me about {task} after {time} minutes",
                    "notify me to {task} in {time} minutes",
                    "alert me to {task} in {time} minutes"
                ],
                "examples": [
                    "remind me to check email in 30 minutes",
                    "remind me in 5 minutes to take medicine",
                    "set a reminder for meeting in 60 minutes",
                    "create reminder to call mom in 15 minutes",
                    "set an alarm to go for a walk in 45 minutes",
                    "remind me about laundry after 20 minutes",
                    "notify me to drink water in 30 minutes",
                    "alert me to submit report in 10 minutes"
                ],
                "template": "remind me in {time} minutes to {task}",
                "params": ["task", "time"],
                "param_extractors": {
                    "task": self._extract_reminder_task,
                    "time": self._extract_time_value
                },
                
            },
            {
                "id": "currency_conversion",
                "patterns": [
                    "convert currency {amount} {from_currency} to {to_currency}",
                    "exchange rate from {from_currency} to {to_currency}",
                    "how much is {amount} {from_currency} in {to_currency}",
                    "convert {amount} {from_currency} to {to_currency}",
                    "what's {amount} {from_currency} in {to_currency}",
                    "{amount} {from_currency} to {to_currency}",
                    "exchange {amount} {from_currency} for {to_currency}",
                    "calculate {amount} {from_currency} in {to_currency}"
                ],
                "examples": [
                    "convert currency 100 dollars to euros",
                    "exchange rate from rupees to dollars",
                    "how much is 50 euros in yen",
                    "convert 25 pounds to rupees",
                    "what's 200 yuan in dollars",
                    "75 dollars to euros",
                    "exchange 300 euros for pounds",
                    "calculate 500 yen in dollars"
                ],
                "template": "convert currency {amount} {from_currency} to {to_currency}",
                "params": ["amount", "from_currency", "to_currency"],
                "param_extractors": {
                    "amount": self._extract_currency_amount,
                    "from_currency": self._extract_from_currency,
                    "to_currency": self._extract_to_currency
                },
                
            },
            {
                "id": "get_time",
                "patterns": [
                    "what's the time",
                    "tell me the time",
                    "what time is it",
                    "current time",
                    "time now",
                    "check the time",
                    "display time",
                    "show me the time",
                    "clock"
                ],
                "examples": [
                    "what's the time right now",
                    "tell me the current time",
                    "what time is it",
                    "current time please",
                    "time now",
                    "check the time for me",
                    "display time on screen",
                    "show me the time",
                    "clock"
                ],
                "template": "the time",
                "params": [],
                
            },
            {
                "id": "get_date",
                "patterns": [
                    "what's the date",
                    "tell me the date",
                    "what date is it today",
                    "today's date",
                    "current date",
                    "check the date",
                    "display date",
                    "show me the date",
                    "what day is it"
                ],
                "examples": [
                    "what's today's date",
                    "tell me what date it is",
                    "what's the date today",
                    "today's date please",
                    "current date",
                    "check the date for me",
                    "display date on screen",
                    "show me the date",
                    "what day is it today"
                ],
                "template": "the date",
                "params": [],
                
            },
            {
                "id": "take_note",
                "patterns": [
                    "take a note {content}",
                    "create a note {content}",
                    "note down {content}",
                    "make a note of {content}",
                    "save a note {content}",
                    "write down {content}",
                    "remember {content}",
                    "jot down {content}",
                    "add note {content}"
                ],
                "examples": [
                    "take a note buy groceries tomorrow",
                    "create a note meeting with John at 3pm",
                    "note down ideas for the project",
                    "make a note of birthday gift ideas",
                    "save a note call dentist",
                    "write down finish report by friday",
                    "remember pick up dry cleaning",
                    "jot down flight number AA123",
                    "add note renew passport"
                ],
                "template": "take a note {content}",
                "params": ["content"],
                "param_extractors": {
                    "content": self._extract_note_content
                },
                
            },
            {
                "id": "list_notes",
                "patterns": [
                    "list notes",
                    "show my notes",
                    "read my notes",
                    "what notes do I have",
                    "display notes",
                    "view all notes",
                    "show saved notes",
                    "read notes",
                    "show me my notes"
                ],
                "examples": [
                    "list all my notes",
                    "show my saved notes",
                    "what notes do I have",
                    "display notes",
                    "view all notes",
                    "show saved notes",
                    "read notes to me",
                    "show me my notes"
                ],
                "template": "list notes",
                "params": [],
                
            },
            {
                "id": "take_screenshot",
                "patterns": [
                    "take a screenshot",
                    "capture screen",
                    "screenshot this",
                    "screen capture",
                    "snap screenshot",
                    "get screenshot",
                    "save screenshot",
                    "capture window",
                    "grab screenshot"
                ],
                "examples": [
                    "take a screenshot please",
                    "capture my screen",
                    "I need a screenshot",
                    "screen capture now",
                    "snap screenshot",
                    "get screenshot of this",
                    "save screenshot",
                    "capture window",
                    "grab screenshot right now"
                ],
                "template": "take a screenshot",
                "params": [],
                
            },
            {
                "id": "play_music",
                "patterns": [
                    "play music",
                    "play some songs",
                    "play a song",
                    "start music",
                    "open music player",
                    "play some tunes",
                    "play audio",
                    "I want to listen to music",
                    "play some music"
                ],
                "examples": [
                    "play some music",
                    "play a random song",
                    "I want to listen to music",
                    "start music player",
                    "open music player",
                    "play some tunes for me",
                    "play audio files",
                    "I want to listen to some songs",
                    "play some good music"
                ],
                "template": "play music",
                "params": [],
                
            },
            {
                "id": "get_weather",
                "patterns": [
                    "weather",
                    "what's the weather",
                    "weather forecast",
                    "how's the weather",
                    "weather today",
                    "is it going to rain",
                    "check weather",
                    "weather report",
                    "temperature today"
                ],
                "examples": [
                    "what's the weather like today",
                    "tell me the weather forecast",
                    "is it going to rain today",
                    "how's the weather outside",
                    "weather today",
                    "is it sunny today",
                    "check weather for me",
                    "weather report for today",
                    "temperature today"
                ],
                "template": "weather",
                "params": [],
                
            },
            {
                "id": "system_info",
                "patterns": [
                    "system info",
                    "computer info",
                    "tell me about this computer",
                    "system specs",
                    "hardware info",
                    "specs",
                    "computer specs",
                    "pc info",
                    "device info"
                ],
                "examples": [
                    "show system information",
                    "what are my computer specs",
                    "tell me about this system",
                    "system specs please",
                    "hardware info",
                    "what specs does this computer have",
                    "computer specs",
                    "pc info",
                    "device info"
                ],
                "template": "system info",
                "params": [],
                
            },
            {
                "id": "record_audio",
                "patterns": [
                    "record audio for {duration} seconds",
                    "record voice for {duration} seconds",
                    "record {duration} seconds of audio",
                    "voice recording for {duration} seconds",
                    "capture audio for {duration} seconds",
                    "record sound for {duration} seconds",
                    "start audio recording for {duration} seconds",
                    "record my voice for {duration} seconds",
                    "audio capture for {duration} seconds"
                ],
                "examples": [
                    "record audio for 10 seconds",
                    "record my voice for 30 seconds",
                    "start voice recording for 15 seconds",
                    "voice recording for 20 seconds",
                    "capture audio for 5 seconds",
                    "record sound for 45 seconds",
                    "start audio recording for 60 seconds",
                    "record my voice for 25 seconds",
                    "audio capture for 10 seconds"
                ],
                "template": "record audio for {duration} seconds",
                "params": ["duration"],
                "param_extractors": {
                    "duration": self._extract_duration
                },
                
            },
            {
                "id": "open_application",
                "patterns": [
                    "open {application}",
                    "launch {application}",
                    "start {application}",
                    "run {application}",
                    "execute {application}",
                    "fire up {application}",
                    "boot up {application}",
                    "start up {application}",
                    "initiate {application}"
                ],
                "examples": [
                    "open notepad",
                    "launch excel",
                    "start spotify",
                    "run calculator",
                    "execute chrome",
                    "fire up paint",
                    "boot up photoshop",
                    "start up word",
                    "initiate powerpoint"
                ],
                "template": "open {application}",
                "params": ["application"],
                "param_extractors": {
                    "application": self._extract_application_name
                },
                
            },
            {
                "id": "close_application",
                "patterns": [
                    "close {application}",
                    "exit {application}",
                    "quit {application}",
                    "terminate {application}",
                    "shut down {application}",
                    "kill {application}",
                    "end {application}",
                    "stop {application}",
                    "close out of {application}"
                ],
                "examples": [
                    "close chrome",
                    "exit word",
                    "quit photoshop",
                    "terminate calculator",
                    "shut down spotify",
                    "kill notepad",
                    "end excel",
                    "stop vlc",
                    "close out of firefox"
                ],
                "template": "close {application}",
                "params": ["application"],
                "param_extractors": {
                    "application": self._extract_application_name
                },
                
            }
              
        ]
        
        # Generate more examples from patterns
        for cmd in commands:
            if "params" in cmd and cmd["params"]:
                # Add additional examples using pattern variations
                placeholder_values = {
                    "query": ["recent news", "python programming", "climate change", "healthy recipes", "electric cars"],
                    "task": ["call John", "send email", "check stocks", "take medicine", "submit report"],
                    "time": ["5", "10", "30", "15", "45"],
                    "amount": ["100", "50", "200", "25", "75"],
                    "from_currency": ["dollars", "euros", "rupees", "yen", "pounds"],
                    "to_currency": ["yen", "pounds", "euros", "dollars", "yuan"],
                    "content": ["meeting at 2pm", "buy groceries", "call mom", "dentist appointment", "review document"],
                    "duration": ["10", "30", "60", "15", "5"],
                    "application": ["notepad", "chrome", "word", "excel", "spotify"],
                    "filename": ["report.docx", "budget.xlsx", "presentation.pptx", "notes.txt", "image.jpg"],
                    "recipient": ["John", "boss", "mom", "team", "support"],
                    "subject": ["meeting", "update", "question", "schedule", "request"]
                }
                
                # Generate additional examples from patterns
                if "patterns" in cmd:
                    for pattern in cmd["patterns"]:
                        # Skip if this is already an example
                        if pattern in cmd["examples"]:
                            continue
                            
                        # Create new examples by substituting placeholders
                        example = pattern
                        for param in cmd["params"]:
                            if "{" + param + "}" in pattern and param in placeholder_values:
                                example = example.replace("{" + param + "}", placeholder_values[param][0])
                        
                        # Add the example if it's not already there
                        if example not in cmd["examples"]:
                            cmd["examples"].append(example)
        
        return commands
        
    def generate_command_paraphrases(self):
        """Generate paraphrases of existing command examples for better coverage"""
        new_examples = []
        
        for cmd in self.commands:
            for example in cmd["examples"]:
                words = example.split()
                
                # Try replacing words with synonyms
                for i, word in enumerate(words):
                    if len(word) <= 3 or word in ["the", "and", "for", "with"]:
                        continue
                        
                    # Find synonyms
                    synonyms = []
                    for syn in wordnet.synsets(word):
                        for lemma in syn.lemmas():
                            if lemma.name() != word and lemma.name() not in synonyms:
                                synonyms.append(lemma.name())
                    
                    # Create new examples with synonyms
                    for synonym in synonyms[:2]:  # Limit to top 2 synonyms
                        new_words = words.copy()
                        new_words[i] = synonym
                        new_example = " ".join(new_words)
                        if new_example not in cmd["examples"]:
                            new_examples.append((cmd["id"], new_example))
                            
        # Add the new examples to their respective commands
        for cmd_id, new_example in new_examples:
            for cmd in self.commands:
                if cmd["id"] == cmd_id:
                    cmd["examples"].append(new_example)
                    break
                
    def generate_embeddings(self):
        """Generate embeddings for all command examples"""
        all_examples = []
        self.generate_command_paraphrases()
        # Collect all examples for embedding
        for cmd in self.commands:
            all_examples.extend(cmd["examples"])
            
        # Generate embeddings
        embeddings = self.model.encode(all_examples)
        
        return {
            "examples": all_examples,
            "vectors": embeddings
        }
    
    def classify_intent(self, query):
        """Classify the high-level intent of the query before specific matching"""
        intents = {
            "information": ["tell me", "what is", "how to", "when is", "where is", "check", "find out"],
            "action": ["open", "close", "start", "launch", "play", "record", "send", "create"],
            "reminder": ["remind", "remember", "notification", "alert", "alarm"],
            "system": ["screenshot", "system", "computer", "specs", "info"],
            "search": ["search", "look up", "find", "google", "youtube", "locate"]
        }
        
        # Determine primary intent
        query_lower = query.lower()
        for intent, keywords in intents.items():
            if any(kw in query_lower for kw in keywords):
                return intent
        
        return "general"
        
    def process_query(self, query):
        """Enhanced query processing with semantic understanding and context"""
        # Preprocess the query
        cleaned_query = self.preprocess(query)
        
        # Add to conversation history
        self.context["conversation_history"].append(cleaned_query)
        
        # Check for follow-up commands that refer to previous context
        follow_up = self._check_follow_up_command(cleaned_query)
        if follow_up["is_follow_up"]:
            # Reconstruct the query using previous context
            cleaned_query = follow_up["reconstructed_query"]
        
        # Classify the general intent
        intent = self.classify_intent(cleaned_query)
        
        # Find the most similar command
        matched_command, similarity = self.match_command(cleaned_query, intent)
        
        if matched_command is None:
            return {
                "status": "no_match",
                "message": "I didn't understand that command. Could you try rephrasing it?"
            }
        
        # Extract parameters using the command's extractors
        params = self._extract_parameters(cleaned_query, matched_command)
        
        # Format the command with the extracted parameters
        command = matched_command["template"]
        for param, value in params.items():
            if value:  # Only replace if we have a value
                command = command.replace("{" + param + "}", str(value))
        
        # Update conversation context
        self.context["last_command"] = matched_command["id"]
        self.context["last_parameters"] = params
        
        # Track opened applications
        if matched_command["id"] == "open_application" and "application" in params:
            self.context["session_apps"].add(params["application"])
            
        # Execute the command if execution function exists
        result = {
            "status": "success",
            "command": command,
            "command_id": matched_command["id"],
            "similarity": float(similarity),
            "original_query": query,
            "parameters": params  # Return the extracted parameters too
        }
        
        # Execute the command if it has an execution function
        if "execution" in matched_command:
            try:
                execution_result = matched_command["execution"](params)
                result["execution_result"] = execution_result
            except Exception as e:
                result["execution_error"] = str(e)
        
        return result

    def _check_follow_up_command(self, query):
        """Check if this is a follow-up command referring to previous context"""
        # Words that suggest this is a follow-up
        follow_up_indicators = ["it", "that", "this", "the same", "again", "too", "also"]
        
        # Check if query contains follow-up indicators and is short
        is_follow_up = any(indicator in query.lower() for indicator in follow_up_indicators) and len(query.split()) < 5
        
        reconstructed_query = query
        
        if is_follow_up and self.context["last_command"]:
            # Reconstruct based on previous command
            if self.context["last_command"] == "wikipedia_search" and "search" in query.lower():
                # For example: "look that up too" -> "search wikipedia for {previous_topic}"
                reconstructed_query = f"search wikipedia for {self.context['last_parameters'].get('query', '')}"
            
            elif self.context["last_command"] in ["open_application", "close_application"] and any(x in query.lower() for x in ["close", "open", "it"]):
                # For example: "close it" -> "close {previous_app}"
                app = self.context["last_parameters"].get("application", "")
                action = "close" if "close" in query.lower() else "open"
                reconstructed_query = f"{action} {app}"
                
            elif self.context["last_command"] == "youtube_search" and any(x in query.lower() for x in ["find", "search", "it"]):
                # For example: "find more of that" -> "search youtube for {previous_topic}"
                reconstructed_query = f"search youtube for {self.context['last_parameters'].get('query', '')}"
                
            elif self.context["last_command"] == "google_search" and any(x in query.lower() for x in ["search", "google", "find"]):
                # For example: "google that again" -> "search google for {previous_topic}"
                reconstructed_query = f"search google for {self.context['last_parameters'].get('query', '')}"
        
        return {
            "is_follow_up": is_follow_up,
            "reconstructed_query": reconstructed_query
        }

    def match_command(self, query, intent=None):
        """Find the best matching command with intent filtering"""
        # Generate embedding for the query
        query_embedding = self.model.encode([query])[0]
        
        # Calculate similarities with optional intent filtering
        similarities = []
        for i, example_embedding in enumerate(self.command_embeddings["vectors"]):
            example = self.command_embeddings["examples"][i]
            
            # If intent is provided, check if this example aligns with the intent
            if intent:
                example_intent = self.classify_intent(example)
                if example_intent != intent and intent != "general":
                    continue
            
            similarity = self._cosine_similarity(query_embedding, example_embedding)
            similarities.append((similarity, i))
        
        # If no matches after intent filtering, try without filtering
        if not similarities and intent:
            return self.match_command(query)  # Recursive call without intent
        
        # Sort by similarity (highest first)
        similarities.sort(reverse=True)
        
        if not similarities:
            return None, 0
        
        # Get the command for the top match
        best_match_idx = similarities[0][1]
        best_match_example = self.command_embeddings["examples"][best_match_idx]
        best_match_score = similarities[0][0]
        
        # Find which command this example belongs to
        for cmd in self.commands:
            if best_match_example in cmd["examples"]:
                # Adjust threshold based on intent and query length
                threshold = 0.5
                if len(query.split()) <= 2:  # Very short queries need higher confidence
                    threshold = 0.65
                
                if best_match_score < threshold:
                    return None, 0
                
                return cmd, best_match_score
        
        return None, 0
    
    def _extract_parameters(self, query, command):
        """Extract parameters from a query using command-specific extractors"""
        params = {}
        
        # Extract each parameter using its specific extractor
        if "param_extractors" in command:
            for param, extractor in command["param_extractors"].items():
                if param in command.get("params", []):
                    params[param] = extractor(query)
        
        return params
    
    # Parameter extraction methods
    def _extract_wikipedia_query(self, query):
        """Extract the search query from a Wikipedia request"""
        # Remove terms related to Wikipedia
        query = query.lower()
        query = re.sub(r'(wikipedia|search|look up|for|on)\s+', ' ', query)
        query = re.sub(r'\s+', ' ', query).strip()
        return query
    
    def _extract_search_query(self, query):
        """Extract the search query from a search request"""
        # Remove search prefixes
        query = query.lower()
        query = re.sub(r'(search|google|youtube|look up|find|for|on|online|videos)\s+', ' ', query)
        query = re.sub(r'\s+', ' ', query).strip()
        return query
    
    def _extract_reminder_task(self, query):
        """Extract the task part from a reminder request"""
        # Try to find task between "remind me to" and "in X minutes"
        query = query.lower()
        match = re.search(r'remind me to\s+(.+?)\s+in \d+', query)
        if match:
            return match.group(1)
        
        # Try to find task after "in X minutes to"
        match = re.search(r'in \d+ minutes to\s+(.+)', query)
        if match:
            return match.group(1)
        
        # Fallback: remove time references
        query = re.sub(r'(remind me|to|in \d+ minutes|set a reminder for)\s+', ' ', query)
        return query.strip()
    
    def _extract_time_value(self, query):
        """Extract the time value from a time-related query"""
        query = query.lower()
        
        # Try to extract numeric value
        match = re.search(r'(\d+)\s+(minute|minutes|min|mins)', query)
        if match:
            return match.group(1)
        
        # Try to extract text numbers
        word_to_number = {
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            'fifteen': '15', 'twenty': '20', 'thirty': '30', 'forty': '40',
            'fifty': '50', 'sixty': '60'
        }
        
        for word, number in word_to_number.items():
            pattern = r'(?:in|for)\s+(' + word + r')\s+(?:minute|minutes|min|mins)'
            match = re.search(pattern, query)
            if match:
                return number
        
        # Default if no time is found
        return "1"  # Default to 5 minutes
    
    def _extract_currency_amount(self, query):
        """Extract the currency amount from a currency conversion query"""
        query = query.lower()
        
        # Try to extract numeric amount
        match = re.search(r'(\d+(?:\.\d+)?)', query)
        if match:
            return match.group(1)
        
        # Default if no amount is found
        return "1"
    
    def _extract_from_currency(self, query):
        """Extract the source currency from a currency conversion query"""
        query = query.lower()
        currencies = ["dollars", "euros", "rupees", "pounds", "yen", "yuan"]
        
        # Try to find currency after amount
        for currency in currencies:
            match = re.search(r'\d+(?:\.\d+)?\s+(' + currency + r')', query)
            if match:
                return match.group(1)
        
        # Try to find currency after "from"
        match = re.search(r'from\s+(\w+)', query)
        if match and match.group(1) in currencies:
            return match.group(1)
        
        # Default
        return "dollars"
    
    def _extract_to_currency(self, query):
        """Extract the target currency from a currency conversion query"""
        query = query.lower()
        currencies = ["dollars", "euros", "rupees", "pounds", "yen", "yuan"]
        
        # Try to find currency after "to"
        match = re.search(r'to\s+(\w+)', query)
        if match and match.group(1) in currencies:
            return match.group(1)
        
        # Try to find currency at the end
        match = re.search(r'in\s+(\w+)$', query)
        if match and match.group(1) in currencies:
            return match.group(1)
        
        # Default
        return "euros"
    
    def _extract_note_content(self, query):
        """Extract note content from a note-taking query"""
        query = query.lower()
        
        # Remove note-taking prefixes
        query = re.sub(r'(take a note|create a note|note down)\s+', '', query)
        return query.strip()
    
    def _extract_duration(self, query):
        """Extract duration in seconds from a recording query"""
        query = query.lower()
        
        # Try to extract numeric duration
        match = re.search(r'(\d+)\s+(second|seconds|sec|secs)', query)
        if match:
            return match.group(1)
        
        # Extract numeric value anywhere in the query as fallback
        match = re.search(r'(\d+)', query)
        if match:
            return match.group(1)
        
        # Default
        return "10"  # Default to 10 seconds
    
    def _extract_application_name(self, query):
        """Extract application name from an open/close application query"""
        query = query.lower()
        
        # Common applications
        common_apps = ["chrome", "firefox", "edge", "notepad", "word", "excel", 
                      "Powerpoint", "spotify", "vlc", "calculator", "paint", "command prompt"]
        
        # Try to find application name after open/close/launch/start
        for action in ["open", "close", "launch", "start", "exit", "quit"]:
            match = re.search(action + r'\s+(\w+)', query)
            if match:
                app_name = match.group(1)
                # Check if it's a common app or extract whatever is there
                if app_name in common_apps:
                    return app_name
                return app_name
        
        # Default
        return "notepad"
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot / (norm1 * norm2)

# Example usage
if __name__ == "__main__":
    matcher = CommandMatcher()
    
    # Test queries
    test_queries = [
        "can you open youtube please",
        "tell me what time it is right now",
        "I need to know the weather today",
        "remind me to check my email in 15 minutes",
        "can you check what's on wikipedia about quantum physics",
        "I need to look something up on google about pandas",
        "take a screenshot of my screen",
        "please write down that I need to buy milk",
        "can you open notepad for me",
        "hey can you remind me to call my mom in 30 minutes",
        "what's the date today",
        "show me what notes I have saved",
        "play some music for me",
        "how much is 50 dollars in euros",
        "what are the specs of this computer"
    ]
    
    # Process each query
    for query in test_queries:
        result = matcher.process_query(query)
        print(f"Query: {query}")
        print(f"Result: {json.dumps(result, indent=2)}")
        print("-" * 50)