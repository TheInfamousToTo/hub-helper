#!/bin/bash

# Hub Helper - Git Configuration Fix
# Run this script if you encounter Git ownership issues

echo "🔧 Fixing Git Configuration for Hub Helper"
echo "=" * 50

# Set global safe directory for all repositories
echo "Setting safe.directory for all paths..."
git config --global --add safe.directory '*'

# Set default user information
echo "Setting default Git user information..."
git config --global user.name "Hub Helper"
git config --global user.email "hub-helper@automation.local"

# Fix specific project directories if they exist
echo "Fixing common project directories..."
if [ -d "/projects" ]; then
    for project in /projects/*; do
        if [ -d "$project" ]; then
            echo "  Adding safe directory: $project"
            git config --global --add safe.directory "$project"
        fi
    done
fi

echo "✅ Git configuration fixed!"
echo "You can now deploy your projects without ownership errors."
echo ""
echo "Current Git configuration:"
git config --global --list | grep -E "(safe.directory|user.name|user.email)"
