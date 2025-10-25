"""
Test script for protocol execution engine.

Tests the complete protocol execution flow WITHOUT hardware:
1. Create test protocol
2. Execute via ProtocolEngine
3. Monitor execution progress
4. Verify completion

Run this script to validate protocol engine implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.protocol import (
    ActionType,
    MoveActuatorParams,
    Protocol,
    ProtocolAction,
    RampLaserPowerParams,
    SetLaserPowerParams,
    WaitParams,
)
from core.protocol_engine import ExecutionState, ProtocolEngine


def create_test_protocol() -> Protocol:
    """Create a test protocol with various actions."""
    return Protocol(
        protocol_name="Test Protocol",
        version="1.0.0",
        description="Protocol to test execution engine",
        actions=[
            # Action 1: Set laser power to 0.1W
            ProtocolAction(
                action_id=1,
                action_type=ActionType.SET_LASER_POWER,
                parameters=SetLaserPowerParams(power_watts=0.1),
                notes="Turn on laser at low power",
            ),
            # Action 2: Move actuator to 1000µm
            ProtocolAction(
                action_id=2,
                action_type=ActionType.MOVE_ACTUATOR,
                parameters=MoveActuatorParams(target_position_um=1000.0, speed_um_per_sec=100.0),
                notes="Move actuator to initial position",
            ),
            # Action 3: Wait 2 seconds
            ProtocolAction(
                action_id=3,
                action_type=ActionType.WAIT,
                parameters=WaitParams(duration_seconds=2.0),
                notes="Wait for stabilization",
            ),
            # Action 4: Ramp laser power
            ProtocolAction(
                action_id=4,
                action_type=ActionType.RAMP_LASER_POWER,
                parameters=RampLaserPowerParams(
                    start_power_watts=0.1,
                    end_power_watts=0.5,
                    duration_seconds=3.0,
                    ramp_type="linear",
                ),
                notes="Ramp up laser power",
            ),
            # Action 5: Move actuator to 2000µm
            ProtocolAction(
                action_id=5,
                action_type=ActionType.MOVE_ACTUATOR,
                parameters=MoveActuatorParams(target_position_um=2000.0, speed_um_per_sec=200.0),
                notes="Move to treatment position",
            ),
            # Action 6: Wait 1 second
            ProtocolAction(
                action_id=6,
                action_type=ActionType.WAIT,
                parameters=WaitParams(duration_seconds=1.0),
                notes="Short wait",
            ),
            # Action 7: Turn off laser
            ProtocolAction(
                action_id=7,
                action_type=ActionType.SET_LASER_POWER,
                parameters=SetLaserPowerParams(power_watts=0.0),
                notes="Turn off laser",
            ),
        ],
    )


async def test_protocol_execution():
    """Test protocol execution without hardware."""
    print("=" * 80)
    print("PROTOCOL EXECUTION TEST")
    print("=" * 80)
    print()

    # Create protocol engine (no hardware controllers)
    print("[1] Creating protocol engine without hardware...")
    engine = ProtocolEngine(laser_controller=None, actuator_controller=None)

    # Set up callbacks for monitoring
    def on_action_start(action):
        print(f"  -> Starting action {action.action_id}: {action.notes}")

    def on_action_complete(action):
        print(f"  [OK] Completed action {action.action_id}")

    def on_progress_update(progress):
        bar_length = 40
        filled = int(bar_length * progress)
        bar = "#" * filled + "-" * (bar_length - filled)
        print(f"\r  Progress: [{bar}] {progress*100:.1f}%", end="", flush=True)

    def on_state_change(state):
        print(f"\n[STATE] Protocol state: {state.value}")

    engine.on_action_start = on_action_start
    engine.on_action_complete = on_action_complete
    engine.on_progress_update = on_progress_update
    engine.on_state_change = on_state_change

    # Create test protocol
    print("\n[2] Creating test protocol with 7 actions...")
    protocol = create_test_protocol()

    # Validate protocol
    valid, errors = protocol.validate()
    if not valid:
        print(f"[X] Protocol validation failed: {errors}")
        return False

    print("[OK] Protocol validated successfully")

    # Execute protocol
    print("\n[3] Starting protocol execution...")
    print("-" * 40)

    success, message = await engine.execute_protocol(protocol, record=False)

    print("\n" + "-" * 40)

    if success:
        print(f"\n[OK] SUCCESS: {message}")

        # Get execution summary
        summary = engine.get_execution_summary()
        print("\nExecution Summary:")
        print(f"  Protocol: {summary['protocol_name']}")
        print(f"  Duration: {summary['duration_seconds']:.1f} seconds")
        print(f"  Actions executed: {summary['total_actions_executed']}")
        print(f"  Final state: {summary['state']}")

        return True
    else:
        print(f"\n[X] FAILED: {message}")
        return False


async def test_pause_resume():
    """Test pause and resume functionality."""
    print("\n" + "=" * 80)
    print("PAUSE/RESUME TEST")
    print("=" * 80)
    print()

    engine = ProtocolEngine(laser_controller=None, actuator_controller=None)

    # Simple protocol with wait actions
    protocol = Protocol(
        protocol_name="Pause Test",
        version="1.0.0",
        actions=[
            ProtocolAction(
                action_id=1,
                action_type=ActionType.WAIT,
                parameters=WaitParams(duration_seconds=3.0),
                notes="Wait 3 seconds",
            ),
            ProtocolAction(
                action_id=2,
                action_type=ActionType.WAIT,
                parameters=WaitParams(duration_seconds=3.0),
                notes="Wait another 3 seconds",
            ),
        ],
    )

    # Start execution in background
    print("[1] Starting protocol execution...")
    execution_task = asyncio.create_task(engine.execute_protocol(protocol, record=False))

    # Wait 1 second then pause
    await asyncio.sleep(1)
    print("[2] Pausing execution...")
    engine.pause()
    print(f"    State: {engine.state.value}")

    # Wait 2 seconds (protocol should not progress)
    await asyncio.sleep(2)
    print("[3] Resuming execution...")
    engine.resume()
    print(f"    State: {engine.state.value}")

    # Wait for completion
    success, message = await execution_task

    if success:
        print(f"[OK] Pause/Resume test passed: {message}")
        return True
    else:
        print(f"[X] Pause/Resume test failed: {message}")
        return False


async def test_stop():
    """Test stop functionality."""
    print("\n" + "=" * 80)
    print("STOP TEST")
    print("=" * 80)
    print()

    engine = ProtocolEngine(laser_controller=None, actuator_controller=None)

    # Protocol with multiple actions
    protocol = Protocol(
        protocol_name="Stop Test",
        version="1.0.0",
        actions=[
            ProtocolAction(
                action_id=i,
                action_type=ActionType.WAIT,
                parameters=WaitParams(duration_seconds=1.0),
                notes=f"Wait action {i}",
            )
            for i in range(1, 6)
        ],
    )

    # Start execution
    print("[1] Starting protocol with 5 wait actions...")
    execution_task = asyncio.create_task(engine.execute_protocol(protocol, record=False))

    # Wait briefly then stop
    await asyncio.sleep(2)
    print("[2] Stopping execution...")
    engine.stop()

    # Wait for task to complete
    success, message = await execution_task

    if not success and "stopped" in message.lower():
        print(f"[OK] Stop test passed: {message}")
        return True
    else:
        print(f"[X] Stop test failed: {message}")
        return False


async def main():
    """Run all tests."""
    print("\n")
    print("=" * 80)
    print(" " * 25 + "PROTOCOL ENGINE TEST SUITE")
    print("=" * 80)
    print("\n")

    all_passed = True

    # Test 1: Basic execution
    if await test_protocol_execution():
        print("\n[PASS] Basic execution test")
    else:
        print("\n[FAIL] Basic execution test")
        all_passed = False

    # Test 2: Pause/Resume
    if await test_pause_resume():
        print("\n[PASS] Pause/Resume test")
    else:
        print("\n[FAIL] Pause/Resume test")
        all_passed = False

    # Test 3: Stop
    if await test_stop():
        print("\n[PASS] Stop test")
    else:
        print("\n[FAIL] Stop test")
        all_passed = False

    # Summary
    print("\n" + "=" * 80)
    if all_passed:
        print("[PASS] ALL TESTS PASSED - Protocol Engine Working Correctly!")
    else:
        print("[FAIL] Some tests failed - Review implementation")
    print("=" * 80)
    print()

    return all_passed


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Test error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)