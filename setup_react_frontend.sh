#!/bin/bash

# MedExplain React Frontend Setup Script

echo "🚀 Setting up MedExplain React Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOL
VITE_API_BASE_URL=http://localhost:8000
EOL
    echo "✅ Created .env file"
fi

# Install backend dependencies
echo "🐍 Installing backend dependencies..."
cd ..
pip install fastapi uvicorn python-multipart

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start the backend server:"
echo "   python backend_server.py"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser:"
echo "   - Frontend: http://localhost:3000"
echo "   - API docs: http://localhost:8000/docs"
echo ""
echo "🚀 Happy coding!"