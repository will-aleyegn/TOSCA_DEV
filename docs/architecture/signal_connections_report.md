# PyQt6 Signal/Slot Connection Analysis Report

**Total Connections:** 187
**Files Analyzed:** 27

## Connection Types

- **direct**: 169 connections
- **lambda**: 18 connections

## Connections by File

### hardware_test_dialog.py
*File: `src\ui\dialogs\hardware_test_dialog.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 94 | `button_box.rejected` | `self.reject` | direct |

### research_mode_warning_dialog.py
*File: `src\ui\dialogs\research_mode_warning_dialog.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 110 | `self.acknowledge_checkbox.stateChanged` | `self._on_checkbox_changed` | direct |
| 118 | `self.cancel_button.clicked` | `self.reject` | direct |
| 129 | `self.ok_button.clicked` | `self.accept` | direct |

### main_window.py
*File: `src\ui\main_window.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 158 | `self.camera_controller.connection_changed` | `lambda.lambda` | lambda |
| 161 | `self.actuator_controller.connection_changed` | `lambda.lambda` | lambda |
| 372 | `self.subject_widget.session_started` | `self._on_session_started` | direct |
| 431 | `self.treatment_setup_widget.ready_button.clicked` | `self._on_start_treatment` | direct |
| 435 | `self.dev_mode_changed` | `self.camera_live_view.set_dev_mode` | direct |
| 436 | `self.dev_mode_changed` | `self.treatment_setup_widget.set_dev_mode` | direct |
| 462 | `self.line_protocol_builder.protocol_ready` | `self._on_line_protocol_ready` | direct |
| 502 | `exit_action.triggered` | `self.close` | direct |
| 514 | `self.dev_mode_action.triggered` | `self._on_dev_mode_changed_menubar` | direct |
| 533 | `self.global_estop_btn.clicked` | `self._on_global_estop_clicked` | direct |
| 547 | `self.connect_all_btn.clicked` | `self._on_connect_all_clicked` | direct |
| 555 | `self.disconnect_all_btn.clicked` | `self._on_disconnect_all_clicked` | direct |
| 569 | `self.test_all_btn.clicked` | `self._on_test_all_clicked` | direct |
| 579 | `self.pause_protocol_btn.clicked` | `self._on_pause_protocol_clicked` | direct |
| 587 | `self.resume_protocol_btn.clicked` | `self._on_resume_protocol_clicked` | direct |
| 652 | `self.safety_manager.safety_state_changed` | `self._update_master_safety_indicator` | direct |
| 816 | `gpio_widget.gpio_connection_changed` | `self._on_gpio_connection_changed` | direct |
| 826 | `self.safety_manager.safety_state_changed` | `lambda.lambda` | lambda |
| 829 | `self.safety_manager.laser_enable_changed` | `lambda.lambda` | lambda |
| 832 | `self.safety_manager.safety_event` | `lambda.lambda` | lambda |
| 910 | `gpio_widget.controller.safety_interlock_changed` | `self.safety_manager.set_gpio_interlock_status` | direct |
| 930 | `self.safety_watchdog.heartbeat_failed` | `lambda.lambda` | lambda |
| 933 | `self.safety_watchdog.watchdog_timeout_detected` | `self._handle_watchdog_timeout` | direct |
| 1002 | `self.session_manager.session_started` | `self._on_event_logger_session_started` | direct |
| 1003 | `self.session_manager.session_ended` | `self._on_event_logger_session_ended` | direct |
| 1007 | `self.event_logger.event_logged` | `lambda.lambda` | lambda |
| 1122 | `worker.signals.finished` | `self._on_protocol_execution_finished` | direct |
| 1123 | `worker.signals.error` | `self._on_protocol_execution_error` | direct |

### active_treatment_widget.py
*File: `src\ui\widgets\active_treatment_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 240 | `self.stop_button.clicked` | `self._on_stop_treatment` | direct |
| 259 | `camera_live_view.pixmap_ready` | `self._on_camera_frame_ready` | direct |

### actuator_connection_widget.py
*File: `src\ui\widgets\actuator_connection_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 155 | `self.refresh_btn.clicked` | `self._on_refresh_clicked` | direct |
| 174 | `self.connect_btn.clicked` | `self._on_connect_clicked` | direct |
| 181 | `self.disconnect_btn.clicked` | `self._on_disconnect_clicked` | direct |
| 195 | `self.home_btn.clicked` | `self._on_home_clicked` | direct |
| 206 | `self.query_settings_btn.clicked` | `self._on_query_settings_clicked` | direct |
| 255 | `self.controller.connection_changed` | `self._on_connection_changed` | direct |
| 256 | `self.controller.homing_progress` | `self._on_homing_progress` | direct |
| 257 | `self.controller.status_changed` | `self._on_status_changed` | direct |
| 258 | `self.controller.position_changed` | `self._on_position_changed` | direct |
| 259 | `self.controller.limits_changed` | `self._on_limits_changed` | direct |
| 300 | `self.controller` | `global.selected_port` | direct |

### camera_hardware_panel.py
*File: `src\ui\widgets\camera_hardware_panel.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 70 | `self.connect_btn.clicked` | `self._on_connect_clicked` | direct |
| 77 | `self.disconnect_btn.clicked` | `self._on_disconnect_clicked` | direct |

### camera_widget.py
*File: `src\ui\widgets\camera_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 77 | `self.camera_controller.pixmap_ready` | `self._on_pixmap_received` | direct |
| 78 | `self.camera_controller.fps_update` | `self._on_fps_update` | direct |
| 79 | `self.camera_controller.connection_changed` | `self._on_connection_changed` | direct |
| 80 | `self.camera_controller.error_occurred` | `self._on_error` | direct |
| 81 | `self.camera_controller.recording_status_changed` | `self._on_recording_status_changed` | direct |
| 83 | `self.camera_controller.exposure_changed` | `self._on_exposure_hardware_changed` | direct |
| 84 | `self.camera_controller.gain_changed` | `self._on_gain_hardware_changed` | direct |
| 256 | `self.connect_btn.clicked` | `self._on_connect_clicked` | direct |
| 261 | `self.stream_btn.clicked` | `self._on_stream_clicked` | direct |
| 277 | `self.auto_exposure_check.stateChanged` | `self._on_auto_exposure_changed` | direct |
| 291 | `self.allow_long_exposure_check.stateChanged` | `self._on_allow_long_exposure_changed` | direct |
| 299 | `self.exposure_slider.valueChanged` | `self._on_exposure_changed` | direct |
| 309 | `self.exposure_input.returnPressed` | `self._on_exposure_input_changed` | direct |
| 327 | `self.auto_gain_check.stateChanged` | `self._on_auto_gain_changed` | direct |
| 337 | `self.gain_slider.valueChanged` | `self._on_gain_changed` | direct |
| 347 | `self.gain_input.returnPressed` | `self._on_gain_input_changed` | direct |
| 357 | `self.auto_wb_check.stateChanged` | `self._on_auto_wb_changed` | direct |
| 380 | `self.scale_combo.currentIndexChanged` | `self._on_scale_changed` | direct |
| 412 | `self.image_path_browse_btn.clicked` | `self._on_browse_image_path` | direct |
| 422 | `self.capture_btn.clicked` | `self._on_capture_image` | direct |
| 457 | `self.video_path_browse_btn.clicked` | `self._on_browse_video_path` | direct |
| 467 | `self.record_btn.clicked` | `self._on_record_clicked` | direct |

### config_display_widget.py
*File: `src\ui\widgets\config_display_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 101 | `self.open_btn.clicked` | `self._open_config_file` | direct |

### gpio_widget.py
*File: `src\ui\widgets\gpio_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 71 | `self.controller.connection_changed` | `self._on_connection_changed` | direct |
| 72 | `self.controller.smoothing_motor_changed` | `self._on_motor_changed` | direct |
| 73 | `self.controller.smoothing_vibration_changed` | `self._on_vibration_changed` | direct |
| 74 | `self.controller.vibration_level_changed` | `self._on_vibration_level_changed` | direct |
| 75 | `self.controller.photodiode_voltage_changed` | `self._on_voltage_changed` | direct |
| 76 | `self.controller.photodiode_power_changed` | `self._on_power_changed` | direct |
| 77 | `self.controller.safety_interlock_changed` | `self._on_safety_changed` | direct |
| 78 | `self.controller.error_occurred` | `self._on_error` | direct |
| 195 | `self.refresh_btn.clicked` | `self._on_refresh_clicked` | direct |
| 223 | `self.connect_btn.clicked` | `self._on_connect_clicked` | direct |
| 228 | `self.disconnect_btn.clicked` | `self._on_disconnect_clicked` | direct |
| 252 | `self.motor_enable_btn.clicked` | `lambda.lambda` | lambda |
| 257 | `self.motor_disable_btn.clicked` | `lambda.lambda` | lambda |
| 282 | `self.voltage_spinbox.valueChanged` | `self._on_voltage_set` | direct |
| 287 | `self.apply_voltage_btn.clicked` | `self._on_apply_voltage_clicked` | direct |
| 320 | `self.accel_reinit_btn.clicked` | `self._on_accel_reinit_clicked` | direct |

### interlocks_widget.py
*File: `src\ui\widgets\interlocks_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 130 | `safety_manager.safety_state_changed` | `self._on_safety_state_changed` | direct |
| 131 | `safety_manager.laser_enable_changed` | `self._on_laser_enable_changed` | direct |
| 132 | `safety_manager.safety_event` | `self._on_safety_event` | direct |

### laser_widget.py
*File: `src\ui\widgets\laser_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 62 | `self.controller.connection_changed` | `self._on_connection_changed` | direct |
| 63 | `self.controller.output_changed` | `self._on_output_changed` | direct |
| 64 | `self.controller.current_changed` | `self._on_current_changed_signal` | direct |
| 65 | `self.controller.error_occurred` | `self._on_error` | direct |
| 103 | `self.connect_btn.clicked` | `self._on_connect_clicked` | direct |
| 108 | `self.disconnect_btn.clicked` | `self._on_disconnect_clicked` | direct |
| 153 | `self.current_spinbox.valueChanged` | `self._on_current_changed` | direct |
| 165 | `self.current_spinbox.valueChanged` | `lambda.lambda` | lambda |
| 168 | `self.current_slider.valueChanged` | `self.current_spinbox.setValue` | direct |
| 178 | `self.enable_btn.clicked` | `lambda.lambda` | lambda |
| 187 | `self.disable_btn.clicked` | `lambda.lambda` | lambda |
| 205 | `self.aiming_laser_on_btn.clicked` | `lambda.lambda` | lambda |
| 213 | `self.aiming_laser_off_btn.clicked` | `lambda.lambda` | lambda |
| 278 | `self.controller` | `unknown.'COM10'` | direct |
| 393 | `gpio_controller.aiming_laser_changed` | `self._on_aiming_laser_changed` | direct |

### line_protocol_builder.py
*File: `src\ui\widgets\line_protocol_builder.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 127 | `self.protocol_name_input.textChanged` | `self._on_metadata_changed` | direct |
| 136 | `self.loop_count_spin.valueChanged` | `self._on_metadata_changed` | direct |
| 166 | `self.sequence_list.currentRowChanged` | `self._on_line_selected` | direct |
| 173 | `self.add_line_btn.clicked` | `self._on_add_line` | direct |
| 177 | `self.remove_line_btn.clicked` | `self._on_remove_line` | direct |
| 182 | `self.move_up_btn.clicked` | `self._on_move_line_up` | direct |
| 187 | `self.move_down_btn.clicked` | `self._on_move_line_down` | direct |
| 223 | `self.notes_input.textChanged` | `self._on_line_params_changed` | direct |
| 232 | `self.apply_changes_btn.clicked` | `self._on_apply_changes` | direct |
| 255 | `self.movement_enable_check.toggled` | `self._on_movement_enable_toggled` | direct |
| 266 | `self.move_position_radio.toggled` | `self._on_movement_type_changed` | direct |
| 270 | `self.move_home_radio.toggled` | `self._on_movement_type_changed` | direct |
| 288 | `self.target_position_spin.valueChanged` | `self._on_line_params_changed` | direct |
| 301 | `self.move_speed_spin.valueChanged` | `self._on_line_params_changed` | direct |
| 311 | `self.move_type_combo.currentIndexChanged` | `self._on_line_params_changed` | direct |
| 331 | `self.home_speed_spin.valueChanged` | `self._on_line_params_changed` | direct |
| 352 | `self.laser_enable_check.toggled` | `self._on_laser_enable_toggled` | direct |
| 363 | `self.laser_set_radio.toggled` | `self._on_laser_type_changed` | direct |
| 367 | `self.laser_ramp_radio.toggled` | `self._on_laser_type_changed` | direct |
| 384 | `self.laser_set_power_spin.valueChanged` | `self._on_line_params_changed` | direct |
| 404 | `self.laser_start_power_spin.valueChanged` | `self._on_line_params_changed` | direct |
| 416 | `self.laser_end_power_spin.valueChanged` | `self._on_line_params_changed` | direct |
| 429 | `self.laser_ramp_duration_spin.valueChanged` | `self._on_line_params_changed` | direct |
| 450 | `self.dwell_enable_check.toggled` | `self._on_dwell_enable_toggled` | direct |
| 464 | `self.dwell_duration_spin.valueChanged` | `self._on_line_params_changed` | direct |
| 477 | `self.new_protocol_btn.clicked` | `self._on_new_protocol` | direct |
| 481 | `self.save_protocol_btn.clicked` | `self._on_save_protocol` | direct |
| 485 | `self.load_protocol_btn.clicked` | `self._on_load_protocol` | direct |
| 494 | `self.execute_protocol_btn.clicked` | `self._on_execute_protocol` | direct |

### performance_dashboard_widget.py
*File: `src\ui\widgets\performance_dashboard_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 185 | `self.vacuum_button.clicked` | `self._on_vacuum_clicked` | direct |
| 190 | `refresh_button.clicked` | `self.update_metrics` | direct |
| 214 | `self.refresh_timer.timeout` | `self.update_metrics` | direct |
| 387 | `worker.signals.finished` | `self._on_vacuum_finished` | direct |
| 388 | `worker.signals.error` | `self._on_vacuum_error` | direct |

### protocol_builder_widget.py
*File: `src\ui\widgets\protocol_builder_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 143 | `self.action_type_combo.currentIndexChanged` | `self._on_action_type_changed` | direct |
| 267 | `self.add_action_btn.clicked` | `self._on_add_action` | direct |
| 293 | `self.move_up_btn.clicked` | `self._on_move_up` | direct |
| 297 | `self.move_down_btn.clicked` | `self._on_move_down` | direct |
| 302 | `self.remove_btn.clicked` | `self._on_remove_action` | direct |
| 306 | `self.clear_btn.clicked` | `self._on_clear_all` | direct |
| 329 | `self.save_btn.clicked` | `self._on_save_protocol` | direct |
| 334 | `self.load_btn.clicked` | `self._on_load_protocol` | direct |
| 339 | `self.validate_btn.clicked` | `self._on_validate_protocol` | direct |
| 351 | `self.play_btn.clicked` | `self._on_play_protocol` | direct |

### protocol_selector_widget.py
*File: `src\ui\widgets\protocol_selector_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 76 | `self.protocol_list.itemSelectionChanged` | `self._on_selection_changed` | direct |
| 77 | `self.protocol_list.itemDoubleClicked` | `self._on_list_double_click` | direct |
| 82 | `refresh_btn.clicked` | `self._scan_protocols` | direct |
| 114 | `self.load_btn.clicked` | `self._on_load_selected` | direct |
| 120 | `browse_btn.clicked` | `self._on_browse_clicked` | direct |

### safety_widget.py
*File: `src\ui\widgets\safety_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 114 | `self.refresh_button.clicked` | `self._load_database_events` | direct |
| 170 | `safety_manager.safety_state_changed` | `self._on_safety_state_changed` | direct |
| 171 | `safety_manager.laser_enable_changed` | `self._on_laser_enable_changed` | direct |
| 172 | `safety_manager.safety_event` | `self._on_safety_event` | direct |
| 175 | `self.estop_button.clicked` | `self._on_estop_clicked` | direct |

### smoothing_status_widget.py
*File: `src\ui\widgets\smoothing_status_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 64 | `self.enable_btn.clicked` | `lambda.lambda` | lambda |
| 73 | `self.disable_btn.clicked` | `lambda.lambda` | lambda |
| 93 | `self.voltage_spinbox.valueChanged` | `self._on_voltage_changed` | direct |
| 99 | `self.apply_btn.clicked` | `self._on_apply_voltage` | direct |
| 135 | `controller.connection_changed` | `self._on_connection_changed` | direct |
| 136 | `controller.smoothing_motor_changed` | `self._on_motor_changed` | direct |
| 137 | `controller.vibration_level_changed` | `self._on_vibration_level_changed` | direct |
| 138 | `controller.photodiode_power_changed` | `self._on_power_changed` | direct |

### subject_widget.py
*File: `src\ui\widgets\subject_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 98 | `self.search_button.clicked` | `self._on_search_subject` | direct |
| 102 | `self.create_button.clicked` | `self._on_create_subject` | direct |
| 106 | `self.view_sessions_button.clicked` | `self._on_view_sessions` | direct |
| 146 | `self.start_session_button.clicked` | `self._on_start_session` | direct |
| 155 | `self.end_session_button.clicked` | `self._on_end_session` | direct |

### tec_widget.py
*File: `src\ui\widgets\tec_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 57 | `self.controller.connection_changed` | `self._on_connection_changed` | direct |
| 58 | `self.controller.output_changed` | `self._on_output_changed` | direct |
| 59 | `self.controller.temperature_changed` | `self._on_temperature_changed` | direct |
| 60 | `self.controller.temperature_setpoint_changed` | `self._on_setpoint_changed` | direct |
| 61 | `self.controller.current_changed` | `self._on_current_changed` | direct |
| 62 | `self.controller.voltage_changed` | `self._on_voltage_changed` | direct |
| 63 | `self.controller.error_occurred` | `self._on_error` | direct |
| 64 | `self.controller.limit_warning` | `self._on_limit_warning` | direct |
| 98 | `self.connect_btn.clicked` | `self._on_connect_clicked` | direct |
| 103 | `self.disconnect_btn.clicked` | `self._on_disconnect_clicked` | direct |
| 171 | `self.set_temp_btn.clicked` | `self._on_set_temperature` | direct |
| 186 | `self.enable_btn.clicked` | `lambda.lambda` | lambda |
| 195 | `self.disable_btn.clicked` | `lambda.lambda` | lambda |
| 257 | `self.controller` | `unknown.'COM9'` | direct |

### treatment_setup_widget.py
*File: `src\ui\widgets\treatment_setup_widget.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 104 | `self.protocol_btn.clicked` | `self._on_load_protocol_clicked` | direct |

### view_sessions_dialog.py
*File: `src\ui\widgets\view_sessions_dialog.py`*

| Line | Signal | Slot | Type |
|------|--------|------|------|
| 98 | `self.close_button.clicked` | `self.accept` | direct |
