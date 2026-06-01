import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# 1. Dataset for Category Prediction
# Categories: 'Login', 'Payment', 'UI/UX', 'Performance', 'Others'
category_data = [
    # Login
    ("I cannot log in to my account. The login page shows a blank screen.", "Login"),
    ("The password reset link is invalid or expired.", "Login"),
    ("I got locked out of my account after three failed attempts.", "Login"),
    ("Please add Google OAuth or sign in with Apple option.", "Login"),
    ("The login authentication token expires too quickly.", "Login"),
    ("Your application makes logging in very seamless and quick.", "Login"),
    
    # Payment
    ("The checkout page throws a 500 error when processing credit cards.", "Payment"),
    ("My Apple Pay transaction keeps hanging and never finishes.", "Payment"),
    ("I was billed twice for this month's subscription.", "Payment"),
    ("Please support PayPal or stripe payments.", "Payment"),
    ("I want to download my PDF invoices from the billing dashboard.", "Payment"),
    ("The payment interface is very clear and easy to navigate.", "Payment"),
    
    # UI/UX
    ("Can you please add a Dark Mode option? My eyes are hurting.", "UI/UX"),
    ("The buttons on the main screen are misaligned and overlap.", "UI/UX"),
    ("The fonts are too small and hard to read on mobile devices.", "UI/UX"),
    ("Love the modern design and interactive charts on the dashboard.", "UI/UX"),
    ("The layout of the settings page is very intuitive.", "UI/UX"),
    ("It would be great to customize the theme colors of the workspace.", "UI/UX"),
    
    # Performance
    ("The page loading speed is extremely slow on mobile Safari.", "Performance"),
    ("The app freezes and crashes when generating large reports.", "Performance"),
    ("Excellent loading time and snappy page transitions!", "Performance"),
    ("Rendering of the charts takes forever to load.", "Performance"),
    ("Optimizing the search query performance would help a lot.", "Performance"),
    ("The main dashboard renders instantly, very impressed.", "Performance"),
    
    # Others
    ("Thank you for the support, you guys are doing a great job.", "Others"),
    ("The documentation is missing details on how to set up webhooks.", "Others"),
    ("Is there an offline mode available for the application?", "Others"),
    ("Wonderful application, saved me hours of manual labor today.", "Others"),
    ("The exported CSV file has incorrect encoding.", "Others")
]

# 2. Dataset for Issue Type Prediction
# Types: 'Bug', 'Feature Request', 'Praise'
type_data = [
    # Bug
    ("The application crashes when clicking the export button.", "Bug"),
    ("I see a blank screen after trying to reset my password.", "Bug"),
    ("The system throws a payment error code 402 on checkout.", "Bug"),
    ("The layout overlaps on Safari browsers.", "Bug"),
    ("It hangs and freezes every time I upload a file.", "Bug"),
    ("My authentication token keeps expiring in under 5 minutes.", "Bug"),
    
    # Feature Request
    ("Please add support for dark mode.", "Feature Request"),
    ("Can you integrate Google and Apple sign-in options?", "Feature Request"),
    ("We need a way to export invoice history to PDF.", "Feature Request"),
    ("It would be great to customize dashboard colors.", "Feature Request"),
    ("Please add automated email notifications on report completion.", "Feature Request"),
    ("Support for PayPal payments is highly requested.", "Feature Request"),
    
    # Praise
    ("This is a beautiful dashboard, extremely polished!", "Praise"),
    ("The page loading is very fast, great job guys.", "Praise"),
    ("Amazing support team, resolved my ticket in minutes.", "Praise"),
    ("Love the seamless user experience and modern design.", "Praise"),
    ("It saved me hours of manual work today.", "Praise"),
    ("Logging in is so fast and simple.", "Praise")
]

def train_and_save_models():
    print("=== Training FeedLoop ML Models ===")
    
    # Split text and labels
    X_cat, y_cat = zip(*category_data)
    X_type, y_type = zip(*type_data)
    
    # 1. Build and Train Category Classifier Pipeline
    print("Training Category Classifier (TF-IDF + Logistic Regression)...")
    category_pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(ngram_range=(1, 2), stop_words='english', min_df=1)),
        ('classifier', LogisticRegression(C=1.0, max_iter=200))
    ])
    category_pipeline.fit(X_cat, y_cat)
    
    # 2. Build and Train Issue Type Classifier Pipeline
    print("Training Issue Type Classifier (TF-IDF + Logistic Regression)...")
    type_pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(ngram_range=(1, 2), stop_words='english', min_df=1)),
        ('classifier', LogisticRegression(C=1.0, max_iter=200))
    ])
    type_pipeline.fit(X_type, y_type)
    
    # Create directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Save the models
    category_model_path = os.path.join("models", "category_model.pkl")
    type_model_path = os.path.join("models", "type_model.pkl")
    
    joblib.dump(category_pipeline, category_model_path)
    joblib.dump(type_pipeline, type_model_path)
    
    print(f"Successfully saved category model to: {category_model_path}")
    print(f"Successfully saved issue type model to: {type_model_path}")
    print("=== Training Completed! ===")

if __name__ == "__main__":
    train_and_save_models()
