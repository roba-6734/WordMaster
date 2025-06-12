/**
 * Background Script - Handles context menu and API communication
 */

// API Configuration
const API_BASE_URL = 'http://localhost:5000';  // Update for production

// Context menu IDs
const CONTEXT_MENU_IDS = {
    ADD_WORD: 'add-word-to-vocabulary',
    LOOKUP_WORD: 'lookup-word-definition'
};

// Initialize extension
chrome.runtime.onInstalled.addListener(( ) => {
    console.log('🚀 WordMaster extension installed');
    createContextMenus();
});

// Create context menus
function createContextMenus() {
    // Remove existing menus
    chrome.contextMenus.removeAll(() => {
        // Add word to vocabulary
        chrome.contextMenus.create({
            id: CONTEXT_MENU_IDS.ADD_WORD,
            title: "Add '%s' to WordMaster",
            contexts: ["selection"],
            documentUrlPatterns: ["http://*/*", "https://*/*"]
        } );

        // Look up word definition
        chrome.contextMenus.create({
            id: CONTEXT_MENU_IDS.LOOKUP_WORD,
            title: "Look up '%s' definition",
            contexts: ["selection"],
            documentUrlPatterns: ["http://*/*", "https://*/*"]
        } );

        console.log('✅ Context menus created');
    });
}

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    const selectedText = info.selectionText?.trim();
    
    if (!selectedText) {
        console.error('❌ No text selected');
        return;
    }

    console.log(`🔤 Context menu clicked: ${info.menuItemId} for word: "${selectedText}"`);

    try {
        switch (info.menuItemId) {
            case CONTEXT_MENU_IDS.ADD_WORD:
                await handleAddWord(selectedText, tab);
                break;
            case CONTEXT_MENU_IDS.LOOKUP_WORD:
                await handleLookupWord(selectedText, tab);
                break;
            default:
                console.error('❌ Unknown menu item:', info.menuItemId);
        }
    } catch (error) {
        console.error('❌ Context menu error:', error);
        await showNotification(tab.id, `Error: ${error.message}`, 'error');
    }
});

// Handle adding word to vocabulary
async function handleAddWord(word, tab) {
    console.log(`📝 Adding word: "${word}"`);
    
    // Check authentication
    const authToken = await getAuthToken();
    if (!authToken) {
        await showNotification(tab.id, 'Please login first by clicking the WordMaster icon', 'warning');
        return;
    }

    // Show loading notification
    await showNotification(tab.id, `Adding "${word}" to your vocabulary...`, 'loading');

    try {
        // Call API to add word
        const response = await fetch(`${API_BASE_URL}/api/words`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                word: word.toLowerCase(),
                source: 'extension',
                sourceUrl: tab.url
            })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            // Success
            const wordData = result.data;
            const definitionCount = wordData.definitions?.length || 0;
            
            await showNotification(
                tab.id, 
                `✅ "${wordData.word}" added! Found ${definitionCount} definitions.`, 
                'success'
            );

            // Update badge to show word count
            await updateBadge();

            console.log('✅ Word added successfully:', wordData);
        } else {
            // API error
            const errorMsg = result.detail || result.message || 'Failed to add word';
            await showNotification(tab.id, `❌ ${errorMsg}`, 'error');
            console.error('❌ API error:', result);
        }
    } catch (error) {
        // Network or other error
        await showNotification(tab.id, `❌ Network error: ${error.message}`, 'error');
        console.error('❌ Network error:', error);
    }
}

// Handle looking up word definition
async function handleLookupWord(word, tab) {
    console.log(`🔍 Looking up word: "${word}"`);
    
    // Show loading notification
    await showNotification(tab.id, `Looking up "${word}"...`, 'loading');

    try {
        // Call dictionary API directly (no auth needed for lookup)
        const response = await fetch(`${API_BASE_URL}/api/dictionary/lookup?word=${encodeURIComponent(word)}`);
        const result = await response.json();

        if (response.ok && result.success) {
            const definitions = result.data.definitions || [];
            if (definitions.length > 0) {
                const firstDef = definitions[0];
                const message = `📖 ${word} (${firstDef.partOfSpeech}): ${firstDef.definition}`;
                await showNotification(tab.id, message, 'info', 8000); // Show longer for reading
            } else {
                await showNotification(tab.id, `📖 "${word}" - No definition found`, 'warning');
            }
        } else {
            await showNotification(tab.id, `❌ Could not find definition for "${word}"`, 'error');
        }
    } catch (error) {
        await showNotification(tab.id, `❌ Lookup error: ${error.message}`, 'error');
        console.error('❌ Lookup error:', error);
    }
}

// Get authentication token from storage
async function getAuthToken() {
    try {
        const result = await chrome.storage.local.get(['authToken']);
        return result.authToken || null;
    } catch (error) {
        console.error('❌ Error getting auth token:', error);
        return null;
    }
}

// Save authentication token to storage
async function saveAuthToken(token) {
    try {
        await chrome.storage.local.set({ authToken: token });
        console.log('✅ Auth token saved');
    } catch (error) {
        console.error('❌ Error saving auth token:', error);
    }
}

// Clear authentication token
async function clearAuthToken() {
    try {
        await chrome.storage.local.remove(['authToken']);
        console.log('✅ Auth token cleared');
    } catch (error) {
        console.error('❌ Error clearing auth token:', error);
    }
}

// Show notification to user on the page
async function showNotification(tabId, message, type = 'info', duration = 4000) {
    try {
        await chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: displayNotification,
            args: [message, type, duration]
        });
    } catch (error) {
        console.error('❌ Error showing notification:', error);
        // Fallback to browser notification
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: 'WordMaster',
            message: message
        });
    }
}

// Function to inject into page for showing notifications
function displayNotification(message, type, duration) {
    // Remove existing notification
    const existing = document.getElementById('wordmaster-notification');
    if (existing) {
        existing.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.id = 'wordmaster-notification';
    notification.className = `wordmaster-notification wordmaster-${type}`;
    
    // Add icon based on type
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️',
        loading: '⏳'
    };
    
    notification.innerHTML = `
        <div class="wordmaster-notification-content">
            <span class="wordmaster-notification-icon">${icons[type] || 'ℹ️'}</span>
            <span class="wordmaster-notification-message">${message}</span>
            <button class="wordmaster-notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Auto-remove after duration (except for loading)
    if (type !== 'loading') {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    }
}

// Update extension badge with word count
async function updateBadge() {
    try {
        const authToken = await getAuthToken();
        if (!authToken) return;

        const response = await fetch(`${API_BASE_URL}/api/progress/stats`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const stats = await response.json();
            const wordCount = stats.total_words || 0;
            
            // Show badge with word count
            chrome.action.setBadgeText({
                text: wordCount > 99 ? '99+' : wordCount.toString()
            });
            chrome.action.setBadgeBackgroundColor({ color: '#667eea' });
        }
    } catch (error) {
        console.error('❌ Error updating badge:', error);
    }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Background received message:', request);

    switch (request.action) {
        case 'login':
            handleLogin(request.credentials)
                .then(result => sendResponse(result))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true; // Keep message channel open for async response

        case 'logout':
            handleLogout()
                .then(result => sendResponse(result))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true;

        case 'getStats':
            getStats()
                .then(result => sendResponse(result))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true;

        case 'checkAuth':
            checkAuth()
                .then(result => sendResponse(result))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true;

        default:
            sendResponse({ success: false, error: 'Unknown action' });
    }
});

// Handle login from popup
async function handleLogin(credentials) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(credentials.body)  // Send the inner body object directly
        });

        const result = await response.json();

        if (response.ok && result.access_token) {
            await saveAuthToken(result.access_token);
            return { success: true, user: { email: credentials.body.email } };
        } else {
            console.error('❌ Login failed:', result);
            return { 
                success: false, 
                error: result.detail || 'Login failed. Please check your credentials.'
            };
        }
    } catch (error) {
        console.error('❌ Login error:', error);
        return { 
            success: false, 
            error: 'Network error. Please try again.'
        };
    }
}

// Handle logout
async function handleLogout() {
    try {
        await clearAuthToken();
        chrome.action.setBadgeText({ text: '' });
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Get user stats
async function getStats() {
    try {
        const authToken = await getAuthToken();
        if (!authToken) {
            return { success: false, error: 'Not authenticated' };
        }

        const response = await fetch(`${API_BASE_URL}/api/progress/stats`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const stats = await response.json();
            return { success: true, stats };
        } else {
            return { success: false, error: 'Failed to get stats' };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Check authentication status
async function checkAuth() {
    try {
        const authToken = await getAuthToken();
        if (!authToken) {
            return { success: false, authenticated: false };
        }

        const response = await fetch(`${API_BASE_URL}/api/auth/user`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const user = await response.json();
            return { success: true, authenticated: true, user };
        } else {
            // Token might be expired
            await clearAuthToken();
            return { success: false, authenticated: false };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Initialize badge on startup
chrome.runtime.onStartup.addListener(() => {
    updateBadge();
});
