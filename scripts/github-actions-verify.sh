#!/bin/bash
# GitHub Actions Setup Helper Script
# Run this script to help verify GitHub Actions setup for v7 deployment

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

log_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

log_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║ Stock Debate Advisor v7 - GitHub Actions Setup Verification ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check 1: Workflow file exists
echo -e "${BLUE}[1/8] Checking workflow file...${NC}"
if [ -f ".github/workflows/deploy-dev.yml" ]; then
    log_success "Workflow file exists: .github/workflows/deploy-dev.yml"
else
    log_error "Workflow file not found at .github/workflows/deploy-dev.yml"
    echo "      Creating directory structure..."
    mkdir -p .github/workflows
    log_warn "Please download or create the workflow file"
fi
echo ""

# Check 2: v7 directory structure
echo -e "${BLUE}[2/8] Checking v7 directory structure...${NC}"
required_dirs=("v7/cdk" "v7/frontend" "v7/ai-service" "v7/data_store")
all_exist=true

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir"
    else
        echo "  ✗ $dir (missing)"
        all_exist=false
    fi
done

if [ "$all_exist" = true ]; then
    log_success "All required v7 directories exist"
else
    log_error "Some required directories are missing"
fi
echo ""

# Check 3: AWS CLI availability
echo -e "${BLUE}[3/8] Checking AWS CLI...${NC}"
if command -v aws &> /dev/null; then
    VERSION=$(aws --version)
    log_success "AWS CLI installed: $VERSION"
else
    log_warn "AWS CLI not found - needed for verification commands"
    log_info "Install from: https://aws.amazon.com/cli/"
fi
echo ""

# Check 4: GitHub CLI availability
echo -e "${BLUE}[4/8] Checking GitHub CLI...${NC}"
if command -v gh &> /dev/null; then
    VERSION=$(gh --version)
    log_success "GitHub CLI installed: $VERSION"
else
    log_warn "GitHub CLI not found - optional but helpful"
    log_info "Install from: https://cli.github.com/"
fi
echo ""

# Check 5: v7 package.json files
echo -e "${BLUE}[5/8] Checking package.json files...${NC}"
package_files=("v7/cdk/package.json" "v7/frontend/package.json")

for pkg in "${package_files[@]}"; do
    if [ -f "$pkg" ]; then
        echo "  ✓ $pkg"
    else
        log_warn "  Missing: $pkg"
    fi
done
echo ""

# Check 6: AWS credentials
echo -e "${BLUE}[6/8] Checking AWS credentials...${NC}"
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    log_success "Local AWS credentials configured"
    log_info "Note: GitHub Actions uses GitHub Secrets, not local credentials"
else
    log_warn "No local AWS credentials found (this is OK for GitHub Actions)"
fi
echo ""

# Check 7: Git repository
echo -e "${BLUE}[7/8] Checking Git repository...${NC}"
if [ -d ".git" ]; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    REMOTE=$(git config --get remote.origin.url | grep -o '[^/]*$' | sed 's/.git$//')
    log_success "Git repository found (branch: $BRANCH, repo: $REMOTE)"
else
    log_error "Not in a Git repository"
fi
echo ""

# Check 8: GitHub Actions secrets configured
echo -e "${BLUE}[8/8] Checking GitHub Actions setup...${NC}"
if command -v gh &> /dev/null; then
    log_info "To view/add GitHub Secrets, run:"
    log_info "  gh secret list  (view existing secrets)"
    log_info "  gh secret set SECRET_NAME -b 'secret_value'  (add new secret)"
else
    log_warn "GitHub CLI not available - use GitHub web interface to add secrets"
    log_info "Go to: Settings → Secrets and variables → Actions"
fi
echo ""

# Final summary
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║ Setup Verification Complete                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Add GitHub Secrets (if not already done):"
echo "   - AWS_ACCESS_KEY_ID"
echo "   - AWS_SECRET_ACCESS_KEY"
echo "   - AWS_ACCOUNT_ID"
echo ""
echo "2. Verify workflow file is in place:"
echo "   .github/workflows/deploy-dev.yml"
echo ""
echo "3. Push changes to trigger workflow:"
echo "   git add ."
echo "   git commit -m 'Initial v7 deployment setup'"
echo "   git push origin main"
echo ""
echo "4. Monitor deployment:"
echo "   - Go to GitHub Actions tab"
echo "   - Watch 'Deploy v7 to Development' workflow"
echo ""

echo -e "${YELLOW}For detailed setup instructions, see:${NC}"
echo "  - v7/GITHUB_ACTIONS_SETUP.md"
echo "  - v7/GITHUB_ACTIONS_DEPLOYMENT.md"
echo "  - v7/DEPLOYMENT_QUICK_REFERENCE.md"
echo ""
