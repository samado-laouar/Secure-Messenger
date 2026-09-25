# Secure Messenger

**Secure Messenger** is an advanced encrypted communication application that provides end-to-end encryption for secure messaging between users. It implements multiple classical and modern cryptographic algorithms and includes biometric authentication via face recognition.

**Author:** LAOUAR Abdessamed  
**Date:** September 25, 2026

---

## Overview

Secure Messenger allows multiple users to communicate securely through a central server. Users can choose from six different encryption methods, exchange keys securely, and exchange encrypted messages in real time. Face recognition is used for registration, authentication support, and password recovery.

### Key Features

- **Multi-User Support** — Connect multiple users through a central server
- **Multiple Encryption Methods** — Choose from 6 different encryption algorithms
- **Face Recognition Authentication** — Biometric security for user authentication and password recovery
- **User-Friendly Interface** — Modern, intuitive graphical interface built with PyQt5
- **Key Exchange Protocol** — Secure key negotiation between communicating parties
- **Real-Time Messaging** — Instant encrypted message delivery
- **Auto-Decryption** — Automatic Caesar cipher decryption using dictionary-based frequency analysis

---

## System Requirements

- **Python** 3.7 or higher
- **Webcam** (required for face recognition features)
- **Network connection** (for server communication)
- **Operating System**: Windows, macOS, or Linux

---

## Installation

### Required Python Packages

```bash
pip install PyQt5 face_recognition opencv-python numpy
```

> **Note:** `pickle` is part of the Python standard library.

### Running the Application

1. Start the server (if running a multi-user setup).
2. Launch the client:
   ```bash
   python client.py
   ```
3. The authentication dialog will appear automatically.

---

## Getting Started

### 1. User Registration

1. Select **Create Account**.
2. Enter a unique username and a strong password.
3. Complete the mandatory face recognition capture.
4. Upon success, you are switched to login mode.

**Username rules:**
- 3–20 characters
- Letters (a-z, A-Z), numbers (0-9), dots (.), hyphens (-), underscores (_)
- Cannot start with `.`, `-`, or `_`

**Password rules:**
- At least 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (e.g. `!@#$%&`)

### 2. User Login

1. Select **Sign In**.
2. Enter your username and password.
3. Click **Continue**.

### 3. Password Recovery

1. Click **Forgot Password? Recover with Face Recognition**.
2. Enter your username.
3. Complete face verification.
4. Set a new password.

---

## Connecting to the Server

After authentication:

| Setting   | Default     | Description                  |
|-----------|-------------|------------------------------|
| Host      | `127.0.0.1` | Server IP address            |
| Port      | `12345`     | Server port                  |
| Username  | (pre-filled)| Your authenticated username  |

Click **Connect →** to establish the connection.

**Progress steps:**
1. Server Connection
2. Communication Configuration
3. Secure Messaging

---

## Communication Configuration

### Selecting a Recipient

Choose a connected user from the recipient dropdown.

### Encryption Methods

| Method                  | Description                                      | Key Type                          | Security Level |
|-------------------------|--------------------------------------------------|-----------------------------------|----------------|
| **Caesar Cipher**       | Classical substitution with fixed shift          | Integer (1–25)                    | Low            |
| **Caesar without Key**  | Auto-decrypt using frequency analysis            | Own shift + language (EN/FR/AR)   | Low–Medium     |
| **Vigenère Cipher**     | Polyalphabetic substitution                      | Text keyword                      | Medium         |
| **Substitution Cipher** | Custom letter mapping                            | 26-letter mapping table           | Medium         |
| **Transposition Cipher**| Rearranges characters based on keyword           | Text keyword                      | Medium         |
| **RSA Encryption**      | Public-key (asymmetric) cryptography             | Auto-generated key pair           | High           |

#### Caesar without Key (Auto-Decrypt)
- Each user chooses their own shift.
- Recipient’s shift is automatically detected.
- Supports English, French, and Arabic.

#### RSA
- Public keys are exchanged.
- Private keys never leave the user’s system.
- Best for sensitive / short messages.

### Key Exchange

1. Select recipient + encryption method + key/settings.
2. Click **Send Key →**.
3. Recipient accepts or rejects the request.
4. On acceptance, a secure channel is established and messaging begins.

---

## Secure Messaging

### Interface

- **Configuration Header** — Current recipient, method, and key
- **Chat Display** — Encrypted (yellow) and decrypted (blue) messages
- **Decrypt Button** — Decrypt selected or latest encrypted message
- **Message Input + Send** — Compose and send encrypted messages

### Sending Messages
1. Type your message.
2. Click **Send** or press **Enter**.
3. Your message appears in plain text on your side (encrypted for the recipient).

### Receiving & Decrypting
1. Encrypted messages appear highlighted in yellow.
2. Select the message (or leave unselected for the latest).
3. Click **Decrypt**.
4. Decrypted content appears in a blue box.

For **Caesar without Key**, the system shows:
- Detected shift
- Confidence percentage
- Selected language

### Changing Configuration
Click **Change** in the header → confirm → return to configuration screen and perform a new key exchange.

---

## Security Features

### Face Recognition
- Mandatory during registration.
- Used for password recovery.
- Face encodings stored locally in encrypted form (no images stored).
- Data is user-specific and never shared.

### Encryption Security Comparison

| Method            | Security     | Speed       | Best For                     |
|-------------------|--------------|-------------|------------------------------|
| Caesar            | Low          | Very Fast   | Learning, demos              |
| Caesar Auto       | Low–Medium   | Fast        | Educational purposes         |
| Vigenère          | Medium       | Fast        | Moderate security needs      |
| Substitution      | Medium       | Fast        | Custom security requirements |
| Transposition     | Medium       | Fast        | Position-based security      |
| RSA               | High         | Moderate    | Sensitive communications     |

### Key Exchange Protocol
1. Sender proposes configuration.
2. Configuration transmitted.
3. Recipient accepts/rejects.
4. Keys established only after mutual agreement.
5. RSA: only public keys are exchanged.

---

## Troubleshooting

### Connection Issues
- Verify the server is running.
- Check IP address and port.
- Ensure firewall allows the port.
- Test network connectivity.

### Authentication Issues
- Double-check username/password.
- Use face-recognition password recovery.
- Ensure face was properly registered.

### Face Recognition Issues
- Ensure webcam is connected and permitted.
- Use good lighting and clear face positioning.
- Close other applications using the camera.

### Messaging Issues
- Confirm successful key exchange.
- Verify recipient is online.
- Re-establish the secure channel if decryption fails.

### Performance (RSA)
- RSA is computationally intensive.
- Prefer RSA for short sensitive messages.
- Use faster ciphers for longer content.
- Split large messages if needed.

---

## Project Structure (Suggested)

```
SecureMessenger/
├── client.py                 # Main client application
├── server.py                 # Central server
├── auth/                     # Authentication & face recognition
├── crypto/                   # Encryption algorithms
│   ├── caesar.py
│   ├── vigenere.py
│   ├── substitution.py
│   ├── transposition.py
│   └── rsa.py
├── ui/                       # PyQt5 interface components
├── requirements.txt
└── README.md
```

---

## License

This project is provided for educational and demonstration purposes.

---

## Contact

For issues or questions regarding Secure Messenger, please contact the author.
```