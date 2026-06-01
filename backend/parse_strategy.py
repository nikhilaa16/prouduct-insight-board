import json
import os
import re

def parse_strategy_chat():
    log_path = r"C:\Users\nikhii 2\.gemini\antigravity\brain\d0fe6530-d07f-40d9-a5b0-601a9099f97d\.system_generated\logs\transcript.jsonl"
    output_path = r"C:\Users\nikhii 2\.gemini\antigravity\scratch\feedloop-insight-board\PROJECTS_STRATEGY_CHAT.md"
    
    if not os.path.exists(log_path):
        print(f"Error: Log file not found at {log_path}")
        return

    print("Compiling projects strategy chat transcript...")
    transcript_md = []
    transcript_md.append("# 🎯 Career Strategy & Placement Projects Analysis Chat History\n")
    transcript_md.append("This document contains the complete conversation history detailing the placement project analysis, service-based vs. product-based companies hiring criteria, non-FinTech project specifications, and interview talking points.\n")
    transcript_md.append("---\n")
    
    with open(log_path, 'r', encoding='utf-8') as f:
        step_num = 1
        for line in f:
            if not line.strip():
                continue
            try:
                step = json.loads(line)
                source = step.get("source", "")
                step_type = step.get("type", "")
                content = step.get("content", "")
                
                # We only want the first 14 steps which represent the strategy discussion
                if step_num > 14:
                    break
                
                # Check for User Inputs
                if source == "USER_EXPLICIT" or step_type == "USER_INPUT":
                    clean_content = content.replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "")
                    clean_content = re.sub(r'<user_information>.*?</user_information>', '', clean_content, flags=re.DOTALL)
                    clean_content = clean_content.strip()
                    
                    if clean_content:
                        transcript_md.append(f"\n### 👤 User Query (Step {step_num})\n")
                        transcript_md.append(f"{clean_content}\n")
                        transcript_md.append("\n---\n")
                        step_num += 1
                        
                # Check for Model Responses
                elif source == "MODEL" and content:
                    clean_content = content.strip()
                    # Skip code blocks or logs that aren't text responses
                    if clean_content and not clean_content.startswith("{") and not clean_content.startswith("["):
                        transcript_md.append(f"\n### 🤖 AI Recruiter & Technical Advisor Response\n")
                        transcript_md.append(f"{clean_content}\n")
                        transcript_md.append("\n---\n")
                        
            except Exception as e:
                continue

    with open(output_path, 'w', encoding='utf-8') as out:
        out.write("".join(transcript_md))
        
    print(f"Successfully compiled strategy chat transcript to: {output_path}")

if __name__ == "__main__":
    parse_strategy_chat()
