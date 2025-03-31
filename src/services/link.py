import random
import string

def generate_short_code(length: int = 6) -> str:
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

