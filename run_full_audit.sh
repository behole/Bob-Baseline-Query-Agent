#!/bin/bash
#
# GEO Audit - Full Workflow Wrapper
# Runs complete audit from init to Cloudflare deployment
#

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🎯 GEO Audit Platform - Full Workflow Runner         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Get client information
echo -e "${BLUE}Step 1: Client Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Client name (lowercase, underscores, e.g., 'nike'): " CLIENT_NAME
read -p "Brand name (e.g., 'Nike', 'Restoration Hardware'): " BRAND_NAME
echo ""
echo "Select industry:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1)  Athletic Wear / Sports Equipment"
echo "  2)  Furniture / Home Furnishings"
echo "  3)  Skincare / Beauty Products"
echo "  4)  Sunscreen / Sun Protection"
echo "  5)  Fashion / Apparel"
echo "  6)  Electronics / Technology"
echo "  7)  Food & Beverage"
echo "  8)  Automotive"
echo "  9)  Healthcare / Wellness"
echo "  10) Travel / Hospitality"
echo "  11) Real Estate / Property"
echo "  12) Financial Services"
echo "  13) Education / E-Learning"
echo "  14) Entertainment / Media"
echo "  15) Other (General)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Choice (1-15): " INDUSTRY_CHOICE

case $INDUSTRY_CHOICE in
    1) INDUSTRY="athletic wear" ;;
    2) INDUSTRY="furniture" ;;
    3) INDUSTRY="skincare" ;;
    4) INDUSTRY="sunscreen" ;;
    5) INDUSTRY="fashion" ;;
    6) INDUSTRY="electronics" ;;
    7) INDUSTRY="food and beverage" ;;
    8) INDUSTRY="automotive" ;;
    9) INDUSTRY="healthcare" ;;
    10) INDUSTRY="travel" ;;
    11) INDUSTRY="real estate" ;;
    12) INDUSTRY="financial services" ;;
    13) INDUSTRY="education" ;;
    14) INDUSTRY="entertainment" ;;
    15) INDUSTRY="general" ;;
    *) INDUSTRY="general" ;;
esac

echo ""
read -p "Product categories (comma-separated, e.g., 'running shoes, athletic wear'): " PRODUCTS
read -p "Number of queries to generate (default: 60): " QUERY_COUNT
QUERY_COUNT=${QUERY_COUNT:-60}

# Step 1.5: Competitor Detection
echo ""
echo -e "${BLUE}Detecting competitors for ${INDUSTRY}...${NC}"
AUTO_COMPETITORS=$(python3 get_competitors.py "$INDUSTRY" 2>/dev/null || echo "")

if [ -n "$AUTO_COMPETITORS" ]; then
    echo -e "${GREEN}✓ Found competitors for $INDUSTRY:${NC}"
    echo "  $AUTO_COMPETITORS"
    echo ""
    read -p "Use these competitors? (y/n/edit): " COMPETITOR_CHOICE

    case $COMPETITOR_CHOICE in
        y|Y)
            COMPETITORS="$AUTO_COMPETITORS"
            ;;
        e|E|edit)
            echo ""
            echo "Enter competitors (comma-separated):"
            echo "Default: $AUTO_COMPETITORS"
            read -p "Competitors: " CUSTOM_COMPETITORS
            if [ -n "$CUSTOM_COMPETITORS" ]; then
                COMPETITORS="$CUSTOM_COMPETITORS"
            else
                COMPETITORS="$AUTO_COMPETITORS"
            fi
            ;;
        n|N)
            echo ""
            read -p "Enter competitors (comma-separated, or leave blank): " CUSTOM_COMPETITORS
            COMPETITORS="$CUSTOM_COMPETITORS"
            ;;
        *)
            COMPETITORS="$AUTO_COMPETITORS"
            ;;
    esac
else
    echo -e "${YELLOW}⚠️  No pre-defined competitors for $INDUSTRY${NC}"
    read -p "Enter competitors manually (comma-separated, or leave blank): " COMPETITORS
fi

# Create filenames
QUERIES_FILE="${CLIENT_NAME}_queries.json"
WORKSHEET_NAME="${BRAND_NAME}_Audit_$(date +%Y-%m-%d)"
REPORT_FILE="${CLIENT_NAME}_geo_report.html"

echo ""
echo -e "${GREEN}✓ Configuration Summary:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Client:      $CLIENT_NAME"
echo "  Brand:       $BRAND_NAME"
echo "  Industry:    $INDUSTRY"
echo "  Products:    $PRODUCTS"
echo "  Competitors: ${COMPETITORS:-None}"
echo "  Queries:     $QUERY_COUNT"
echo "  Worksheet:   $WORKSHEET_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Continue with this configuration? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Aborted."
    exit 0
fi

# Step 2: Initialize client configuration
echo ""
echo -e "${BLUE}Step 2: Initializing client configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create client config directory
mkdir -p config/clients

# Convert brand name to lowercase for keywords
BRAND_LOWER=$(echo "$BRAND_NAME" | tr '[:upper:]' '[:lower:]')

# Create or update client config with competitors
cat > "config/clients/${CLIENT_NAME}.yaml" <<EOF
# Client Configuration: ${BRAND_NAME}
brand_name: "${BRAND_NAME}"
industry: "${INDUSTRY}"

# Custom keywords (auto-generated based on brand)
keywords:
  - "${BRAND_LOWER}"

# Competitors for this industry
competitors:
EOF

# Add competitors to YAML if they exist
if [ -n "$COMPETITORS" ]; then
    IFS=',' read -ra COMPETITOR_ARRAY <<< "$COMPETITORS"
    for competitor in "${COMPETITOR_ARRAY[@]}"; do
        # Trim whitespace
        competitor=$(echo "$competitor" | xargs)
        echo "  - \"$competitor\"" >> "config/clients/${CLIENT_NAME}.yaml"
    done
else
    echo "  []" >> "config/clients/${CLIENT_NAME}.yaml"
fi

# Add client-specific settings
cat >> "config/clients/${CLIENT_NAME}.yaml" <<EOF

# Client-specific settings
settings:
  screenshot_dir: "screenshots/${CLIENT_NAME}"
  report_branding:
    primary_color: "#000000"
    logo_url: ""
EOF

echo -e "${GREEN}✓ Client config created: config/clients/${CLIENT_NAME}.yaml${NC}"

# Step 3: Generate queries (using competitors from client config)
echo ""
echo -e "${BLUE}Step 3: Generating queries with AI${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}⏳ Using AI to generate $QUERY_COUNT queries...${NC}"

IFS=',' read -ra PRODUCT_ARRAY <<< "$PRODUCTS"
PRODUCT_FLAGS=""
for product in "${PRODUCT_ARRAY[@]}"; do
    PRODUCT_FLAGS="$PRODUCT_FLAGS --products \"$(echo $product | xargs)\""
done

# The generate command will automatically load competitors from client config
eval ./geo-audit generate --client "$CLIENT_NAME" --output "$QUERIES_FILE" --count "$QUERY_COUNT" $PRODUCT_FLAGS

echo -e "${GREEN}✓ Queries generated: $QUERIES_FILE${NC}"
echo "  - Generic queries (no brand mentions)"
echo "  - Branded queries (mention $BRAND_NAME)"
if [ -n "$COMPETITORS" ]; then
    echo "  - Competitor comparison queries"
fi
echo "  - Product-specific queries"
echo "  - How-to/informational queries"

# Step 4: Run tracking
echo ""
echo -e "${BLUE}Step 4: Running tracking across AI platforms${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}⏳ This will take several minutes (API calls + screenshots)...${NC}"
./geo-audit track --client "$CLIENT_NAME" --queries "$QUERIES_FILE" --worksheet "$WORKSHEET_NAME"
echo -e "${GREEN}✓ Tracking complete${NC}"

# Step 5: Generate report
echo ""
echo -e "${BLUE}Step 5: Generating comprehensive HTML report${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 generate_comprehensive_report.py --brand "$BRAND_NAME" --sheet "$WORKSHEET_NAME" --output "$REPORT_FILE"
echo -e "${GREEN}✓ Comprehensive report generated: $REPORT_FILE${NC}"
echo "  - 11 detailed sections with strategic insights"
echo "  - Platform-specific analysis (5 points per platform)"
echo "  - High-value opportunities with scoring"
echo "  - Quick wins and implementation roadmap"

# Step 6: Deploy to Cloudflare (optional)
echo ""
echo -e "${BLUE}Step 6: Deploy to Cloudflare Pages${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Deploy to Cloudflare? (y/n): " DEPLOY
if [ "$DEPLOY" == "y" ]; then
    ./deploy_report.sh "$CLIENT_NAME" "$REPORT_FILE"
else
    echo "Skipping Cloudflare deployment"
fi

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    ✅ AUDIT COMPLETE!                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Files created:"
echo "   • Queries:    $QUERIES_FILE"
echo "   • Report:     $REPORT_FILE"
echo "   • Worksheet:  $WORKSHEET_NAME"
echo ""
echo "📊 Next steps:"
echo "   • Review the report: open $REPORT_FILE"
echo "   • Check Google Sheets for raw data"
echo "   • Screenshots saved in screenshots/ folder"
echo ""
