from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# AI Personality Configuration
AI_NAME = "Astra"
CREATOR_NAME = "Danien Aarzoo Luck"
CREATOR_BIRTHDAY = "2008-12-02"

class AstraAI:
    """Custom AI with personality - Created by Danien Aarzoo Luck"""
    
    def __init__(self):
        self.name = AI_NAME
        self.creator = CREATOR_NAME
        self.creator_birthday = CREATOR_BIRTHDAY
        self.personality_traits = [
            "curious", "helpful", "friendly", "honest", "humble"
        ]
        self.memory = {}  # Simple conversation memory
        
    def get_age_of_creator(self):
        """Calculate creator's age"""
        born = datetime.strptime(self.creator_birthday, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return age
    
    def search_wikipedia(self, query):
        """Search Wikipedia and return relevant information"""
        try:
            # Clean the query
            clean_query = query.strip().replace(" ", "_")
            
            # Search Wikipedia
            search_url = f"https://en.wikipedia.org/w/api.php"
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 1
            }
            
            search_response = requests.get(search_url, params=search_params, timeout=10)
            search_data = search_response.json()
            
            if not search_data.get("query", {}).get("search"):
                return None
            
            # Get the first result's title
            page_title = search_data["query"]["search"][0]["title"]
            
            # Get page summary
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"
            summary_response = requests.get(summary_url, timeout=10)
            
            if summary_response.status_code == 200:
                data = summary_response.json()
                return {
                    "title": data.get("title", ""),
                    "summary": data.get("extract", ""),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                }
            
            return None
            
        except Exception as e:
            print(f"Wikipedia error: {e}")
            return None
    
    def detect_intent(self, text):
        """Detect what the user is asking about"""
        text_lower = text.lower()
        
        # Personal questions about the AI
        if any(word in text_lower for word in ["who are you", "what are you", "your name", "who created you"]):
            return "about_me"
        
        # Questions about the creator
        if any(word in text_lower for word in ["danien", "your creator", "who made you", "who built you"]):
            return "about_creator"
        
        # Greetings
        if any(word in text_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "greeting"
        
        # Capabilities
        if any(word in text_lower for word in ["what can you do", "your capabilities", "help me"]):
            return "capabilities"
        
        # Math operations
        if any(op in text for op in ["+", "-", "*", "/", "calculate", "compute"]):
            return "math"
        
        # Wikipedia lookup (default for knowledge questions)
        question_words = ["what", "who", "where", "when", "why", "how", "tell me about", "explain"]
        if any(word in text_lower for word in question_words):
            return "knowledge"
        
        return "general"
    
    def calculate(self, expression):
        """Safely evaluate math expressions"""
        try:
            # Remove any text, keep only numbers and operators
            clean_expr = re.sub(r'[^0-9+\-*/(). ]', '', expression)
            
            # Simple safety check
            if len(clean_expr) > 100:
                return "That calculation is too complex for me!"
            
            result = eval(clean_expr)
            return f"The answer is: {result}"
        except:
            return "I couldn't calculate that. Please use format like: 5 + 3 or 10 * 2"
    
    def generate_response(self, user_input):
        """Generate appropriate response based on input"""
        intent = self.detect_intent(user_input)
        
        # Responses based on intent
        if intent == "about_me":
            responses = [
                f"I'm {self.name}, an AI assistant created by {self.creator}. I'm designed to be helpful, curious, and honest with you!",
                f"My name is {self.name}! I was built by {self.creator}, who is {self.get_age_of_creator()} years old. I can search Wikipedia and have conversations with you.",
                f"I'm {self.name}, your personal AI. {self.creator} created me to help answer questions and chat with you. I'm still learning and growing!"
            ]
            return random.choice(responses)
        
        elif intent == "about_creator":
            age = self.get_age_of_creator()
            responses = [
                f"I was created by {self.creator}, who was born on December 2nd, 2008. That makes them {age} years old! They built me from scratch using Python and Wikipedia.",
                f"My creator is {self.creator}, a {age}-year-old developer born on 12-02-2008. They're the reason I exist!",
                f"{self.creator} is my creator! They're {age} years old and passionate about AI. They built me entirely on their own!"
            ]
            return random.choice(responses)
        
        elif intent == "greeting":
            greetings = [
                f"Hello! I'm {self.name}. How can I help you today?",
                f"Hey there! {self.name} here, ready to chat!",
                f"Hi! Nice to meet you. What would you like to know?",
                f"Greetings! I'm {self.name}, created by {self.creator}. What can I do for you?"
            ]
            return random.choice(greetings)
        
        elif intent == "capabilities":
            return f"""I'm {self.name}, and here's what I can do:

✓ Answer questions using Wikipedia
✓ Do basic math calculations
✓ Have conversations with you
✓ Tell you about my creator, {self.creator}

What I CAN'T do (yet):
✗ Analyze images (requires neural networks)
✗ Write complex code (I'm rule-based)
✗ Remember long conversations (no database)

But I'm honest, helpful, and always improving! What would you like to know?"""
        
        elif intent == "math":
            return self.calculate(user_input)
        
        elif intent == "knowledge":
            # Extract the topic from the question
            question_words = ["what is", "who is", "where is", "when did", "why does", "how does", "tell me about", "explain"]
            topic = user_input.lower()
            
            for qw in question_words:
                if qw in topic:
                    topic = topic.split(qw)[-1].strip()
                    break
            
            # Clean up the topic
            topic = re.sub(r'[?!.,]', '', topic).strip()
            
            if not topic or len(topic) < 2:
                return "I'd love to help! Could you be more specific about what you want to know?"
            
            # Search Wikipedia
            wiki_data = self.search_wikipedia(topic)
            
            if wiki_data:
                summary = wiki_data["summary"]
                # Limit to first 3 sentences for brevity
                sentences = summary.split(". ")[:3]
                short_summary = ". ".join(sentences) + "."
                
                return f"""Based on Wikipedia:

{short_summary}

Want to learn more? Visit: {wiki_data["url"]}

(I'm using Wikipedia's information, so I'm only as accurate as their articles!)"""
            else:
                return f"I searched Wikipedia but couldn't find information about '{topic}'. Could you rephrase or try a different topic?"
        
        else:
            # General conversation
            responses = [
                "That's interesting! I can search Wikipedia for you, do math, or just chat. What would you like?",
                f"I'm {self.name}, and I'm here to help! Ask me about anything you'd like to know.",
                "I'm not sure how to respond to that, but I'm always learning! Try asking me a question or give me a topic to search.",
                "Hmm, I didn't quite catch that. I work best with questions or topics you want to explore!"
            ]
            return random.choice(responses)

# Initialize AI
astra = AstraAI()

@app.route('/')
def home():
    return jsonify({
        "ai_name": AI_NAME,
        "creator": CREATOR_NAME,
        "version": "1.0",
        "message": f"Hello! I'm {AI_NAME}, created by {CREATOR_NAME}",
        "endpoints": ["/chat", "/about"]
    })

@app.route('/about')
def about():
    """Information about the AI"""
    age = astra.get_age_of_creator()
    return jsonify({
        "ai_name": astra.name,
        "personality": astra.personality_traits,
        "creator": {
            "name": astra.creator,
            "birthday": astra.creator_birthday,
            "age": age
        },
        "capabilities": [
            "Wikipedia search and information retrieval",
            "Basic math calculations",
            "Conversational responses with personality",
            "Honest about limitations"
        ],
        "limitations": [
            "Cannot analyze images (requires neural networks)",
            "Cannot generate complex code (rule-based system)",
            "Limited to Wikipedia knowledge",
            "No persistent memory between sessions"
        ]
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Generate response
        ai_response = astra.generate_response(user_message)
        
        return jsonify({
            "user_message": user_message,
            "ai_response": ai_response,
            "ai_name": astra.name,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    """Math calculation endpoint"""
    try:
        data = request.json
        expression = data.get('expression', '')
        
        result = astra.calculate(expression)
        
        return jsonify({
            "expression": expression,
            "result": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
