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
import ipaddress  # <--- Neu importieren für die IP-Adresse

def create_ssl():
    # Schlüssel erstellen
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Zertifikat erstellen
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])


    san = x509.SubjectAlternativeName([
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        x509.IPAddress(ipaddress.IPv6Address("::1"))
    ])


    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))

        .add_extension(san, critical=False)
        .sign(key, hashes.SHA256())
    )


    with open("key.pem", "wb") as f:
        f.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        ))

    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("Sicheres lokales Zertifikat (inkl. SAN für 127.0.0.1) erfolgreich erstellt!")

# *****