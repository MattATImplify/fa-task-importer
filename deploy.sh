#!/bin/bash

echo "🚀 Deploying FA Task Importer to regularcleaning.facilityapps.co.uk"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git not initialized. Run: git init"
    exit 1
fi

# Check if we have a remote
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "📝 Setting up GitHub repository..."
    echo "1. Create a new repository on GitHub: https://github.com/new"
    echo "2. Name it: fa-task-importer"
    echo "3. Don't initialize with README"
    echo "4. Copy the repository URL"
    echo ""
    read -p "Enter your GitHub repository URL: " REPO_URL
    git remote add origin $REPO_URL
fi

# Commit any changes
echo "📦 Committing changes..."
git add .
git commit -m "Deploy: $(date)"

# Push to GitHub
echo "⬆️ Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "🌐 Next steps:"
echo "1. Go to https://share.streamlit.io"
echo "2. Click 'New app'"
echo "3. Connect your GitHub repository"
echo "4. Set app URL to: fa-task-importer"
echo "5. Add secrets in Streamlit Cloud:"
echo "   - auth.password: Your secure password"
echo "   - production.FA_DOMAIN: regularcleaning.facilityapps.com"
echo "   - production.FA_TOKEN: Your API token"
echo "6. Configure custom domain: regularcleaning.facilityapps.co.uk"
echo ""
echo "📖 Full instructions: DEPLOYMENT.md"
