# Project Todos

## Active
- [ ] Add event logging to hardware controllers (camera, laser, actuator, GPIO)
- [ ] Update safety widget to display event log from database
- [ ] Add event export functionality (CSV/JSON)
- [ ] Fix TODO comments without ticket numbers (2 files: actuator_widget.py, laser_controller.py)
- [ ] Implement placeholder functions in protocol_engine.py (safety-critical)
- [ ] Extract magic numbers to named constants in actuator_widget.py
- [ ] Move inline imports to module level (actuator_widget.py)
- [ ] Test GPIO HAL with physical FT232H hardware
- [ ] Test camera HAL with Allied Vision 1800 U-158c
- [ ] Test laser HAL with Arroyo Instruments controller
- [ ] Test actuator HAL with Xeryon linear stage
- [ ] Verify safety interlocks work correctly (motor + vibration + photodiode)
- [ ] Test complete session workflow (subject → session → treatment → completion)
- [ ] Implement ring detection using Hough circle transform
- [ ] Implement focus measurement using Laplacian variance
- [ ] Integrate video recording with session management
- [ ] Set up pytest testing framework
- [ ] Write unit tests for database models and managers
- [ ] Write unit tests for safety system
- [ ] Write integration tests for session lifecycle
- [ ] Create FMEA (Failure Mode and Effects Analysis) documentation

## Completed
