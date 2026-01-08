# Tapo Login Flow Screenshots

## Screens
1. `01-welcome.png` - Initial welcome screen (Log In / Create Account)
2. `02-userid-input.png` - Email/User ID entry + Remember Me checkbox
3. `03-2fa-verification.png` - Two-step verification code entry

## Notes
- "Remember Me" checkbox ticked during login
- 2FA code sent to email AND other logged-in devices
- OTP appears in Tapo app on other authenticated devices

## Dual-Emulator Authentication Strategy
For maintaining persistent login, consider running two sandboxed Android emulators:
- Emulator A gets OTP from Emulator B (and vice versa)
- Allows re-authentication without external phone dependency
