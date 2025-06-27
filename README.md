# Hub Helper

<div align="center">
  <img src="assets/hub-helper-main.png" alt="Hub Helper Logo" width="400">
  
  **Version 1.0**
  
  *A web-based application that automates the deployment of your projects to GitHub and Docker Hub with just a few clicks.*
  
  ![Version](https://img.shields.io/badge/version-1.0-blue.svg)
  ![Docker](https://img.shields.io/badge/docker-ready-green.svg)
  ![GitHub](https://img.shields.io/badge/github-integration-black.svg)
  ![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)
</div>

## Features

- 🚀 **One-Click Deployment**: Push to GitHub and Docker Hub simultaneously
- 🔐 **Secure Authentication**: OAuth integration with GitHub and Docker Hub
- 📁 **Project Discovery**: Automatically detects projects in your specified directory
- 🖥️ **Modern Web Interface**: Clean, responsive UI built with Bootstrap
- 🐳 **Containerized**: Runs as a Docker container with docker-compose
- 📝 **Git Integration**: Automatic commit and push with custom messages
- 🔧 **Docker Integration**: Automatic image building and pushing

## Prerequisites

- Docker and Docker Compose installed
- Projects directory with your code
- GitHub account (for GitHub deployments)
- Docker Hub account (for Docker deployments)

## Quick Start

1. **Clone/Download this project**
   ```bash
   git clone <repository-url>
   cd hub-helper
   ```

2. **Configure your projects path**
   Edit `docker-compose.yml` and change the volume mount to your projects directory:
   ```yaml
   volumes:
     - /path/to/your/projects:/projects  # Change this path
   ```

3. **Set up GitHub OAuth (Optional but recommended)**
   - Go to GitHub > Settings > Developer settings > OAuth Apps
   - Create a new OAuth App
   - Set Authorization callback URL to: `http://localhost:5414/auth/github/callback`
   - Update the environment variables in `docker-compose.yml`:
     ```yaml
     - GITHUB_CLIENT_ID=your-github-client-id
     - GITHUB_CLIENT_SECRET=your-github-client-secret
     ```

4. **Start the application**
   ```bash
   docker-compose up -d
   ```

5. **Access the application**
   Open your browser and go to `http://localhost:5414`

## Usage

### First Time Setup
1. Open the application in your browser
2. Login with your GitHub account (OAuth) or enter credentials manually
3. Enter your Docker Hub username and password
4. Click "Continue to Hub Helper"

### Deploying a Project
1. Select a project from the list
2. Specify the GitHub repository name (format: `username/repo-name`)
3. Specify the Docker Hub repository name
4. Add a commit message (optional)
5. Click "Deploy"

The application will:
- Add all files to git
- Commit with your message
- Push to GitHub
- Build Docker image
- Push to Docker Hub

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PROJECTS_PATH` | Path to your projects directory | Yes |
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID | No* |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret | No* |

*If GitHub OAuth is not configured, users will need to enter GitHub credentials manually.

### Volume Mounts

- `/projects` - Mount your local projects directory here
- `/var/run/docker.sock` - Required for Docker operations
- `/usr/bin/docker` - Required for Docker binary access

## Project Structure Requirements

For a project to be deployable:

**For GitHub deployment:**
- Project should be in a directory under your projects path
- Will automatically initialize Git if not already a Git repository

**For Docker deployment:**
- Project must contain a `Dockerfile`
- Dockerfile should be properly configured for your application

## Security Notes

- Docker Hub credentials are stored in session only (not persisted)
- GitHub tokens are stored in session only
- Change the `SECRET_KEY` in production
- Consider using GitHub OAuth for better security
- The application has access to Docker socket - run in trusted environment only

## Troubleshooting

### Common Issues

1. **Projects not showing up**
   - Check the projects path in docker-compose.yml
   - Ensure the directory exists and contains subdirectories

2. **Docker build/push fails**
   - Ensure Dockerfile exists in project
   - Check Docker Hub credentials
   - Verify Docker socket is properly mounted

3. **GitHub push fails**
   - Check GitHub repository exists
   - Verify authentication (OAuth or credentials)
   - Ensure proper repository name format (username/repo)

### Logs
```bash
# View application logs
docker-compose logs -f hub-helper
```

## Development

To run in development mode:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PROJECTS_PATH=/path/to/your/projects
export SECRET_KEY=dev-secret-key

# Run the application
python app.py
```

## License

MIT License - see LICENSE file for details.
