# Hub Helper

![Hub Helper](assets/hub-helper-main.png)

A streamlined deployment automation tool that simplifies pushing projects to GitHub and Docker Hub with a modern web interface, persistent authentication, containerized deployment, and **real-time global analytics tracking**.

## ✨ New Features

### 📊 **Global Analytics Counters**

- **Real-time deployment tracking** - Live counters showing total GitHub and Docker Hub deployments across all users
- **Integrated analytics API** - Connects to external analytics backend for global statistics
- **Fallback local tracking** - Maintains local analytics as backup when external API is unavailable
- **Visual counters in navbar** - GitHub and Docker Hub icons with live deployment counts and hover tooltips
- **Modern animations** - Smooth hover effects, floating animations, and dynamic counter updates
- **Accurate tracking** - Fixed double-counting issues for precise analytics

### 🔄 **Enhanced User Experience**

- **Persistent authentication** with secure credential encryption
- **Real-time deployment progress** with detailed step-by-step feedback
- **Improved error handling** and user feedback
- **Modern responsive UI** optimized for all screen sizes with smooth animations
- **Automatic counter updates** after successful deployments with visual feedback
- **Interactive hover tooltips** explaining counter functionality
- **Premium animations** including floating effects, shimmer overlays, and color transitions

## Features

• **Global Analytics** - real-time tracking of deployments across all users with animated live counters
• **Modern Animations** - premium UI animations including hover effects, floating counters, and smooth transitions
• **Interactive Tooltips** - hover tooltips explaining counter functionality and global usage statistics
• **Persistent Authentication** - securely stores GitHub OAuth tokens and Docker Hub credentials with encryption
• **Selective Deployment** - choose to deploy to GitHub, Docker Hub, or both with checkbox selection
• **Version Management** - semantic versioning support with automatic Git tagging and Docker image tagging
• **Project Discovery** - automatically detects projects with Git repositories and Dockerfiles
• **Modern UI** - GitHub-themed dark interface with responsive design and premium animations
• **Containerized** - fully containerized deployment with Docker Compose support
• **Git Integration** - automatic Git configuration and safe directory handling
• **Debug Tools** - built-in debugging endpoints and storage management utilities
• **Docker Cleanup** - automatic cleanup of build containers and manual cleanup tools to prevent resource accumulation

## Quick Start

### Prerequisites

• Docker and Docker Compose installed
• GitHub OAuth App configured
• Docker Hub account

### Setup

1. **Create GitHub OAuth App**
   - Go to [GitHub Developer Settings](https://github.com/settings/developers)
   - Click "New OAuth App"
   - Set Homepage URL: `http://localhost:5414`
   - Set Authorization callback URL: `http://localhost:5414/auth/github/callback`

2. **Configure Environment**
   - Update `docker-compose.yml` with your GitHub OAuth credentials:

   ```yaml
   environment:
     - GITHUB_CLIENT_ID=your-client-id
     - GITHUB_CLIENT_SECRET=your-client-secret
   ```

3. **Start the Application**

   ```bash
   docker-compose up -d
   ```

   Or run directly with Docker:

   ```bash
   docker run -d --name hub-helper \
     -p 5414:5414 \
     -v /home/toto:/projects \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -v /usr/bin/docker:/usr/bin/docker:ro \
     -v hub-helper-data:/app/data \
     -e PROJECTS_PATH=/projects \
     -e SECRET_KEY=your-super-secret-key \
     -e GITHUB_CLIENT_ID=your-client-id \
     -e GITHUB_CLIENT_SECRET=your-client-secret \
     theinfamoustoto/hub-helper:latest
   ```

4. **Access the Interface**
   - Open <http://localhost:5414>
   - Complete GitHub OAuth authentication
   - Enter Docker Hub credentials

## Environment Variables

• `GITHUB_CLIENT_ID`: GitHub OAuth App Client ID (required)
• `GITHUB_CLIENT_SECRET`: GitHub OAuth App Client Secret (required)
• `SECRET_KEY`: Flask session encryption key (auto-generated if not provided)
• `PROJECTS_PATH`: Path to scan for projects (default: `/projects`)
• `FLASK_ENV`: Flask environment mode (default: `development`)

## Usage

### Deploying Projects

1. **Select Project**: Click on any discovered project card
2. **Configure Version**: Set semantic version (e.g., v1.0.0, v2.1.3)
3. **Choose Targets**: Select GitHub, Docker Hub, or both
4. **Set Repository Names**: Specify GitHub and Docker Hub repository names
5. **Deploy**: Click Deploy to start the automated process

### Version Management

The application automatically:

- Creates/updates version files in projects
- Creates Git tags for releases
- Tags Docker images with both `latest` and version-specific tags
- Generates appropriate commit messages

### Analytics & Tracking

Hub Helper now includes **global analytics tracking** to show deployment statistics:

**Real-time Counters:**

- GitHub deployments counter (visible in navbar with hover tooltips)
- Docker Hub deployments counter (visible in navbar with hover tooltips)
- Live updates after each successful deployment with smooth animations
- Automatic refresh every 30 seconds with visual feedback
- Modern hover effects including floating, shimmer, and color transitions

**Visual Features:**

- **Hover Tooltips**: Explain that counters show total deployments across all users
- **Smooth Animations**: Floating motion, shimmer effects, and dynamic scaling
- **Color Transitions**: Multi-color pulse animations during counter updates
- **Loading States**: Elegant loading animations while fetching data
- **Entrance Effects**: Staggered slide-in animations when page loads

**Data Sources:**

- **Fallback**: Local file-based analytics for backup tracking
- **Endpoints**: `/analytics/counters` for current counts, `/analytics/reset` for admin reset

**Features:**

- Accurate tracking (fixed double-counting issues)
- Real-time updates across all users with smooth animations
- Persistent local backup for reliability
- API integration with comprehensive error handling
- Premium user experience with modern animations and visual feedback

### Project Requirements

For **GitHub deployment**:

- Project must be a valid Git repository
- Repository name format: `username/repository-name`

For **Docker deployment**:

- Project must contain a valid `Dockerfile`
- Repository name format: `repository-name`

## Docker Compose

```yaml
version: '3.8'

services:
  hub-helper:
    image: theinfamoustoto/hub-helper:latest
    ports:
      - "5414:5414"
    volumes:
      # Mount your projects directory - CHANGE THIS PATH TO YOUR PROJECTS FOLDER
      - /home/toto:/projects
      # Mount Docker socket to allow Docker operations from within container
      - /var/run/docker.sock:/var/run/docker.sock
      # Mount Docker binary (if needed)
      - /usr/bin/docker:/usr/bin/docker:ro
      # Mount data directory for persistent login storage
      - hub-helper-data:/app/data
    environment:
      - PROJECTS_PATH=/projects
      - SECRET_KEY=your-super-secret-key-change-this
      # GitHub OAuth App credentials (optional - get from GitHub Developer Settings)
      - GITHUB_CLIENT_ID=your-github-client-id
      - GITHUB_CLIENT_SECRET=your-github-client-secret
    restart: unless-stopped
    networks:
      - hub-helper-network

networks:
  hub-helper-network:
    driver: bridge

volumes:
  hub-helper-data:
    driver: local
```

## Security Features

• **Credential Encryption**: All stored credentials are encrypted using Fernet symmetric encryption
• **Session Management**: Secure session handling with Flask sessions
• **Token Validation**: GitHub tokens and Docker Hub credentials are validated before storage
• **Safe Git Operations**: Automatic Git configuration and safe directory handling

## API Endpoints

### Core Endpoints

• `GET /`: Main application interface
• `GET /version`: Application version information
• `GET /auth/status`: Authentication status check
• `GET /projects`: List discovered projects
• `POST /deploy`: Deploy project to selected targets

### Analytics Endpoints

• `GET /analytics/counters`: Get current global deployment counters
• `POST /analytics/reset`: Reset local analytics counters (admin only)
• `GET /analytics/debug`: Debug analytics information

### System & Debug Endpoints

• `GET /debug/storage`: Debug persistent storage (development)
• `POST /cleanup/docker`: Clean up stopped containers and unused images
• `GET /system/status`: Get Docker system status and resource usage

## Troubleshooting

### Common Issues

**GitHub OAuth Error**: Verify OAuth app configuration and callback URL
**Docker Permission Denied**: Ensure Docker socket permissions are correct
**Projects Not Found**: Check volume mounts and project directory permissions
**Persistent Login Issues**: Verify data volume mount and container logs

### Debug Commands

```bash
# Check container logs
docker-compose logs -f hub-helper

# Verify authentication status
curl http://localhost:5414/auth/status

# Check storage debug information
curl http://localhost:5414/debug/storage

# Get Docker system status
curl http://localhost:5414/system/status

# Manually clean up Docker resources
curl -X POST http://localhost:5414/cleanup/docker
```

### Docker Resource Management

Hub Helper includes automatic Docker cleanup features to prevent container accumulation:

**Automatic Cleanup:**

- Removes intermediate containers after each build
- Cleans up old containers (created > 10 min, exited > 30 min) after deployments
- Prunes dangling images to reclaim disk space

**Manual Cleanup:**

- Click the "Cleanup" button in the web interface
- Use the `/cleanup/docker` API endpoint
- Check system status with the "Status" button

## Development

### Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run: `python app.py`

### File Structure

```text
hub-helper/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container configuration
├── docker-compose.yml # Docker Compose setup
├── templates/         # HTML templates
├── static/           # Static assets
├── assets/           # Project assets and logos
└── test_analytics.py  # Analytics testing script
```

## 📈 Recent Updates

### Version 1.1.2 - Enhanced Navbar Button Animations

**New Features:**

- **Enhanced Button Animations** - Premium navbar button animations with modern CSS effects
- **Loading State Feedback** - Visual loading spinners for async operations (Cleanup, Status)
- **Success/Error Flash Feedback** - Color-coded button feedback for operation results
- **Press Effect Animation** - Tactile button press feedback with scale animations
- **Glass Morphism Design** - Premium navbar backdrop blur and gradient effects
- **Staggered Entrance Animation** - Sequential button appearance with smooth timing

**Button Enhancements:**

- **Refresh Button** - Enhanced with loading state and smooth reload transition
- **Cleanup Button** - Loading spinner during cleanup operation with success/error feedback
- **Status Button** - Loading state while fetching system information with visual confirmation
- **Logout Button** - Smooth transition animation before redirect
- **All Buttons** - Hover lift effects, ripple animations, and enhanced icon movements

**Visual Improvements:**

- **Glass Morphism Navbar** - Translucent background with backdrop blur effects
- **Gradient Button Backgrounds** - Subtle gradient overlays for premium appearance
- **Animated Background Pattern** - Slow-shifting colored gradient orbs in navbar background
- **Enhanced Hover States** - Improved hover animations with gradient color shifts
- **Modern CSS Transitions** - Smooth cubic-bezier timing functions for natural movement

**Technical Enhancements:**

- Enhanced JavaScript button feedback utilities
- Improved error handling with visual feedback
- Better loading state management for async operations
- Hardware-accelerated animations for smooth 60fps performance

### Version 1.1.0 - Analytics Integration & Modern UI

**New Features:**

- Added global analytics tracking with real-time animated counters
- Integrated external analytics API
- Added fallback local analytics tracking for reliability
- Visual deployment counters in navbar with GitHub and Docker Hub icons
- Interactive hover tooltips explaining counter functionality
- Premium animation system with floating effects and smooth transitions

**UI/UX Improvements:**

- Modern hover animations with lift, scale, and shimmer effects
- Multi-color pulse animations for counter updates (purple → green → yellow → blue)
- Floating animation with staggered timing for visual appeal
- Loading state animations with elegant pulsing effects
- Entrance animations with staggered slide-in from left
- Automatic counter refresh every 30 seconds with visual feedback

**Technical Improvements:**

- Fixed double-counting issues in analytics tracking
- Enhanced error handling for API connectivity
- Added analytics debug endpoints for troubleshooting
- Improved UI responsiveness across all screen sizes
- Hardware-accelerated animations using CSS transforms
- Optimized performance with 60fps smooth animations

**Technical Changes:**

- Added `/analytics/counters` endpoint for real-time data
- Added `/analytics/reset` endpoint for admin functions
- Added `/analytics/debug` endpoint for troubleshooting
- Implemented dual-source analytics (external + local backup)
- Added analytics testing utilities

## Changelog

### v1.1.4 - Sponsorship Integration (Latest)

- **Added comprehensive sponsorship support** - GitHub Sponsors, Buy Me a Coffee, Ko-fi, and PayPal integration
- **Enhanced navbar with sponsor dropdown** - Easy access to all sponsorship options with animated heart icon
- **Updated footer with donation links** - Multiple sponsorship platforms available in both main and login pages
- **Improved README documentation** - Added dedicated sponsorship section with beautiful badges
- **Modern UI enhancements** - Animated sponsorship buttons with heartbeat effects and hover animations

### v1.1.3 - Health Check Fix

- **Fixed critical health endpoint bug** - Resolved JSON serialization error causing 500 Internal Server Error
- **Improved health diagnostics** - Health endpoint now properly returns JSON response instead of HTML error page
- **Enhanced error handling** - Fixed Response object serialization issue in health check function
- **Better debugging** - Health endpoint now includes external API data when available

### v1.1.2 - Analytics Enhancement

- Enhanced analytics tracking with external API integration
- Added real-time global deployment counters
- Improved UI with modern animations and hover effects
- Fixed double-counting issues in analytics tracking

### v1.1.1 - UI & Performance

- Modern responsive UI with GitHub-themed dark interface
- Added persistent authentication with secure credential encryption
- Improved deployment progress feedback and error handling

### v1.1.0 - Core Features

- Initial release with GitHub and Docker Hub deployment automation
- Project discovery and version management
- Containerized deployment with Docker Compose support

## License

MIT License. See LICENSE for details.

## Support This Project ❤️

If you find Hub Helper useful, please consider supporting its development:

[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Sponsor-ff69b4?style=for-the-badge&logo=github)](https://github.com/sponsors/TheInfamousToTo)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/theinfamoustoto)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/theinfamoustoto)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/alsatrawi)

### 🌟 Sponsorship Tiers & Benefits

**🎯 $5/month** - Get a Sponsor badge on your profile  
**📧 $10/month** - Weekly newsletter with project updates  
**🏆 $25/month** - Logo/name in project README + private repo access + community chat  
**🎥 $30/month** - Access to exclusive videos, screencasts, and tutorials  
**💼 $100/month** - Logo on project website + pre-release builds + priority bug reports  
**🏢 $500/month** - Company license for commercial use  
**🤝 $1,000/month** - Direct support via your company chat app  

Your support helps maintain and improve this tool for the developer community! 🚀

### Why Support?

- 🔧 **Continuous Development** - Regular updates and new features
- 🐛 **Bug Fixes** - Quick resolution of issues and improvements
- 📚 **Documentation** - Better guides and tutorials
- 🌟 **New Features** - Community-requested enhancements
- 💡 **Innovation** - Research and development of cutting-edge deployment tools

Every contribution, no matter how small, makes a difference! Thank you for your support! 🙏

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for improvements or bug fixes.

## Acknowledgements

Built with Flask, Docker, and modern web technologies to streamline the deployment workflow for developers and teams.
