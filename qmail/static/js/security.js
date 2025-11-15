/**
 * QMail Security Features
 * - Screenshot prevention
 * - Copy/paste protection
 * - Screen recording detection
 * - Watermarking
 * - Forensic tracking
 */

class QMailSecurity {
    constructor(options = {}) {
        this.options = {
            preventScreenshot: true,
            preventCopy: true,
            preventPrint: true,
            enableWatermark: true,
            enableForensics: true,
            blurOnInactive: true,
            sessionTimeout: 30, // minutes
            ...options
        };
        
        this.isSecureContent = false;
        this.watermarkInterval = null;
        this.sessionTimer = null;
        this.lastActivity = Date.now();
        
        this.init();
    }
    
    init() {
        console.log('🔒 QMail Security initialized');
        
        if (this.options.preventScreenshot) {
            this.preventScreenshots();
        }
        
        if (this.options.preventCopy) {
            this.preventCopyPaste();
        }
        
        if (this.options.preventPrint) {
            this.preventPrinting();
        }
        
        if (this.options.blurOnInactive) {
            this.blurOnWindowInactive();
        }
        
        this.detectScreenRecording();
        this.trackUserActivity();
        this.setupSessionTimeout();
    }
    
    /**
     * Enable security for specific content
     */
    enableSecureMode(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        this.isSecureContent = true;
        element.classList.add('secure-content');
        
        // Add watermark
        if (this.options.enableWatermark) {
            this.addWatermark(element);
        }
        
        // Prevent context menu
        element.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.showSecurityAlert('Right-click is disabled for secure content');
        });
        
        // Prevent drag and drop
        element.addEventListener('dragstart', (e) => {
            e.preventDefault();
        });
        
        // Make content unselectable
        element.style.userSelect = 'none';
        element.style.webkitUserSelect = 'none';
        element.style.mozUserSelect = 'none';
        element.style.msUserSelect = 'none';
        
        console.log('🔐 Secure mode enabled for:', elementId);
    }
    
    /**
     * Disable security (when viewing non-encrypted content)
     */
    disableSecureMode(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        this.isSecureContent = false;
        element.classList.remove('secure-content');
        
        // Remove watermark
        this.removeWatermark(element);
        
        // Re-enable selection
        element.style.userSelect = '';
        element.style.webkitUserSelect = '';
        element.style.mozUserSelect = '';
        element.style.msUserSelect = '';
        
        console.log('🔓 Secure mode disabled for:', elementId);
    }
    
    /**
     * Screenshot Prevention
     * Uses multiple techniques to prevent screenshots
     */
    preventScreenshots() {
        // Method 1: Detect Print Screen key
        document.addEventListener('keyup', (e) => {
            if (e.key === 'PrintScreen' && this.isSecureContent) {
                navigator.clipboard.writeText('');
                this.showSecurityAlert('Screenshots are disabled for encrypted content');
                this.logSecurityEvent('screenshot_attempt', 'PrintScreen key detected');
            }
        });
        
        // Method 2: Detect common screenshot shortcuts
        document.addEventListener('keydown', (e) => {
            if (!this.isSecureContent) return;
            
            // Windows: Win+Shift+S, Win+PrtScn
            // Mac: Cmd+Shift+3, Cmd+Shift+4
            const isScreenshotShortcut = (
                (e.metaKey && e.shiftKey && (e.key === '3' || e.key === '4' || e.key === '5')) || // Mac
                (e.key === 'PrintScreen') || // Windows
                (e.metaKey && e.key === 'PrintScreen') // Windows Snipping Tool
            );
            
            if (isScreenshotShortcut) {
                e.preventDefault();
                this.showSecurityAlert('Screenshots are disabled for encrypted content');
                this.logSecurityEvent('screenshot_attempt', `Shortcut: ${e.key}`);
            }
        });
        
        // Method 3: Blur content when window loses focus (prevents screenshot tools)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isSecureContent) {
                this.blurSecureContent();
            } else {
                this.unblurSecureContent();
            }
        });
        
        // Method 4: Prevent browser screenshot extensions
        window.addEventListener('blur', () => {
            if (this.isSecureContent) {
                this.blurSecureContent();
            }
        });
        
        window.addEventListener('focus', () => {
            this.unblurSecureContent();
        });
    }
    
    /**
     * Copy/Paste Prevention
     */
    preventCopyPaste() {
        // Prevent copy
        document.addEventListener('copy', (e) => {
            if (this.isSecureContent) {
                e.preventDefault();
                e.clipboardData.setData('text/plain', '');
                this.showSecurityAlert('Copying is disabled for encrypted content');
                this.logSecurityEvent('copy_attempt', 'Copy blocked');
            }
        });
        
        // Prevent cut
        document.addEventListener('cut', (e) => {
            if (this.isSecureContent) {
                e.preventDefault();
                this.showSecurityAlert('Cutting is disabled for encrypted content');
                this.logSecurityEvent('cut_attempt', 'Cut blocked');
            }
        });
        
        // Prevent paste (optional - might be too restrictive)
        // document.addEventListener('paste', (e) => {
        //     if (this.isSecureContent) {
        //         e.preventDefault();
        //     }
        // });
        
        // Prevent Ctrl+C, Ctrl+X, Ctrl+A
        document.addEventListener('keydown', (e) => {
            if (!this.isSecureContent) return;
            
            if ((e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'x' || e.key === 'a')) {
                const target = e.target;
                const isSecureElement = target.closest('.secure-content');
                
                if (isSecureElement) {
                    e.preventDefault();
                    this.showSecurityAlert('This action is disabled for encrypted content');
                    this.logSecurityEvent('keyboard_shortcut_attempt', `Key: ${e.key}`);
                }
            }
        });
    }
    
    /**
     * Print Prevention
     */
    preventPrinting() {
        // Detect Ctrl+P
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'p' && this.isSecureContent) {
                e.preventDefault();
                this.showSecurityAlert('Printing is disabled for encrypted content');
                this.logSecurityEvent('print_attempt', 'Ctrl+P blocked');
            }
        });
        
        // Detect print dialog
        window.addEventListener('beforeprint', (e) => {
            if (this.isSecureContent) {
                e.preventDefault();
                this.hideSecureContent();
                this.showSecurityAlert('Printing is disabled for encrypted content');
                this.logSecurityEvent('print_attempt', 'Print dialog blocked');
            }
        });
        
        window.addEventListener('afterprint', () => {
            this.showSecureContent();
        });
    }
    
    /**
     * Screen Recording Detection
     */
    detectScreenRecording() {
        // Check for screen recording APIs
        if (navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
            const originalGetDisplayMedia = navigator.mediaDevices.getDisplayMedia;
            
            navigator.mediaDevices.getDisplayMedia = async function(...args) {
                console.warn('⚠️ Screen recording detected!');
                this.logSecurityEvent('screen_recording_detected', 'getDisplayMedia called');
                this.showSecurityAlert('Screen recording detected. Encrypted content will be hidden.');
                
                // Hide secure content during recording
                this.hideSecureContent();
                
                return originalGetDisplayMedia.apply(navigator.mediaDevices, args);
            }.bind(this);
        }
        
        // Monitor for recording indicators
        setInterval(() => {
            if (this.isSecureContent && this.isScreenBeingRecorded()) {
                this.hideSecureContent();
                this.showSecurityAlert('Screen recording detected. Content hidden for security.');
            }
        }, 5000);
    }
    
    /**
     * Check if screen is being recorded
     */
    isScreenBeingRecorded() {
        // Check for browser recording indicators
        // This is a heuristic and may not catch all recording methods
        return false; // Placeholder - browser APIs don't expose this reliably
    }
    
    /**
     * Watermarking
     */
    addWatermark(element) {
        if (!element) return;
        
        // Create watermark overlay
        const watermark = document.createElement('div');
        watermark.className = 'security-watermark';
        watermark.setAttribute('data-watermark', 'true');
        
        // Add user info and timestamp to watermark
        const userEmail = document.querySelector('[data-user-email]')?.dataset.userEmail || 'Unknown';
        const timestamp = new Date().toLocaleString();
        const sessionId = this.getSessionId();
        
        watermark.innerHTML = `
            <div class="watermark-text">
                ${userEmail} • ${timestamp} • Session: ${sessionId.substring(0, 8)}
            </div>
        `;
        
        element.style.position = 'relative';
        element.appendChild(watermark);
        
        // Rotate watermark position periodically (anti-screenshot measure)
        this.watermarkInterval = setInterval(() => {
            if (watermark.parentElement) {
                const angle = Math.random() * 360;
                const x = Math.random() * 80;
                const y = Math.random() * 80;
                watermark.style.transform = `translate(${x}%, ${y}%) rotate(${angle}deg)`;
            }
        }, 3000);
    }
    
    removeWatermark(element) {
        if (!element) return;
        
        const watermark = element.querySelector('[data-watermark="true"]');
        if (watermark) {
            watermark.remove();
        }
        
        if (this.watermarkInterval) {
            clearInterval(this.watermarkInterval);
            this.watermarkInterval = null;
        }
    }
    
    /**
     * Blur content when window is inactive
     */
    blurOnWindowInactive() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isSecureContent) {
                this.blurSecureContent();
            } else {
                setTimeout(() => this.unblurSecureContent(), 100);
            }
        });
    }
    
    blurSecureContent() {
        const secureElements = document.querySelectorAll('.secure-content');
        secureElements.forEach(el => {
            el.style.filter = 'blur(20px)';
            el.style.pointerEvents = 'none';
        });
    }
    
    unblurSecureContent() {
        const secureElements = document.querySelectorAll('.secure-content');
        secureElements.forEach(el => {
            el.style.filter = '';
            el.style.pointerEvents = '';
        });
    }
    
    hideSecureContent() {
        const secureElements = document.querySelectorAll('.secure-content');
        secureElements.forEach(el => {
            el.style.visibility = 'hidden';
        });
    }
    
    showSecureContent() {
        const secureElements = document.querySelectorAll('.secure-content');
        secureElements.forEach(el => {
            el.style.visibility = '';
        });
    }
    
    /**
     * Session Timeout
     */
    setupSessionTimeout() {
        // Reset timer on user activity
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, () => {
                this.lastActivity = Date.now();
            }, true);
        });
        
        // Check for inactivity
        this.sessionTimer = setInterval(() => {
            const inactiveTime = (Date.now() - this.lastActivity) / 1000 / 60; // minutes
            
            if (inactiveTime >= this.options.sessionTimeout) {
                this.handleSessionTimeout();
            } else if (inactiveTime >= this.options.sessionTimeout - 2) {
                // Warn 2 minutes before timeout
                this.showSecurityAlert(`Session will expire in ${Math.ceil(this.options.sessionTimeout - inactiveTime)} minutes due to inactivity`);
            }
        }, 60000); // Check every minute
    }
    
    handleSessionTimeout() {
        this.logSecurityEvent('session_timeout', 'User inactive');
        alert('Your session has expired due to inactivity. You will be logged out.');
        window.location.href = '/auth/logout';
    }
    
    /**
     * Track User Activity for Forensics
     */
    trackUserActivity() {
        if (!this.options.enableForensics) return;
        
        // Track when user views encrypted content
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.classList && node.classList.contains('secure-content')) {
                            this.logSecurityEvent('secure_content_viewed', 'Encrypted email opened');
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    /**
     * Log Security Events
     */
    logSecurityEvent(eventType, details) {
        const event = {
            type: eventType,
            details: details,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            sessionId: this.getSessionId(),
            url: window.location.href
        };
        
        console.warn('🚨 Security Event:', event);
        
        // Send to server for logging
        fetch('/api/security/log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(event)
        }).catch(err => console.error('Failed to log security event:', err));
    }
    
    /**
     * Show Security Alert
     */
    showSecurityAlert(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'security-toast';
        toast.innerHTML = `
            <i class="fas fa-shield-alt"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    /**
     * Get Session ID
     */
    getSessionId() {
        let sessionId = sessionStorage.getItem('qmail_session_id');
        if (!sessionId) {
            sessionId = this.generateSessionId();
            sessionStorage.setItem('qmail_session_id', sessionId);
        }
        return sessionId;
    }
    
    generateSessionId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    /**
     * Cleanup
     */
    destroy() {
        if (this.watermarkInterval) {
            clearInterval(this.watermarkInterval);
        }
        if (this.sessionTimer) {
            clearInterval(this.sessionTimer);
        }
        console.log('🔒 QMail Security destroyed');
    }
}

// Initialize security when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.qmailSecurity = new QMailSecurity({
        preventScreenshot: true,
        preventCopy: true,
        preventPrint: true,
        enableWatermark: true,
        enableForensics: true,
        blurOnInactive: true,
        sessionTimeout: 30
    });
});
