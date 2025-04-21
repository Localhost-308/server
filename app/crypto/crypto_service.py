from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from app.crypto.key_manager import get_private_key, get_public_key

def encrypt(data: str, user_id: int) -> str:
    pub_key = get_public_key(user_id)
    encrypted = pub_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted.hex()

def decrypt(data_hex: str, user_id: int) -> str:
    priv_key = get_private_key(user_id)
    if not priv_key:
        return ""
    decrypted = priv_key.decrypt(
        bytes.fromhex(data_hex),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode()
