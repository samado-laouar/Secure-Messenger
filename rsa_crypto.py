# rsa_crypto.py - Reliable Small-Key RSA for Educational Messenger

import random

def is_prime(n):
    """Deterministic primality test for small n"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def generate_prime(min_val=300, max_val=700):
    """Generate a prime in range (larger than before for better security, still fast)"""
    while True:
        p = random.randint(min_val, max_val)
        if p % 2 == 0:
            p += 1  # Make odd
        if is_prime(p):
            return p

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_inverse(e, phi):
    """Extended Euclidean Algorithm to find modular inverse"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd_val, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd_val, x, y

    g, x, _ = extended_gcd(e, phi)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % phi

def generate_keypair(bits_target=512):
    """
    Generate RSA key pair with small but functional keys.
    We use small primes so pow() is fast even in pure Python.
    Resulting n will be around 18-20 bits — sufficient for demo, not real security.
    """
    print("Generating RSA key pair (small primes for speed)...")
    
    # Generate two distinct primes
    p = generate_prime()
    q = generate_prime()
    while p == q:
        q = generate_prime()
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Choose small public exponent, prefer 65537 if coprime, else 3, 5, 17...
    for e in (65537, 17, 5, 3):
        if 1 < e < phi and gcd(e, phi) == 1:
            break
    else:
        raise ValueError("Could not find suitable e")
    
    try:
        d = mod_inverse(e, phi)
    except ValueError:
        raise ValueError("Failed to compute private exponent")
    
    print(f"RSA keys generated: n has {n.bit_length()} bits, e={e}")
    return (e, n), (d, n)

def rsa_encrypt(message: str, public_key):
    """
    Encrypt string using public key (e, n)
    Works byte-by-byte → supports full UTF-8
    Each byte encrypted to 4 hex digits (padded) → safe parsing
    """
    e, n = public_key
    message_bytes = message.encode('utf-8')
    encrypted_blocks = []
    
    for byte in message_bytes:
        if byte >= n:
            raise ValueError(f"Message byte {byte} too large for modulus n={n}")
        c = pow(byte, e, n)
        # Use fixed 4 hex digits per block (enough for n < 2^16)
        encrypted_blocks.append(f"{c:04x}")
    
    return " ".join(encrypted_blocks)

def rsa_decrypt(ciphertext: str, private_key):
    """
    Decrypt space-separated hex blocks using private key (d, n)
    Returns plaintext string or raises exception on failure
    """
    d, n = private_key
    blocks = ciphertext.strip().split()
    decrypted_bytes = []
    
    for block in blocks:
        try:
            c = int(block, 16)
            m = pow(c, d, n)
            if not (0 <= m <= 255):
                raise ValueError(f"Decrypted byte out of range: {m}")
            decrypted_bytes.append(m)
        except ValueError as ve:
            raise ValueError(f"Invalid ciphertext block: {block}") from ve
    
    try:
        return bytes(decrypted_bytes).decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("Decrypted bytes are not valid UTF-8")

def key_to_string(key):
    """Convert (exp, n) tuple to transmittable string"""
    exp, n = key
    return f"{exp}:{n}"

def string_to_key(key_str: str):
    """Convert transmitted string back to key tuple"""
    try:
        parts = key_str.split(':')
        if len(parts) != 2:
            raise ValueError("Invalid key format")
        exp = int(parts[0])
        n = int(parts[1])
        return (exp, n)
    except Exception as e:
        raise ValueError(f"Failed to parse key string: {key_str}") from e

# Optional: Test when run directly
if __name__ == "__main__":
    print("=== Testing Simplified RSA Implementation ===\n")
    
    pub_key, priv_key = generate_keypair()
    e, n = pub_key
    d, _ = priv_key
    
    test_message = "Hello RSA! 🌟 This works with emojis too! 123 éàü"
    print(f"Original:  {test_message}")
    
    encrypted = rsa_encrypt(test_message, pub_key)
    print(f"Encrypted: {encrypted}")
    
    decrypted = rsa_decrypt(encrypted, priv_key)
    print(f"Decrypted: {decrypted}")
    
    if test_message == decrypted:
        print("\n✓ RSA encryption/decryption SUCCESS!")
    else:
        print("\n✗ Failed")
    
    print(f"\nPublic key string: {key_to_string(pub_key)}")
    print(f"Round-trip test: {string_to_key(key_to_string(pub_key)) == pub_key}")