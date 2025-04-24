# pre_gateway.py using pyUmbral (from GitHub: https://github.com/nucypher/pyUmbral)

import os
import random
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from umbral import SecretKey, Signer, encrypt, decrypt_original, generate_kfrags, reencrypt, decrypt_reencrypted, CapsuleFrag

KEYSTORE_DIR = "./keystore"
os.makedirs(KEYSTORE_DIR, exist_ok=True)

# --- AES Utility ---
def generate_aes_key() -> bytes:
    return os.urandom(32)  # AES-256

def save_file(data: bytes, name: str):
    path = os.path.join(KEYSTORE_DIR, name)
    with open(path, 'wb') as f:
        f.write(data)

def load_file(name: str) -> bytes:
    path = os.path.join(KEYSTORE_DIR, name)
    with open(path, 'rb') as f:
        return f.read()

def aes_encrypt(data: bytes, key: bytes) -> bytes:
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(pad(data, AES.block_size))

def aes_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    iv = ciphertext[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext[16:]), AES.block_size)

# --- Umbral PRE Flow ---
def generate_umbral_keys(identity: str):
    priv_key = SecretKey.random()
    pub_key = priv_key.public_key()
    signing_key = SecretKey.random()
    signer = Signer(signing_key)
    verifying_key = signing_key.public_key()
    save_file(priv_key.to_secret_bytes(), f"{identity}_sk.key")
    save_file(bytes(pub_key), f"{identity}_pk.key")
    save_file(signing_key.to_secret_bytes(), f"{identity}_sign.key")
    return priv_key, pub_key, signer, verifying_key

# --- Encrypt & PRE Protect File ---
def encrypt_and_capsule(file_path: str, alice_pub_key):
    with open(file_path, 'rb') as f:
        plaintext = f.read()
    aes_key = generate_aes_key()
    enc_data = aes_encrypt(plaintext, aes_key)
    capsule, encrypted_aes_key = encrypt(alice_pub_key, aes_key)
    save_file(encrypted_aes_key, "encrypted_aes.key")
    save_file(bytes(capsule), "capsule.bin")
    return enc_data, capsule, encrypted_aes_key

# --- Decrypt Using PRE ---
def decrypt_with_reencryption(enc_data, capsule, encrypted_aes_key, kfrags, alice_pub_key, alice_verifying_pk, bob_pub_key, bob_sk):
    selected_kfrags = random.sample(kfrags, 1)
    cfrags = [reencrypt(capsule, kfrag) for kfrag in selected_kfrags]
    verified_cfrags = [CapsuleFrag.from_bytes(bytes(cfrag)).verify(
        capsule, 
        verifying_pk=alice_verifying_pk,  # Alice的签名公钥
        delegating_pk=alice_pub_key,      # Alice的加密公钥
        receiving_pk=bob_pub_key          # Bob的加密公钥
    ) for cfrag in cfrags]
    aes_key = decrypt_reencrypted(
        receiving_sk=bob_sk, 
        delegating_pk=alice_pub_key, 
        capsule=capsule,
        verified_cfrags=verified_cfrags, 
        ciphertext=encrypted_aes_key
    )
    return aes_decrypt(enc_data, aes_key)

# --- Example Usage ---
if __name__ == "__main__":
    alice_sk, alice_pk, alice_signer, alice_verifying_pk = generate_umbral_keys("alice")
    bob_sk, bob_pk, _, _ = generate_umbral_keys("bob")

    # Encrypt and store capsule and encrypted key
    enc_data, capsule, encrypted_aes_key = encrypt_and_capsule("./brain_store/knowledge_index.faiss", alice_pk)

    # Generate kfrags for Bob
    kfrags = generate_kfrags(delegating_sk=alice_sk, receiving_pk=bob_pk, signer=alice_signer, threshold=1, shares=1)

    # Decrypt using re-encryption
    decrypted = decrypt_with_reencryption(
        enc_data, capsule, encrypted_aes_key, kfrags,
        alice_pk, alice_verifying_pk, bob_pk, bob_sk
    )
    print("✅ Decryption successful. Bytes:", decrypted[:64])