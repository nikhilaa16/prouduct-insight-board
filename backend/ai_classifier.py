import os
import re
from pydantic import BaseModel, Field
import google.generativeai as genai

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

def _get_simulated_analysis(text: str) -> dict:
    """
    A high-fidelity keywords-based matching algorithm to simulate the AI.
    Runs locally and allows immediate offline testing.
    """
    text_lower = text.lower()
    
    # 1. Determine Category
    category = "Others"
    if any(k in text_lower for k in ["login", "password", "sign in", "signin", "register", "signup", "auth", "otp"]):
        category = "Login"
    elif any(k in text_lower for k in ["pay", "card", "checkout", "billing", "price", "purchase", "stripe", "bank", "money", "transaction"]):
        category = "Payment"
    elif any(k in text_lower for k in ["slow", "lag", "delay", "load", "loading", "speed", "hang", "freeze", "performance"]):
        category = "Performance"
    elif any(k in text_lower for k in ["ui", "button", "color", "screen", "dark mode", "font", "display", "layout", "mobile"]):
        category = "UI/UX"

    # 2. Determine Type
    feedback_type = "Bug"
    if any(k in text_lower for k in ["suggest", "improve", "add", "feature", "would love", "request", "please allow", "hope you can"]):
        feedback_type = "Feature Request"
    elif any(k in text_lower for k in ["great", "awesome", "love", "thanks", "perfect", "good", "happy", "nice"]):
        feedback_type = "Praise"

    # 3. Determine Urgency Score
    urgency_score = 2
    if feedback_type == "Praise":
        urgency_score = 1
    elif feedback_type == "Feature Request":
        urgency_score = 2
    else: # Bug
        urgency_score = 3
        # Elevate urgency if critical keywords are present
        if any(k in text_lower for k in ["crash", "fail", "lose", "lost", "broken", "critical", "blocking", "preventing", "cannot checkout", "unable to login"]):
            urgency_score = 5
        elif any(k in text_lower for k in ["error", "freeze", "wrong", "blank", "incorrect"]):
            urgency_score = 4

    # 4. Generate Summary
    # Extract first sentence or truncate text
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
    If present, calls real Gemini API. Otherwise, falls back to the simulation model.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Using FeedLoop AI local classification simulation.")
        return _get_simulated_analysis(text)
    
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
        # Parse JSON from markdown output block if necessary
        raw_response = response.text.strip()
        
        # Simple regex to extract JSON block if wrapped in ```json
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            import json
            analysis_dict = json.loads(json_match.group(0))
            # Validate key presence
            required = ["category", "feedback_type", "urgency_score", "ai_summary"]
            if all(k in analysis_dict for k in required):
                return analysis_dict
                
        raise ValueError("Could not extract clean JSON structured output from Gemini response.")
        
    except Exception as e:
        print(f"Gemini API call failed, falling back to local simulation: {e}")
        return _get_simulated_analysis(text)
