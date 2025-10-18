# Warpeed Technologies - Stealth Mode Authentication System

## Overview

This stealth mode system protects all website content with email-based verification and NDA acceptance. It's designed to control access during the founding team formation phase.

## How It Works

1. **Access Request** (`access.html`) - Landing page with:
   - Warpeed branding and stealth mode notice
   - Email and name collection form
   - NDA acceptance requirement
   - Email verification code system

2. **Authentication** (`auth.js`) - Core logic:
   - Generates 6-digit verification codes
   - Sends codes via email (EmailJS integration)
   - Validates codes and creates 24-hour sessions
   - Logs all access attempts

3. **Page Protection** (`auth-check.js`) - Included in all pages:
   - Redirects unauthenticated users to `access.html`
   - Displays user info in bottom-right corner
   - Provides logout functionality
   - Warns before session expiration

## Current Status

### ✅ Fully Implemented

- Complete UI/UX for access request
- Form validation and security checks
- Session management (24-hour duration)
- NDA acceptance modal
- Page protection on all HTML files
- Logout functionality
- Session expiry warnings

### ⚠️ Demo Mode (Needs Production Setup)

The system currently runs in **DEMO MODE** where:
- Verification codes are logged to console
- No actual emails are sent
- Everything else works as production

## Production Setup - Email Integration

To enable email sending, you need to set up **EmailJS** (free for up to 200 emails/month):

### Step 1: Create EmailJS Account

1. Go to https://www.emailjs.com/
2. Sign up for a free account
3. Verify your email

### Step 2: Add Email Service

1. Go to **Email Services** in EmailJS dashboard
2. Click **Add New Service**
3. Choose your email provider (Gmail, Outlook, SendGrid, etc.)
4. Follow the setup wizard
5. Note your **Service ID** (e.g., `service_abc123`)

### Step 3: Create Email Template

1. Go to **Email Templates**
2. Click **Create New Template**
3. Use this template:

```
Subject: Your Warpeed Access Code: {{verification_code}}

Hello {{to_name}},

Thank you for your interest in Warpeed Technologies.

Your verification code is: {{verification_code}}

This code will expire in 15 minutes.

If you did not request this code, please ignore this email.

Best regards,
Warpeed Technologies Team
https://warpeed.space

---
This is an automated message. Please do not reply directly to this email.
```

4. Note your **Template ID** (e.g., `template_xyz789`)

### Step 4: Get Public Key

1. Go to **Account** → **API Keys**
2. Copy your **Public Key** (e.g., `user_abc123def456`)

### Step 5: Update Configuration

Edit `auth.js` and update these lines (around line 5):

```javascript
const AUTH_CONFIG = {
    emailJsServiceId: 'service_abc123',      // Your Service ID from Step 2
    emailJsTemplateId: 'template_xyz789',     // Your Template ID from Step 3
    emailJsPublicKey: 'user_abc123def456',    // Your Public Key from Step 4
    sessionDuration: 24 * 60 * 60 * 1000,
    codeExpiration: 15 * 60 * 1000
};
```

### Step 6: Add EmailJS SDK

Add this script tag to `access.html` before the closing `</body>` tag:

```html
<script src="https://cdn.jsdelivr.net/npm/@emailjs/browser@3/dist/email.min.js"></script>
<script src="auth.js"></script>
```

### Step 7: Uncomment Production Code

In `auth.js`, find the `sendVerificationEmail()` function (around line 130) and:
1. **Comment out** the demo console.log code
2. **Uncomment** the EmailJS integration code

### Step 8: Test

1. Open `access.html` in your browser
2. Fill in the form with a real email address
3. Check your inbox for the verification code
4. Enter the code and verify access works

## Disable Stealth Mode

To disable the stealth mode system temporarily:

Edit `auth-check.js` line 8:
```javascript
const STEALTH_MODE_ENABLED = false; // Changed from true
```

## Access Logs

### Current Implementation (Client-Side Only)

Access logs are currently logged to the browser console. In the `auth.js` file, the `logAccess()` function logs:
- Timestamp
- User name and email
- Browser user agent
- NDA acceptance timestamp

### Production Recommendation

For production, you should send access logs to a backend:

```javascript
function logAccess(userData) {
    const accessLog = {
        timestamp: new Date().toISOString(),
        user: userData,
        ip: 'server-side',
        userAgent: navigator.userAgent
    };

    // Send to your backend
    fetch('https://your-backend.com/api/log-access', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(accessLog)
    });
}
```

## Security Considerations

### Current Security

✅ **Implemented:**
- Client-side session management
- Email verification
- NDA acceptance tracking
- Session expiration
- Logout functionality

⚠️ **Limitations:**
- LocalStorage can be cleared by user
- No server-side validation
- Codes stored in localStorage
- No rate limiting

### Production Recommendations

For maximum security, consider adding:

1. **Backend API** for:
   - Code generation and validation
   - Session management
   - Access logging
   - Rate limiting

2. **Database** to store:
   - Authorized users
   - Access logs
   - NDA acceptance records

3. **Additional Security:**
   - IP-based rate limiting
   - CAPTCHA on access form
   - Two-factor authentication
   - Server-side session validation

## Files Overview

```
website/
├── access.html              # Landing page (entry point)
├── auth.js                  # Authentication logic
├── auth-check.js            # Page protection script
├── index.html               # Protected main page
├── spectrix.html            # Protected page
├── research.html            # Protected page
├── publications.html        # Protected page
├── laser.html               # Protected page
├── material.html            # Protected page
├── team.html                # Protected page
├── animations.html          # Protected page
└── mission.html             # Protected page
```

## User Flow

```
1. User visits index.html (or any page)
   ↓
2. auth-check.js runs → No valid session found
   ↓
3. Redirect to access.html
   ↓
4. User fills form and accepts NDA
   ↓
5. Verification code sent to email
   ↓
6. User enters code
   ↓
7. Code validated → Session created
   ↓
8. Redirect to index.html
   ↓
9. auth-check.js runs → Valid session found
   ↓
10. Page loads normally
    ↓
11. User indicator shown in bottom-right
    ↓
12. User can browse all protected pages
```

## Session Management

- **Duration:** 24 hours from login
- **Storage:** LocalStorage (`warpeedSession`)
- **Expiry Warning:** 5 minutes before expiration
- **Extension:** User can extend session when warned
- **Logout:** Manual logout clears session

## NDA Terms

The NDA covers:
- Quantum optimization algorithms
- Lightsail material specifications
- Laser system designs
- Mission parameters
- Business strategies
- Research findings
- Technical documentation

**Duration:** 5 years from acceptance
**Jurisdiction:** California, United States

## Support

For issues or questions:
- **Email:** heinz@warpeed.space
- **Technical Support:** Check console logs for errors
- **EmailJS Issues:** https://www.emailjs.com/docs/

## License

© 2025 Warpeed Technologies Inc. All Rights Reserved.
