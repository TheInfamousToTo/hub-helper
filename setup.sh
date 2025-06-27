#!/bin/bash

# Hub Helper - Quick Setup Script

echo "🚀 Hub Helper Setup"
echo "==================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Get the current directory
CURRENT_DIR=$(pwd)
echo "📁 Current directory: $CURRENT_DIR"

# Ask for projects directory
read -p "📂 Enter the full path to your projects directory (default: $HOME): " PROJECTS_PATH
PROJECTS_PATH=${PROJECTS_PATH:-$HOME}

# Validate projects directory
if [ ! -d "$PROJECTS_PATH" ]; then
    echo "❌ Directory $PROJECTS_PATH does not exist"
    exit 1
fi

echo "✅ Projects directory: $PROJECTS_PATH"

# Create .env file
echo "📝 Creating environment configuration..."
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
PROJECTS_PATH=$PROJECTS_PATH
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
FLASK_ENV=production
FLASK_APP=app.py
EOF

# Update docker-compose.yml with the correct projects path
echo "🔧 Updating docker-compose.yml..."
sed -i "s|/home/toto:/projects|$PROJECTS_PATH:/projects|g" docker-compose.yml

echo "✅ Configuration updated"

# Ask about GitHub OAuth
echo ""
echo "🔐 GitHub OAuth Setup (Optional but recommended)"
echo "   For better security, set up GitHub OAuth:"
echo "   1. Go to: https://github.com/settings/developers"
echo "   2. Create a new OAuth App"
echo "   3. Set Authorization callback URL to: http://localhost:5414/auth/github/callback"
echo ""
read -p "Do you want to configure GitHub OAuth now? (y/N): " SETUP_OAUTH

if [[ $SETUP_OAUTH =~ ^[Yy]$ ]]; then
    read -p "Enter GitHub Client ID: " GITHUB_CLIENT_ID
    read -p "Enter GitHub Client Secret: " GITHUB_CLIENT_SECRET
    
    # Update .env file
    sed -i "s/GITHUB_CLIENT_ID=/GITHUB_CLIENT_ID=$GITHUB_CLIENT_ID/" .env
    sed -i "s/GITHUB_CLIENT_SECRET=/GITHUB_CLIENT_SECRET=$GITHUB_CLIENT_SECRET/" .env
    
    echo "✅ GitHub OAuth configured"
else
    echo "⚠️  GitHub OAuth skipped - users will need to enter credentials manually"
fi

# Build and start the application
echo ""
echo "🚀 Building and starting Hub Helper..."
docker-compose up -d --build

echo ""
echo "✅ Hub Helper is starting up!"
echo ""
echo "📖 Next steps:"
echo "   1. Wait a moment for the application to start"
echo "   2. Open your browser and go to: http://localhost:5414"
echo "   3. Login with your GitHub and Docker Hub accounts"
echo "   4. Start deploying your projects!"
echo ""
echo "🔧 Useful commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop app:     docker-compose down"
echo "   Restart app:  docker-compose restart"
echo ""
echo "📚 For more information, see README.md"
