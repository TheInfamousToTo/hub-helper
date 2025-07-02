# Hub Helper

![Hub Helper](assets/hub-helper-main.png)

A streamlined deployment automation tool that simplifies pushing projects to GitHub and Docker Hub with a modern web interface, persistent authentication, containerized deployment, and **real-time global analytics tracking**.

## ✨ New Features

### 📊 **Global Analytics Counters**

- **Real-time deployment tracking** - Live counters showing total GitHub and Docker Hub deployments across all users
- **Integrated analytics API** - Connects to external analytics backend for global statistics
- **Fallback local tracking** - Maintains local analytics as backup when external API is unavailable
- **Visual counters in navbar** - GitHub and Docker Hub icons with live deployment counts
- **Accurate tracking** - Fixed double-counting issues for precise analytics

### 🔄 **Enhanced User Experience**

- **Persistent authentication** with secure credential encryption
- **Real-time deployment progress** with detailed step-by-step feedback
- **Improved error handling** and user feedback
- **Modern responsive UI** optimized for all screen sizes
- **Automatic counter updates** after successful deployments

## Features

• **Global Analytics** - real-time tracking of deployments across all users with live counters
• **Persistent Authentication** - securely stores GitHub OAuth tokens and Docker Hub credentials with encryption
• **Selective Deployment** - choose to deploy to GitHub, Docker Hub, or both with checkbox selection
• **Version Management** - semantic versioning support with automatic Git tagging and Docker image tagging
• **Project Discovery** - automatically detects projects with Git repositories and Dockerfiles
• **Modern UI** - GitHub-themed dark interface with responsive design and live analytics
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

- GitHub deployments counter (visible in navbar)
- Docker Hub deployments counter (visible in navbar)
- Live updates after each successful deployment

**Data Sources:**

- **Fallback**: Local file-based analytics for backup tracking
- **Endpoints**: `/analytics/counters` for current counts, `/analytics/reset` for admin reset

**Features:**

- Accurate tracking (fixed double-counting issues)
- Real-time updates across all users
- Persistent local backup
- API integration with error handling

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

### Version 1.1.0 - Analytics Integration

**New Features:**

- Added global analytics tracking with real-time counters
- Integrated external analytics API (hub-backend.satrawi.cc)
- Added fallback local analytics tracking
- Visual deployment counters in navbar with GitHub and Docker Hub icons

**Improvements:**

- Fixed double-counting issues in analytics tracking
- Enhanced error handling for API connectivity
- Added analytics debug endpoints
- Improved UI responsiveness and user feedback

**Technical Changes:**

- Added `/analytics/counters` endpoint for real-time data
- Added `/analytics/reset` endpoint for admin functions
- Added `/analytics/debug` endpoint for troubleshooting
- Implemented dual-source analytics (external + local backup)
- Added analytics testing utilities

## License

MIT License. See LICENSE for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for improvements or bug fixes.

## Acknowledgements

Built with Flask, Docker, and modern web technologies to streamline the deployment workflow for developers and teams.
