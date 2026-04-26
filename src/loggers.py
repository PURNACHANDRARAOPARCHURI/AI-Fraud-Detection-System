import json
from datetime import datetime
import os
LOG_FILE = "logs/logs.txt"
def log_transaction(input_data, result):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "input": input_data,
        "result": result
    }
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")