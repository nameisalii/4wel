#!/bin/bash
# Script to push project to GitHub

set -e

echo "=========================================="
echo "Pushing Project to GitHub"
echo "=========================================="
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not available. Please install Xcode Command Line Tools first."
    echo "   Run: xcode-select --install"
    exit 1
fi

# Initialize git if not already initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
    echo ""
fi

# Check if there are changes to commit
if [ -z "$(git status --porcelain)" ]; then
    echo "ℹ️  No changes to commit. Repository is up to date."
else
    echo "📝 Adding files to git..."
    git add .
    echo "✅ Files added"
    echo ""
    
    echo "💾 Committing changes..."
    git commit -m "Add robot navigation training project with extended training scripts

- Single robot and multi-robot navigation training
- Extended training scripts for improved performance
- MCAP recording support for Foxglove visualization
- PPO-based reinforcement learning implementation"
    echo "✅ Changes committed"
    echo ""
fi

# Check if remote is configured
if git remote get-url origin &> /dev/null; then
    REMOTE_URL=$(git remote get-url origin)
    echo "🔗 Remote repository found: $REMOTE_URL"
    echo ""
    echo "🚀 Pushing to GitHub..."
    git push -u origin main 2>&1 || git push -u origin master 2>&1
    echo ""
    echo "✅ Successfully pushed to GitHub!"
else
    echo "⚠️  No remote repository configured."
    echo ""
    echo "To push to GitHub, you need to:"
    echo "1. Create a new repository on GitHub (https://github.com/new)"
    echo "2. Run one of these commands:"
    echo ""
    echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    echo "Or if you already have a repository URL, run:"
    echo "   git remote add origin YOUR_GITHUB_REPO_URL"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    read -p "Do you want to add a remote repository now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your GitHub repository URL: " REPO_URL
        if [ ! -z "$REPO_URL" ]; then
            git remote add origin "$REPO_URL"
            git branch -M main
            echo ""
            echo "🚀 Pushing to GitHub..."
            git push -u origin main
            echo ""
            echo "✅ Successfully pushed to GitHub!"
        else
            echo "❌ No URL provided. Exiting."
        fi
    fi
fi

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="

