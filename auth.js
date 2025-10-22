// Warpeed Technologies - Stealth Mode Authentication System
// This system uses EmailJS for email verification (you'll need to set up an account)

const AUTH_CONFIG = {
    emailJsServiceId: 'service_2bdmaks', // EmailJS Service ID
    emailJsTemplateId: 'template_qd1we8t', // EmailJS Template ID
    emailJsPublicKey: 'Uoq5AonGyDGvl5kvE', // EmailJS Public Key
    sessionDuration: 24 * 60 * 60 * 1000, // 24 hours in milliseconds
    codeExpiration: 15 * 60 * 1000, // 15 minutes in milliseconds
    creatorMasterCode: 'WARPEED2025CREATOR', // Master code for creator access (change this!)
    creatorEmail: 'heinz@warpeed.space' // Creator email for bypass
};

// Global state
let currentUserData = {};
let generatedCode = '';
let codeTimestamp = 0;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Check if already authenticated
    if (isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }

    // Setup form handlers
    setupFormHandlers();
});

function setupFormHandlers() {
    const accessForm = document.getElementById('accessForm');
    const verificationForm = document.getElementById('verificationForm');

    if (accessForm) {
        accessForm.addEventListener('submit', handleAccessRequest);
    }

    if (verificationForm) {
        verificationForm.addEventListener('submit', handleVerification);
    }
}

async function handleAccessRequest(e) {
    e.preventDefault();

    const fullName = document.getElementById('fullName').value.trim();
    const email = document.getElementById('email').value.trim();
    const organization = document.getElementById('organization').value.trim();
    const ndaAccept = document.getElementById('ndaAccept').checked;

    // Validation
    if (!fullName || !email || !ndaAccept) {
        showMessage('Please fill in all required fields and accept the NDA.', 'error');
        return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showMessage('Please enter a valid email address.', 'error');
        return;
    }

    // CREATOR BYPASS: Check for master code
    if (organization === AUTH_CONFIG.creatorMasterCode || email === AUTH_CONFIG.creatorEmail) {
        const creatorData = {
            fullName: fullName || 'Creator',
            email: email || AUTH_CONFIG.creatorEmail,
            organization: 'Warpeed Technologies',
            ndaAccepted: true,
            ndaAcceptedTimestamp: new Date().toISOString(),
            isCreator: true
        };
        grantAccess(creatorData);
        return;
    }

    // Store user data
    currentUserData = {
        fullName,
        email,
        organization,
        ndaAccepted: true,
        ndaAcceptedTimestamp: new Date().toISOString()
    };

    // Generate verification code
    generatedCode = generateVerificationCode();
    codeTimestamp = Date.now();

    // Store in localStorage for demo purposes (replace with backend in production)
    localStorage.setItem('pendingUser', JSON.stringify(currentUserData));
    localStorage.setItem('verificationCode', generatedCode);
    localStorage.setItem('codeTimestamp', codeTimestamp.toString());

    // Show loading
    showLoading(true);

    // Send verification email
    try {
        await sendVerificationEmail(fullName, email, generatedCode);

        // Hide loading
        showLoading(false);

        // Show success message
        showMessage(`Verification code sent successfully to ${email}. Please check your inbox.`, 'success');

        // Show verification section
        document.getElementById('verificationSection').classList.add('active');
        document.getElementById('accessForm').style.display = 'none';

        // Focus on code input
        setTimeout(() => {
            document.getElementById('verificationCode').focus();
        }, 500);

    } catch (error) {
        showLoading(false);
        console.error('Error sending verification:', error);

        // For demo purposes, still show the verification section
        // In production, you'd handle this error properly
        showMessage('Demo Mode: Your verification code is: ' + generatedCode, 'success');
        document.getElementById('verificationSection').classList.add('active');
        document.getElementById('accessForm').style.display = 'none';
    }
}

async function handleVerification(e) {
    e.preventDefault();

    const enteredCode = document.getElementById('verificationCode').value.trim();
    const storedCode = localStorage.getItem('verificationCode');
    const storedTimestamp = parseInt(localStorage.getItem('codeTimestamp') || '0');

    // Check if code has expired
    if (Date.now() - storedTimestamp > AUTH_CONFIG.codeExpiration) {
        showMessage('Verification code has expired. Please request a new code.', 'error');
        resetForm();
        return;
    }

    // Verify code
    if (enteredCode === storedCode) {
        // Code is correct - grant access
        const userData = JSON.parse(localStorage.getItem('pendingUser') || '{}');
        grantAccess(userData);
    } else {
        showMessage('Invalid verification code. Please try again.', 'error');
        document.getElementById('verificationCode').value = '';
        document.getElementById('verificationCode').focus();
    }
}

function grantAccess(userData) {
    // Create session
    const session = {
        user: userData,
        authenticated: true,
        loginTimestamp: Date.now(),
        expiresAt: Date.now() + AUTH_CONFIG.sessionDuration
    };

    // Store session
    localStorage.setItem('warpeedSession', JSON.stringify(session));

    // Log access (in production, send this to your backend)
    logAccess(userData);

    // Clean up pending data
    localStorage.removeItem('pendingUser');
    localStorage.removeItem('verificationCode');
    localStorage.removeItem('codeTimestamp');

    // Show success and redirect
    showMessage('Access granted! Redirecting...', 'success');

    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1500);
}

function generateVerificationCode() {
    // Generate a random 6-digit code
    return Math.floor(100000 + Math.random() * 900000).toString();
}

async function sendVerificationEmail(name, email, code) {
    // Always log for debugging (check console in case of issues)
    console.log('=================================');
    console.log('SENDING VERIFICATION CODE');
    console.log('EMAIL:', email);
    console.log('NAME:', name);
    console.log('CODE:', code);
    console.log('=================================');

    // Check if EmailJS is configured
    const isConfigured = AUTH_CONFIG.emailJsServiceId !== 'YOUR_EMAILJS_SERVICE_ID' &&
                        AUTH_CONFIG.emailJsTemplateId !== 'YOUR_EMAILJS_TEMPLATE_ID' &&
                        AUTH_CONFIG.emailJsPublicKey !== 'YOUR_EMAILJS_PUBLIC_KEY';

    if (!isConfigured) {
        console.warn('⚠️ EmailJS not configured. Running in DEMO MODE.');
        console.log('📧 Demo verification code:', code);
        // Simulate async operation in demo mode
        return new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Production mode with EmailJS
    try {
        // Check if emailjs is available
        if (typeof emailjs === 'undefined') {
            console.error('❌ EmailJS SDK not loaded!');
            throw new Error('EmailJS SDK not loaded');
        }

        console.log('✓ EmailJS SDK loaded');
        console.log('Service ID:', AUTH_CONFIG.emailJsServiceId);
        console.log('Template ID:', AUTH_CONFIG.emailJsTemplateId);

        const templateParams = {
            to_name: name,
            to_email: email,
            verification_code: code,
            company_name: 'Warpeed Technologies'
        };

        console.log('Template params:', templateParams);
        console.log('Sending email via EmailJS...');

        const response = await emailjs.send(
            AUTH_CONFIG.emailJsServiceId,
            AUTH_CONFIG.emailJsTemplateId,
            templateParams
        );

        console.log('✅ Email sent successfully!');
        console.log('Response status:', response.status);
        console.log('Response text:', response.text);
        console.log('Full response:', response);

        return response;
    } catch (error) {
        console.error('❌ FAILED TO SEND EMAIL');
        console.error('Error type:', error.name);
        console.error('Error message:', error.message);
        console.error('Error details:', error.text || error);
        console.error('Full error object:', error);

        // Provide more specific error messages
        if (error.text) {
            throw new Error('EmailJS error: ' + error.text);
        } else {
            throw new Error('Failed to send verification email: ' + error.message);
        }
    }
}

function resendCode() {
    const userData = JSON.parse(localStorage.getItem('pendingUser') || '{}');

    if (!userData.email) {
        showMessage('Session expired. Please start again.', 'error');
        resetForm();
        return;
    }

    // Generate new code
    generatedCode = generateVerificationCode();
    codeTimestamp = Date.now();

    localStorage.setItem('verificationCode', generatedCode);
    localStorage.setItem('codeTimestamp', codeTimestamp.toString());

    showLoading(true);

    sendVerificationEmail(userData.fullName, userData.email, generatedCode)
        .then(() => {
            showLoading(false);
            showMessage('New verification code sent!', 'success');
        })
        .catch((error) => {
            showLoading(false);
            showMessage('Demo Mode: Your new verification code is: ' + generatedCode, 'success');
        });
}

function isAuthenticated() {
    const session = localStorage.getItem('warpeedSession');

    if (!session) return false;

    try {
        const sessionData = JSON.parse(session);

        // Check if session has expired
        if (sessionData.expiresAt < Date.now()) {
            // Session expired - clean up
            localStorage.removeItem('warpeedSession');
            return false;
        }

        return sessionData.authenticated === true;
    } catch (error) {
        return false;
    }
}

function logout() {
    localStorage.removeItem('warpeedSession');
    window.location.href = 'access.html';
}

function showMessage(message, type) {
    const container = document.getElementById('messageContainer');
    const className = type === 'error' ? 'error-message' : 'success-message';

    container.innerHTML = `<div class="${className}">${message}</div>`;

    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            container.innerHTML = '';
        }, 5000);
    }
}

function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    const submitBtn = document.getElementById('submitBtn');

    if (show) {
        spinner.classList.add('active');
        if (submitBtn) submitBtn.disabled = true;
    } else {
        spinner.classList.remove('active');
        if (submitBtn) submitBtn.disabled = false;
    }
}

function resetForm() {
    document.getElementById('verificationSection').classList.remove('active');
    document.getElementById('accessForm').style.display = 'block';
    document.getElementById('accessForm').reset();
    document.getElementById('messageContainer').innerHTML = '';
}

function showNDA() {
    document.getElementById('ndaModal').style.display = 'block';
}

function closeNDA() {
    document.getElementById('ndaModal').style.display = 'none';
}

function logAccess(userData) {
    // In production, send this to your backend
    const accessLog = {
        timestamp: new Date().toISOString(),
        user: userData,
        ip: 'client-side', // Get from backend
        userAgent: navigator.userAgent
    };

    console.log('Access Log:', accessLog);

    // You could send this to a backend endpoint:
    /*
    fetch('/api/log-access', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(accessLog)
    });
    */
}

// Export functions for use in other pages
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        isAuthenticated,
        logout
    };
}
