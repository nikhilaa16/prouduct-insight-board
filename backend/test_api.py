import requests
import json
import sys

# Configure console encoding to print emojis on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("=== STARTING FEEDLOOP AI API VERIFICATION ===")
    
    # 1. Test Feedback Submission
    print("\n1. Submitting test bug ticket...")
    bug_payload = {
        "raw_text": "The payment page crashes when checking out. I lost my order and money!",
        "source": "iOS App",
        "customer_email": "test-buyer@gmail.com"
    }
    res = requests.post(f"{BASE_URL}/api/feedback/submit", json=bug_payload)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        item = res.json()
        print(f"Successfully processed! AI Classification Results:")
        print(f"  - Category: {item['category']} (Expected: Payment)")
        print(f"  - Issue Type: {item['feedback_type']} (Expected: Bug)")
        print(f"  - Urgency Score: {item['urgency_score']} (Expected: 5)")
        print(f"  - Summary: '{item['ai_summary']}'")
    else:
        print(f"Error: {res.text}")
        return

    print("\n2. Submitting test feature request ticket...")
    feature_payload = {
        "raw_text": "Please add dark mode to the main settings panel, it is very important.",
        "source": "Web Portal",
        "customer_email": "test-user@gmail.com"
    }
    res = requests.post(f"{BASE_URL}/api/feedback/submit", json=feature_payload)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        item = res.json()
        print(f"Successfully processed! AI Classification Results:")
        print(f"  - Category: {item['category']} (Expected: UI/UX)")
        print(f"  - Issue Type: {item['feedback_type']} (Expected: Feature Request)")
        print(f"  - Urgency Score: {item['urgency_score']} (Expected: 2)")
    else:
        print(f"Error: {res.text}")
        return

    # 2. Test Get Stats
    print("\n3. Querying aggregated stats...")
    res = requests.get(f"{BASE_URL}/api/feedback/stats")
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        stats = res.json()
        print("Stats:")
        print(f"  - Total Count: {stats['total_count']}")
        print(f"  - Bug Count: {stats['bug_count']}")
        print(f"  - Feature Count: {stats['feature_count']}")
        print(f"  - Average Urgency: {stats['average_urgency']}")
        print(f"  - Category Distribution: {stats['category_distribution']}")
    else:
        print(f"Error: {res.text}")
        return

    # 3. Test Get List
    print("\n4. Querying sorted ticket queue...")
    res = requests.get(f"{BASE_URL}/api/feedback/list")
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        items = res.json()
        print(f"Retrieved {len(items)} tickets from PostgreSQL.")
        for item in items:
            print(f"  - [{item['status']}] [Urgency: {item['urgency_score']}] Category: {item['category']} | {item['ai_summary']}")
    else:
        print(f"Error: {res.text}")
        return

    # 4. Test Roadmap Generation
    print("\n5. Triggering AI Sprint Roadmap Planner...")
    res = requests.post(f"{BASE_URL}/api/roadmap/generate")
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        roadmap = res.json()["roadmap"]
        print("\n=== GENERATED ROADMAP ===")
        print(roadmap)
        print("=========================")
    else:
        print(f"Error: {res.text}")
        return

    print("\n=== VERIFICATION SUCCESSFULLY COMPLETED! ===")

if __name__ == "__main__":
    test_api()
