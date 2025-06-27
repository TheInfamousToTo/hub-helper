# Hub Helper

![Hub Helper](assets/hub-helper-main.png)

A streamlined deployment automation tool that simplifies pushing projects to GitHub and Docker Hub with a modern web interface, persistent authentication, and containerized deployment.

## Features

• **Persistent Authentication** - securely stores GitHub OAuth tokens and Docker Hub credentials with encryption
• **Selective Deployment** - choose to deploy to GitHub, Docker Hub, or both with checkbox selection
• **Version Management** - semantic versioning support with automatic Git tagging and Docker image tagging
• **Project Discovery** - automatically detects projects with Git repositories and Dockerfiles
• **Modern UI** - GitHub-themed dark interface with responsive design
• **Containerized** - fully containerized deployment with Docker Compose support
• **Git Integration** - automatic Git configuration and safe directory handling
• **Debug Tools** - built-in debugging endpoints and storage management utilities

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
   docker-compose up -d --build
   ```

4. **Access the Interface**
   - Open http://localhost:5414
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
    build: .
    ports:
      - "5414:5414"
    volumes:
      - /home/toto:/projects
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker:ro
      - hub-helper-data:/app/data
    environment:
      - PROJECTS_PATH=/projects
      - SECRET_KEY=your-secret-key
      - GITHUB_CLIENT_ID=your-client-id
      - GITHUB_CLIENT_SECRET=your-client-secret
    restart: unless-stopped
```

## Security Features

• **Credential Encryption**: All stored credentials are encrypted using Fernet symmetric encryption
• **Session Management**: Secure session handling with Flask sessions
• **Token Validation**: GitHub tokens and Docker Hub credentials are validated before storage
• **Safe Git Operations**: Automatic Git configuration and safe directory handling

## API Endpoints

• `GET /`: Main application interface
• `GET /version`: Application version information
• `GET /auth/status`: Authentication status check
• `GET /projects`: List discovered projects
• `POST /deploy`: Deploy project to selected targets
• `GET /debug/storage`: Debug persistent storage (development)

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
```

## Development

### Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run: `python app.py`

### File Structure

```
hub-helper/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container configuration
├── docker-compose.yml # Docker Compose setup
├── templates/         # HTML templates
├── static/           # Static assets
└── assets/           # Project assets and logos
```

## License

MIT License. See LICENSE for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for improvements or bug fixes.

## Acknowledgements

Built with Flask, Docker, and modern web technologies to streamline the deployment workflow for developers and teams.
