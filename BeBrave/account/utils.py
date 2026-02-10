import uuid

def generate_human_readable_key():
    return f"key_{uuid.uuid4().hex[:8]}"
