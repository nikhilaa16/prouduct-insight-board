import os
import re
from pydantic import BaseModel, Field
import google.generativeai as genai
import joblib
from textblob import TextBlob

# Define Pydantic Schema for structured AI response
class FeedbackAnalysis(BaseModel):
    category: str = Field(
        description="Category of the feedback. Must be one of: Login, Payment, UI/UX, Performance, Others"
    )
    feedback_type: str = Field(
        description="Type of issue. Must be one of: Bug, Feature Request, Praise"
    )
    urgency_score: int = Field(
        description="Priority score from 1 (lowest) to 5 (highest, e.g. system down/payment failed)"
    )
    ai_summary: str = Field(
        description="A concise summary of the issue under 10 words"
    )

# Global variables for local ML models
category_model = None
type_model = None

# Attempt to load local ML models
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cat_path = os.path.join(base_dir, "models", "category_model.pkl")
    type_path = os.path.join(base_dir, "models", "type_model.pkl")
    
    if os.path.exists(cat_path) and os.path.exists(type_path):
        category_model = joblib.load(cat_path)
        type_model = joblib.load(type_path)
        print("Successfully loaded local Scikit-Learn ML models.")
    else:
        print("Local ML model files not found. Fallback to keyword-based simulator will be used.")
except Exception as e:
    print(f"Error loading local ML models: {e}. Falling back to keyword simulator.")


def _get_local_ml_analysis(text: str) -> dict:
    """
    Analyzes raw customer text using local Machine Learning pipelines.
    - Category & Type: Scikit-Learn Logistic Regression TF-IDF models
    - Urgency Score: TextBlob Sentiment Polarity mapped to a 1-5 scale with custom fallback rules
    """
    text_lower = text.lower()
    
    # 1. Category Classification via ML
    if category_model is not None:
        try:
            category = category_model.predict([text])[0]
        except Exception as e:
            print(f"Category prediction error: {e}")
            category = "Others"
    else:
        # Fallback to simple matching if model not trained yet
        category = "Others"
        if any(k in text_lower for k in ["login", "password", "sign in", "signin", "register", "signup", "auth", "otp"]):
            category = "Login"
        elif any(k in text_lower for k in ["pay", "card", "checkout", "billing", "price", "purchase", "stripe", "bank", "money", "transaction"]):
            category = "Payment"
        elif any(k in text_lower for k in ["slow", "lag", "delay", "load", "loading", "speed", "hang", "freeze", "performance"]):
            category = "Performance"
        elif any(k in text_lower for k in ["ui", "button", "color", "screen", "dark mode", "font", "display", "layout", "mobile"]):
            category = "UI/UX"

    # 2. Issue Type Classification via ML
    if type_model is not None:
        try:
            feedback_type = type_model.predict([text])[0]
        except Exception as e:
            print(f"Type prediction error: {e}")
            feedback_type = "Bug"
    else:
        feedback_type = "Bug"
        if any(k in text_lower for k in ["suggest", "improve", "add", "feature", "would love", "request", "please allow", "hope you can"]):
            feedback_type = "Feature Request"
        elif any(k in text_lower for k in ["great", "awesome", "love", "thanks", "perfect", "good", "happy", "nice"]):
            feedback_type = "Praise"

    # 3. Urgency Score via NLP Sentiment Polarity
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
    except Exception as e:
        print(f"TextBlob sentiment extraction error: {e}")
        polarity = 0.0

    if feedback_type == "Praise":
        urgency_score = 1
    elif feedback_type == "Feature Request":
        urgency_score = 2
    else: # Bug
        # Map negative polarity to higher urgency scores
        if polarity <= -0.4:
            urgency_score = 5  # Critical defect
        elif polarity < 0.0:
            urgency_score = 4  # Serious defect
        else:
            urgency_score = 3  # Normal bug
            
        # Hybrid Rule-Model check: Elevate urgency if critical keywords exist
        critical_keywords = ["crash", "fail", "lose", "lost", "broken", "critical", "blocking", "preventing", "cannot checkout", "unable to login"]
        if any(k in text_lower for k in critical_keywords):
            urgency_score = 5

    # 4. Generate Summary
    sentences = re.split(r'[.!?]', text)
    first_sentence = sentences[0].strip() if sentences else text
    words = first_sentence.split()
    if len(words) > 8:
        ai_summary = " ".join(words[:8]) + "..."
    else:
        ai_summary = first_sentence

    return {
        "category": category,
        "feedback_type": feedback_type,
        "urgency_score": urgency_score,
        "ai_summary": ai_summary
    }


def analyze_feedback(text: str) -> dict:
    """
    Main entrypoint to classify feedback.
    Checks for GEMINI_API_KEY environment variable. 
    If present, calls real Gemini API. Otherwise, falls back to local ML models.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Using FeedLoop Local ML Classification Pipeline.")
        return _get_local_ml_analysis(text)
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Analyze this customer support/experience feedback.
        Categorize it into a category ('Login', 'Payment', 'UI/UX', 'Performance', 'Others'), 
        classify its type ('Bug', 'Feature Request', 'Praise'), 
        assign an urgency score (1 to 5, where 5 is critical/crashes/money issues), 
        and write a short summary under 10 words.
        
        Feedback Text: "{text}"
        
        Provide the response strictly as a JSON object matching this schema:
        {{
          "category": "String",
          "feedback_type": "String",
          "urgency_score": Integer,
          "ai_summary": "String"
        }}
        """
        
        response = model.generate_content(prompt)
        raw_response = response.text.strip()
        
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            import json
            analysis_dict = json.loads(json_match.group(0))
            required = ["category", "feedback_type", "urgency_score", "ai_summary"]
            if all(k in analysis_dict for k in required):
                return analysis_dict
                
        raise ValueError("Could not extract clean JSON structured output from Gemini response.")
        
    except Exception as e:
        print(f"Gemini API call failed, falling back to local ML pipeline: {e}")
        return _get_local_ml_analysis(text)
