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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECTS_PATH = os.environ.get('PROJECTS_PATH', '/projects')
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
DATA_DIR = '/app/data'
CREDENTIALS_FILE = os.path.join(DATA_DIR, 'credentials.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

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
    commit_message = data.get('commit_message', f'Update {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400
    
    project_path = os.path.join(PROJECTS_PATH, project_name)
    if not os.path.exists(project_path):
        return jsonify({'error': 'Project not found'}), 404
    
    try:
        result = {'steps': []}
        
        # Step 1: Git operations
        if github_repo:
            git_result = push_to_github(project_path, github_repo, commit_message)
            result['steps'].append(git_result)
        
        # Step 2: Docker operations  
        if dockerhub_repo:
            docker_result = push_to_dockerhub(project_path, dockerhub_repo)
            result['steps'].append(docker_result)
        
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

def push_to_github(project_path, repo_name, commit_message):
    """Push project to GitHub"""
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
        
        return {
            'step': 'GitHub Push',
            'success': True,
            'message': f'Successfully pushed to {repo_name}',
            'committed': committed
        }
        
    except Exception as e:
        return {
            'step': 'GitHub Push',
            'success': False,
            'error': str(e)
        }

def push_to_dockerhub(project_path, repo_name):
    """Build and push Docker image to Docker Hub"""
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
        
        # Build image
        image, build_logs = client.images.build(
            path=project_path,
            tag=f"{dockerhub_creds['username']}/{repo_name}:latest"
        )
        
        # Push image
        push_logs = client.images.push(
            f"{dockerhub_creds['username']}/{repo_name}",
            tag='latest'
        )
        
        return {
            'step': 'Docker Push',
            'success': True,
            'message': f'Successfully pushed to {dockerhub_creds["username"]}/{repo_name}:latest'
        }
        
    except Exception as e:
        return {
            'step': 'Docker Push',
            'success': False,
            'error': str(e)
        }

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5414, debug=True)
