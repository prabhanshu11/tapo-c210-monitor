# Login Flow - Tapo App

**Documented:** 2026-01-11
**Test Status:** Partially tested (password entry blocked by adb limitations)

## Overview
Complete login flow from fresh app install to authenticated home screen.

---

## Screen 1: Terms Acceptance

**Activity:** `com.tplink.iot/.view.welcome.StartupActivity`
**Resolution:** 720x1280 (physical pixels)

### Elements

| Element | Resource ID | Bounds | Type |
|---------|-------------|--------|------|
| UEIP Checkbox | `cb_ueip` | [24,650][120,746] | CheckBox |
| Privacy/ToU Checkbox | `cb_pp_tou` | [24,826][120,922] | CheckBox |
| Continue Button | `btn_agree` | [40,1006][680,1108] | Button |
| Disagree Button | `btn_disagree` | [40,1136][680,1232] | Button |

### Required Actions
1. Check UEIP checkbox: `adb shell input tap 72 698`
2. Check Privacy/ToU checkbox: `adb shell input tap 72 874`
3. Tap Continue: `adb shell input tap 360 1057`

**Note:** Continue button is disabled until both checkboxes are checked.

---

## Screen 2: Account Selection

**Activity:** `com.tplink.iot/.view.welcome.StartupActivity`

### Elements

| Element | Resource ID | Bounds | Action |
|---------|-------------|--------|--------|
| Create TP-Link ID | `btn_sign_up` | [40,862][680,958] | Opens signup flow |
| Log In | `btn_login` | [40,1006][680,1102] | Opens login form |

### Navigation
- To login: `adb shell input tap 360 1054`
- To signup: `adb shell input tap 360 910`

---

## Screen 3: Login Form

**Activity:** `com.tplink.iot/.view.login.LoginActivity`

### Form Elements

| Element | Resource ID | Bounds | Type |
|---------|-------------|--------|------|
| Email Field | `edit_text` (in `et_account_email`) | [112,292][568,407] | AutoCompleteTextView |
| Password Field | `edit_text` (in `et_account_password`) | [112,408][456,523] | AutoCompleteTextView (password=true) |
| Email Clear Button | `edit_text_clear` | [568,301][664,397] | ImageView |
| Password Clear Button | `edit_text_clear` | [456,417][552,513] | ImageView |
| Password Toggle | `edit_text_password_toggle` | [568,417][664,513] | Button (Show/Hide) |
| Remember Me | `cb_account_remember` | [24,563][303,659] | CheckBox |
| Log In Button | `refreshablebutton_Button` | [40,960][680,1056] | Button |
| Sign Up Link | `tv_sign_up` | [48,1116][150,1212] | Button |
| Forgot Password | `tv_login_forget` | [432,1116][672,1212] | Button |

### Tap Coordinates (Physical Pixels)

```bash
# Enter email
adb shell input tap 340 349
adb shell input text "your.email@example.com"

# Enter password
adb shell input tap 284 465
# ISSUE: adb input text doesn't handle special characters (^, ", etc.)
# Workaround: Type manually or use simple password

# Submit
adb shell input keyevent KEYCODE_ESCAPE  # hide keyboard
adb shell input tap 360 1008  # Log In button
```

### Login Button States

| State | Condition | Enabled |
|-------|-----------|---------|
| Disabled | Empty email or password | `enabled="false"` |
| Enabled | Both fields filled | `enabled="true"` |

---

## Known Issues

### ADB Input Limitations

**Problem:** `adb shell input text` mangles special characters in passwords:
- `^` becomes `\%5e` or `\^`
- `"` becomes `%22` or `&apos;`
- Commas may duplicate

**Impact:** Cannot automate login with complex passwords using adb.

**Workarounds:**
1. **Manual typing:** Focus password field, type on host keyboard via emulator window
2. **Simple password:** Use test account with alphanumeric-only password
3. **Clipboard:** `adb shell am broadcast -a clipper.set -e text "password"` (requires clipper app)
4. **Python UIAutomator:** Use `uiautomator2` library with `element.set_text()`

---

## Success Indicators

After successful login, activity changes to:
- `com.tplink.iot/.view.main.MainActivity` (Home screen)

Failed login will show:
- Error toast or banner (not yet documented)

---

## Testing Checklist

- [x] Terms acceptance screen identified
- [x] Checkboxes tap coordinates verified
- [x] Account selection screen identified
- [x] Login form elements documented
- [x] Email field accepts input
- [ ] Password field (blocked by adb limitation)
- [ ] Login button tap triggers auth request
- [ ] Successful login redirects to home
- [ ] Failed login shows error message

---

## Next Steps

1. Test login with simple password OR manual password entry
2. Document post-login flows (device pairing if no devices)
3. Document error states (wrong password, no connection, etc.)
4. Add login flow to `user-actions.md`
