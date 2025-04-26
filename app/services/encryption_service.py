# app/services/encryption_service.py

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

class EncryptionService:
    @staticmethod
    def generate_keys():
        """
        Gera um par de chave pública e privada para o usuário.
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()

        # Serializa as chaves
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem, public_pem

    @staticmethod
    def encrypt(public_key_pem, plaintext: str) -> bytes:
        """
        Criptografa uma string usando a chave pública.
        """
        public_key = serialization.load_pem_public_key(public_key_pem)
        ciphertext = public_key.encrypt(
            plaintext.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    @staticmethod
    def decrypt(private_key_pem, ciphertext: bytes) -> str:
        """
        Descriptografa uma string usando a chave privada.
        """
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode('utf-8')
