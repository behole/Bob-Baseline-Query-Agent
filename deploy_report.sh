#!/bin/bash
#
# Deploy GEO Report to Cloudflare Pages
# Usage: ./deploy_report.sh <brand_name> <report_file.html>
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ $# -lt 2 ]; then
    echo -e "${RED}Usage: $0 <brand_name> <report_file.html>${NC}"
    echo ""
    echo "Example:"
    echo "  $0 nike nike_geo_report.html"
    echo ""
    echo "This will deploy to: https://<brand_name>.watermelonghost.com/<brand_name>_report_<date>"
    exit 1
fi

BRAND_NAME="$1"
REPORT_FILE="$2"

# Validate inputs
if [ ! -f "$REPORT_FILE" ]; then
    echo -e "${RED}Error: Report file '$REPORT_FILE' not found!${NC}"
    exit 1
fi

# Generate deployment filename with date
DATE=$(date +%Y-%m-%d)
DEPLOY_FILENAME="${BRAND_NAME}_report_${DATE}.html"

# Cloudflare worker directory
CF_DIR="/Users/jjoosshhmbpm1/reports-worker/watermelonghost/public"

if [ ! -d "$CF_DIR" ]; then
    echo -e "${RED}Error: Cloudflare directory not found: $CF_DIR${NC}"
    exit 1
fi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          📊 GEO Report Cloudflare Deployment                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${BLUE}Brand:${NC}       $BRAND_NAME"
echo -e "${BLUE}Source:${NC}      $REPORT_FILE"
echo -e "${BLUE}Deploy as:${NC}   $DEPLOY_FILENAME"
echo -e "${BLUE}Location:${NC}    $CF_DIR/"
echo ""

# Copy report to Cloudflare public directory
echo -e "${BLUE}Step 1:${NC} Copying report to Cloudflare worker..."
cp "$REPORT_FILE" "$CF_DIR/$DEPLOY_FILENAME"
echo -e "${GREEN}✓${NC} Report copied"

# Deploy to Cloudflare
echo ""
echo -e "${BLUE}Step 2:${NC} Deploying to Cloudflare Pages..."
cd "$CF_DIR/.."
npm run deploy
cd - > /dev/null

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ DEPLOYMENT COMPLETE!                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}📊 Report URL:${NC}"
echo -e "   ${BLUE}https://${BRAND_NAME}.watermelonghost.com/${DEPLOY_FILENAME}${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} Subdomain routing may need DNS configuration"
echo ""
