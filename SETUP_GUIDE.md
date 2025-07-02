# Hub Helper v1.1.2 - Complete Setup Guide

![Hub Helper](assets/hub-helper-main.png)

**Version 1.1.2** - Your deployment automation companion with global analytics and premium animated UI

## ✨ What's New in v1.1.2

### 🎮 Enhanced Navbar Button Animations

- **Premium button effects** with modern hover animations (lift, ripple, scale)
- **Loading state feedback** with visual spinners for async operations
- **Success/error flash feedback** with color-coded button responses
- **Press effect animations** providing tactile feedback on button clicks
- **Glass morphism design** with backdrop blur and gradient effects
- **Staggered entrance animations** for sequential button appearance

### 🔄 Improved Button Functionality

- **Refresh Button**: Enhanced with loading state during page reload
- **Cleanup Button**: Visual feedback during Docker cleanup operations
- **Status Button**: Loading animation while fetching system information
- **Logout Button**: Smooth transition animation before redirect

### 🎨 Visual Design Enhancements

- **Glass morphism navbar** with translucent background and backdrop blur
- **Gradient button backgrounds** with subtle overlay effects
- **Animated background pattern** with slow-shifting colored gradient orbs
- **Enhanced CSS transitions** with smooth cubic-bezier timing functions

## ✨ Previous Features (v1.1.0)

### 📊 Global Analytics Integration

- **Live deployment counters** in the navbar showing total GitHub and Docker Hub pushes across all users
- **Real-time updates** with smooth animations after each deployment
- **Interactive tooltips** explaining counter functionality on hover
- **Dual-source tracking** with external API and local backup for reliability

### 🎨 Premium Animation System

- **Modern hover effects** with lift, scale, and shimmer animations
- **Floating counters** with gentle continuous motion
- **Multi-color pulse animations** during counter updates
- **Loading states** with elegant pulsing effects
- **Hardware-accelerated** animations for smooth 60fps performance

### 🛠️ Enhanced Features

- **Fixed double-counting** issues for accurate analytics
- **Automatic refresh** every 30 seconds with visual feedback
- **Debug endpoints** for troubleshooting analytics
- **Cross-browser compatibility** for all modern browsers

## 🚀 Quick Setup

### 1. Set up GitHub OAuth (Required)

**Step 1: Create GitHub OAuth App**

1. Go to: <https://github.com/settings/developers>
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

## 🎨 New User Interface Features

### Analytics Counters

- **Location**: Top-right corner of the navbar
- **Functionality**: Shows total deployments across all Hub Helper users
- **GitHub Counter**: Displays total GitHub pushes with GitHub icon
- **Docker Hub Counter**: Displays total Docker Hub pushes with Docker icon
- **Tooltips**: Hover over counters to see explanatory tooltips
- **Real-time Updates**: Counters update automatically after deployments

### Modern Animations

- **Hover Effects**: Counters lift and scale when you hover over them
- **Floating Motion**: Gentle floating animation for visual appeal
- **Shimmer Effect**: Light sweep across counters on hover
- **Pulse Animations**: Multi-color pulse when counters update
- **Loading States**: Elegant animations while fetching data

### Visual Feedback

- **Color Coding**: GitHub (white), Docker Hub (blue) themed hover states
- **Smooth Transitions**: All animations use smooth CSS transitions
- **Performance**: Hardware-accelerated for 60fps smooth motion
- **Responsive**: Works perfectly on all screen sizes

## 🔐 Persistent Login Feature

The Hub Helper saves your login credentials securely:

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

## 🌍 Deployment Scenarios

### Local Development

```bash
# Standard local setup
docker-compose up -d --build
```

### Production Server

```bash
# Production with specific configurations
docker run -d \
  --name hub-helper-prod \
  --restart unless-stopped \
  -p 5414:5414 \
  -v /var/projects:/projects \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/docker:/usr/bin/docker:ro \
  -v hub-helper-prod-data:/app/data \
  -e PROJECTS_PATH=/projects \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  -e GITHUB_CLIENT_ID=your-prod-client-id \
  -e GITHUB_CLIENT_SECRET=your-prod-client-secret \
  -e FLASK_ENV=production \
  hub-helper:latest
```

### Multi-User Environment

```yaml
# docker-compose.yml for shared server
version: '3.8'
services:
  hub-helper:
    build: .
    ports:
      - "5414:5414"
    volumes:
      - /shared/projects:/projects
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker:ro
      - hub-helper-shared-data:/app/data
    environment:
      - PROJECTS_PATH=/projects
      - SECRET_KEY=${SECRET_KEY}
      - GITHUB_CLIENT_ID=${GITHUB_CLIENT_ID}
      - GITHUB_CLIENT_SECRET=${GITHUB_CLIENT_SECRET}
      - FLASK_ENV=production
    restart: unless-stopped
```

## 🔐 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_CLIENT_ID` | ✅ Yes | None | GitHub OAuth App Client ID |
| `GITHUB_CLIENT_SECRET` | ✅ Yes | None | GitHub OAuth App Client Secret |
| `SECRET_KEY` | Recommended | Auto-generated | Flask session encryption key |
| `PROJECTS_PATH` | No | `/projects` | Path to scan for projects |
| `FLASK_ENV` | No | `development` | Flask environment mode |
| `FLASK_APP` | No | `app.py` | Flask application entry point |

## 🚨 Known Issues & Solutions

Based on development experience, here are issues you might encounter:

### Issue: "Git push fails silently"

**Symptoms**: Commits appear local but don't show on GitHub
**Solution**:

```bash
# Force a sync push
docker exec -it hub-helper-container git -C /projects/your-project push --force origin master
```

### Issue: "Docker build fails with permission denied"

**Symptoms**: Cannot build Docker images from within container
**Solution**: Ensure Docker socket has correct permissions:

```bash
sudo chmod 666 /var/run/docker.sock
# OR add your user to docker group
sudo usermod -aG docker $USER
```

### Issue: "Projects directory empty"

**Symptoms**: No projects show in web interface
**Solution**: Check volume mount and permissions:

```bash
# Check mount
docker exec -it hub-helper-container ls -la /projects
# Fix ownership if needed
sudo chown -R $USER:$USER /home/toto/your-projects
```

### Issue: "GitHub OAuth redirect fails"

**Symptoms**: Callback URL errors during GitHub login
**Solution**: Verify OAuth app settings:

- Homepage URL: `http://localhost:5414`
- Callback URL: `http://localhost:5414/auth/github/callback`
- **Exact match required - no trailing slashes**

### Issue: "Persistent login not working after container restart"

**Symptoms**: Need to login again after `docker-compose restart`
**Solution**: Ensure volume is properly mounted:

```bash
# Check volume exists
docker volume ls | grep hub-helper
# Verify mount
docker exec -it hub-helper-container ls -la /app/data
```

## 🎯 Quick Verification Commands

After setup, run these commands to verify everything works:

```bash
# 1. Container health
docker-compose ps
curl -f http://localhost:5414/version || echo "Container not responding"

# 2. Authentication endpoints
curl -s http://localhost:5414/auth/status | jq '.'

# 3. Project discovery
curl -s http://localhost:5414/projects | jq '.'

# 4. Storage encryption
curl -s http://localhost:5414/debug/storage | jq '.'

# 5. Log check (should show no errors)
docker-compose logs hub-helper | grep -i error
```

## 📝 Success Indicators

Your Hub Helper is working correctly when:

- ✅ Web interface loads at `http://localhost:5414`
- ✅ GitHub OAuth redirects work without errors
- ✅ Docker Hub login succeeds
- ✅ Projects are discovered and listed
- ✅ Credentials persist after container restart
- ✅ Git operations complete successfully
- ✅ Docker builds and pushes work
- ✅ No permission errors in logs

---

**Hub Helper v1.0** - Built with experience from real deployment challenges!

*This guide includes solutions for all issues encountered during development and testing.*
