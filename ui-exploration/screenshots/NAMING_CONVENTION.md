# Screenshot Naming Convention

## Format
```
tapo-app_<activity>_<screen-description>_<state>_worker-N.png
```

## Documented Screens

### Home Screen
```
tapo-app_main-activity_home-dashboard_favorites-tab-selected_worker-1.png
tapo-app_main-activity_home-dashboard_all-devices-tab-selected_worker-1.png
tapo-app_main-activity_home-dashboard_bedroom-room-tab-selected_worker-1.png
```

### Camera Live Screen
```
tapo-app_video-play-activity_camera-live-streaming_privacy-off-alarm-off_worker-1.png
tapo-app_video-play-activity_camera-live-streaming_privacy-on-alarm-off_worker-1.png
tapo-app_video-play-activity_camera-live-streaming_recording-active_worker-1.png
tapo-app_video-play-activity_camera-live-fullscreen_landscape-mode_worker-1.png
```

## Discovered Screens (Pending Documentation)

### From Home Screen Actions
```
tapo-app_main-activity_device-options-menu_long-press-camera-card_worker-1.png
tapo-app_notifications-activity_notifications-list_unread-messages_worker-1.png
tapo-app_add-device-activity_add-device-wizard_step-1-select-type_worker-1.png
tapo-app_main-activity_family-picker-dialog_home-selection_worker-1.png
tapo-app_main-activity_room-management-sheet_room-list-expanded_worker-1.png
```

### Bottom Navigation Tabs
```
tapo-app_cameras-tab-activity_cameras-list_all-cameras-view_worker-1.png
tapo-app_vacuums-tab-activity_vacuums-list_no-devices_worker-1.png
tapo-app_smart-tab-activity_smart-actions_automation-list_worker-1.png
tapo-app_me-tab-activity_user-profile_account-settings_worker-1.png
```

### Camera Live Sub-screens
```
tapo-app_video-play-activity_pan-tilt-controls_joystick-overlay_worker-1.png
tapo-app_video-play-activity_multi-view-grid_two-cameras_worker-1.png
tapo-app_video-play-activity_video-mode-picker_day-night-auto-options_worker-1.png
tapo-app_video-play-activity_volume-control-slider_mic-adjustment_worker-1.png
tapo-app_voice-call-activity_two-way-audio_call-active_worker-1.png
tapo-app_tapo-care-activity_cloud-subscription_plan-options_worker-1.png
tapo-app_playback-activity_recording-timeline_date-picker-visible_worker-1.png
```

### Device Settings
```
tapo-app_device-settings-activity_camera-settings_main-menu_worker-1.png
tapo-app_device-settings-activity_camera-settings_detection-sensitivity_worker-1.png
tapo-app_device-settings-activity_camera-settings_notification-preferences_worker-1.png
tapo-app_device-settings-activity_camera-settings_device-info_worker-1.png
tapo-app_device-settings-activity_camera-settings_privacy-schedule_worker-1.png
```

## State Suffixes

| State | Suffix Example |
|-------|---------------|
| Default/Initial | `_default` |
| Loading | `_loading-spinner` |
| Error | `_error-state` |
| Empty | `_empty-no-devices` |
| Toggle On | `_privacy-on` |
| Toggle Off | `_alarm-off` |
| Dialog Open | `_confirmation-dialog` |
| Menu Expanded | `_overflow-menu-open` |

## Capture Command Template
```bash
adb -s emulator-555X exec-out screencap -p | convert - -resize 'x1900>' \
  ui-exploration/screenshots/tapo-app_<activity>_<screen>_<state>_worker-N.png
```
