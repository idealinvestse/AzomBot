import os
import json

class SupportPipeline:
    """Pipeline för support och FAQ."""
    def __init__(self, faq_path=None):
        self.faq = []
        
        if faq_path:
            # Load from the provided path if specified (for testing)
            try:
                with open(faq_path, 'r', encoding='utf-8') as f:
                    self.faq = json.load(f)
            except Exception as e:
                print(f"Error loading FAQ from {faq_path}: {e}")
        else:
            # Default behavior - load from data directory
            data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
            # Ladda från faq.json
            try:
                with open(os.path.join(data_dir, 'faq.json'), encoding='utf-8') as f:
                    self.faq += json.load(f)
            except Exception as e:
                print(f"Error loading faq.json: {e}")
            # Ladda från other_*.json
            for fname in os.listdir(data_dir):
                if fname.startswith('other_') and fname.endswith('.json'):
                    try:
                        with open(os.path.join(data_dir, fname), encoding='utf-8') as f:
                            for item in json.load(f):
                                if 'question' in item and 'answer' in item:
                                    self.faq.append(item)
                    except Exception as e:
                        print(f"Error loading {fname}: {e}")

    async def run_support(self, user_input: str):
        print(f"Debug - User input: {user_input}")
        print(f"Debug - FAQ questions: {[f.get('question', '') for f in self.faq]}")
        user_input_lower = user_input.lower()
        
        # First try exact match
        for f in self.faq:
            question = f.get("question", "").lower()
            if question == user_input_lower:
                print(f"Debug - Exact match: {question}")
                return {"answer": f.get("answer")}
        
        # Then try partial match with keywords
        for f in self.faq:
            question = f.get("question", "").lower()
            answer = f.get("answer", "").lower()
            
            # Check if any significant word from the question is in the user input
            question_keywords = [word for word in question.split() if len(word) > 3]
            if any(keyword in user_input_lower for keyword in question_keywords):
                print(f"Debug - Keyword match: {question}")
                return {"answer": f.get("answer")}
                
            # Also check if any significant word from the answer is in the user input
            answer_keywords = [word for word in answer.split() if len(word) > 3]
            if any(keyword in user_input_lower for keyword in answer_keywords):
                print(f"Debug - Answer keyword match: {question}")
                return {"answer": f.get("answer")}
                
        print("Debug - No match found")
        return {"answer": "Din fråga matchade ingen FAQ. Kontakta support@azom.se."}

    async def get_all_faq(self):
        # Returnera hela FAQ-listan
        return [{"question": f.get("question"), "answer": f.get("answer")} for f in self.faq]
