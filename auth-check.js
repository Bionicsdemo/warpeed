// Warpeed Technologies - Page Protection Script
// Include this script in the <head> of every protected page

(function() {
    'use strict';

    // Configuration
    const STEALTH_MODE_ENABLED = true; // Set to false to disable stealth mode
    const ACCESS_PAGE = 'access.html';

    // Check authentication immediately
    if (STEALTH_MODE_ENABLED && !isAuthenticated()) {
        // Redirect to access page
        window.location.href = ACCESS_PAGE;
        return;
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

    // Add logout functionality
    window.warpeedLogout = function() {
        if (confirm('Are you sure you want to log out?')) {
            localStorage.removeItem('warpeedSession');
            window.location.href = ACCESS_PAGE;
        }
    };

    // Add authentication info to page
    function displayAuthInfo() {
        const session = localStorage.getItem('warpeedSession');

        if (session) {
            try {
                const sessionData = JSON.parse(session);
                const userName = sessionData.user.fullName;

                // Create auth indicator
                const authIndicator = document.createElement('div');
                authIndicator.style.cssText = `
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: rgba(0, 0, 0, 0.8);
                    backdrop-filter: blur(10px);
                    color: white;
                    padding: 12px 20px;
                    border-radius: 30px;
                    font-size: 0.85rem;
                    z-index: 9999;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(102, 126, 234, 0.3);
                `;

                authIndicator.innerHTML = `
                    <span style="color: #00ff88;">●</span>
                    <span style="font-weight: 500;">${userName}</span>
                    <button onclick="warpeedLogout()" style="
                        background: rgba(255, 255, 255, 0.1);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        color: white;
                        padding: 4px 12px;
                        border-radius: 15px;
                        cursor: pointer;
                        font-size: 0.8rem;
                        margin-left: 8px;
                    ">Logout</button>
                `;

                document.body.appendChild(authIndicator);
            } catch (error) {
                console.error('Error displaying auth info:', error);
            }
        }
    }

    // Display auth info when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', displayAuthInfo);
    } else {
        displayAuthInfo();
    }

    // Session timeout warning
    function checkSessionExpiry() {
        const session = localStorage.getItem('warpeedSession');

        if (session) {
            try {
                const sessionData = JSON.parse(session);
                const timeRemaining = sessionData.expiresAt - Date.now();
                const fiveMinutes = 5 * 60 * 1000;

                // Warn if less than 5 minutes remaining
                if (timeRemaining > 0 && timeRemaining < fiveMinutes && !sessionStorage.getItem('expiryWarningShown')) {
                    sessionStorage.setItem('expiryWarningShown', 'true');

                    const minutes = Math.ceil(timeRemaining / 60000);

                    if (confirm(`Your session will expire in ${minutes} minute(s). Would you like to extend it?`)) {
                        // Extend session
                        sessionData.expiresAt = Date.now() + (24 * 60 * 60 * 1000);
                        localStorage.setItem('warpeedSession', JSON.stringify(sessionData));
                        sessionStorage.removeItem('expiryWarningShown');
                        alert('Session extended for 24 hours.');
                    }
                }
            } catch (error) {
                console.error('Error checking session expiry:', error);
            }
        }
    }

    // Check session expiry every minute
    setInterval(checkSessionExpiry, 60000);

})();
