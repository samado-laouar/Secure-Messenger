# client.py - Polished Simple Light UI
import sys
import socket
import threading
import json
import re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QTimer
from PyQt5.QtGui import QFont
from ui import AuthDialog, SubstitutionDialog
from crypto import *
from rsa_crypto import generate_keypair, rsa_decrypt, rsa_encrypt, key_to_string, string_to_key

# In cipher_changed, send_key_request, handle_key_request, etc.:
# No changes needed — just make sure you're using the new functions!
# In cipher_changed, send_key_request, handle_key_request, etc.:
# No changes needed — just make sure you're using the new functions!
class Signals(QObject):
    key_request = pyqtSignal(str, dict)
    key_response = pyqtSignal(str, bool)
    message_received = pyqtSignal(str, str)

class Client(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.sock = None
        self.shared_keys = {}
        self.cipher = "Caesar"
        self.key = 3
        # IMPROVEMENT: Initialize to identity map, not Caesar 3 (Change 3)
        self.sub_map = {chr(65+i): chr(65 + i) for i in range(26)}
        self.current_step = 0
        self.selected_dest = None
        self.pending_key_request = False
        self.encrypted_messages = {}
        self.message_counter = 0

        self.peer_rsa_public_keys = {}
        self.rsa_public_key, self.rsa_private_key = None, None

        self.signals = Signals()
        self.signals.key_request.connect(self.handle_key_request)
        self.signals.key_response.connect(self.handle_key_response)
        self.signals.message_received.connect(self.display_encrypted_message)

        self.setWindowTitle(f"Secure Messenger - {username}")
        self.setMinimumSize(900, 700)
        self.setup_style()
        self.ui()
        self.show()

    def setup_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                color: #1a1a1a;
            }
            QGroupBox {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 8px;
                padding: 16px;
                font-weight: 600;
                font-size: 13px;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                background-color: #ffffff;
                border-radius: 4px;
            }
            QLineEdit, QComboBox {
                padding: 10px 12px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: #ffffff;
                font-size: 14px;
                color: #1a1a1a;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #0066cc;
                padding: 9px 11px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #666;
                margin-right: 8px;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #999;
            }
            QPushButton#secondaryBtn {
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #d0d0d0;
            }
            QPushButton#secondaryBtn:hover {
                background-color: #e0e0e0;
            }
            QPushButton#successBtn {
                background-color: #28a745;
            }
            QPushButton#successBtn:hover {
                background-color: #218838;
            }
            QPushButton#dangerBtn {
                background-color: #dc3545;
            }
            QPushButton#dangerBtn:hover {
                background-color: #c82333;
            }
            QPushButton#warningBtn {
                background-color: #ffc107;
                color: #1a1a1a;
            }
            QPushButton#warningBtn:hover {
                background-color: #e0a800;
            }
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                color: #1a1a1a;
            }
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                text-align: center;
                height: 24px;
                background-color: #f5f5f5;
                font-weight: 600;
                color: #666;
            }
            QProgressBar::chunk {
                background-color: #0066cc;
                border-radius: 5px;
                margin: 1px;
            }
            QLabel#headerLabel {
                background-color: #f8f9fa;
                color: #1a1a1a;
                padding: 16px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 15px;
                border: 1px solid #e0e0e0;
            }
        """)

    def ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_connection_step())
        self.stack.addWidget(self.create_config_step())
        self.stack.addWidget(self.create_key_waiting_step())
        self.stack.addWidget(self.create_messaging_step())
        main_layout.addWidget(self.stack)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(3)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Step %v of %m")
        main_layout.addWidget(self.progress_bar)
        
        # Navigation
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.setObjectName("secondaryBtn")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.go_next)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        main_layout.addLayout(nav_layout)
        
        self.setLayout(main_layout)

    def create_connection_step(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        title = QLabel("Connect to Server")
        title.setObjectName("headerLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        conn = QGroupBox("Connection Settings")
        fl = QFormLayout()
        fl.setSpacing(12)
        fl.setLabelAlignment(Qt.AlignRight)
        
        self.host = QLineEdit("127.0.0.1")
        self.host.setPlaceholderText("Server IP address")
        self.port = QLineEdit("12345")
        self.port.setPlaceholderText("Server port")
        self.name = QLineEdit(self.username)
        self.name.setPlaceholderText("Your username")
        
        fl.addRow("Host:", self.host)
        fl.addRow("Port:", self.port)
        fl.addRow("Username:", self.name)
        conn.setLayout(fl)
        layout.addWidget(conn)
        
        self.conn_status = QLabel("")
        self.conn_status.setAlignment(Qt.AlignCenter)
        self.conn_status.setWordWrap(True)
        layout.addWidget(self.conn_status)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_config_step(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        title = QLabel("Communication Configuration")
        title.setObjectName("headerLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        dest_box = QGroupBox("Recipient")
        dest_layout = QVBoxLayout()
        dest_layout.setSpacing(8)
        dest_layout.addWidget(QLabel("Select who you want to communicate with:"))
        self.dest = QComboBox()
        self.dest.addItem("Choose a recipient...")
        self.dest.setMinimumHeight(40)
        dest_layout.addWidget(self.dest)
        dest_box.setLayout(dest_layout)
        layout.addWidget(dest_box)
        
        crypto_box = QGroupBox("Encryption Method")
        crypto_layout = QVBoxLayout()
        crypto_layout.setSpacing(12)
        
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Method:"))
        self.combo = QComboBox()
        self.combo.addItems(["Caesar", "Caesar without Key", "Vigenère", "Substitution", "Transposition", "RSA"])
        self.combo.setMinimumHeight(40)
        self.combo.currentTextChanged.connect(self.cipher_changed)
        method_layout.addWidget(self.combo, 1)
        crypto_layout.addLayout(method_layout)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Key:"))
        self.key_in = QLineEdit("3")
        self.key_in.setMinimumHeight(40)
        key_layout.addWidget(self.key_in, 1)
        self.edit_sub = QPushButton("Edit Table")
        self.edit_sub.setObjectName("warningBtn")
        self.edit_sub.clicked.connect(self.edit_substitution)
        self.edit_sub.setEnabled(False)
        key_layout.addWidget(self.edit_sub)
        crypto_layout.addLayout(key_layout)
        
        crypto_box.setLayout(crypto_layout)
        layout.addWidget(crypto_box)
        
        info = QLabel("💡 Click 'Send Key' to propose this configuration to the recipient.")
        info.setStyleSheet("background-color: #e7f3ff; color: #004085; padding: 12px; border-radius: 6px; "
                          "border-left: 3px solid #0066cc;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_key_waiting_step(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        title = QLabel("Waiting for Confirmation")
        title.setObjectName("headerLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        waiting_container = QWidget()
        waiting_container.setStyleSheet("background-color: #fafafa; border-radius: 8px; border: 1px solid #e0e0e0;")
        waiting_layout = QVBoxLayout()
        waiting_layout.setContentsMargins(32, 32, 32, 32)
        waiting_layout.setSpacing(16)
        
        waiting_icon = QLabel("⏳")
        waiting_icon.setAlignment(Qt.AlignCenter)
        waiting_icon.setStyleSheet("font-size: 64px;")
        waiting_layout.addWidget(waiting_icon)
        
        self.waiting_label = QLabel()
        self.waiting_label.setAlignment(Qt.AlignCenter)
        self.waiting_label.setWordWrap(True)
        self.waiting_label.setStyleSheet("font-size: 15px; color: #333; font-weight: 600;")
        waiting_layout.addWidget(self.waiting_label)
        
        self.key_details = QLabel()
        self.key_details.setAlignment(Qt.AlignCenter)
        self.key_details.setWordWrap(True)
        self.key_details.setStyleSheet("background-color: #ffffff; padding: 16px; border-radius: 6px; "
                                       "font-family: 'Consolas', monospace; font-size: 13px; border: 1px solid #e0e0e0;")
        waiting_layout.addWidget(self.key_details)
        
        self.key_status = QLabel("")
        self.key_status.setAlignment(Qt.AlignCenter)
        self.key_status.setWordWrap(True)
        self.key_status.setStyleSheet("font-size: 14px; padding: 8px;")
        waiting_layout.addWidget(self.key_status)
        
        waiting_container.setLayout(waiting_layout)
        layout.addWidget(waiting_container)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def create_messaging_step(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        header_container = QWidget()
        header_container.setStyleSheet("background-color: #fafafa; border-radius: 8px; border: 1px solid #e0e0e0;")
        header = QHBoxLayout()
        header.setContentsMargins(12, 8, 12, 8)
        
        self.config_label = QLabel()
        self.config_label.setStyleSheet("background-color: transparent; color: #333; padding: 8px; font-weight: 600;")
        header.addWidget(self.config_label, 1)
        
        self.change_config_btn = QPushButton("Change")
        self.change_config_btn.setObjectName("secondaryBtn")
        self.change_config_btn.setMaximumWidth(120)
        self.change_config_btn.clicked.connect(self.change_configuration)
        header.addWidget(self.change_config_btn)
        
        header_container.setLayout(header)
        layout.addWidget(header_container)
        
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setFont(QFont("Consolas", 11))
        layout.addWidget(self.chat, 1)
        
        action_layout = QHBoxLayout()
        self.decrypt_btn = QPushButton("🔓 Decrypt")
        self.decrypt_btn.setObjectName("successBtn")
        self.decrypt_btn.clicked.connect(self.decrypt_selected_message)
        action_layout.addWidget(self.decrypt_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        send_container = QWidget()
        send_container.setStyleSheet("background-color: #fafafa; border-radius: 8px; border: 1px solid #e0e0e0;")
        send_layout = QHBoxLayout()
        send_layout.setContentsMargins(8, 8, 8, 8)
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type your message...")
        self.input.setMinimumHeight(44)
        self.input.returnPressed.connect(self.send)
        
        send_btn = QPushButton("Send")
        send_btn.setObjectName("successBtn")
        send_btn.setMinimumWidth(100)
        send_btn.setMinimumHeight(44)
        send_btn.clicked.connect(self.send)
        
        send_layout.addWidget(self.input, 1)
        send_layout.addWidget(send_btn)
        send_container.setLayout(send_layout)
        layout.addWidget(send_container)
        
        widget.setLayout(layout)
        return widget

    def update_progress(self):
        self.progress_bar.setValue(min(self.current_step + 1, 3))

    def go_next(self):
        if self.current_step == 0:
            if not self.sock:
                self.connect()
            else:
                self.current_step = 1
                self.stack.setCurrentIndex(1)
                self.back_btn.setEnabled(True)
                self.next_btn.setText("Send Key →")
                self.update_progress()
        elif self.current_step == 1:
            dest = self.dest.currentText()
            if dest == "Choose a recipient...":
                QMessageBox.warning(self, "Incomplete Configuration", 
                    "Please select a recipient.")
                return
            self.selected_dest = dest
            if self.selected_dest in self.shared_keys:
                self.go_to_messaging()
            else:
                self.send_key_request()

    def send_key_request(self):
        config = {"cipher": self.cipher}
        
        if self.cipher == "RSA":
            # ### CORRECTED: Ensure keys are generated before sending
            if self.rsa_public_key is None:
                print("[RSA DEBUG] Generating RSA key pair for myself...")
                self.rsa_public_key, self.rsa_private_key = generate_keypair()  # ou 1024            
                print(f"[RSA DEBUG] Generating RSA key pair for myself done E : {self.rsa_public_key}\n D:{self.rsa_private_key}")
            # Send our public key
            config["public_key"] = key_to_string(self.rsa_public_key)
            print(f"[RSA DEBUG] Config {config}")
        
        elif self.cipher == "Substitution":
            config["key"] = self.sub_map
        
        elif self.cipher == "Caesar without Key":
                # Ask user to select their own encryption key
                key_dialog = QInputDialog()
                key_value, ok = key_dialog.getInt(
                    self, 
                    "Select Your Encryption Key", 
                    "Enter the Caesar shift you want to use for YOUR messages\n(The recipient will auto-decrypt):",
                    5,  # default value
                    1,  # minimum
                    25,  # maximum
                    1   # step
                )
                if ok:
                    config["sender_key"] = key_value
                    self.selected_sender_key = key_value
                else:
                    config["sender_key"] = 5  # default
                    self.selected_sender_key = 5
                
                # Ask for language preference for auto-decryption
                lang_dialog = QInputDialog()
                lang, ok = lang_dialog.getItem(
                    self, 
                    "Language Selection", 
                    "Select the language for auto-decryption:", 
                    ["English", "French", "Arabic"], 
                    0, 
                    False
                )
                if ok:
                    config["language"] = lang.lower()
                    self.selected_language = lang.lower()
                else:
                    config["language"] = "english"
                    self.selected_language = "english"
        
        else:
            try:
                if self.cipher == "Caesar":
                    config["key"] = int(self.key_in.text())
                elif self.cipher in ["Vigenère", "Transposition"]:
                    # IMPROVEMENT: Sanitize key input (Change 1)
                    key_text = self.key_in.text().upper().strip()
                    sanitized_key = "".join(c for c in key_text if c.isalpha())
                    if not sanitized_key:
                        QMessageBox.warning(self, "Invalid Key", "The keyword cannot be empty or contain only non-alphabetic characters.")
                        return
                    config["key"] = sanitized_key
                else:
                    config["key"] = self.key_in.text().upper()

            except ValueError:
                QMessageBox.warning(self, "Invalid Key", "Please enter a valid key.")
                return
        
        pkt = json.dumps({"type": "key_request", "from": self.username, "to": self.selected_dest, "config": config}) + "\n"
        self.sock.send(pkt.encode())
        
        self.current_step = 2
        self.stack.setCurrentIndex(2)
        self.pending_key_request = True
        self.update_progress()
        
        self.waiting_label.setText(f"Waiting for response from {self.selected_dest}...")
        if self.cipher == "Caesar without Key":
            key_text = f"Auto-detect ({config.get('language', 'english').capitalize()})"
        elif self.cipher == "RSA":
            key_text = "Public Key Exchange (RSA)"
        else:
            key_text = self.key_in.text() if self.cipher != "Substitution" else "Custom Table"
            
        self.key_details.setText(f"<b>Method:</b> {self.cipher}<br><b>Key:</b> {key_text}")
        self.key_status.setText("⏳ Request sent, please wait...")
        self.next_btn.setVisible(False)
        self.back_btn.setText("← Cancel")
        
    def go_back(self):
        if self.current_step == 3:
            reply = QMessageBox.question(self, "Confirmation",
                "Do you want to change the configuration?\nThis will require a new key exchange.")
            if reply == QMessageBox.Yes:
                if self.selected_dest in self.shared_keys:
                    del self.shared_keys[self.selected_dest]
                self.current_step = 1
                self.stack.setCurrentIndex(1)
                self.next_btn.setVisible(True)
                self.next_btn.setText("Send Key →")
                self.back_btn.setText("← Back")
                self.update_progress()
        elif self.current_step == 2:
            self.pending_key_request = False
            self.current_step = 1
            self.stack.setCurrentIndex(1)
            self.next_btn.setVisible(True)
            self.next_btn.setText("Send Key →")
            self.back_btn.setText("← Back")
            self.update_progress()
        elif self.current_step == 1:
            self.current_step = 0
            self.stack.setCurrentIndex(0)
            self.back_btn.setEnabled(False)
            self.next_btn.setText("Connect →")
            self.update_progress()

    def change_configuration(self):
        self.go_back()

    def update_config_label(self):
        if self.cipher == "Caesar without Key":
             key_text = f"Encrypt shift: {self.shared_keys[self.selected_dest][1]['encrypt_key']}"
        elif self.cipher == "RSA":
            key_text = "Public Key Exchange"
        else:
            key_text = self.key_in.text() if self.cipher != "Substitution" else "Custom Table"
            
        self.config_label.setText(f"Recipient: {self.selected_dest}  •  Method: {self.cipher}  •  Key: {key_text}")

    def log(self, html):
        self.chat.append(html)

    def cipher_changed(self, name):
        self.cipher = name
        self.edit_sub.setEnabled(name == "Substitution")
        
        # Update key input based on cipher type
        if name == "Substitution":
            self.key_in.setEnabled(False)
        elif name == "Caesar without Key":
            self.key_in.setText("Auto-detect")
            self.key_in.setEnabled(False)
        elif name == "RSA":
            self.key_in.setText("Public Key Exchange")
            self.key_in.setEnabled(False)
        else:
            self.key_in.setEnabled(True)
            if name == "Caesar": 
                self.key_in.setPlaceholderText("Enter shift value")
            elif name == "Vigenère": 
                self.key_in.setPlaceholderText("Enter keyword")
            elif name == "Transposition":
                self.key_in.setPlaceholderText("Enter keyword (e.g., SECRET)")

    def edit_substitution(self):
        d = SubstitutionDialog(self.sub_map)
        if d.exec_() == QDialog.Accepted:
            self.sub_map = d.get_map()

    def connect(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.host.text(), int(self.port.text())))
            self.sock.send(f"USER:{self.name.text().strip()}\n".encode())
            self.username = self.name.text().strip()
            self.conn_status.setText("✅ Successfully connected to server!")
            self.conn_status.setStyleSheet("color: #28a745; font-weight: 600; font-size: 14px; "
                                          "background-color: #d4edda; padding: 12px; border-radius: 6px; "
                                          "border-left: 3px solid #28a745;")
            threading.Thread(target=self.recv_loop, daemon=True).start()
            QTimer.singleShot(1000, self.go_next)
        except Exception as e:
            self.conn_status.setText(f"❌ Connection failed: {e}")
            self.conn_status.setStyleSheet("color: #dc3545; font-weight: 600; font-size: 14px; "
                                          "background-color: #f8d7da; padding: 12px; border-radius: 6px; "
                                          "border-left: 3px solid #dc3545;")

    def recv_loop(self):
        buf = ""
        while True:
            try:
                # Increased buffer for RSA encrypted messages
                data = self.sock.recv(65536).decode()
                print(f"data recived {data}")
                if not data: break
                buf += data
                while "\n" in buf:
                    pkt, buf = buf.split("\n", 1)
                    if pkt.startswith("USER:"): continue
                    try:
                        self.handle(json.loads(pkt))
                    except Exception as e:
                        print(f"Error handling packet: {e}")
            except Exception as e:
                print(f"Connection error: {e}")
                break

    def handle(self, pkt):
        t = pkt["type"]
        if t == "user_list":
            curr = self.dest.currentText()
            self.dest.clear()
            self.dest.addItem("Choose a recipient...")
            for u in pkt["users"]:
                if u != self.username: 
                    self.dest.addItem(u)
            if curr in [self.dest.itemText(i) for i in range(self.dest.count())]:
                self.dest.setCurrentText(curr)
        elif t == "message":
            self.signals.message_received.emit(pkt["from"], pkt["cipher"])
        elif t == "key_request":
            self.signals.key_request.emit(pkt["from"], pkt["config"])
        elif t == "key_response":
            self.signals.key_response.emit(pkt["from"], pkt["accept"])

    def display_encrypted_message(self, sender, encrypted_text):
        msg_id = self.message_counter
        self.message_counter += 1
        self.encrypted_messages[msg_id] = {'sender': sender, 'encrypted': encrypted_text, 'decrypted': None}
        
        self.log("<div style='background-color: #fff3cd; padding: 16px; margin: 10px 0; "
                "border-radius: 6px; border-left: 3px solid #ffc107;'>")
        self.log(f"<div style='margin-bottom: 8px;'><b style='font-size: 14px; color: #856404;'>🔒 Encrypted from {sender}</b> "
                f"<span style='background-color: #ffc107; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;'>ID: {msg_id}</span></div>")
        self.log(f"<code style='background-color: white; padding: 10px; display: block; border-radius: 4px; "
                f"color: #d63384; font-weight: 600; border: 1px solid #e0e0e0;'>{encrypted_text}</code></div>")

    def decrypt_selected_message(self):
        sel = self.chat.textCursor().selectedText()
        msg_id = None
        
        # Try to extract the ID from the selection if a user selected the ID span
        match = re.search(r'ID:\s*(\d+)', sel)
        if match: 
            msg_id = int(match.group(1))
        
        # Fallback: Find the ID of the last message logged in HTML
        if msg_id is None:
            html = self.chat.toHtml()
            # Find all IDs and take the largest one
            all_ids = re.findall(r'ID:\s*(\d+)', html)
            if all_ids:
                msg_id = int(max(all_ids, key=int))
        
        if msg_id is None or msg_id not in self.encrypted_messages:
            QMessageBox.warning(self, "No Message", "No encrypted message found.")
            return
        
        msg_data = self.encrypted_messages[msg_id]
        if msg_data['decrypted']:
            QMessageBox.information(self, "Already Decrypted", f"This message was already decrypted:\n\n{msg_data['decrypted']}")
            return
        
        if msg_data['sender'] not in self.shared_keys:
            QMessageBox.warning(self, "Missing Key", "No shared key with this user.")
            return
        
        ciph, key = self.shared_keys[msg_data['sender']]
        try:
            plain = self.decrypt(msg_data['encrypted'], ciph, key)
            msg_data['decrypted'] = plain
            
            # The decrypt function logs its own detection/shift message if Caesar without Key is used
            
            self.log("<div style='background-color: #d1ecf1; padding: 16px; margin: 10px 0; "
                    "border-radius: 6px; border-left: 3px solid #17a2b8;'>")
            self.log(f"<div style='margin-bottom: 8px;'><b style='font-size: 14px; color: #0c5460;'>🔓 Decrypted from {msg_data['sender']}</b> "
                    f"<span style='background-color: #17a2b8; color: white; padding: 3px 8px; border-radius: 4px; "
                    f"font-size: 11px; font-weight: 600;'>ID: {msg_id}</span></div>")
            self.log(f"<div style='background-color: white; padding: 12px; border-radius: 4px; color: #155724; "
                    f"font-weight: 600; font-size: 13px; border: 1px solid #e0e0e0;'>{plain}</div></div>")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot decrypt:\n{e}")

    def handle_key_response(self, sender, accept_bool):
        # FIXED: accept_bool is now the boolean directly (from pkt["accept"])
        print(f"[RSA DEBUG] Received key_response from {sender}: accept={accept_bool}")
        if sender == self.selected_dest and self.pending_key_request:
            self.pending_key_request = False
            
            if accept_bool:
                # Success — store shared configuration
                if self.cipher == "RSA":
                    self.shared_keys[sender] = ("RSA", sender)  # key = username → lookup in peer_rsa_public_keys
                    print(f"RSA key exchange completed with {sender}")
                    print(f"[RSA DEBUG] RSA key exchange SUCCESS with {sender}")
                    print(f"     Do I have their public key? {sender in self.peer_rsa_public_keys}{self.peer_rsa_public_keys}")

                elif self.cipher == "Caesar without Key":
                    # IMPROVEMENT: Store OUR chosen encryption key for sending to them, and the language they will use to crack (Change 2)
                    self.shared_keys[sender] = ("Caesar without Key", {
                        "encrypt_key": self.selected_sender_key,
                        "language": self.selected_language
                    })

                else:
                    # Standard ciphers: store key as proposed
                    try:
                        if self.cipher == "Caesar":
                            key_val = int(self.key_in.text())
                        elif self.cipher == "Substitution":
                            # Use the local map that was sent in the request (Change 4)
                            key_val = self.sub_map 
                        else: # Vigenère, Transposition
                            # Ensure key is stored clean (consistent with send_key_request)
                            key_text = self.key_in.text().upper().strip()
                            key_val = "".join(c for c in key_text if c.isalpha())
                            if not key_val:
                                raise ValueError("Empty key after sanitization")

                        self.shared_keys[sender] = (self.cipher, key_val)
                    except ValueError as e:
                        QMessageBox.warning(self, "Error", f"Invalid key format: {e}")
                        return

                self.key_status.setText(
                    f"<b style='color:green; font-size: 16px;'>✓ Key accepted by {sender}!</b>"
                )
                self.waiting_label.setText("Secure communication established.")

                QTimer.singleShot(1500, self.go_to_messaging)

            else:
                self.key_status.setText(
                    f"<b style='color:red; font-size: 16px;'>✗ {sender} rejected the configuration</b>"
                )
                self.waiting_label.setText("You can modify and try again.")
                self.back_btn.setVisible(True)
                self.back_btn.setText("← Modify Configuration")

                QMessageBox.warning(self, "Rejected",
                    f"{sender} did not accept your encryption configuration.\n"
                    "Try changing the method or key.")

    def handle_key_request(self, sender, config):
        ciph = config["cipher"]
        
        try:
            receiver_pub_key = None
            
            if ciph == "RSA":
                # Generate our keys if not present
                if self.rsa_public_key is None:
                    print("[RSA DEBUG] Generating my own RSA key pair (first time responding)")
                    self.rsa_public_key, self.rsa_private_key = generate_keypair()
                
                # Store sender's public key from request
                sender_pub_str = config.get("public_key")
                if sender_pub_str:
                    self.peer_rsa_public_keys[sender] = string_to_key(sender_pub_str)
                    print(f"[RSA DEBUG] Stored public key from {sender}")
                else:
                    raise ValueError("No public key provided in RSA request")
                
                key_preview = "Public Key Exchange (RSA)"
                
            elif ciph == "Substitution":
                key_preview = "Custom Table"
            elif ciph == "Caesar without Key":
                language = config.get("language", "english").capitalize()
                sender_key = config.get("sender_key", 5)
                key_preview = f"Auto-detect ({language}), Sender uses shift {sender_key}"
            else:
                key = config.get("key")
                key_preview = str(key)

            # Show dialog
            reply = QMessageBox.question(self, "Key Request",
                f"<b>{sender}</b> wants to communicate securely.<br><br>"
                f"<b>Method:</b> {ciph}<br>"
                f"<b>Details:</b> {key_preview}<br><br>"
                "Do you accept this configuration?")

            accept = (reply == QMessageBox.Yes)
            receiver_key = None

            if accept and ciph == "Caesar without Key":
                key_val, ok = QInputDialog.getInt(
                    self, "Your Encryption Key",
                    f"Choose the Caesar shift YOU will use when sending to {sender}:",
                    5, 1, 25, 1)
                receiver_key = key_val if ok else 5

            # Build response
            response = {
                "type": "key_response",
                "from": self.username,
                "to": sender,
                "accept": accept
            }

            # Include our public key if RSA and accepted
            if accept and ciph == "RSA":
                response["public_key"] = key_to_string(self.rsa_public_key)
                print(f"[RSA DEBUG] Accepting RSA request - sending my public key back to {sender}")

            # Include our encryption key if Caesar without Key
            if accept and ciph == "Caesar without Key":
                response["receiver_key"] = receiver_key

            self.sock.send((json.dumps(response) + "\n").encode())
            print(f"[RSA DEBUG] Sent key_response to {sender}: accept={accept}")

            if accept:
                # Store shared config locally
                if ciph == "RSA":
                    self.shared_keys[sender] = ("RSA", sender)
                    print(f"[RSA DEBUG] RSA secure channel established with {sender}")
                elif ciph == "Caesar without Key":
                    # IMPROVEMENT: Store only OUR encrypt key and the language (Change 2)
                    self.shared_keys[sender] = ("Caesar without Key", {
                        "encrypt_key": receiver_key or 5,
                        "language": config.get("language", "english")
                    })
                elif ciph == "Substitution":
                    self.shared_keys[sender] = ("Substitution", config.get("key", {}))
                else:
                    self.shared_keys[sender] = (ciph, config.get("key"))

                # Update UI to reflect new active conversation
                self.selected_dest = sender
                self.cipher = ciph
                self.combo.setCurrentText(ciph)
                
                if ciph == "Substitution":
                    self.sub_map = config.get("key", self.sub_map)
                    self.key_in.setEnabled(False)
                elif ciph == "Caesar without Key":
                    self.key_in.setText(f"Encrypt shift: {receiver_key or 5}")
                elif ciph == "RSA":
                    self.key_in.setText("RSA Key Exchange")
                else:
                    self.key_in.setText(str(config.get("key", "")))

                self.go_to_messaging()
                self.log(f"<span style='color:#28a745; font-weight:bold'>✓ Secure channel established with {sender}</span>")

            else:
                self.log(f"<span style='color:#dc3545; font-weight:bold'>✗ Rejected key request from {sender}</span>")

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to handle key request:\n{e}")

    def go_to_messaging(self):
        self.current_step = 3
        self.stack.setCurrentIndex(3)
        self.update_config_label()
        self.next_btn.setVisible(False)
        self.back_btn.setVisible(True)
        self.back_btn.setText("← Retour à la configuration")
        self.log(f"<b style='color:green'>✓ Communication sécurisée établie avec {self.selected_dest}</b>")


    def send(self):
        dest = self.selected_dest
        if not dest:
            QMessageBox.warning(self, "Erreur", "Aucun destinataire sélectionné.")
            return
        
        text = self.input.text()
        if not text: 
            return

        # Debug: Print current shared keys
        print(f"DEBUG - Attempting to send to: {dest}")
        print(f"DEBUG - Shared keys: {self.shared_keys.keys()}")
        print(f"DEBUG - Selected dest: {self.selected_dest}")
        
        if dest not in self.shared_keys:
            QMessageBox.warning(self, "Erreur",
                f"Aucune clé partagée avec {dest}.\n"
                f"Veuillez établir une clé d'abord.\n\n"
                f"DEBUG INFO:\n"
                f"Shared keys available: {list(self.shared_keys.keys())}\n"
                f"Trying to send to: {dest}")
            return

        ciph, key = self.shared_keys[dest]
        
        
        print(f"DEBUG - Using cipher: {ciph}, key type: {type(key)}, shared keys {key}")
        
        try:
            enc = self.encrypt(text, ciph, key)
            print(f"DEBUG - Encrypted message length: {len(enc)}")
            print(f"DEBUG - key: {key}")
            
            pkt = json.dumps({
                "type": "message", 
                "from": self.username, 
                "to": dest, 
                "cipher": enc
            }) + "\n"
            
            self.sock.send(pkt.encode())
            print(f"DEBUG - Message sent successfully")
            
            # Display sent message
            self.log(f"<b>Vous → {dest}:</b> {text}")
            
            self.input.clear()
            
        except Exception as e:
            print(f"ERROR in send: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur d'envoi", 
                f"Impossible d'envoyer le message:\n{e}")
            
    def encrypt(self, text, ciph, key):
        if ciph == "Caesar":
            return caesar_encrypt(text, key)
        if ciph == "Caesar without Key":
            encrypt_key = key["encrypt_key"] if isinstance(key, dict) else key
            return caesar_encrypt(text, encrypt_key)
        if ciph == "Vigenère":
            return vigenere_encrypt(text, key)
        if ciph == "Substitution":
            return substitution_encrypt(text, key)
        if ciph == "Transposition":
            return transposition_encrypt(text, key)
        if ciph == "RSA":
            if key not in self.peer_rsa_public_keys:
                raise ValueError(f"No public key for {key}")
            peer_pub = self.peer_rsa_public_keys[key]
            return rsa_encrypt(text, peer_pub)
        raise ValueError("Unknown cipher")

    def decrypt(self, text, ciph, key):
        if ciph == "Caesar":
            return caesar_encrypt(text, -key % 26)
        if ciph == "Caesar without Key":
            # IMPROVEMENT: Use only auto-decryption, as intended by this cipher's name (Change 2)
            language = key["language"] if isinstance(key, dict) else "english"
            plain, detected, conf = auto_decrypt_caesar(text, language)
            self.log(f"<small style='color:#0066cc'>🔍 Auto-detected shift: {detected} (confidence: {conf:.1f}%)</small>")
            return plain
        if ciph == "Vigenère":
            return vigenere_decrypt(text, key)
        if ciph == "Substitution":
            return substitution_decrypt(text, key)
        if ciph == "Transposition":
            return transposition_decrypt(text, key)
        if ciph == "RSA":
            if not self.rsa_private_key:
                raise ValueError("Private key missing")
            return rsa_decrypt(text, self.rsa_private_key)
        raise ValueError("Unknown cipher")
    
            
    def crack(self):
        sel = self.chat.textCursor().selectedText()
        if not sel:
            m = re.search(r'<code[^>]*>([^<]+)</code>', self.chat.toHtml())
            if m: sel = m.group(1)
        if not sel or not any(c.isalpha() for c in sel):
            QMessageBox.information(self, "", "Sélectionnez un message Caesar à cracker")
            return
        plain, shift = crack_caesar(sel)
        QMessageBox.information(self, "Cracké!",
            f"Décalage: <b>{shift}</b><br><br><code>{plain}</code>")

if __name__ == "__main__":
    from PyQt5.QtCore import QTimer
    app = QApplication(sys.argv)
    auth = AuthDialog()
    if auth.exec_() != QDialog.Accepted:
        sys.exit(0)
    win = Client(auth.username)
    sys.exit(app.exec_())