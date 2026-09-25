# ui.py - Modified with Face Recognition for Password Recovery
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from db import register_user, verify_user, update_password, user_exists
from face_auth import (
    capture_face_for_registration, 
    save_face_encoding, 
    has_face_recognition,
    verify_face_for_user
)

class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Messenger - Authentication")
        self.setFixedSize(720, 680)
        self.setup_style()
        self.setup_ui()

    def setup_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #1a1a1a;
                font-size: 14px;
            }
            QLabel#titleLabel {
                font-size: 28px;
                font-weight: 700;
                color: #0066cc;
                padding: 12px;
            }
            QLabel#subtitleLabel {
                font-size: 14px;
                color: #666;
                font-weight: 500;
            }
            QRadioButton {
                color: #333;
                font-size: 14px;
                font-weight: 600;
                spacing: 8px;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #d0d0d0;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #0066cc;
                background-color: #0066cc;
            }
            QLineEdit {
                padding: 12px 14px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: #fafafa;
                font-size: 14px;
                color: #1a1a1a;
            }
            QLineEdit:focus {
                border: 2px solid #0066cc;
                background-color: white;
                padding: 11px 13px;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 14px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
            QPushButton#recoveryBtn {
                background-color: #ffc107;
                color: #1a1a1a;
            }
            QPushButton#recoveryBtn:hover {
                background-color: #e0a800;
            }
            QGroupBox {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 12px;
                padding: 16px;
            }
            QCheckBox {
                font-weight: 600;
                color: #28a745;
            }
        """)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(32, 32, 32, 32)

        # Title
        title = QLabel("🔐 Secure Messenger")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Encrypted and Secure Communication")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        # Mode selection
        mode_group = QGroupBox()
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(16)
        
        self.mode_login = QRadioButton("Sign In")
        self.mode_register = QRadioButton("Create Account")
        self.mode_login.setChecked(True)
        self.mode_login.toggled.connect(self.update_ui_for_mode)
        
        mode_layout.addWidget(self.mode_login)
        mode_layout.addWidget(self.mode_register)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter your username")
        
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Enter your password")
        
        user_label = QLabel("Username:")
        user_label.setStyleSheet("font-weight: 600;")
        pass_label = QLabel("Password:")
        pass_label.setStyleSheet("font-weight: 600;")
        
        form.addRow(user_label, self.user_input)
        form.addRow(pass_label, self.pass_input)
        layout.addLayout(form)

        # Face recognition checkbox (only for registration)
        self.face_recognition_group = QGroupBox()
        face_layout = QVBoxLayout()
        self.enable_face_cb = QCheckBox("Enable Face Recognition for Password Recovery")
        self.enable_face_cb.setStyleSheet("font-weight: 600; color: #28a745;")
        face_info = QLabel("📸 Capture your face to recover your password if you forget it")
        face_info.setStyleSheet("font-size: 12px; color: #666; margin-left: 25px;")
        face_info.setWordWrap(True)
        face_layout.addWidget(self.enable_face_cb)
        face_layout.addWidget(face_info)
        self.face_recognition_group.setLayout(face_layout)
        self.face_recognition_group.hide()
        layout.addWidget(self.face_recognition_group)

        # Submit button
        btn = QPushButton("Continue")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.validate)
        layout.addWidget(btn)

        # Password recovery button (only for login mode)
        self.recovery_btn = QPushButton("🔓 Forgot Password? Recover with Face Recognition")
        self.recovery_btn.setObjectName("recoveryBtn")
        self.recovery_btn.setCursor(Qt.PointingHandCursor)
        self.recovery_btn.clicked.connect(self.password_recovery)
        layout.addWidget(self.recovery_btn)

        # Status
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("color: #dc3545; font-weight: 600; background-color: #f8d7da; "
                                  "padding: 10px; border-radius: 6px; border: 1px solid #f5c6cb;")
        self.status.setWordWrap(True)
        self.status.hide()
        layout.addWidget(self.status)

        self.setLayout(layout)
        self.update_ui_for_mode()

    def update_ui_for_mode(self):
        """Update UI based on selected mode (login/register)"""
        is_register = self.mode_register.isChecked()
        self.face_recognition_group.setVisible(is_register)
        self.recovery_btn.setVisible(not is_register)

    def password_recovery(self):
        """Handle password recovery with face recognition"""
        self.status.hide()
        
        # Ask for username
        username, ok = QInputDialog.getText(self, "Password Recovery",
            "Enter your username to recover your password:")
        
        if not ok or not username.strip():
            return
        
        username = username.strip()
        
        # Check if user exists
        if not user_exists(username):
            QMessageBox.warning(self, "User Not Found",
                f"Username '{username}' does not exist.")
            return
        
        # Check if user has face recognition enabled
        if not has_face_recognition(username):
            QMessageBox.warning(self, "Face Recognition Not Enabled",
                f"User '{username}' does not have face recognition enabled.\n\n"
                "Password recovery is not available for this account.")
            return
        
        # Verify face
        reply = QMessageBox.information(self, "Face Verification",
            "The camera will open to verify your identity.\n\n"
            "Make sure you're in a well-lit area.\n"
            "Press OK to continue.",
            QMessageBox.Ok | QMessageBox.Cancel)
        
        if reply != QMessageBox.Ok:
            return
        
        # Show progress dialog
        progress = QProgressDialog("Verifying face...", "Cancel", 0, 0, self)
        progress.setWindowTitle("Face Verification")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        QApplication.processEvents()
        
        success, message = verify_face_for_user(username)
        
        progress.close()
        
        if success:
            # Face verified, allow password reset
            self.reset_password(username)
        else:
            QMessageBox.critical(self, "Verification Failed",
                f"Face verification failed: {message}\n\n"
                "Password recovery is not possible.")

    def reset_password(self, username):
        """Reset password after successful face verification"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Reset Password")
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        info_label = QLabel(f"✅ Face verified successfully!\n\nEnter a new password for '{username}':")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #28a745; font-weight: 600; padding: 10px;")
        layout.addWidget(info_label)
        
        form = QFormLayout()
        new_pass = QLineEdit()
        new_pass.setEchoMode(QLineEdit.Password)
        new_pass.setPlaceholderText("New password (min 4 characters)")
        
        confirm_pass = QLineEdit()
        confirm_pass.setEchoMode(QLineEdit.Password)
        confirm_pass.setPlaceholderText("Confirm new password")
        
        form.addRow("New Password:", new_pass)
        form.addRow("Confirm:", confirm_pass)
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Password")
        cancel_btn = QPushButton("Cancel")
        
        def save_new_password():
            if new_pass.text() != confirm_pass.text():
                QMessageBox.warning(dialog, "Error", "Passwords do not match!")
                return
            
            success, msg = update_password(username, new_pass.text())
            if success:
                QMessageBox.information(dialog, "Success",
                    "Password updated successfully!\n\nYou can now sign in with your new password.")
                dialog.accept()
                # Pre-fill username
                self.user_input.setText(username)
                self.pass_input.clear()
                self.pass_input.setFocus()
            else:
                QMessageBox.warning(dialog, "Error", msg)
        
        save_btn.clicked.connect(save_new_password)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def validate(self):
        u, p = self.user_input.text().strip(), self.pass_input.text()
        if not u or not p:
            self.status.setText("⚠️ All fields are required")
            self.status.show()
            return
        
        if self.mode_register.isChecked():
            ok, msg = register_user(u, p)
            if ok:
                # Check if face recognition should be enabled
                if self.enable_face_cb.isChecked():
                    self.setup_face_recognition(u)
                else:
                    self.show_success_and_switch_to_login(msg)
            else:
                self.status.setStyleSheet("color: #dc3545; font-weight: 600; background-color: #f8d7da; "
                                         "padding: 10px; border-radius: 6px; border: 1px solid #f5c6cb;")
                self.status.setText(f"✗ {msg}")
                self.status.show()
        else:
            if verify_user(u, p):
                self.username = u
                self.accept()
            else:
                self.status.setText("✗ Incorrect credentials")
                self.status.setStyleSheet("color: #dc3545; font-weight: 600; background-color: #f8d7da; "
                                         "padding: 10px; border-radius: 6px; border: 1px solid #f5c6cb;")
                self.status.show()

    def setup_face_recognition(self, username):
        """Setup face recognition for new user"""
        reply = QMessageBox.information(self, "Face Recognition Setup",
            "The camera will open to capture your face for password recovery.\n\n"
            "Instructions:\n"
            "• Position your face in the frame\n"
            "• Ensure good lighting\n"
            "• Press SPACE to capture\n"
            "• Press ESC to skip\n\n"
            "Press OK to continue.",
            QMessageBox.Ok | QMessageBox.Cancel)
        
        if reply != QMessageBox.Ok:
            self.show_success_and_switch_to_login("Account created (without face recognition)")
            return
        
        success, message, encoding = capture_face_for_registration(username)
        
        if success and encoding is not None:
            save_success, save_msg = save_face_encoding(username, encoding)
            if save_success:
                QMessageBox.information(self, "Success",
                    "Account created successfully!\n\n"
                    "✅ Face recognition has been enabled for password recovery.\n"
                    "You can now recover your password using your face if you forget it.")
            else:
                QMessageBox.warning(self, "Warning",
                    f"Account created but face recognition setup failed:\n{save_msg}\n\n"
                    "Password recovery will not be available.")
        else:
            QMessageBox.warning(self, "Warning",
                f"Account created but face recognition setup failed:\n{message}\n\n"
                "Password recovery will not be available.")
        
        self.show_success_and_switch_to_login("Account created successfully")

    def show_success_and_switch_to_login(self, message):
        """Show success message and switch to login mode"""
        self.status.setStyleSheet("color: #28a745; font-weight: 600; background-color: #d4edda; "
                                 "padding: 10px; border-radius: 6px; border: 1px solid #c3e6cb;")
        self.status.setText(f"✓ {message}")
        self.status.show()
        self.mode_login.setChecked(True)
        self.update_ui_for_mode()


class SubstitutionDialog(QDialog):
    def __init__(self, current_map):
        super().__init__()
        self.setWindowTitle("Substitution Table")
        self.setMinimumWidth(460)
        self.setMinimumHeight(550)
        self.setup_style()
        self.setup_ui(current_map)

    def setup_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                font-size: 13px;
                font-weight: 600;
                color: #333;
                min-width: 30px;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: 700;
                color: #0066cc;
            }
            QLabel#descLabel {
                font-size: 13px;
                color: #666;
                font-weight: normal;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: #fafafa;
                font-size: 14px;
                font-weight: 600;
            }
            QLineEdit:focus {
                border: 2px solid #0066cc;
                background-color: white;
                padding: 7px;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton#resetBtn {
                background-color: #6c757d;
            }
            QPushButton#resetBtn:hover {
                background-color: #5a6268;
            }
            QPushButton#cancelBtn {
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #d0d0d0;
            }
            QPushButton#cancelBtn:hover {
                background-color: #e0e0e0;
            }
            QScrollArea {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #fafafa;
            }
        """)

    def setup_ui(self, current_map):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Substitution Table Configuration")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        desc = QLabel("Define the mapping between each letter and its substitution:")
        desc.setObjectName("descLabel")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc)

        # Scroll area for table
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QGridLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        self.inputs = {}
        
        # Create grid with 2 columns
        for idx, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            row = idx % 13
            col = (idx // 13) * 3
            
            label = QLabel(f"{c} →")
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            le = QLineEdit(current_map.get(c, c))
            le.setMaxLength(1)
            le.setFixedWidth(45)
            le.setAlignment(Qt.AlignCenter)
            le.textChanged.connect(lambda t, x=c, widget=le: widget.setText(t.upper()[:1]))
            
            self.inputs[c] = le
            layout.addWidget(label, row, col)
            layout.addWidget(le, row, col + 1)
        
        container.setLayout(layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll, 1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        reset_btn = QPushButton("Reset")
        reset_btn.setObjectName("resetBtn")
        reset_btn.clicked.connect(self.reset_map)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def reset_map(self):
        """Reset table to identity (A->A, B->B, etc.)"""
        for c, le in self.inputs.items():
            le.setText(c)

    def get_map(self):
        m = {}
        used = set()
        for c, le in self.inputs.items():
            t = le.text().upper() or c
            if t in used:
                t = c
            m[c] = t
            used.add(t)
        return m