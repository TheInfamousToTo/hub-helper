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

### Git Permission Issues (IMPORTANT!)

**Problem**: Git operations fail with "fatal: detected dubious ownership" or permission errors.

**Solution**: The container automatically fixes this, but if you encounter issues:

1. **Check file ownership** (run outside container):
   ```bash
   sudo chown -R $USER:$USER /home/toto/hub-helper
   sudo chmod -R 755 /home/toto/hub-helper
   ```

2. **Fix Git safe directory** (the container does this automatically):
   ```bash
   # This is handled automatically by the Dockerfile, but for reference:
   git config --global --add safe.directory /projects/your-project-name
   ```

3. **If Git operations still fail**, use the included fix script:
   ```bash
   docker exec -it hub-helper-container /app/fix-git.sh
   ```

### Container Build Issues

**Problem**: Container fails to build or start.

**Solutions**:
1. **Clean Docker cache**:
   ```bash
   docker-compose down
   docker system prune -f
   docker-compose up -d --build
   ```

2. **Check Docker daemon**:
   ```bash
   sudo systemctl status docker
   sudo systemctl start docker  # if not running
   ```

3. **Verify Docker socket permissions**:
   ```bash
   sudo chmod 666 /var/run/docker.sock
   # Or add your user to docker group:
   sudo usermod -aG docker $USER
   # Then logout and login again
   ```

### Project Not Found Errors

**Problem**: Projects don't appear in the web interface.

**Solution**: 
1. **Verify volume mount**: Ensure `/home/toto:/projects` is correctly mounted
2. **Check project structure**: Projects should be direct subdirectories of `/home/toto`
3. **Restart container**: Sometimes a restart helps refresh the project list

### Push to GitHub Fails

**Problem**: Git push operations fail even after authentication.

**Solutions**:
1. **Token permissions**: Ensure your GitHub token has `repo` scope
2. **Repository exists**: Make sure the GitHub repository exists and is accessible
3. **Branch issues**: The app pushes to `master` branch by default
4. **Force refresh**: If commits seem to disappear, they might need a sync push

### Docker Build/Push Fails

**Problem**: Docker operations fail during deployment.

**Solutions**:
1. **Dockerfile exists**: Ensure your project has a valid Dockerfile
2. **Docker Hub access**: Verify Docker Hub credentials and repository access
3. **Image size**: Large images might timeout - optimize your Dockerfile
4. **Network issues**: Check internet connectivity for Docker Hub access

### Environment Variable Issues

**Problem**: Configuration not being picked up.

**Solution**: 
1. **Check docker-compose.yml**: Verify all environment variables are set
2. **Restart after changes**: Always restart the container after environment changes:
   ```bash
   docker-compose down
   docker-compose up -d
   ```
3. **Use .env file**: Create a `.env` file for easier management:
   ```bash
   GITHUB_CLIENT_ID=your-client-id
   GITHUB_CLIENT_SECRET=your-client-secret
   SECRET_KEY=your-secret-key
   ```

### Port Already in Use

**Problem**: Port 5414 is already occupied.

**Solution**: 
1. **Check what's using the port**:
   ```bash
   sudo lsof -i :5414
   sudo netstat -tulnp | grep 5414
   ```
2. **Kill the process** or **change the port** in docker-compose.yml:
   ```yaml
   ports:
     - "5415:5414"  # Use different external port
   ```

### Debug and Monitoring

**Useful commands for troubleshooting**:

```bash
# Check container status
docker-compose ps

# View real-time logs
docker-compose logs -f hub-helper

# Enter container for debugging
docker exec -it hub-helper-container bash

# Check persistent storage
docker exec -it hub-helper-container ls -la /app/data

# Test storage debug endpoint (when container is running)
curl http://localhost:5414/debug/storage

# Check authentication status
curl http://localhost:5414/auth/status
```

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

## 🚨 Pre-Deployment Checklist

Before using Hub Helper, ensure these prerequisites are met:

### System Requirements
- [ ] **Docker installed and running**
  ```bash
  docker --version
  docker-compose --version
  ```
- [ ] **User in docker group** (or use sudo)
  ```bash
  groups $USER | grep docker
  ```
- [ ] **Port 5414 available**
  ```bash
  netstat -tulnp | grep 5414
  ```

### GitHub Setup
- [ ] **OAuth App created** on GitHub
- [ ] **Client ID and Secret** copied to docker-compose.yml
- [ ] **Callback URL** set to `http://localhost:5414/auth/github/callback`
- [ ] **Personal Access Token** ready (if needed for private repos)

### Docker Hub Setup
- [ ] **Docker Hub account** active
- [ ] **Repository permissions** verified
- [ ] **Username and password** ready

### File Permissions
- [ ] **Project directory** owned by your user
  ```bash
  ls -la /home/toto/hub-helper
  ```
- [ ] **Docker socket** accessible
  ```bash
  ls -la /var/run/docker.sock
  ```

## 🛠️ First-Time Setup Verification

After starting the container, verify everything works:

1. **Container Status**:
   ```bash
   docker-compose ps
   # Should show hub-helper as "Up"
   ```

2. **Web Interface**:
   - Open http://localhost:5414
   - Should show login page with Hub Helper logo

3. **GitHub OAuth**:
   - Click "Login with GitHub"
   - Should redirect to GitHub authorization
   - After approval, should return to Hub Helper

4. **Docker Hub Login**:
   - Enter Docker Hub credentials
   - Should show "Login successful"

5. **Project Discovery**:
   - Should list projects from `/home/toto/`
   - Each project should show Git/Docker status

## 🔍 Health Check Endpoints

Use these endpoints to verify the application health:

```bash
# Check application version
curl http://localhost:5414/version

# Check authentication status
curl http://localhost:5414/auth/status

# Debug persistent storage (shows encrypted data status)
curl http://localhost:5414/debug/storage

# Get projects list
curl http://localhost:5414/projects
```

## 🛡️ Security Notes

- Credentials are encrypted using Fernet symmetric encryption
- Each container instance generates its own encryption key
- Logout will completely remove stored credentials
- GitHub tokens have limited scope (repo access only)
- Docker Hub credentials are only stored in memory and encrypted files

## 🔧 Built-in Problem Fixes

Hub Helper v1.0 includes automatic fixes for common Docker container issues:

### Automatic Git Configuration
The container automatically handles:
- **Safe directory configuration**: Prevents "dubious ownership" errors
- **Default user/email setup**: Sets hub-helper@automation.local for commits
- **Permission fixes**: Ensures Git operations work in containerized environment

### Docker Socket Access
- **Automatic mounting**: Docker socket is properly mounted for build operations
- **Permission handling**: Container runs with appropriate Docker access
- **Binary availability**: Docker binary is available inside the container

### Persistent Storage Encryption
- **Automatic key generation**: Each container generates unique encryption keys
- **Secure credential storage**: All tokens and passwords are encrypted at rest
- **Volume persistence**: Data survives container restarts and rebuilds

### Network Configuration
- **Port management**: Runs on port 5414 by default
- **OAuth callback**: Properly configured for GitHub authentication
- **API endpoints**: Health check and debug endpoints available

## 🚀 Advanced Features

### Debugging Tools
Hub Helper includes several debugging utilities:

1. **Storage Debug Script**: `/app/debug_storage.py`
   - Shows encryption key status
   - Displays credential storage information
   - Helps troubleshoot persistent login issues

2. **Git Fix Script**: `/app/fix-git.sh`
   - Repairs Git configuration issues
   - Fixes ownership problems
   - Resolves safe directory errors

3. **Debug Endpoints**:
   - `/debug/storage` - Storage status
   - `/auth/status` - Authentication status
   - `/version` - Application version

### Container Optimization
- **Efficient layering**: Dockerfile optimized for fast rebuilds
- **Minimal attack surface**: Only necessary components installed
- **Resource efficient**: Lightweight Python Flask application
- **Health checks**: Built-in application health monitoring

## ✨ Features

- ✅ **GitHub OAuth Integration**: Secure authentication
- ✅ **Persistent Login**: Stay logged in across container restarts  
- ✅ **Encrypted Storage**: Credentials safely encrypted
- ✅ **One-Click Deployment**: Push to GitHub and Docker Hub
- ✅ **Project Discovery**: Automatically finds your projects
- ✅ **GitHub Dark Theme**: Professional developer UI
- ✅ **Docker Integration**: Build and push images automatically

Your Hub Helper is now ready with persistent login capabilities!
