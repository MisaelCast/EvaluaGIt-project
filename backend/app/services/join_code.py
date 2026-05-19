import random
import string


def generate_join_code(length: int = 6) -> str:
    """Genera un codigo de union corto con letras mayusculas y numeros"""
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    return ''.join(random.choices(chars, k=length))