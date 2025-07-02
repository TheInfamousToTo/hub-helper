from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import subprocess
import json
import requests
from pathlib import Path
import git
from git import Repo
import docker
import logging
from datetime import datetime
from cryptography.fernet import Fernet
import base64

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Early startup logging
logger.info("Hub Helper Flask application initializing...")

# Configuration
PROJECTS_PATH = os.environ.get('PROJECTS_PATH', '/projects')
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
DATA_DIR = '/app/data'
CREDENTIALS_FILE = os.path.join(DATA_DIR, 'credentials.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Analytics configuration
ANALYTICS_API = 'https://hub-backend.satrawi.cc'
LOCAL_ANALYTICS_FILE = os.path.join(DATA_DIR, 'local_analytics.json')

def track_deployment_analytics(push_type):
    """Track deployment to external analytics API"""
    try:
        response = requests.post(
            f'{ANALYTICS_API}/click',
            json={
                'project_name': 'hub-helper',
                'push_type': push_type
            },
            timeout=5  # 5 second timeout
        )
        if response.status_code == 200:
            logger.info(f"Successfully tracked {push_type} deployment to external API")
        else:
            logger.warning(f"Failed to track {push_type} deployment: HTTP {response.status_code}")
    except Exception as e:
        logger.warning(f"Failed to track {push_type} deployment to external API: {e}")
    
    # Always update local analytics as backup
    update_local_analytics(push_type)

def update_local_analytics(push_type):
    """Update local analytics counter"""
    try:
        # Load existing counters
        if os.path.exists(LOCAL_ANALYTICS_FILE):
            with open(LOCAL_ANALYTICS_FILE, 'r') as f:
                analytics = json.load(f)
        else:
            analytics = {'github_count': 0, 'dockerhub_count': 0}
        
        # Update counter
        if push_type == 'github':
            analytics['github_count'] = analytics.get('github_count', 0) + 1
        elif push_type == 'dockerhub':
            analytics['dockerhub_count'] = analytics.get('dockerhub_count', 0) + 1
        
        # Save updated counters
        with open(LOCAL_ANALYTICS_FILE, 'w') as f:
            json.dump(analytics, f)
        
        logger.info(f"Updated local analytics: {push_type} count is now {analytics.get(push_type + '_count', 0)}")
        
    except Exception as e:
        logger.error(f"Failed to update local analytics for {push_type}: {e}")

def get_local_analytics():
    """Get local analytics counters"""
    try:
        if os.path.exists(LOCAL_ANALYTICS_FILE):
            with open(LOCAL_ANALYTICS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load local analytics: {e}")
    
    return {'github_count': 0, 'dockerhub_count': 0}

def get_encryption_key():
    """Get or create encryption key for storing credentials"""
    key_file = os.path.join(DATA_DIR, 'key.key')
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

def encrypt_data(data):
    """Encrypt sensitive data"""
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(json.dumps(data).encode()).decode()

def decrypt_data(encrypted_data):
    """Decrypt sensitive data"""
    key = get_encryption_key()
    f = Fernet(key)
    return json.loads(f.decrypt(encrypted_data.encode()).decode())

def save_credentials(github_token=None, dockerhub_creds=None):
    """Save credentials to file"""
    creds = {}
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                encrypted_data = f.read()
                if encrypted_data:
                    creds = decrypt_data(encrypted_data)
        except:
            creds = {}
    
    if github_token:
        creds['github_token'] = github_token
    if dockerhub_creds:
        creds['dockerhub_credentials'] = dockerhub_creds
    
    with open(CREDENTIALS_FILE, 'w') as f:
        f.write(encrypt_data(creds))

def load_credentials():
    """Load credentials from file"""
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                encrypted_data = f.read()
                if encrypted_data:
                    return decrypt_data(encrypted_data)
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
    return {}

def validate_dockerhub_credentials(dockerhub_creds):
    """Validate Docker Hub credentials by attempting to login"""
    try:
        client = docker.from_env()
        client.login(
            username=dockerhub_creds['username'],
            password=dockerhub_creds['password'],
            registry='https://index.docker.io/v1/'
        )
        return True
    except Exception as e:
        logger.error(f"Docker Hub credentials validation failed: {e}")
        return False

def validate_github_token(github_token):
    """Validate GitHub token by making a simple API call"""
    try:
        headers = {'Authorization': f'token {github_token}'}
        response = requests.get('https://api.github.com/user', headers=headers)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"GitHub token validation failed: {e}")
        return False

@app.route('/')
def index():
    """Main page - check if user is authenticated"""
    # Load saved credentials
    saved_creds = load_credentials()
    valid_github = False
    valid_dockerhub = False
    
    if saved_creds:
        # Validate and restore GitHub token
        if 'github_token' in saved_creds:
            github_token = saved_creds['github_token']
            if validate_github_token(github_token):
                session['github_token'] = github_token
                valid_github = True
                logger.info("GitHub session restored from persistent storage")
            else:
                logger.warning("Stored GitHub token is invalid, clearing...")
                
        # Validate and restore Docker Hub credentials
        if 'dockerhub_credentials' in saved_creds:
            dockerhub_creds = saved_creds['dockerhub_credentials']
            if validate_dockerhub_credentials(dockerhub_creds):
                session['dockerhub_credentials'] = dockerhub_creds
                valid_dockerhub = True
                logger.info("Docker Hub session restored from persistent storage")
            else:
                logger.warning("Stored Docker Hub credentials are invalid, clearing...")
                
        # If any credentials are invalid, remove them from storage
        if not valid_github or not valid_dockerhub:
            new_creds = {}
            if valid_github:
                new_creds['github_token'] = saved_creds['github_token']
            if valid_dockerhub:
                new_creds['dockerhub_credentials'] = saved_creds['dockerhub_credentials']
            
            if new_creds:
                with open(CREDENTIALS_FILE, 'w') as f:
                    f.write(encrypt_data(new_creds))
            else:
                # Remove the file if no valid credentials remain
                if os.path.exists(CREDENTIALS_FILE):
                    os.remove(CREDENTIALS_FILE)
    
    if 'github_token' not in session or 'dockerhub_credentials' not in session:
        return render_template('login.html')
    
    # Get project folders
    projects = get_project_folders()
    return render_template('index.html', projects=projects)

@app.route('/login')
def login():
    """Display login page"""
    return render_template('login.html')

@app.route('/auth/github')
def github_auth():
    """Redirect to GitHub OAuth"""
    if not GITHUB_CLIENT_ID:
        return jsonify({'error': 'GitHub OAuth not configured'}), 500
    
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=repo"
    return redirect(github_auth_url)

@app.route('/auth/github/callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code received'}), 400
    
    # Exchange code for access token
    token_url = 'https://github.com/login/oauth/access_token'
    token_data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    }
    
    response = requests.post(token_url, data=token_data, headers={'Accept': 'application/json'})
    token_info = response.json()
    
    if 'access_token' in token_info:
        github_token = token_info['access_token']
        session['github_token'] = github_token
        # Save GitHub token to persistent storage
        save_credentials(github_token=github_token)
        return redirect(url_for('index'))
    else:
        return jsonify({'error': 'Failed to get access token'}), 400

@app.route('/auth/dockerhub', methods=['POST'])
def dockerhub_auth():
    """Store Docker Hub credentials"""
    username = request.json.get('username')
    password = request.json.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    # Test Docker Hub login
    dockerhub_creds = {'username': username, 'password': password}
    
    if validate_dockerhub_credentials(dockerhub_creds):
        session['dockerhub_credentials'] = dockerhub_creds
        # Save Docker Hub credentials to persistent storage
        save_credentials(dockerhub_creds=dockerhub_creds)
        logger.info(f"Docker Hub login successful for user: {username}")
        return jsonify({'success': True})
    else:
        logger.error(f"Docker Hub login failed for user: {username}")
        return jsonify({'error': 'Invalid Docker Hub credentials'}), 401

@app.route('/projects')
def get_projects():
    """Get list of project folders"""
    projects = get_project_folders()
    return jsonify(projects)

@app.route('/deploy', methods=['POST'])
def deploy():
    """Deploy project to GitHub and Docker Hub"""
    data = request.json
    project_name = data.get('project_name')
    github_repo = data.get('github_repo')
    dockerhub_repo = data.get('dockerhub_repo')
    project_version = data.get('project_version', 'v1.0.0')
    commit_message = data.get('commit_message', f'Release {project_name} {project_version}')
    
    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400
    
    if not github_repo and not dockerhub_repo:
        return jsonify({'error': 'At least one deployment target is required'}), 400
    
    project_path = os.path.join(PROJECTS_PATH, project_name)
    if not os.path.exists(project_path):
        return jsonify({'error': 'Project not found'}), 404
    
    try:
        result = {'steps': []}
        
        # Step 1: Git operations
        if github_repo:
            git_result = push_to_github(project_path, github_repo, commit_message, project_version)
            result['steps'].append(git_result)
        
        # Step 2: Docker operations  
        if dockerhub_repo:
            docker_result = push_to_dockerhub(project_path, dockerhub_repo, project_version)
            result['steps'].append(docker_result)
            
            # Automatic cleanup after Docker operations
            if docker_result['success']:
                try:
                    cleanup_old_containers()
                    logger.info("Automatic cleanup completed after Docker deployment")
                except Exception as cleanup_error:
                    logger.warning(f"Automatic cleanup failed: {cleanup_error}")
        
        result['success'] = True
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_project_folders():
    """Get list of project folders"""
    projects = []
    if os.path.exists(PROJECTS_PATH):
        for item in os.listdir(PROJECTS_PATH):
            item_path = os.path.join(PROJECTS_PATH, item)
            if os.path.isdir(item_path):
                projects.append({
                    'name': item,
                    'path': item_path,
                    'has_git': os.path.exists(os.path.join(item_path, '.git')),
                    'has_dockerfile': os.path.exists(os.path.join(item_path, 'Dockerfile'))
                })
    return projects

def push_to_github(project_path, repo_name, commit_message, project_version='v1.0.0'):
    """Push project to GitHub with version tagging"""
    try:
        # Fix Git safe directory issue first
        subprocess.run(['git', 'config', '--global', '--add', 'safe.directory', project_path], 
                      capture_output=True, check=False)
        
        # Initialize or open git repo
        if not os.path.exists(os.path.join(project_path, '.git')):
            repo = Repo.init(project_path)
        else:
            repo = Repo(project_path)
        
        # Configure git user if not set (required for commits)
        try:
            repo.config_reader().get_value("user", "name")
        except:
            repo.config_writer().set_value("user", "name", "Hub Helper").release()
            repo.config_writer().set_value("user", "email", "hub-helper@automation.local").release()
        
        # Create or update version file in the project
        version_file_path = os.path.join(project_path, 'version')
        with open(version_file_path, 'w') as f:
            f.write(project_version)
        
        # Add all files
        repo.git.add('.')
        
        # Commit changes
        try:
            repo.index.commit(commit_message)
            committed = True
        except Exception as e:
            # Check if it's because there are no changes
            if "nothing to commit" in str(e).lower():
                committed = False
            else:
                raise e
        
        # Create Git tag for version
        try:
            # Delete existing tag if it exists
            existing_tags = [tag.name for tag in repo.tags]
            if project_version in existing_tags:
                repo.delete_tag(project_version)
            
            # Create new tag
            repo.create_tag(project_version, message=f'Release {project_version}')
            tagged = True
        except Exception as e:
            logger.warning(f"Failed to create tag {project_version}: {e}")
            tagged = False
        
        # Set remote if not exists
        github_token = session.get('github_token')
        remote_url = f"https://{github_token}@github.com/{repo_name}.git"
        
        try:
            origin = repo.remote('origin')
            origin.set_url(remote_url)
        except:
            origin = repo.create_remote('origin', remote_url)
        
        # Push to GitHub
        current_branch = repo.active_branch.name if repo.heads else 'main'
        origin.push(current_branch)
        
        # Push tags
        if tagged:
            try:
                origin.push(tags=True)
                tag_pushed = True
            except Exception as e:
                logger.warning(f"Failed to push tags: {e}")
                tag_pushed = False
        else:
            tag_pushed = False
        
        message = f'Successfully pushed to {repo_name}'
        if tagged and tag_pushed:
            message += f' with tag {project_version}'
        
        # Track successful GitHub deployment
        track_deployment_analytics('github')
        
        return {
            'step': 'GitHub Push',
            'success': True,
            'message': message,
            'committed': committed,
            'tagged': tagged and tag_pushed,
            'version': project_version
        }
        
    except Exception as e:
        return {
            'step': 'GitHub Push',
            'success': False,
            'error': str(e)
        }

def push_to_dockerhub(project_path, repo_name, project_version='v1.0.0'):
    """Build and push Docker image to Docker Hub with version tagging"""
    client = None
    built_image = None
    
    try:
        dockerfile_path = os.path.join(project_path, 'Dockerfile')
        if not os.path.exists(dockerfile_path):
            return {
                'step': 'Docker Push',
                'success': False,
                'error': 'Dockerfile not found in project'
            }
        
        client = docker.from_env()
        dockerhub_creds = session.get('dockerhub_credentials')
        
        # Login to Docker Hub
        client.login(
            username=dockerhub_creds['username'],
            password=dockerhub_creds['password'],
            registry='https://index.docker.io/v1/'
        )
        
        # Clean version for Docker tag (remove 'v' prefix if present)
        docker_version = project_version.lstrip('v')
        
        # Build image with multiple tags
        image_name = f"{dockerhub_creds['username']}/{repo_name}"
        
        # Build image with cleanup options
        built_image, build_logs = client.images.build(
            path=project_path,
            tag=f"{image_name}:latest",
            rm=True,  # Remove intermediate containers
            forcerm=True,  # Always remove intermediate containers
            pull=True,  # Always attempt to pull newer version of base image
            nocache=False  # Use cache for faster builds
        )
        
        # Tag with version
        built_image.tag(image_name, docker_version)
        
        # Push both latest and version tags
        push_logs_latest = client.images.push(image_name, tag='latest')
        push_logs_version = client.images.push(image_name, tag=docker_version)
        
        # Clean up: remove old/unused images to save space
        try:
            # Remove dangling images (untagged intermediate images)
            client.images.prune(filters={'dangling': True})
            logger.info("Cleaned up dangling Docker images")
        except Exception as cleanup_error:
            logger.warning(f"Failed to clean up dangling images: {cleanup_error}")
        
        # Track successful Docker Hub deployment
        track_deployment_analytics('dockerhub')
        
        return {
            'step': 'Docker Push',
            'success': True,
            'message': f'Successfully pushed to {image_name}:latest and {image_name}:{docker_version}',
            'version': docker_version,
            'tags': ['latest', docker_version]
        }
        
    except Exception as e:
        return {
            'step': 'Docker Push',
            'success': False,
            'error': str(e)
        }
    finally:
        # Additional cleanup in case of any issues
        if client:
            try:
                # Clean up any stopped containers from the build process
                containers = client.containers.list(all=True, filters={'status': 'exited'})
                for container in containers:
                    # Only remove containers created in the last hour to avoid removing unrelated containers
                    from datetime import datetime, timezone
                    created_time = datetime.fromisoformat(container.attrs['Created'].replace('Z', '+00:00'))
                    current_time = datetime.now(timezone.utc)
                    if (current_time - created_time).total_seconds() < 3600:  # 1 hour
                        try:
                            container.remove(force=True)
                            logger.info(f"Removed container: {container.short_id}")
                        except Exception as remove_error:
                            logger.warning(f"Failed to remove container {container.short_id}: {remove_error}")
            except Exception as final_cleanup_error:
                logger.warning(f"Failed during final cleanup: {final_cleanup_error}")
            
            # Close the Docker client connection
            try:
                client.close()
            except:
                pass

@app.route('/logout')
def logout():
    """Clear session and persistent credentials"""
    session.clear()
    # Remove persistent credentials file
    if os.path.exists(CREDENTIALS_FILE):
        os.remove(CREDENTIALS_FILE)
    return redirect(url_for('login'))

@app.route('/auth/status')
def auth_status():
    """Check authentication status"""
    status = {
        'github_authenticated': 'github_token' in session,
        'dockerhub_authenticated': 'dockerhub_credentials' in session,
        'persistent_storage_exists': os.path.exists(CREDENTIALS_FILE)
    }
    
    # Load persistent credentials info without exposing sensitive data
    saved_creds = load_credentials()
    if saved_creds:
        status['persistent_github'] = 'github_token' in saved_creds
        status['persistent_dockerhub'] = 'dockerhub_credentials' in saved_creds
        
        # Validate stored credentials
        if 'github_token' in saved_creds:
            status['github_token_valid'] = validate_github_token(saved_creds['github_token'])
        if 'dockerhub_credentials' in saved_creds:
            status['dockerhub_creds_valid'] = validate_dockerhub_credentials(saved_creds['dockerhub_credentials'])
    
    return jsonify(status)

@app.route('/version')
def get_version():
    """Get application version"""
    try:
        with open('version', 'r') as f:
            version = f.read().strip()
        return jsonify({'version': version})
    except:
        return jsonify({'version': 'v1.0'})

@app.route('/cleanup/docker', methods=['POST'])
def cleanup_docker():
    """Clean up Docker containers and images"""
    try:
        client = docker.from_env()
        cleanup_results = {
            'containers_removed': 0,
            'images_removed': 0,
            'space_reclaimed': '0 MB'
        }
        
        # Remove stopped containers
        containers = client.containers.list(all=True, filters={'status': 'exited'})
        for container in containers:
            try:
                container.remove(force=True)
                cleanup_results['containers_removed'] += 1
                logger.info(f"Removed stopped container: {container.short_id}")
            except Exception as e:
                logger.warning(f"Failed to remove container {container.short_id}: {e}")
        
        # Remove created but not started containers
        created_containers = client.containers.list(all=True, filters={'status': 'created'})
        for container in created_containers:
            try:
                container.remove(force=True)
                cleanup_results['containers_removed'] += 1
                logger.info(f"Removed created container: {container.short_id}")
            except Exception as e:
                logger.warning(f"Failed to remove container {container.short_id}: {e}")
        
        # Remove dangling images
        try:
            pruned = client.images.prune(filters={'dangling': True})
            cleanup_results['images_removed'] = len(pruned.get('ImagesDeleted', []))
            space_reclaimed = pruned.get('SpaceReclaimed', 0)
            cleanup_results['space_reclaimed'] = f"{space_reclaimed / 1024 / 1024:.2f} MB"
            logger.info(f"Removed {cleanup_results['images_removed']} dangling images, reclaimed {cleanup_results['space_reclaimed']}")
        except Exception as e:
            logger.warning(f"Failed to prune images: {e}")
        
        # Close client
        client.close()
        
        return jsonify({
            'success': True,
            'message': f"Cleanup completed: {cleanup_results['containers_removed']} containers and {cleanup_results['images_removed']} images removed",
            'details': cleanup_results
        })
        
    except Exception as e:
        logger.error(f"Docker cleanup failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/system/status')
def system_status():
    """Get system status including Docker resource usage"""
    try:
        client = docker.from_env()
        
        # Get container counts
        running_containers = len(client.containers.list())
        all_containers = len(client.containers.list(all=True))
        stopped_containers = all_containers - running_containers
        
        # Get image counts
        all_images = len(client.images.list())
        dangling_images = len(client.images.list(filters={'dangling': True}))
        
        # Get basic system info
        system_info = client.info()
        
        client.close()
        
        return jsonify({
            'containers': {
                'running': running_containers,
                'stopped': stopped_containers,
                'total': all_containers
            },
            'images': {
                'total': all_images,
                'dangling': dangling_images
            },
            'docker_version': system_info.get('ServerVersion', 'Unknown'),
            'cleanup_recommended': stopped_containers > 5 or dangling_images > 10
        })
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return jsonify({
            'error': str(e),
            'containers': {'running': 0, 'stopped': 0, 'total': 0},
            'images': {'total': 0, 'dangling': 0},
            'docker_version': 'Unknown',
            'cleanup_recommended': False
        }), 500

def cleanup_old_containers():
    """Automatically clean up old containers created during builds"""
    try:
        client = docker.from_env()
        removed_count = 0
        
        # Remove containers in 'created' state (often leftover from builds)
        created_containers = client.containers.list(all=True, filters={'status': 'created'})
        for container in created_containers:
            try:
                # Check if container is older than 10 minutes
                from datetime import datetime, timezone
                created_time = datetime.fromisoformat(container.attrs['Created'].replace('Z', '+00:00'))
                current_time = datetime.now(timezone.utc)
                if (current_time - created_time).total_seconds() > 600:  # 10 minutes
                    container.remove(force=True)
                    removed_count += 1
                    logger.info(f"Auto-cleanup: Removed old created container {container.short_id}")
            except Exception as e:
                logger.warning(f"Failed to remove created container {container.short_id}: {e}")
        
        # Remove exited containers older than 30 minutes
        exited_containers = client.containers.list(all=True, filters={'status': 'exited'})
        for container in exited_containers:
            try:
                created_time = datetime.fromisoformat(container.attrs['Created'].replace('Z', '+00:00'))
                current_time = datetime.now(timezone.utc)
                if (current_time - created_time).total_seconds() > 1800:  # 30 minutes
                    container.remove(force=True)
                    removed_count += 1
                    logger.info(f"Auto-cleanup: Removed old exited container {container.short_id}")
            except Exception as e:
                logger.warning(f"Failed to remove exited container {container.short_id}: {e}")
        
        # Clean up dangling images if we removed containers
        if removed_count > 0:
            try:
                client.images.prune(filters={'dangling': True})
                logger.info("Auto-cleanup: Pruned dangling images")
            except Exception as e:
                logger.warning(f"Failed to prune images during auto-cleanup: {e}")
        
        client.close()
        logger.info(f"Auto-cleanup completed: {removed_count} containers removed")
        
    except Exception as e:
        logger.error(f"Auto-cleanup failed: {e}")

@app.route('/analytics/debug')
def debug_analytics():
    """Debug endpoint to check analytics API status"""
    debug_info = {
        'analytics_api': ANALYTICS_API,
        'local_analytics': get_local_analytics(),
        'endpoints_tested': []
    }
    
    # Test different endpoints
    possible_endpoints = [
        f'{ANALYTICS_API}/stats/hub-helper',
        f'{ANALYTICS_API}/stats',
        f'{ANALYTICS_API}/analytics/hub-helper',
        f'{ANALYTICS_API}/analytics',
        f'{ANALYTICS_API}/health'
    ]
    
    for endpoint in possible_endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            debug_info['endpoints_tested'].append({
                'url': endpoint,
                'status_code': response.status_code,
                'content_length': len(response.text),
                'headers': dict(response.headers)
            })
        except Exception as e:
            debug_info['endpoints_tested'].append({
                'url': endpoint,
                'error': str(e)
            })
    
    return jsonify(debug_info)

@app.route('/analytics/counters')
def get_analytics_counters():
    """Get analytics counters from external API with fallback"""
    try:
        # The working endpoint is /analytics/hub-helper
        response = requests.get(f'{ANALYTICS_API}/analytics/hub-helper', timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Successfully fetched analytics from external API")
            return jsonify({
                'success': True,
                'github_count': data.get('github_clicks', 0),
                'dockerhub_count': data.get('dockerhub_clicks', 0),
                'source': 'external_api',
                'total_clicks': data.get('total_clicks', 0)
            })
        else:
            logger.debug(f"External API returned {response.status_code}")
    except Exception as e:
        logger.warning(f"Failed to fetch analytics from external API: {e}")
    
    # Fallback: use local analytics
    logger.info("Using local analytics counters as fallback")
    local_analytics = get_local_analytics()
    return jsonify({
        'success': True,
        'github_count': local_analytics.get('github_count', 0),
        'dockerhub_count': local_analytics.get('dockerhub_count', 0),
        'source': 'local_backup'
    })

@app.route('/analytics/reset', methods=['POST'])
def reset_analytics():
    """Reset analytics counters (local only)"""
    try:
        # Reset local analytics file
        analytics = {'github_count': 0, 'dockerhub_count': 0}
        
        with open(LOCAL_ANALYTICS_FILE, 'w') as f:
            json.dump(analytics, f)
        
        logger.info("Analytics counters reset successfully")
        
        return jsonify({
            'success': True,
            'message': 'Local analytics counters reset to zero',
            'github_count': 0,
            'dockerhub_count': 0
        })
    except Exception as e:
        logger.error(f"Failed to reset analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Configure logging for production
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/app/data/hub-helper.log')
        ]
    )
    
    logger.info("Starting Hub Helper application...")
    logger.info(f"Projects path: {PROJECTS_PATH}")
    logger.info(f"Data directory: {DATA_DIR}")
    
    # Check if required environment variables are set
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        logger.warning("GitHub OAuth credentials not configured - OAuth login will not work")
    else:
        logger.info("GitHub OAuth configured successfully")
    
    # Check if projects directory exists
    if os.path.exists(PROJECTS_PATH):
        logger.info(f"Projects directory found: {PROJECTS_PATH}")
    else:
        logger.warning(f"Projects directory not found: {PROJECTS_PATH}")
    
    # Start the Flask application
    logger.info("Starting Flask server on 0.0.0.0:5414")
    app.run(host='0.0.0.0', port=5414, debug=False)
