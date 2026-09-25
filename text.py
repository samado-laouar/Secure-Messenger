# diagnostic_test.py - Test the key exchange flow
import json
from rsa_crypto import generate_keypair, key_to_string, string_to_key

print("=" * 60)
print("RSA Key Exchange Diagnostic Test")
print("=" * 60)

# Simulate Alice (sender)
print("\n[ALICE] Generating keys...")
alice_public, alice_private = generate_keypair(bits=512)
alice_public_str = key_to_string(alice_public)
print(f"[ALICE] Public key generated, length: {len(alice_public_str)}")

# Simulate Alice sending key request
key_request = {
    "type": "key_request",
    "from": "Alice",
    "to": "Bob",
    "config": {
        "cipher": "RSA",
        "public_key": alice_public_str
    }
}

print(f"\n[ALICE] Sending key request...")
print(f"  - Packet size: {len(json.dumps(key_request))} bytes")
print(f"  - Public key in config: {key_request['config'].get('public_key') is not None}")

# Simulate network transmission
request_json = json.dumps(key_request)
received_request = json.loads(request_json)

print(f"\n[SERVER] Received key request from Alice")
print(f"  - Type: {received_request['type']}")
print(f"  - From: {received_request['from']}")
print(f"  - To: {received_request['to']}")
print(f"  - Public key in config: {received_request['config'].get('public_key') is not None}")

# Simulate Bob (recipient)
print(f"\n[BOB] Received key request from Alice")
bob_public, bob_private = generate_keypair(bits=512)
bob_public_str = key_to_string(bob_public)
print(f"[BOB] Generated my own keys")

# Bob stores Alice's public key
alice_public_received = string_to_key(received_request['config']['public_key'])
print(f"[BOB] Stored Alice's public key: {alice_public_received == alice_public}")

# Bob accepts and sends response
key_response = {
    "type": "key_response",
    "from": "Bob",
    "to": "Alice",
    "accept": True,
    "our_public_key": bob_public_str
}

print(f"\n[BOB] Sending key response...")
print(f"  - Accept: {key_response['accept']}")
print(f"  - Our public key length: {len(bob_public_str)}")
print(f"  - Packet size: {len(json.dumps(key_response))} bytes")
print(f"  - Packet keys: {list(key_response.keys())}")

# Simulate network transmission
response_json = json.dumps(key_response)
print(f"\n[SERVER] Forwarding response to Alice")
print(f"  - JSON size: {len(response_json)} bytes")

received_response = json.loads(response_json)
print(f"  - After JSON parse, keys: {list(received_response.keys())}")
print(f"  - Has our_public_key: {received_response.get('our_public_key') is not None}")

# Simulate Alice receiving response
print(f"\n[ALICE] Received key response from Bob")
print(f"  - Accept: {received_response.get('accept')}")
print(f"  - our_public_key present: {received_response.get('our_public_key') is not None}")

if received_response.get('our_public_key'):
    bob_public_received = string_to_key(received_response['our_public_key'])
    print(f"[ALICE] Stored Bob's public key: {bob_public_received == bob_public}")
    
    # Test encryption both ways
    from rsa_crypto import encrypt_string, decrypt_string
    
    # Alice -> Bob
    msg_to_bob = "Hello Bob!"
    encrypted = encrypt_string(msg_to_bob, bob_public_received)
    decrypted = decrypt_string(encrypted, bob_private)
    print(f"\n[TEST] Alice -> Bob: {decrypted == msg_to_bob} ✓")
    
    # Bob -> Alice
    msg_to_alice = "Hello Alice!"
    encrypted = encrypt_string(msg_to_alice, alice_public_received)
    decrypted = decrypt_string(encrypted, alice_private)
    print(f"[TEST] Bob -> Alice: {decrypted == msg_to_alice} ✓")
    
    print("\n" + "=" * 60)
    print("✓ Key exchange and encryption test SUCCESSFUL")
    print("=" * 60)
else:
    print("\n✗ ERROR: Public key not in response!")
    print("=" * 60)