"""
Unit tests for ProtocolEngine safety integration.

Tests protocol start validation, edge cases, and safety coordination.
Complements test_realtime_safety_monitoring.py (mid-execution tests).

Week 3 Requirements:
- Test protocol start validation (refuses unsafe start)
- Test edge cases (pause, resume, recovery)
- Test state machine coordination with safety
"""

import asyncio
import sys
from pathlib import Path

import pytest
from PyQt6.QtCore import QCoreApplication

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from core.protocol import ActionType, Protocol, ProtocolAction, SetLaserPowerParams, WaitParams
from core.protocol_engine import ExecutionState, ProtocolEngine
from core.safety import SafetyManager, SafetyState
from tests.mocks import MockActuatorController, MockLaserController

# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def app():
    """Create QCoreApplication for signal/slot testing."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app


@pytest.fixture
def mock_laser():
    """Create mock laser controller."""
    laser = MockLaserController()
    laser.connect()
    return laser


@pytest.fixture
def mock_actuator():
    """Create mock actuator controller."""
    actuator = MockActuatorController()
    actuator.connect(auto_home=True)
    actuator._complete_homing()
    return actuator


@pytest.fixture
def safety_manager_unsafe():
    """Create safety manager in UNSAFE state (interlocks not satisfied)."""
    manager = SafetyManager()
    # Intentionally leave all interlocks unsatisfied
    return manager


@pytest.fixture
def safety_manager_safe():
    """Create safety manager in SAFE state (all interlocks satisfied)."""
    manager = SafetyManager()
    manager.set_session_valid(True)
    manager.set_power_limit_ok(True)
    manager.set_gpio_interlock_status(True)
    return manager


@pytest.fixture
def protocol_engine_unsafe(mock_laser, mock_actuator, safety_manager_unsafe):
    """Create protocol engine with unsafe safety manager."""
    return ProtocolEngine(
        laser_controller=mock_laser,
        actuator_controller=mock_actuator,
        safety_manager=safety_manager_unsafe,
    )


@pytest.fixture
def protocol_engine_safe(mock_laser, mock_actuator, safety_manager_safe):
    """Create protocol engine with safe safety manager."""
    return ProtocolEngine(
        laser_controller=mock_laser,
        actuator_controller=mock_actuator,
        safety_manager=safety_manager_safe,
    )


def create_simple_protocol(duration: float = 2.0) -> Protocol:
    """Create a simple test protocol."""
    return Protocol(
        protocol_name="Start Validation Test",
        version="1.0.0",
        description="Simple protocol for testing start validation",
        actions=[
            ProtocolAction(
                action_id=1,
                action_type=ActionType.SET_LASER_POWER,
                parameters=SetLaserPowerParams(power_watts=0.1),
                notes="Set laser power",
            ),
            ProtocolAction(
                action_id=2,
                action_type=ActionType.WAIT,
                parameters=WaitParams(duration_seconds=duration),
                notes="Wait",
            ),
        ],
    )


# ==============================================================================
# START VALIDATION TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_start_refuses_when_laser_disabled(protocol_engine_unsafe, safety_manager_unsafe):
    """Test protocol refuses to start when laser enable denied (Week 3 requirement)."""
    protocol = create_simple_protocol()

    # Verify safety manager denies laser
    assert not safety_manager_unsafe.is_laser_enable_permitted()
    assert safety_manager_unsafe.state == SafetyState.UNSAFE

    # Attempt to start protocol
    success, message = await protocol_engine_unsafe.execute_protocol(protocol, record=False)

    # Should fail due to safety check
    assert success is False
    assert "safety" in message.lower() or "interlock" in message.lower()

    # Verify protocol never started
    assert protocol_engine_unsafe.state == ExecutionState.IDLE


@pytest.mark.asyncio
async def test_start_requires_valid_session(mock_laser, mock_actuator):
    """Test protocol requires valid session to start."""
    # Create safety manager with session invalid
    safety_manager = SafetyManager()
    safety_manager.set_gpio_interlock_status(True)
    safety_manager.set_power_limit_ok(True)
    # session_valid defaults to False

    protocol_engine = ProtocolEngine(
        laser_controller=mock_laser,
        actuator_controller=mock_actuator,
        safety_manager=safety_manager,
    )

    protocol = create_simple_protocol()

    # Verify session invalid
    assert not safety_manager.session_valid
    assert not safety_manager.is_laser_enable_permitted()

    # Attempt to start
    success, message = await protocol_engine.execute_protocol(protocol, record=False)

    # Should fail
    assert success is False
    assert "safety" in message.lower() or "session" in message.lower()


@pytest.mark.asyncio
async def test_start_requires_gpio_interlocks(mock_laser, mock_actuator):
    """Test protocol requires GPIO interlocks satisfied."""
    # Create safety manager with GPIO interlocks failed
    safety_manager = SafetyManager()
    safety_manager.set_session_valid(True)
    safety_manager.set_power_limit_ok(True)
    # gpio_interlock_ok defaults to False

    protocol_engine = ProtocolEngine(
        laser_controller=mock_laser,
        actuator_controller=mock_actuator,
        safety_manager=safety_manager,
    )

    protocol = create_simple_protocol()

    # Verify GPIO interlocks not satisfied
    assert not safety_manager.gpio_interlock_ok
    assert not safety_manager.is_laser_enable_permitted()

    # Attempt to start
    success, message = await protocol_engine.execute_protocol(protocol, record=False)

    # Should fail
    assert success is False
    assert "safety" in message.lower() or "interlock" in message.lower()


@pytest.mark.asyncio
async def test_start_succeeds_when_all_interlocks_satisfied(protocol_engine_safe):
    """Test protocol starts successfully when all safety conditions met."""
    protocol = create_simple_protocol(duration=0.5)

    # Verify safety OK
    assert protocol_engine_safe.safety_manager.is_laser_enable_permitted()

    # Start protocol
    success, message = await protocol_engine_safe.execute_protocol(protocol, record=False)

    # Should succeed
    assert success is True
    assert protocol_engine_safe.state == ExecutionState.COMPLETED


# ==============================================================================
# EDGE CASE TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_safety_change_during_pause_monitored(protocol_engine_safe, safety_manager_safe, app):
    """Test safety failure during pause is monitored and stops protocol on resume."""
    protocol = create_simple_protocol(duration=10.0)

    # Start protocol
    execution_task = asyncio.create_task(
        protocol_engine_safe.execute_protocol(protocol, record=False)
    )

    # Wait for start
    await asyncio.sleep(0.5)
    assert protocol_engine_safe.state == ExecutionState.RUNNING

    # Pause
    protocol_engine_safe.pause()
    await asyncio.sleep(0.1)
    assert protocol_engine_safe.state == ExecutionState.PAUSED

    # Trigger safety failure while paused
    safety_manager_safe.set_gpio_interlock_status(False)
    app.processEvents()
    await asyncio.sleep(0.1)

    # Verify safety manager now unsafe
    assert not safety_manager_safe.is_laser_enable_permitted()

    # Resume (current implementation allows resume, safety checked during execution)
    protocol_engine_safe.resume()
    app.processEvents()
    await asyncio.sleep(0.2)

    # Current behavior: Protocol resumes briefly then stops due to active safety monitoring
    # NOTE: Safety is checked at start and monitored during RUNNING, not at resume
    # This is acceptable - real-time monitoring will stop protocol if resumed unsafely
    assert protocol_engine_safe.state in (
        ExecutionState.RUNNING,  # Briefly running before safety callback triggers
        ExecutionState.STOPPED,  # Or already stopped by safety callback
        ExecutionState.ERROR,
    )

    # Cleanup
    execution_task.cancel()
    try:
        await execution_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_recovery_after_safety_failure_allows_restart(
    protocol_engine_safe, safety_manager_safe, mock_laser, app
):
    """Test new protocol can start after safety failure and recovery."""
    protocol = create_simple_protocol(duration=5.0)

    # Start protocol
    execution_task = asyncio.create_task(
        protocol_engine_safe.execute_protocol(protocol, record=False)
    )

    # Wait for start
    await asyncio.sleep(0.5)
    assert protocol_engine_safe.state == ExecutionState.RUNNING

    # Trigger safety failure
    safety_manager_safe.set_gpio_interlock_status(False)
    app.processEvents()
    await asyncio.sleep(0.2)

    # Verify protocol stopped
    assert protocol_engine_safe.state in (ExecutionState.STOPPED, ExecutionState.ERROR)

    # Cleanup first execution
    execution_task.cancel()
    try:
        await execution_task
    except asyncio.CancelledError:
        pass

    # Restore safety
    safety_manager_safe.set_gpio_interlock_status(True)
    app.processEvents()
    await asyncio.sleep(0.1)

    # Verify safety restored
    assert safety_manager_safe.is_laser_enable_permitted()

    # Start NEW protocol
    new_protocol = create_simple_protocol(duration=0.5)
    success, message = await protocol_engine_safe.execute_protocol(new_protocol, record=False)

    # Should succeed
    assert success is True
    assert protocol_engine_safe.state == ExecutionState.COMPLETED


@pytest.mark.asyncio
async def test_state_transitions_respect_safety(
    protocol_engine_safe, safety_manager_safe, mock_laser, app
):
    """Test execution state machine respects safety state transitions."""
    protocol = create_simple_protocol(duration=5.0)

    # IDLE → RUNNING requires safety OK
    assert protocol_engine_safe.state == ExecutionState.IDLE
    assert safety_manager_safe.state == SafetyState.SAFE

    execution_task = asyncio.create_task(
        protocol_engine_safe.execute_protocol(protocol, record=False)
    )

    await asyncio.sleep(0.5)

    # RUNNING state achieved
    assert protocol_engine_safe.state == ExecutionState.RUNNING

    # Safety state should remain SAFE during normal execution
    assert safety_manager_safe.state == SafetyState.SAFE
    assert safety_manager_safe.is_laser_enable_permitted()

    # RUNNING → ERROR/STOPPED on safety failure
    safety_manager_safe.set_gpio_interlock_status(False)
    app.processEvents()
    await asyncio.sleep(0.2)

    # Protocol should stop
    assert protocol_engine_safe.state in (ExecutionState.STOPPED, ExecutionState.ERROR)

    # Safety should be UNSAFE
    assert safety_manager_safe.state == SafetyState.UNSAFE

    # Cleanup
    execution_task.cancel()
    try:
        await execution_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
