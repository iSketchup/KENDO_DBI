# *****
# KI-TEIL
# Prompt:
# Erstelle eine Python-Funktion die mit der
# cryptography-Bibliothek automatisch ein
# selbstsigniertes SSL-Zertifikat generiert
# und als key.pem und cert.pem speichert.

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

def create_ssl():
    # Schlüssel generieren
    key = rsa.generate_private_key(public_exponent=65537, key_size=4096)

    # Zertifikat erstellen
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .sign(key, hashes.SHA256())
    )

    # Als .pem speichern
    with open("key.pem", "wb") as f:
        f.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        ))

    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("Zertifikat erstellt")

# *****