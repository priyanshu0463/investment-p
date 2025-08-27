from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from typing import Dict


class KeyManager:
    def __init__(self) -> None:
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

    def sign(self, message: bytes) -> bytes:
        return self.private_key.sign(message, ec.ECDSA(hashes.SHA256()))

    @staticmethod
    def verify(public_key, signature: bytes, message: bytes) -> bool:
        try:
            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False

    def public_key_bytes(self) -> bytes:
        return self.public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)


PublicKeyRegistry = Dict[str, object]



