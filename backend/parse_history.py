import json
import os
import re

def parse_transcript():
    log_path = r"C:\Users\nikhii 2\.gemini\antigravity\brain\d0fe6530-d07f-40d9-a5b0-601a9099f97d\.system_generated\logs\transcript.jsonl"
    output_path = r"C:\Users\nikhii 2\.gemini\antigravity\scratch\feedloop-insight-board\CHAT_TRANSCRIPT.md"
    
    if not os.path.exists(log_path):
        print(f"Error: Log file not found at {log_path}")
        return

    print("Parsing raw conversation logs...")
    transcript_md = []
    transcript_md.append("# 💬 FeedLoop AI: Full Conversation Transcript & Q&A History\n")
    transcript_md.append("This file contains the complete step-by-step chat logs, explanations, design decisions, and interview preparation guides compiled during the development of FeedLoop AI.\n")
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
                
                # Check for User Explicit Inputs
                if source == "USER_EXPLICIT" or step_type == "USER_INPUT":
                    # Clean up XML tags like USER_REQUEST or additional metadata
                    clean_content = content.replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "")
                    # Remove user information metadata block if present
                    clean_content = re.sub(r'<user_information>.*?</user_information>', '', clean_content, flags=re.DOTALL)
                    clean_content = clean_content.strip()
                    
                    if clean_content:
                        transcript_md.append(f"\n### 👤 User Step {step_num}\n")
                        transcript_md.append(f"{clean_content}\n")
                        transcript_md.append("\n---\n")
                        step_num += 1
                        
                # Check for Model Text Outputs
                elif source == "MODEL" and content:
                    # Exclude model messages that are purely tool calls without visible text
                    clean_content = content.strip()
                    if clean_content and not clean_content.startswith("{") and not clean_content.startswith("["):
                        transcript_md.append(f"\n### 🤖 AI Co-Pilot Response\n")
                        transcript_md.append(f"{clean_content}\n")
                        transcript_md.append("\n---\n")
                        
            except Exception as e:
                # Silently skip malformed lines
                continue

    with open(output_path, 'w', encoding='utf-8') as out:
        out.write("".join(transcript_md))
        
    print(f"Successfully generated chat history! Saved to: {output_path}")

if __name__ == "__main__":
    parse_transcript()
