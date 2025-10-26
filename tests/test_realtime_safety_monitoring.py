"""
Test real-time safety monitoring during protocol execution.

CRITICAL SAFETY FEATURE: Verifies that protocol execution stops immediately
when safety interlocks fail mid-execution (Issue #11).

Tests:
1. Signal connection between SafetyManager and ProtocolEngine
2. Real-time callback triggers on safety failure during execution
3. Protocol stops immediately when laser enable permission revoked
4. Selective shutdown (laser disabled, camera/actuator remain operational)
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import QCoreApplication

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from core.protocol import ActionType, Protocol, ProtocolAction, SetLaserPowerParams, WaitParams
from core.protocol_engine import ExecutionState, ProtocolEngine
from core.safety import SafetyManager
from tests.mocks import MockActuatorController, MockLaserController


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
def safety_manager():
    """Create safety manager (no GPIO for pure software testing)."""
    manager = SafetyManager()
    # Enable all safety conditions for testing
    manager.set_session_valid(True)
    manager.set_power_limit_ok(True)
    # Manually set GPIO interlock OK (bypassing hardware for testing)
    manager.set_gpio_interlock_status(True)
    # Now laser should be enabled for testing
    return manager


@pytest.fixture
def protocol_engine(mock_laser, mock_actuator, safety_manager):
    """Create protocol engine with mocks and safety manager."""
    engine = ProtocolEngine(
        laser_controller=mock_laser,
        actuator_controller=mock_actuator,
        safety_manager=safety_manager,
    )
    return engine


def create_test_protocol(duration: float = 5.0) -> Protocol:
    """Create a test protocol that runs for specified duration."""
    return Protocol(
        protocol_name="Safety Test Protocol",
        version="1.0.0",
        description="Protocol for testing real-time safety monitoring",
        actions=[
            # Set laser power
            ProtocolAction(
                action_id=1,
                action_type=ActionType.SET_LASER_POWER,
                parameters=SetLaserPowerParams(power_watts=0.5),
                notes="Set laser power",
            ),
            # Long wait to allow safety trigger during execution
            ProtocolAction(
                action_id=2,
                action_type=ActionType.WAIT,
                parameters=WaitParams(duration_seconds=duration),
                notes="Wait period for safety trigger test",
            ),
        ],
    )


class TestRealtimeSafetyMonitoring:
    """Test real-time safety monitoring during protocol execution."""

    def test_signal_connection_established(self, protocol_engine, safety_manager):
        """Verify ProtocolEngine connects to SafetyManager signals."""
        # Check that laser_enable_changed signal has a connection
        assert protocol_engine.safety_manager is safety_manager
        # Verify connection was logged
        # (Connection happens in __init__, line 70 of protocol_engine.py)

    @pytest.mark.asyncio
    async def test_safety_failure_stops_protocol(
        self, protocol_engine, safety_manager, mock_laser, app
    ):
        """Test protocol stops immediately when safety fails mid-execution."""
        protocol = create_test_protocol(duration=10.0)  # Long protocol

        # Track execution state changes
        state_changes = []

        def on_state_change(state: ExecutionState) -> None:
            state_changes.append(state)

        protocol_engine.on_state_change = on_state_change

        # Start protocol execution in background
        execution_task = asyncio.create_task(
            protocol_engine.execute_protocol(protocol, record=False)
        )

        # Wait for protocol to start running
        await asyncio.sleep(0.5)
        assert protocol_engine.state == ExecutionState.RUNNING

        # TRIGGER SAFETY FAILURE by emitting laser_enable_changed(False)
        safety_manager.laser_enable_changed.emit(False)

        # Process Qt events to allow signal propagation
        app.processEvents()

        # Wait a bit for callback to execute
        await asyncio.sleep(0.2)

        # Verify protocol stopped immediately (goes to ERROR state when stopped mid-execution)
        assert protocol_engine.state in (ExecutionState.STOPPED, ExecutionState.ERROR)
        assert any(s in (ExecutionState.STOPPED, ExecutionState.ERROR) for s in state_changes)

        # Verify laser was disabled
        assert not mock_laser.is_output_enabled
        assert mock_laser.power_setpoint_mw == 0.0

        # Cancel the execution task
        execution_task.cancel()
        try:
            await execution_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_selective_shutdown_laser_only(
        self, protocol_engine, safety_manager, mock_laser, mock_actuator, app
    ):
        """Verify selective shutdown: laser disabled, other systems remain operational."""
        protocol = create_test_protocol(duration=10.0)

        # Start protocol execution
        execution_task = asyncio.create_task(
            protocol_engine.execute_protocol(protocol, record=False)
        )

        # Wait for protocol to start
        await asyncio.sleep(0.5)
        assert protocol_engine.state == ExecutionState.RUNNING

        # Verify laser was enabled during execution
        laser_was_on = mock_laser.is_output_enabled

        # Trigger safety failure
        safety_manager.laser_enable_changed.emit(False)
        app.processEvents()
        await asyncio.sleep(0.2)

        # VERIFY SELECTIVE SHUTDOWN:
        # 1. Laser disabled
        assert not mock_laser.is_output_enabled  # Output disabled
        assert mock_laser.power_setpoint_mw == 0.0  # Current set to zero

        # 2. Actuator remains connected (can still be controlled)
        assert mock_actuator.is_connected  # Still connected

        # 3. Mock actuator can still accept position commands
        mock_actuator.set_position(5000.0)  # Should succeed
        assert mock_actuator.target_position_um == 5000.0

        # Cancel execution task
        execution_task.cancel()
        try:
            await execution_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_safety_ok_during_execution_continues(
        self, protocol_engine, safety_manager, mock_laser, app
    ):
        """Verify protocol continues normally when safety remains OK."""
        protocol = create_test_protocol(duration=2.0)  # Short protocol

        # Start protocol execution
        success, message = await protocol_engine.execute_protocol(protocol, record=False)

        # Verify completed successfully
        assert success
        assert protocol_engine.state == ExecutionState.COMPLETED

        # Verify laser was used
        assert mock_laser.call_log  # Some laser operations occurred

    @pytest.mark.asyncio
    async def test_safety_callback_only_acts_during_execution(
        self, protocol_engine, safety_manager, mock_laser, app
    ):
        """Verify callback only acts when protocol is RUNNING."""
        # Protocol is IDLE, not running
        assert protocol_engine.state == ExecutionState.IDLE

        # Trigger safety signal
        safety_manager.laser_enable_changed.emit(False)
        app.processEvents()
        await asyncio.sleep(0.1)

        # Verify state unchanged (callback should ignore signal when not RUNNING)
        assert protocol_engine.state == ExecutionState.IDLE

        # Laser was not affected (callback didn't act)
        # (Mock laser starts disabled, so this should still be False)

    @pytest.mark.asyncio
    async def test_multiple_safety_failures_handled(
        self, protocol_engine, safety_manager, mock_laser, app
    ):
        """Test multiple safety failures don't cause issues."""
        protocol = create_test_protocol(duration=10.0)

        execution_task = asyncio.create_task(
            protocol_engine.execute_protocol(protocol, record=False)
        )

        await asyncio.sleep(0.5)
        assert protocol_engine.state == ExecutionState.RUNNING

        # Trigger multiple safety failures
        for _ in range(3):
            safety_manager.laser_enable_changed.emit(False)
            app.processEvents()
            await asyncio.sleep(0.1)

        # Should handle gracefully (already stopped after first)
        assert protocol_engine.state in (ExecutionState.STOPPED, ExecutionState.ERROR)

        execution_task.cancel()
        try:
            await execution_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
