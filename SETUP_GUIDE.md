# Hub Helper v1.0 - Complete Setup Guide

![Hub Helper](assets/hub-helper-main.png)

**Version 1.0** - Your deployment automation companion

## 🚀 Quick Setup

### 1. Set up GitHub OAuth (Required)

**Step 1: Create GitHub OAuth App**
1. Go to: https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: `Hub Helper`
   - **Homepage URL**: `http://localhost:5414`
   - **Authorization callback URL**: `http://localhost:5414/auth/github/callback`
4. Click "Register application"
5. Copy the **Client ID** and **Client Secret**

### 2. Choose Your Setup Method

#### Option A: Using Docker Compose (Recommended)

1. **Update the GitHub OAuth credentials** in `docker-compose.yml`:
   ```yaml
   environment:
     - GITHUB_CLIENT_ID=your-actual-client-id-here
     - GITHUB_CLIENT_SECRET=your-actual-client-secret-here
   ```

2. **Start the application**:
   ```bash
   cd /home/toto/hub-helper
   docker-compose up -d --build
   ```

#### Option B: Using Docker Run Command

```bash
docker build -t hub-helper .

docker run -d \
  --name hub-helper \
  -p 5414:5414 \
  -v /home/toto:/projects \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/docker:/usr/bin/docker:ro \
  -v hub-helper-data:/app/data \
  -e PROJECTS_PATH=/projects \
  -e SECRET_KEY=your-super-secret-key-change-this \
  -e GITHUB_CLIENT_ID=your-actual-client-id-here \
  -e GITHUB_CLIENT_SECRET=your-actual-client-secret-here \
  -e FLASK_APP=app.py \
  -e FLASK_ENV=production \
  hub-helper:latest
```

#### Option C: Using the Setup Script

```bash
cd /home/toto/hub-helper
./setup.sh
```
The script will prompt you for your GitHub OAuth credentials.

## 🔐 Persistent Login Feature

The Hub Helper now saves your login credentials securely:

- **Encrypted Storage**: Credentials are encrypted and stored in `/app/data/credentials.json`
- **Auto-Login**: When you restart the container, you'll stay logged in
- **Secure**: Uses Fernet encryption to protect your GitHub tokens and Docker Hub credentials
- **Volume Persistence**: Data persists through container rebuilds using Docker volumes

## 📁 Volume Mounts Explained

| Volume | Purpose | Required |
|--------|---------|----------|
| `/home/toto:/projects` | Your projects directory | ✅ Yes |
| `/var/run/docker.sock:/var/run/docker.sock` | Docker operations | ✅ Yes |
| `/usr/bin/docker:/usr/bin/docker:ro` | Docker binary | ✅ Yes |
| `hub-helper-data:/app/data` | Persistent login storage | ✅ Yes |

## 🌐 Access the Application

1. Open your browser
2. Go to: `http://localhost:5414`
3. Login with GitHub (OAuth) and Docker Hub credentials
4. Your login will be remembered even after container restarts!

## 🔧 Troubleshooting

### GitHub OAuth Error
If you get `"GitHub OAuth not configured"`:
1. Make sure you've created the OAuth app on GitHub
2. Double-check your Client ID and Client Secret in the environment variables
3. Ensure the callback URL is exactly: `http://localhost:5414/auth/github/callback`

### Docker Hub Login Issues
- Make sure your Docker Hub credentials are correct
- Check if Docker Hub is accessible from your network

### Persistent Login Not Working
- Ensure the `hub-helper-data` volume is mounted correctly
- Check container logs: `docker-compose logs -f hub-helper`

## 🔄 Managing the Application

```bash
# View logs
docker-compose logs -f hub-helper

# Restart the application
docker-compose restart hub-helper

# Stop the application
docker-compose down

# Rebuild and start
docker-compose up -d --build

# Clear all data (including saved logins)
docker-compose down -v
```

## 🛡️ Security Notes

- Credentials are encrypted using Fernet symmetric encryption
- Each container instance generates its own encryption key
- Logout will completely remove stored credentials
- GitHub tokens have limited scope (repo access only)
- Docker Hub credentials are only stored in memory and encrypted files

## ✨ Features

- ✅ **GitHub OAuth Integration**: Secure authentication
- ✅ **Persistent Login**: Stay logged in across container restarts  
- ✅ **Encrypted Storage**: Credentials safely encrypted
- ✅ **One-Click Deployment**: Push to GitHub and Docker Hub
- ✅ **Project Discovery**: Automatically finds your projects
- ✅ **GitHub Dark Theme**: Professional developer UI
- ✅ **Docker Integration**: Build and push images automatically

Your Hub Helper is now ready with persistent login capabilities!
