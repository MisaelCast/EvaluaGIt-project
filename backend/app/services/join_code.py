import random
import string


def generate_join_code(length: int = 6) -> str:
    """Genera un código de unión corto con letras mayúsculas y números."""
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    return ''.join(random.choices(chars, k=length))