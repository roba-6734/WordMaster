# WordMaster - Vocabulary Learning Platform

A comprehensive vocabulary learning platform that combines spaced repetition algorithms with web browsing integration to help users build their vocabulary efficiently.

## 🚀 Features

- **Spaced Repetition Learning**: Advanced algorithm that adapts to your learning pace
- **Web Integration**: Browser extension to capture words while browsing
- **Progress Tracking**: Comprehensive analytics and learning statistics
- **Quiz System**: Multiple quiz types to reinforce learning
- **User Authentication**: Secure login and registration system
- **Responsive Design**: Modern, mobile-friendly web interface

## 🏗️ Architecture

WordMaster consists of three main components:

1. **Backend API** - FastAPI-based REST API with Firebase integration
2. **Frontend Web App** - React-based dashboard and learning interface
3. **Browser Extension** - Chrome extension for word capture during browsing

## 📁 Project Structure

```
WordMaster/
├── backend/                 # FastAPI backend server
│   ├── src/
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── models/         # Data models
│   │   ├── config/         # Configuration
│   │   └── firebase/       # Firebase integration
│   ├── requirements.txt    # Python dependencies
│   └── .venv/             # Virtual environment
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── context/        # React context providers
│   │   └── services/       # API service calls
│   ├── package.json        # Node.js dependencies
│   └── tailwind.config.js  # Tailwind CSS configuration
├── extension/              # Browser extension
│   ├── popup/             # Extension popup interface
│   ├── content/            # Content scripts
│   ├── background/         # Background service worker
│   └── manifest.json       # Extension manifest
├── docs/                   # Documentation
└── .env                    # Environment variables
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Firebase Admin SDK** - Backend services and database
- **Python 3.8+** - Core programming language
- **Uvicorn** - ASGI server for running FastAPI

### Frontend
- **React 19** - Modern React with latest features
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Accessible component primitives
- **React Router** - Client-side routing

### Browser Extension
- **Manifest V3** - Latest Chrome extension standard
- **Service Workers** - Background processing
- **Content Scripts** - Web page integration

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- Firebase project with Firestore database
- Chrome browser (for extension)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables in `.env`:
   ```env
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_PRIVATE_KEY=your-private-key
   FIREBASE_CLIENT_EMAIL=your-client-email
   ```

5. Run the development server:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:5173](http://localhost:5173) in your browser

### Extension Setup

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `extension/` folder
4. The WordMaster extension should now appear in your extensions list

## 📚 API Documentation

Once the backend is running, you can access the interactive API documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key API Endpoints

- `POST /api/user/register` - User registration
- `POST /api/user/login` - User authentication
- `GET /api/words` - Get user's word collection
- `POST /api/words` - Add new word
- `GET /api/progress/due` - Get words due for review
- `POST /api/progress/update` - Update word progress
- `GET /api/quiz/next` - Get next quiz question

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
```

### Firebase Setup

1. Create a new Firebase project
2. Enable Firestore database
3. Create a service account and download the private key
4. Add the service account credentials to your environment variables

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest src/test/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Building for Production

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
npm run preview
```

### Extension
1. Update the `host_permissions` in `extension/manifest.json` with your production API domain
2. Load the extension in Chrome as described in the setup section

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/WordMaster/issues) page
2. Create a new issue with detailed information
3. Include your environment details and error logs

## 🔮 Roadmap

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Social learning features
- [ ] Integration with popular learning platforms
- [ ] AI-powered word difficulty assessment
- [ ] Multi-language support

## 🙏 Acknowledgments

- Spaced repetition algorithm based on research by Piotr Wozniak
- UI components built with Radix UI primitives
- Icons provided by Lucide React
- Built with modern web technologies for optimal performance

---

**Happy Learning! 📚✨** 