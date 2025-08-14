# WordMaster Browser Extension

A Chrome extension that allows users to capture words while browsing and add them to their vocabulary learning collection.

## 🚀 Features

- **Word Capture**: Right-click on any word to add it to your vocabulary
- **Quick Add**: Use Ctrl+Shift+A keyboard shortcut for fast word addition
- **Word Lookup**: Get instant definitions for selected words
- **Context Menu Integration**: Seamless integration with browser context menus
- **User Authentication**: Secure login system integrated with WordMaster backend
- **Real-time Notifications**: Beautiful in-page notifications for user feedback
- **Badge Updates**: Extension badge shows your current word count

## 📦 Installation

### Development Mode

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the `extension/` folder
4. The WordMaster extension should now appear in your extensions list

### Production Installation

1. Download the extension from the Chrome Web Store (when available)
2. Click "Add to Chrome" to install

## 🧪 Testing

### Test Page

Use the included `test.html` file to test the extension:

1. Open `test.html` in Chrome
2. Make sure the extension is loaded and you're logged in
3. Select words and test the various features

### Test Scenarios

1. **Word Selection & Right-Click**
   - Select any word on a webpage
   - Right-click and choose "Add to WordMaster"

2. **Keyboard Shortcut**
   - Select a word
   - Press `Ctrl + Shift + A`

3. **Word Lookup**
   - Select a word
   - Right-click and choose "Look up definition"

4. **Extension Popup**
   - Click the WordMaster extension icon
   - View your stats and manage vocabulary

## 🔧 Configuration

### API Endpoint

Update the `API_BASE_URL` in `background/background.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000'; // Development
const API_BASE_URL = 'https://your-domain.com'; // Production
```

### Permissions

The extension requires these permissions:

- `activeTab` - Access to current tab
- `storage` - Store authentication tokens
- `contextMenus` - Create right-click menus
- `scripting` - Inject notifications into pages
- `notifications` - Show browser notifications

## 🏗️ Architecture

### Files Structure

```
extension/
├── manifest.json          # Extension configuration
├── background/
│   └── background.js      # Background service worker
├── content/
│   └── content.js         # Content scripts for page interaction
├── popup/
│   ├── popup.html         # Extension popup interface
│   ├── popup.js           # Popup functionality
│   └── popup.css          # Popup styling
├── assets/
│   └── notification.css   # In-page notification styles
└── icons/                 # Extension icons
```

### Key Components

1. **Background Script** (`background.js`)
   - Handles context menu creation
   - Manages API communication
   - Handles authentication
   - Updates extension badge

2. **Content Script** (`content.js`)
   - Detects text selection
   - Handles keyboard shortcuts
   - Manages word highlighting
   - Communicates with background script

3. **Popup Interface** (`popup/`)
   - User login/logout
   - Statistics display
   - Quick access to web app

## 🔌 API Integration

The extension integrates with the WordMaster backend API:

- `POST /api/words` - Add new words to vocabulary
- `GET /api/dictionary/lookup/{word}` - Look up word definitions
- `GET /api/progress/stats` - Get user learning statistics
- `POST /api/auth/login` - User authentication

## 🎨 Customization

### Notification Styles

Modify `assets/notification.css` to customize the appearance of in-page notifications.

### Context Menu Items

Edit the context menu creation in `background.js` to add or modify menu items.

### Keyboard Shortcuts

Update the keyboard shortcut handling in `content.js` to change or add new shortcuts.

## 🐛 Troubleshooting

### Common Issues

1. **Extension not working**
   - Check if the extension is enabled
   - Verify backend API is running
   - Check browser console for errors

2. **Authentication issues**
   - Ensure you're logged into the extension
   - Check if the auth token is valid
   - Try logging out and back in

3. **Words not being added**
   - Verify API endpoint is correct
   - Check network requests in DevTools
   - Ensure backend is accessible

### Debug Mode

Enable debug logging by uncommenting console.log statements in the code.

## 📱 Browser Compatibility

- **Chrome**: Full support (tested)
- **Edge**: Full support (Chromium-based)
- **Firefox**: Partial support (may need manifest adjustments)
- **Safari**: Not supported (different extension system)

## 🔄 Updates

To update the extension:

1. Make your code changes
2. Go to `chrome://extensions/`
3. Click the refresh icon on the WordMaster extension
4. The extension will reload with your changes

## 📄 License

This extension is part of the WordMaster project and follows the same license terms.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Happy Learning! 📚✨** 