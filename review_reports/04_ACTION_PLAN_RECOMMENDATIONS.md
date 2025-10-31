# TOSCA Medical Device - Action Plan & Recommendations

**Review Date:** 2025-10-30
**System Version:** v0.9.11-alpha
**Target:** Production Readiness for Phase 6 Pre-Clinical Validation

---

## Executive Action Plan

### Timeline Overview

**Total Estimated Effort:** 6-8 weeks (1 senior engineer + 1 security specialist)

```
Week 1-2: Critical Security Fixes (P0)
Week 3-4: Testing & Validation (P1)
Week 5-6: Compliance Documentation (P1)
Week 7-8: Final Hardening & Validation (P2)
```

---

## Phase 1: Critical Security Fixes (Weeks 1-2)

### Priority P0 - CRITICAL BLOCKERS

#### Task 1.1: Database Encryption (5 days)

**Objective:** Implement SQLCipher AES-256-CBC encryption for patient data

**Technical Approach:**
```python
# 1. Install SQLCipher
pip install sqlcipher3

# 2. Generate encryption key (Windows DPAPI)
import win32crypt
encryption_key = secrets.token_bytes(32)
encrypted_key = win32crypt.CryptProtectData(encryption_key, "TOSCA DB Key")
# Store encrypted_key in config

# 3. Migrate existing database
import sqlcipher3 as sqlite3
new_conn = sqlite3.connect("data/tosca_encrypted.db")
new_conn.execute(f"PRAGMA key = '{encryption_key.hex()}'")
new_conn.execute("PRAGMA cipher = 'aes-256-cbc'")
new_conn.execute("PRAGMA kdf_iter = 100000")

# Attach old database and export
new_conn.execute("ATTACH DATABASE 'data/tosca.db' AS plaintext KEY ''")
new_conn.execute("SELECT sqlcipher_export('main')")
new_conn.execute("DETACH DATABASE plaintext")

# 4. Update db_manager.py to use sqlcipher3
```

**Testing:**
- [ ] Verify encrypted database cannot be opened without key
- [ ] Verify all CRUD operations work with encryption
- [ ] Verify key recovery from DPAPI
- [ ] Verify performance impact <10%

**Documentation:**
- Update `docs/architecture/DATABASE_ENCRYPTION.md`
- Document key management procedure
- Create key recovery runbook

**Files Modified:**
- `src/database/db_manager.py`
- `requirements.txt` (add sqlcipher3)
- `config/config.yaml` (add encrypted_key field)

**Acceptance Criteria:**
- [ ] Database file unreadable without decryption key
- [ ] All existing functionality preserved
- [ ] Key stored securely via Windows DPAPI
- [ ] Backup/restore procedure documented

**Effort:** 5 days (includes testing + documentation)

---

#### Task 1.2: User Authentication System (7 days)

**Objective:** Implement bcrypt authentication with session management

**Technical Approach:**

**Day 1-2: Database Schema + Password Hashing**
```python
# 1. Add password fields to TechUser model
class TechUser(Base):
    __tablename__ = "tech_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column(String(60))  # bcrypt hash
    full_name: Mapped[str]
    role: Mapped[str]  # admin, technician, observer
    is_active: Mapped[bool] = mapped_column(default=True)
    failed_login_attempts: Mapped[int] = mapped_column(default=0)
    last_login: Mapped[Optional[datetime]]
    must_change_password: Mapped[bool] = mapped_column(default=True)

    def set_password(self, password: str):
        import bcrypt
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, password: str) -> bool:
        import bcrypt
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

# 2. Migrate existing users
default_password = secrets.token_urlsafe(16)
admin_user.set_password(default_password)
print(f"INITIAL ADMIN PASSWORD: {default_password}")  # Print once, then delete
```

**Day 3-4: Login Dialog UI**
```python
# src/ui/dialogs/login_dialog.py
class LoginDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.authenticated_user = None
        self._login_attempts = 0
        self._max_attempts = 3
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self._attempt_login)

        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        layout.addWidget(login_button)
        self.setLayout(layout)

    def _attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return

        user = self.db_manager.get_user_by_username(username)

        if user and user.is_active and user.verify_password(password):
            # Successful login
            self.authenticated_user = user
            self.db_manager.update_last_login(user.id)
            self.db_manager.reset_failed_login_attempts(user.id)

            # Check if password change required
            if user.must_change_password:
                change_dialog = ChangePasswordDialog(user, self.db_manager)
                if change_dialog.exec() != QDialog.DialogCode.Accepted:
                    return  # User cancelled password change

            logger.info(f"User '{username}' logged in successfully")
            self.event_logger.log_event(EventType.USER_LOGIN, EventSeverity.INFO,
                                        details={"username": username, "role": user.role})
            self.accept()

        else:
            # Failed login
            self._login_attempts += 1
            if user:
                self.db_manager.increment_failed_login_attempts(user.id)
                if user.failed_login_attempts >= 3:
                    self.db_manager.deactivate_user(user.id)
                    QMessageBox.critical(self, "Account Locked",
                                       "Account has been locked due to too many failed login attempts. Contact administrator.")
                    logger.warning(f"User '{username}' account locked due to failed login attempts")
                    self.reject()
                    return

            remaining = self._max_attempts - self._login_attempts
            if remaining > 0:
                QMessageBox.warning(self, "Login Failed",
                                  f"Invalid username or password. {remaining} attempts remaining.")
            else:
                QMessageBox.critical(self, "Login Failed", "Maximum login attempts exceeded.")
                logger.warning(f"Maximum login attempts exceeded for username: {username}")
                self.reject()
```

**Day 5-6: Session Management**
```python
# src/core/session_manager.py - Add authenticated_user tracking
class SessionManager:
    def __init__(self, db_manager, authenticated_user):
        self.db_manager = db_manager
        self.authenticated_user = authenticated_user  # TechUser object
        self.current_session = None
        self.session_start_time = None

    def create_session(self, subject_code, protocol_name, notes=""):
        """Create new session with authenticated user attribution."""
        session = self.db_manager.create_session(
            subject_code=subject_code,
            tech_id=self.authenticated_user.id,  # ← Link to authenticated user
            protocol_name=protocol_name,
            notes=notes
        )
        self.current_session = session
        self.session_start_time = datetime.now()
        logger.info(f"Session {session.id} created by {self.authenticated_user.username}")
        return session
```

**Day 7: Integration + Testing**
```python
# src/main.py - Add login requirement
def main():
    app = QApplication(sys.argv)

    # Initialize database
    db_manager = DatabaseManager()
    event_logger = EventLogger(db_manager=db_manager)

    # SHOW LOGIN DIALOG FIRST
    login_dialog = LoginDialog(db_manager)
    if login_dialog.exec() != QDialog.DialogCode.Accepted:
        logger.info("Login cancelled by user")
        sys.exit(0)

    # Get authenticated user
    authenticated_user = login_dialog.authenticated_user
    logger.info(f"Application started by user: {authenticated_user.username}")

    # Launch main window with authenticated user
    window = MainWindow(
        authenticated_user=authenticated_user,
        db_manager=db_manager,
        event_logger=event_logger
    )
    window.show()

    sys.exit(app.exec())
```

**Testing:**
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (3 attempts → account lock)
- [ ] Forced password change on first login
- [ ] Session attribution to authenticated user
- [ ] Logout functionality
- [ ] Role-based access control (admin vs technician)

**Documentation:**
- User management guide
- Password reset procedure
- Account unlock procedure

**Files Modified:**
- `src/database/models.py`
- `src/database/db_manager.py`
- `src/ui/dialogs/login_dialog.py` (new)
- `src/ui/dialogs/change_password_dialog.py` (new)
- `src/main.py`
- `src/core/session_manager.py`

**Acceptance Criteria:**
- [ ] No access to application without authentication
- [ ] Password hashed with bcrypt (12 rounds)
- [ ] Account lockout after 3 failed attempts
- [ ] All user actions attributed to authenticated user in audit trail
- [ ] Role-based permissions enforced

**Effort:** 7 days

---

#### Task 1.3: Video Encryption (3 days)

**Objective:** Encrypt all video recordings with AES-256-GCM

**Technical Approach:**

**Day 1: Encryption Module**
```python
# src/core/video_encryptor.py (new)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class VideoEncryptor:
    def __init__(self, encryption_key: bytes):
        if len(encryption_key) != 32:
            raise ValueError("Encryption key must be 32 bytes (256-bit)")
        self.key = encryption_key

    def encrypt_file(self, plaintext_path: str, encrypted_path: str) -> None:
        """Encrypt video file using AES-256-GCM (authenticated encryption)."""
        nonce = os.urandom(12)  # 96-bit nonce for GCM

        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Read plaintext
        with open(plaintext_path, 'rb') as f_in:
            plaintext = f_in.read()

        # Encrypt
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Write: nonce (12) + tag (16) + ciphertext
        with open(encrypted_path, 'wb') as f_out:
            f_out.write(nonce)
            f_out.write(encryptor.tag)
            f_out.write(ciphertext)

        # Securely delete plaintext
        os.remove(plaintext_path)
        logger.info(f"Video encrypted: {plaintext_path} → {encrypted_path}")

    def decrypt_file(self, encrypted_path: str, plaintext_path: str) -> None:
        """Decrypt video file for playback."""
        with open(encrypted_path, 'rb') as f_in:
            nonce = f_in.read(12)
            tag = f_in.read(16)
            ciphertext = f_in.read()

        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Decrypt and verify authentication tag
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Write decrypted file
        with open(plaintext_path, 'wb') as f_out:
            f_out.write(plaintext)

        logger.info(f"Video decrypted: {encrypted_path} → {plaintext_path}")
```

**Day 2: Camera Controller Integration**
```python
# src/hardware/camera_controller.py
class CameraController:
    def __init__(self, event_logger, video_encryptor):
        # ...
        self.video_encryptor = video_encryptor

    def stop_recording(self):
        if self.video_writer:
            self.video_writer.release()
            logger.info(f"Video recording stopped: {self.current_video_path}")

            # Encrypt immediately
            plaintext_path = self.current_video_path
            encrypted_path = plaintext_path.replace('.mp4', '.enc')

            try:
                self.video_encryptor.encrypt_file(plaintext_path, encrypted_path)
                self.recording_stopped.emit(encrypted_path)
                logger.info(f"Video encrypted successfully: {encrypted_path}")
            except Exception as e:
                logger.error(f"Video encryption failed: {e}")
                self.error_occurred.emit(f"Video encryption failed: {e}")
```

**Day 3: Playback Viewer**
```python
# src/ui/dialogs/video_viewer_dialog.py
import tempfile

class VideoViewerDialog(QDialog):
    def __init__(self, encrypted_video_path, video_encryptor):
        super().__init__()
        self.encrypted_path = encrypted_video_path
        self.video_encryptor = video_encryptor
        self.temp_file = None
        self._decrypt_and_play()

    def _decrypt_and_play(self):
        # Decrypt to temporary file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        self.video_encryptor.decrypt_file(self.encrypted_path, self.temp_file.name)

        # Play using OpenCV or VLC
        self._play_video(self.temp_file.name)

    def closeEvent(self, event):
        # Securely delete temporary plaintext
        if self.temp_file:
            os.remove(self.temp_file.name)
        super().closeEvent(event)
```

**Testing:**
- [ ] Video encrypted immediately after recording stops
- [ ] Plaintext video deleted after encryption
- [ ] Encrypted video cannot be played without decryption
- [ ] Playback viewer decrypts and plays correctly
- [ ] Temporary plaintext deleted after playback

**Files Modified:**
- `src/core/video_encryptor.py` (new)
- `src/hardware/camera_controller.py`
- `src/ui/dialogs/video_viewer_dialog.py` (new)
- `requirements.txt` (add cryptography)

**Acceptance Criteria:**
- [ ] All video files encrypted with AES-256-GCM
- [ ] No plaintext videos remain on disk
- [ ] Authenticated encryption (tamper detection)
- [ ] Secure playback with temporary decryption

**Effort:** 3 days

---

#### Task 1.4: Audit Trail Integrity (2 days)

**Objective:** Add HMAC-SHA256 signatures to all event logs

**Implementation:** See Phase 2 Security Report Section 4

**Testing:**
- [ ] All new events signed with HMAC-SHA256
- [ ] Signature verification on audit trail load
- [ ] Tampered events detected by verification tool
- [ ] Signing key securely stored (600 permissions)

**Files Modified:**
- `src/core/event_logger.py`
- `src/database/models.py` (add signature field)
- `scripts/verify_audit_trail.py` (new)

**Acceptance Criteria:**
- [ ] All events have cryptographic signatures
- [ ] Manual tampering detected by verification
- [ ] Signing key protected from unauthorized access

**Effort:** 2 days

---

#### Task 1.5: Remove TestSafetyManager from Production (1 day)

**Objective:** Separate test and production builds

**Technical Approach:**

**Option 1: Move to tests/ directory (RECOMMENDED)**
```bash
# Move TestSafetyManager to test package
mkdir -p tests/mocks
mv src/core/test_safety_manager.py tests/mocks/

# Update imports in test files
# OLD: from core.safety import TestSafetyManager
# NEW: from tests.mocks.test_safety_manager import TestSafetyManager
```

**Option 2: Build-time exclusion**
```python
# pyproject.toml
[tool.poetry]
packages = [
    { include = "src" },
    { include = "tests", optional = true, extras = ["dev"] }
]

[tool.poetry.extras]
dev = []  # Test code only in dev builds

# Build production package WITHOUT tests:
poetry build --without dev
```

**Testing:**
- [ ] TestSafetyManager not importable in production build
- [ ] Test suite still works with moved TestSafetyManager
- [ ] Production build 5-10% smaller

**Files Modified:**
- Move `src/core/safety.py` TestSafetyManager class → `tests/mocks/test_safety_manager.py`
- Update all test imports

**Acceptance Criteria:**
- [ ] TestSafetyManager not accessible in production code
- [ ] All existing tests still pass
- [ ] Import error raised if attempted in production

**Effort:** 1 day

---

## Phase 2: Testing & Validation (Weeks 3-4)

### Priority P1 - HIGH PRIORITY

#### Task 2.1: Safety State Machine Unit Tests (5 days)

**Objective:** Achieve 100% coverage of safety-critical code

**Test Suite:**

```python
# tests/core/test_safety_manager.py
import pytest
from src.core.safety import SafetyManager, SafetyState
from tests.mocks.mock_gpio_controller import MockGPIOController
from tests.mocks.mock_event_logger import MockEventLogger

class TestSafetyManager:

    def test_initial_state_is_unsafe(self):
        """System starts in UNSAFE state (fail-safe default)."""
        safety = SafetyManager(gpio_controller=MockGPIOController(), event_logger=MockEventLogger())
        assert safety.state == SafetyState.UNSAFE

    def test_transition_to_safe_when_all_conditions_met(self):
        """Transition to SAFE when all interlocks pass."""
        safety = SafetyManager(gpio_controller=MockGPIOController(), event_logger=MockEventLogger())

        # Satisfy all conditions
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)

        assert safety.state == SafetyState.SAFE
        assert safety.laser_enable_permitted is True

    def test_transition_to_unsafe_when_gpio_fails(self):
        """Transition to UNSAFE when GPIO interlock fails."""
        safety = SafetyManager(gpio_controller=MockGPIOController(), event_logger=MockEventLogger())

        # Start in SAFE state
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)
        assert safety.state == SafetyState.SAFE

        # GPIO interlock fails
        safety.set_gpio_interlock_status(False)

        assert safety.state == SafetyState.UNSAFE
        assert safety.laser_enable_permitted is False

    def test_emergency_stop_has_highest_priority(self):
        """Emergency stop overrides all other states."""
        safety = SafetyManager(gpio_controller=MockGPIOController(), event_logger=MockEventLogger())

        # Start in SAFE state
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)
        assert safety.state == SafetyState.SAFE

        # Trigger emergency stop
        safety.trigger_emergency_stop()

        assert safety.state == SafetyState.EMERGENCY_STOP
        assert safety.laser_enable_permitted is False
        assert safety.emergency_stop_active is True

    def test_cannot_exit_emergency_stop_without_reset(self):
        """Once in E-STOP, cannot exit without explicit reset."""
        safety = SafetyManager(gpio_controller=MockGPIOController(), event_logger=MockEventLogger())

        safety.trigger_emergency_stop()
        assert safety.state == SafetyState.EMERGENCY_STOP

        # Try to satisfy all conditions
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)

        # Should remain in E-STOP
        assert safety.state == SafetyState.EMERGENCY_STOP

    def test_reset_emergency_stop_requires_all_conditions(self):
        """Resetting E-STOP requires all interlocks to be satisfied."""
        safety = SafetyManager(gpio_controller=MockGPIOController(), event_logger=MockEventLogger())

        safety.trigger_emergency_stop()

        # Try to reset without satisfying conditions
        with pytest.raises(RuntimeError):
            safety.reset_emergency_stop()

        # Satisfy all conditions
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)

        # Now reset should succeed
        safety.reset_emergency_stop()
        assert safety.state == SafetyState.SAFE
        assert safety.emergency_stop_active is False

    def test_selective_shutdown_preserves_monitoring(self):
        """Emergency stop disables laser only, not monitoring."""
        gpio_controller = MockGPIOController()
        safety = SafetyManager(gpio_controller=gpio_controller, event_logger=MockEventLogger())

        # Verify GPIO controller still polling
        assert gpio_controller.is_connected is True

        safety.trigger_emergency_stop()

        # GPIO controller should STILL be active (selective shutdown)
        assert gpio_controller.is_connected is True
        assert safety.laser_enable_permitted is False
```

**Additional Test Cases:**
- [ ] Test watchdog timeout triggers emergency stop
- [ ] Test footpedal release transitions to UNSAFE
- [ ] Test vibration sensor failure disables laser
- [ ] Test photodiode power mismatch detection
- [ ] Test state transition event logging
- [ ] Test concurrent state updates (thread safety)

**Coverage Target:** 100% of `src/core/safety.py`

**Effort:** 5 days

---

#### Task 2.2: Protocol Engine Safety Tests (3 days)

**Objective:** Verify protocol execution halts on safety failures

**Test Suite:**

```python
# tests/core/test_protocol_engine_safety.py
import pytest
import asyncio
from src.core.protocol_engine import ProtocolEngine
from src.core.protocol import Protocol, ProtocolAction, SetLaserPowerParams
from tests.mocks.mock_laser_controller import MockLaserController
from tests.mocks.mock_safety_manager import MockSafetyManager

@pytest.mark.asyncio
async def test_protocol_halts_on_interlock_failure():
    """Protocol execution stops when interlock fails mid-execution."""
    laser = MockLaserController()
    safety = MockSafetyManager()
    engine = ProtocolEngine(laser_controller=laser, safety_manager=safety)

    # Create protocol with 3 actions
    protocol = Protocol(
        name="Test Protocol",
        actions=[
            ProtocolAction(type="set_laser_power", parameters=SetLaserPowerParams(power_watts=1.0)),
            ProtocolAction(type="wait", parameters=WaitParams(duration_sec=2.0)),
            ProtocolAction(type="set_laser_power", parameters=SetLaserPowerParams(power_watts=2.0)),
        ]
    )

    # Start execution
    execution_task = asyncio.create_task(engine.execute_protocol(protocol))

    # Wait 1 second, then fail interlock
    await asyncio.sleep(1.0)
    safety.set_gpio_interlock_status(False)  # ← Simulate footpedal release

    # Protocol should halt
    success, message = await execution_task

    assert success is False
    assert "interlock" in message.lower()
    assert engine.is_running is False

@pytest.mark.asyncio
async def test_emergency_stop_during_protocol():
    """Emergency stop immediately halts protocol execution."""
    laser = MockLaserController()
    safety = MockSafetyManager()
    engine = ProtocolEngine(laser_controller=laser, safety_manager=safety)

    protocol = Protocol(
        name="Long Protocol",
        actions=[ProtocolAction(type="wait", parameters=WaitParams(duration_sec=10.0))]
    )

    # Start execution
    execution_task = asyncio.create_task(engine.execute_protocol(protocol))

    # Wait 1 second, then trigger E-stop
    await asyncio.sleep(1.0)
    safety.trigger_emergency_stop()

    # Protocol should halt within 100ms
    start_time = asyncio.get_event_loop().time()
    success, message = await execution_task
    halt_time = asyncio.get_event_loop().time() - start_time

    assert success is False
    assert halt_time < 0.1  # Halt within 100ms
    assert engine.is_running is False
```

**Coverage Target:** Safety-critical paths in `src/core/protocol_engine.py`

**Effort:** 3 days

---

#### Task 2.3: 72-Hour Soak Test (3 days)

**Objective:** Validate system stability under extended operation

**Test Procedure:**

```python
# tests/integration/test_72hour_soak.py
def test_72hour_continuous_operation():
    """
    Run system for 72 hours with simulated treatment sessions.
    Monitor for memory leaks, crashes, and resource exhaustion.
    """
    duration_hours = 72
    session_interval_minutes = 30
    total_sessions = duration_hours * 60 // session_interval_minutes

    start_time = time.time()
    sessions_completed = 0
    errors = []

    while time.time() - start_time < duration_hours * 3600:
        try:
            # Start new session
            session = create_mock_session()

            # Execute protocol (5-10 minutes)
            execute_mock_protocol(session)

            # End session
            session.end()
            sessions_completed += 1

            # Log memory usage
            memory_mb = get_memory_usage()
            logger.info(f"Session {sessions_completed}/{total_sessions} - Memory: {memory_mb} MB")

            # Wait for next session
            time.sleep(session_interval_minutes * 60)

        except Exception as e:
            errors.append((time.time() - start_time, str(e)))
            logger.error(f"Soak test error at {time.time() - start_time:.1f}s: {e}")

    # Assertions
    assert sessions_completed >= total_sessions * 0.95  # 95% success rate
    assert len(errors) < total_sessions * 0.05  # <5% error rate
    assert get_memory_usage() < initial_memory * 1.2  # <20% memory growth
```

**Monitoring:**
- [ ] Memory usage (should remain stable)
- [ ] CPU usage (should not increase over time)
- [ ] Disk usage (log file growth within limits)
- [ ] Database file size (vacuum if needed)
- [ ] Error rate (<5% acceptable)
- [ ] Uptime (target: 72 hours continuous)

**Pass Criteria:**
- No crashes
- Memory usage <20% growth
- All safety interlocks responsive
- Database integrity maintained

**Effort:** 3 days (includes setup + monitoring + analysis)

---

## Phase 3: Compliance Documentation (Weeks 5-6)

### Priority P1 - HIGH PRIORITY

#### Task 3.1: Risk Management File (ISO 14971) (5 days)

**Objective:** Document hazard analysis and risk mitigation

**Template:**

```markdown
# Risk Management File - TOSCA Laser Control System

## Hazard Identification

### Hazard 1: Excessive Laser Power
- **Severity:** Catastrophic (tissue damage, blindness)
- **Probability:** Remote (hardware + software limits)
- **Risk Level:** Medium
- **Mitigation:**
  1. Hardware current limit (2000 mA) - IMPLEMENTED
  2. Software power limit (10W configurable) - IMPLEMENTED
  3. Photodiode continuous monitoring - IMPLEMENTED
  4. Operator training - PLANNED (Phase 7)
- **Residual Risk:** Low (acceptable)

### Hazard 2: Laser Activation Without Consent
- **Severity:** Critical (unauthorized treatment)
- **Probability:** Unlikely (footpedal required)
- **Risk Level:** Medium
- **Mitigation:**
  1. Footpedal deadman switch - IMPLEMENTED
  2. User authentication - IMPLEMENTED (Phase 6)
  3. Session validation - IMPLEMENTED
  4. Audit trail - IMPLEMENTED
- **Residual Risk:** Very Low (acceptable)

### Hazard 3: Database Breach (PHI/PII Exposure)
- **Severity:** Serious (HIPAA violation, patient privacy)
- **Probability:** Possible (laptop theft, USB copy)
- **Risk Level:** High
- **Mitigation:**
  1. Database encryption (AES-256) - IMPLEMENTED (Phase 6)
  2. User authentication - IMPLEMENTED (Phase 6)
  3. Audit trail integrity - IMPLEMENTED (Phase 6)
  4. Physical access controls - RECOMMENDED
- **Residual Risk:** Low (acceptable)

... (30-50 hazards total)
```

**Sections:**
1. Scope and applicability
2. Hazard identification (FMEA)
3. Risk estimation (severity × probability)
4. Risk evaluation (acceptable/unacceptable)
5. Risk control measures
6. Residual risk evaluation
7. Risk management review

**Tools:**
- FMEA (Failure Modes and Effects Analysis) template
- Risk matrix (severity vs probability)

**Effort:** 5 days

---

#### Task 3.2: Software Requirements Specification (SRS) (5 days)

**Objective:** Formalize functional and safety requirements

**Template:**

```markdown
# Software Requirements Specification - TOSCA

## 1. Functional Requirements

### FR-001: User Authentication
- **Description:** System shall require user authentication before granting access
- **Priority:** Critical
- **Verification:** Test case TC-AUTH-001
- **Traceability:** Implements security requirement SR-001
- **Status:** IMPLEMENTED (Phase 6)

### FR-002: Laser Power Control
- **Description:** System shall allow operator to set laser power between 0-10W
- **Priority:** Critical
- **Verification:** Test case TC-LASER-001
- **Traceability:** Implements safety requirement SR-010
- **Status:** IMPLEMENTED

... (100-200 requirements)

## 2. Safety Requirements

### SR-001: Emergency Stop
- **Description:** System shall provide emergency stop button that immediately disables laser
- **Priority:** Critical (IEC 62304 Class C)
- **Verification:** Test case TC-SAFETY-001
- **Traceability:** Mitigates hazard H-001 (excessive laser power)
- **Status:** IMPLEMENTED

... (30-50 safety requirements)

## 3. Performance Requirements

### PR-001: Camera Frame Rate
- **Description:** System shall maintain minimum 25 FPS camera streaming
- **Priority:** Medium
- **Verification:** Performance test PT-001
- **Status:** VERIFIED (30 FPS achieved)

... (10-20 performance requirements)
```

**Effort:** 5 days

---

#### Task 3.3: Verification & Validation (V&V) Protocols (4 days)

**Objective:** Document test procedures for FDA submission

**Template:**

```markdown
# Verification & Validation Protocol - TOSCA

## Test Protocol: TP-SAFETY-001 - Emergency Stop Verification

### Objective
Verify emergency stop button immediately disables laser output

### Prerequisites
- System powered and initialized
- Laser controller connected
- GPIO controller connected
- Active treatment session

### Test Procedure
1. Start protocol with laser power set to 5W
2. Verify laser is outputting (photodiode reading ~5W)
3. Press emergency stop button
4. Measure time to laser disable

### Expected Results
- Laser output disabled within 100ms
- System enters EMERGENCY_STOP state
- Event logged to audit trail
- Laser cannot be re-enabled without supervisor reset

### Pass Criteria
- Time to disable ≤ 100ms
- All safety interlocks verified

### Test Data
| Run | Laser Power (W) | Time to Disable (ms) | State After | Pass/Fail |
|-----|-----------------|----------------------|-------------|-----------|
| 1   | 5.0             | 42                   | E-STOP      | PASS      |
| 2   | 8.0             | 38                   | E-STOP      | PASS      |
| 3   | 2.0             | 45                   | E-STOP      | PASS      |

### Result: PASS
```

**Test Protocols Needed:**
- TP-SAFETY-001 to TP-SAFETY-010 (Safety tests)
- TP-FUNC-001 to TP-FUNC-020 (Functional tests)
- TP-PERF-001 to TP-PERF-005 (Performance tests)
- TP-SEC-001 to TP-SEC-008 (Security tests)

**Effort:** 4 days

---

## Phase 4: Final Hardening (Weeks 7-8)

### Priority P2 - MEDIUM PRIORITY

#### Task 4.1: Protocol File HMAC Signatures (2 days)

**Implementation:** See Phase 2 Security Report Section 6

**Effort:** 2 days

---

#### Task 4.2: Multi-Factor Authentication (TOTP) (3 days)

**Objective:** Add TOTP-based MFA for high-risk operations

**Implementation:**

```python
# Install pyotp
pip install pyotp

# database/models.py - Add MFA field
class TechUser(Base):
    mfa_secret: Mapped[Optional[str]]  # TOTP secret (base32)
    mfa_enabled: Mapped[bool] = mapped_column(default=False)

# ui/dialogs/mfa_setup_dialog.py
import pyotp
import qrcode

class MFASetupDialog(QDialog):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.secret = pyotp.random_base32()
        self._setup_ui()

    def _setup_ui(self):
        # Generate QR code for Google Authenticator
        totp_uri = pyotp.totp.TOTP(self.secret).provisioning_uri(
            name=self.user.username,
            issuer_name="TOSCA Laser System"
        )

        qr = qrcode.make(totp_uri)
        # Display QR code + manual entry code

    def verify_and_enable(self):
        # User enters code from authenticator app
        code = self.code_input.text()
        totp = pyotp.TOTP(self.secret)

        if totp.verify(code, valid_window=1):
            self.user.mfa_secret = self.secret
            self.user.mfa_enabled = True
            QMessageBox.information(self, "Success", "MFA enabled successfully")
            self.accept()
        else:
            QMessageBox.warning(self, "Invalid Code", "Please try again")

# login_dialog.py - Add MFA verification
def _attempt_login(self):
    user = self.db_manager.get_user_by_username(username)

    if user and user.verify_password(password):
        if user.mfa_enabled:
            # Show MFA verification dialog
            mfa_dialog = MFAVerificationDialog(user)
            if mfa_dialog.exec() != QDialog.DialogCode.Accepted:
                QMessageBox.warning(self, "MFA Failed", "Invalid MFA code")
                return

        # Proceed with login
        self.authenticated_user = user
        self.accept()
```

**Effort:** 3 days

---

#### Task 4.3: 7-Year Log Retention Policy (2 days)

**Objective:** Implement automated log rotation and archival

**Implementation:**

```python
# core/log_rotator.py
from datetime import datetime, timedelta
import shutil
import gzip

class LogRotator:
    def __init__(self, log_dir="data/logs", retention_years=7):
        self.log_dir = Path(log_dir)
        self.retention_years = retention_years

    def rotate_daily(self):
        """Rotate JSONL log file daily."""
        today = datetime.now().strftime("%Y-%m-%d")
        current_log = self.log_dir / "events.jsonl"

        if current_log.exists():
            # Rename to dated file
            rotated_log = self.log_dir / f"events_{today}.jsonl"
            shutil.move(current_log, rotated_log)

            # Compress
            self._compress_file(rotated_log)

            # Create new empty log
            current_log.touch()

    def _compress_file(self, file_path):
        """Compress log file with gzip."""
        with open(file_path, 'rb') as f_in:
            with gzip.open(f"{file_path}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        file_path.unlink()  # Delete uncompressed

    def cleanup_old_logs(self):
        """Delete logs older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_years * 365)

        for log_file in self.log_dir.glob("events_*.jsonl.gz"):
            # Extract date from filename
            date_str = log_file.stem.replace("events_", "").replace(".jsonl", "")
            log_date = datetime.strptime(date_str, "%Y-%m-%d")

            if log_date < cutoff_date:
                logger.warning(f"Deleting log older than {self.retention_years} years: {log_file}")
                log_file.unlink()

# Schedule in main_window.py
self.log_rotator = LogRotator()
self.rotation_timer = QTimer()
self.rotation_timer.timeout.connect(self.log_rotator.rotate_daily)
self.rotation_timer.start(86400000)  # 24 hours
```

**Effort:** 2 days

---

#### Task 4.4: Penetration Testing (White-Box) (5 days)

**Objective:** Security validation by external specialist

**Test Scenarios:**

1. **SQL Injection Testing**
   - Attempt SQL injection in all input fields
   - Verify parameterized queries prevent injection

2. **Authentication Bypass Testing**
   - Attempt to access MainWindow without login
   - Attempt session hijacking
   - Attempt account enumeration

3. **Encryption Verification**
   - Verify database file cannot be opened without key
   - Verify video files cannot be played without decryption
   - Verify audit trail signatures prevent tampering

4. **Privilege Escalation Testing**
   - Attempt to elevate technician to admin role
   - Attempt to modify other users' data

5. **Physical Security Testing**
   - USB autorun attacks
   - COM port hijacking
   - Firmware update hijacking

**Deliverables:**
- Penetration test report
- Remediation recommendations
- Re-test verification

**Effort:** 5 days (external consultant + internal remediation)

---

## Summary

### Total Effort Estimate

| Phase | Duration | FTE | Key Deliverables |
|-------|----------|-----|------------------|
| Phase 1: Security Fixes | 2 weeks | 2 engineers | Database encryption, authentication, video encryption, audit trail integrity |
| Phase 2: Testing | 2 weeks | 1 engineer | Safety tests, protocol tests, 72-hour soak test |
| Phase 3: Documentation | 2 weeks | 1 engineer + 1 regulatory | Risk file, SRS, V&V protocols |
| Phase 4: Hardening | 2 weeks | 1 engineer + 1 security | Protocol signatures, MFA, log retention, penetration testing |

**Total:** 8 weeks, 2-3 FTE

---

### Budget Estimate (Labor Only)

- Senior Software Engineer: $150/hr × 320 hrs = $48,000
- Security Specialist: $175/hr × 80 hrs = $14,000
- Regulatory Consultant: $200/hr × 80 hrs = $16,000
- **Total:** $78,000

---

### Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SQLCipher performance degradation | Medium | High | Benchmark early (Task 1.1), optimize if needed |
| Authentication UX complexity | Low | Medium | User testing with technicians (Phase 2) |
| 72-hour soak test failures | Medium | High | Fix issues incrementally, re-run until stable |
| FDA regulatory delays | High | High | Engage consultant early (Phase 3) |
| Penetration testing finds critical issues | Medium | High | Budget 1-week buffer for remediation |

---

## Next Steps

1. **Immediate (This Week):**
   - Review this action plan with stakeholders
   - Allocate budget and resources
   - Prioritize P0 tasks (security fixes)

2. **Week 1:**
   - Start Task 1.1 (Database Encryption)
   - Start Task 1.2 (Authentication System)

3. **Week 2:**
   - Complete Task 1.1-1.5 (All P0 security fixes)
   - Begin Phase 2 testing

4. **Weeks 3-8:**
   - Execute Phases 2-4 per schedule
   - Weekly progress reviews

---

**Report Complete**
**For questions or clarifications, see full reports in `review_reports/` directory**
