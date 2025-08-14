/**
 * Popup Script - Handles authentication and stats display
 */

// DOM elements
let loginSection, mainContent, loading;
let loginForm, emailInput, passwordInput, loginBtn;
let userEmail, logoutBtn;
let totalWordsEl, dueWordsEl, accuracyEl, streakEl;
let openAppBtn, refreshStatsBtn;
let successMessage, errorMessage;
let recentActivity, recentWords;

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
    //console.log('🚀 WordMaster popup loaded');
    
    // Get DOM elements
    initializeElements();
    
    // Set up event listeners
    setupEventListeners();
    
    // Check authentication status
    await checkAuthenticationStatus();
});

// Initialize DOM elements
function initializeElements() {
    loginSection = document.getElementById('loginSection');
    mainContent = document.getElementById('mainContent');
    loading = document.getElementById('loading');
    
    loginForm = document.getElementById('loginForm');
    emailInput = document.getElementById('email');
    passwordInput = document.getElementById('password');
    loginBtn = document.getElementById('loginBtn');
    
    userEmail = document.getElementById('userEmail');
    logoutBtn = document.getElementById('logoutBtn');
    
    totalWordsEl = document.getElementById('totalWords');
    dueWordsEl = document.getElementById('dueWords');
    accuracyEl = document.getElementById('accuracy');
    streakEl = document.getElementById('streak');
    
    openAppBtn = document.getElementById('openAppBtn');
    refreshStatsBtn = document.getElementById('refreshStatsBtn');
    
    successMessage = document.getElementById('successMessage');
    errorMessage = document.getElementById('errorMessage');
    
    recentActivity = document.getElementById('recentActivity');
    recentWords = document.getElementById('recentWords');
}

// Set up event listeners
function setupEventListeners() {
    // Login form
    loginForm.addEventListener('submit', handleLogin);
    
    // Logout button
    logoutBtn.addEventListener('click', handleLogout);
    
    // Open web app button
    openAppBtn.addEventListener('click', () => {
        chrome.tabs.create({ url: 'https://word-master-nu.vercel.app/' } ); // Update with your web app URL
    });
    
    // Refresh stats button
    refreshStatsBtn.addEventListener('click', loadUserStats);

    // Auto-focus email input when login section is visible
//     const observer = new MutationObserver((mutations) => {
//         mutations.forEach((mutation) => {
//             if (mutation.target === loginSection && loginSection.style.display !== 'none') {
//                 setTimeout(() => emailInput.focus(), 1000);
//             }
//         });
//     });
//     observer.observe(loginSection, { attributes: true, attributeFilter: ['style'] });
}

// Check authentication status
async function checkAuthenticationStatus() {
    showLoading(true);
    
    try {
        const response = await sendMessageToBackground('checkAuth');
        
        if (response.success && response.authenticated) {
            // User is authenticated
            showMainContent(response.user);
            await loadUserStats();
        } else {
            // User needs to login
            showLoginSection();
        }
    } catch (error) {
        console.error('❌ Auth check error:', error);
        showLoginSection();
        showError('Failed to check authentication status');
    } finally {
        showLoading(false);
    }
}

// Handle login form submission
async function handleLogin(e) {
    
    e.preventDefault();
    
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    
    if (!email || !password) {
        showError('Please enter both email and password');
        return;
    }
    
    // Show loading state
    setLoginButtonLoading(true);
    hideMessages();
    
    try {
        
        const response = await sendMessageToBackground('login', {
            credentials: {
                email: email,
                password: password
            }
        });
        
        if (response.success) {
            console.log("Login Successful")
            showSuccess('Login successful!');
            showMainContent(response.user);
            await loadUserStats();
            
            // Clear form
            loginForm.reset();
        } else {
            console.log("Login failed ", response.error)
            showError(response.error || 'Login failed');
        }
    } catch (error) {
        console.error('❌ Login error:', error);
        showError('Network error. Please try again.');
    } finally {
        setLoginButtonLoading(false);
    }
}

// Handle logout
async function handleLogout() {
    showLoading(true);
    
    try {
        const response = await sendMessageToBackground('logout');
        
        if (response.success) {
            showSuccess('Logged out successfully');
            showLoginSection();
        } else {
            showError('Logout failed');
        }
    } catch (error) {
        console.error('❌ Logout error:', error);
        showError('Logout failed');
    } finally {
        showLoading(false);
    }
}

// Load user statistics
async function loadUserStats() {
    try {
        const response = await sendMessageToBackground('getStats');
        
        if (response.success) {
            updateStatsDisplay(response.stats);
        } else {
            console.error('❌ Failed to load stats:', response.error);
            // Don't show error to user for stats failure
        }
    } catch (error) {
        console.error('❌ Stats loading error:', error);
    }
}

// Update stats display
function updateStatsDisplay(stats) {
    totalWordsEl.textContent = stats.total_words_added || 0;
    dueWordsEl.textContent = stats.due_today || 0;
    accuracyEl.textContent = stats.overall_accuracy ? `${Math.round(stats.overall_accuracy)}%` : '0%';
    streakEl.textContent = stats.current_streak || 0;
    
    // Show recent activity if there are words
    if (stats.total_words > 0) {
        recentActivity.style.display = 'block';
        loadRecentWords();
    }
}

// Load recent words (placeholder - implement if needed)
async function loadRecentWords() {
    // This would require an additional API endpoint
    // For now, just show a placeholder
    recentWords.innerHTML = `
        <div class="recent-word-item">
            <span class="recent-word-text">Recent words will appear here</span>
            <span class="recent-word-time">Coming soon</span>
        </div>
    `;
}

// Show login section
function showLoginSection() {
    loginSection.style.display = 'block';
    mainContent.style.display = 'none';
    setTimeout(() => emailInput.focus(), 100);
}

// Show main content
function showMainContent(user) {
    loginSection.style.display = 'none';
    mainContent.style.display = 'block';
    
    if (user && user.email) {
        userEmail.textContent = user.email;
    }
}

// Show/hide loading
function showLoading(show) {
    loading.style.display = show ? 'flex' : 'none';
    
    if (show) {
        loginSection.style.display = 'none';
        mainContent.style.display = 'none';
    }
}

// Set login button loading state
function setLoginButtonLoading(isLoading) {
    const btnText = loginBtn.querySelector('.btn-text');
    const btnSpinner = loginBtn.querySelector('.btn-spinner');
    
    if (isLoading) {
        btnText.style.display = 'none';
        btnSpinner.style.display = 'inline';
        loginBtn.disabled = true;
    } else {
        btnText.style.display = 'inline';
        btnSpinner.style.display = 'none';
        loginBtn.disabled = false;
    }
}

// Show success message
function showSuccess(message) {
    document.getElementById('successText').textContent = message;
    successMessage.style.display = 'block';
    errorMessage.style.display = 'none';
    
    setTimeout(() => {
        successMessage.style.display = 'none';
    }, 3000);
}

// Show error message
function showError(message) {
    document.getElementById('errorText').textContent = message;
    document.getElementById('loginError').textContent = message;
    errorMessage.style.display = 'block';
    successMessage.style.display = 'none';
    document.getElementById('loginError').style.display = 'block';
    
    setTimeout(() => {
        errorMessage.style.display = 'none';
        document.getElementById('loginError').style.display = 'none';
    }, 5000);
}

// Hide all messages
function hideMessages() {
    successMessage.style.display = 'none';
    errorMessage.style.display = 'none';
    document.getElementById('loginError').style.display = 'none';
}

// Send message to background script
function sendMessageToBackground(action, data = {}) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(
            { action, ...data },
            (response) => {
                if (chrome.runtime.lastError) {
                    reject(new Error(chrome.runtime.lastError.message));
                } else {
                    resolve(response);
                }
            }
        );
    });
}

// Handle keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Enter key in login form
    if (e.key === 'Enter' && (emailInput === document.activeElement || passwordInput === document.activeElement)) {
        e.preventDefault();
        loginForm.dispatchEvent(new Event('submit'));
    }
    
    // Escape key to close popup
    if (e.key === 'Escape') {
        window.close();
    }
});

// Auto-refresh stats every 30 seconds when popup is open
let statsRefreshInterval;

// Start auto-refresh when main content is shown
function startStatsAutoRefresh() {
    if (statsRefreshInterval) {
        clearInterval(statsRefreshInterval);
    }
    
    statsRefreshInterval = setInterval(() => {
        if (mainContent.style.display !== 'none') {
            loadUserStats();
        }
    }, 30000); // 30 seconds
}

// Stop auto-refresh
function stopStatsAutoRefresh() {
    if (statsRefreshInterval) {
        clearInterval(statsRefreshInterval);
        statsRefreshInterval = null;
    }
}

// Start auto-refresh when popup loads
document.addEventListener('DOMContentLoaded', () => {
    startStatsAutoRefresh();
});

// Stop auto-refresh when popup unloads
window.addEventListener('beforeunload', () => {
    stopStatsAutoRefresh();
});

console.log('✅ WordMaster popup script initialized');
