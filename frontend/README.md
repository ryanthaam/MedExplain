# MedExplain React Frontend

A modern React frontend for MedExplain - AI-powered medication information from FDA sources.

## Features

- 🏠 **Landing Page**: Professional homepage with trust indicators and FDA source information
- 💬 **Interactive Chat**: Real-time chat interface for medication queries
- 🔍 **Multi-Drug Support**: Ask about multiple medications in a single query
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile
- 🛡️ **Safety First**: Comprehensive safety warnings and disclaimers
- 🌟 **Plain English**: Complex medical terms automatically translated
- ⚡ **Real-time**: Instant responses with loading states and error handling
- ⌨️ **Typewriter Effects**: Engaging typewriter animations throughout the UI
- 🎨 **Interactive Elements**: Dynamic text animations and smooth transitions

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Axios** for API communication
- **Lucide React** for icons

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Start the backend API** (in separate terminal):
   ```bash
   # From the project root
   python backend_server.py
   ```

4. **Open your browser:**
   - Frontend: http://localhost:3000
   - API docs: http://localhost:8000/docs

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (buttons, etc.)
│   ├── HeroSection.tsx # Homepage hero section
│   ├── ChatWindow.tsx  # Main chat interface
│   ├── MessageBubble.tsx # Individual chat messages
│   └── ...
├── pages/              # Page components
│   ├── HomePage.tsx    # Landing page
│   └── ChatPage.tsx    # Chat interface page
├── hooks/              # Custom React hooks
│   └── useChat.ts      # Chat functionality hook
├── api/                # API client
│   └── medexplain.ts   # Backend API integration
├── types/              # TypeScript type definitions
│   └── index.ts        # Shared types
└── lib/                # Utility functions
    └── utils.ts        # Helper functions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## API Integration

The frontend connects to the MedExplain backend via REST API:

- `POST /query` - Submit medication questions
- `GET /drug/{name}` - Get detailed drug information
- `GET /suggest` - Get drug name suggestions
- `GET /drugs` - List all available drugs

## Key Features

### Multi-Drug Queries
Ask about multiple medications at once:
```
"What do Aripiprazole, Quetiapine, and Risperidone do?"
```

### Smart Commands
Use quick commands for specific queries:
- `/compare Ibuprofen vs Acetaminophen`
- `/interactions Warfarin and Aspirin`
- `/explain how does Metformin work`

### Safety Features
- Automatic safety warnings for dangerous queries
- Drug interaction checks
- Professional medical disclaimers
- Dosage safety advisories

### Plain English Translation
Complex medical jargon is automatically converted to simple language:
- "contraindication" → "reason not to use"
- "hepatotoxicity" → "liver damage"
- "administered orally" → "taken by mouth"

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Deployment

1. **Build the frontend:**
   ```bash
   npm run build
   ```

2. **Deploy the `dist` folder** to your hosting provider

3. **Update API base URL** for production in `src/api/medexplain.ts`

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test on both desktop and mobile
4. Ensure proper error handling
5. Add loading states for async operations

## License

This project is part of MedExplain and follows the same licensing terms.