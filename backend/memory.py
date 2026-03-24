import json
import os
from datetime import datetime

MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"conversations": [], "user_facts": {}}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def add_conversation(role, content):
    memory = load_memory()
    memory["conversations"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    # Keep only the last 20 messages to avoid context overflow
    memory["conversations"] = memory["conversations"][-20:]
    save_memory(memory)

def get_recent_conversations():
    memory = load_memory()
    return memory["conversations"]

def get_memory_summary():
    memory = load_memory()
    convos = memory["conversations"]
    if not convos:
        return ""
    summary = "Here is a summary of recent conversations:\n"
    for c in convos:
        role = "User" if c["role"] == "user" else "Assistant"
        summary += f"{role}: {c['content'][:200]}\n"
    return summary
