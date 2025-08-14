/**
 * Content Script - Handles text selection and user feedback
 */

// Initialize content script
console.log('🔤 WordMaster content script loaded' );

// Track selected text for context menu
let lastSelectedText = '';

// Listen for text selection
document.addEventListener('selectionchange', () => {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();
    
    if (selectedText && selectedText !== lastSelectedText) {
        lastSelectedText = selectedText;
        
        // Only log if it's a reasonable word (not too long, contains letters)
        if (isValidWord(selectedText)) {
            //console.log(`📝 Text selected: "${selectedText}"`);
        }
    }
});

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Content script received message:', request);
    
    switch (request.action) {
        case 'getSelectedText':
            const selection = window.getSelection();
            sendResponse({ text: selection.toString().trim() });
            break;
            
        case 'highlightWord':
            highlightWordOnPage(request.word);
            sendResponse({ success: true });
            break;
            
        default:
            sendResponse({ success: false, error: 'Unknown action' });
    }
});

// Highlight word on page (optional feature)
function highlightWordOnPage(word) {
    // This is a simple implementation - could be enhanced
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    const textNodes = [];
    let node;
    
    while (node = walker.nextNode()) {
        if (node.textContent.toLowerCase().includes(word.toLowerCase())) {
            textNodes.push(node);
        }
    }
    
    textNodes.forEach(textNode => {
        const parent = textNode.parentNode;
        if (parent && parent.tagName !== 'SCRIPT' && parent.tagName !== 'STYLE') {
            const regex = new RegExp(`\\b${word}\\b`, 'gi');
            const newHTML = textNode.textContent.replace(regex, `<mark class="wordmaster-highlight">$&</mark>`);
            
            if (newHTML !== textNode.textContent) {
                const wrapper = document.createElement('span');
                wrapper.innerHTML = newHTML;
                parent.replaceChild(wrapper, textNode);
                
                // Remove highlight after 3 seconds
                setTimeout(() => {
                    const highlights = wrapper.querySelectorAll('.wordmaster-highlight');
                    highlights.forEach(highlight => {
                        const text = document.createTextNode(highlight.textContent);
                        highlight.parentNode.replaceChild(text, highlight);
                    });
                }, 3000);
            }
        }
    });
}

// Prevent context menu on WordMaster notifications
document.addEventListener('contextmenu', (e) => {
    if (e.target.closest('#wordmaster-notification')) {
        e.preventDefault();
        e.stopPropagation();
    }
});

// Clean up notifications when page unloads
window.addEventListener('beforeunload', () => {
    const notification = document.getElementById('wordmaster-notification');
    if (notification) {
        notification.remove();
    }
});

// Helper function to check if text is a valid word
function isValidWord(text) {
    // Basic validation for word selection
    if (!text || text.length === 0) return false;
    if (text.length > 50) return false; // Too long
    if (!/[a-zA-Z]/.test(text)) return false; // No letters
    if (/^\d+$/.test(text)) return false; // Only numbers
    if (text.includes('\n')) return false; // Multiple lines
    
    return true;
}

// Enhanced text selection handler for better UX
document.addEventListener('mouseup', () => {
    setTimeout(() => {
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();
        
        if (isValidWord(selectedText)) {
            // Could add visual feedback here
            console.log(`✅ Valid word selected: "${selectedText}"`);
        }
    }, 10); // Small delay to ensure selection is complete
});

// Keyboard shortcut for quick word addition (Ctrl+Shift+A)
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'A') {
        e.preventDefault();
        
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();
        
        if (isValidWord(selectedText)) {
            // Send message to background script to add word
            chrome.runtime.sendMessage({
                action: 'addWordFromKeyboard',
                word: selectedText,
                url: window.location.href
            });
        } else {
            console.log('⚠️ No valid word selected for keyboard shortcut');
        }
    }
});

console.log('✅ WordMaster content script initialized');
