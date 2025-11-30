#!/bin/bash
# PHINEAS Tool Installation Script
# Installs free OSINT tools for PHINEAS framework

set -e

echo "PHINEAS Tool Installation"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}Please do not run as root${NC}"
   exit 1
fi

echo -e "${CYAN}Installing Python OSINT tools...${NC}\n"

# Core Python packages
pip3 install --user sherlock-project && echo -e "${GREEN}[OK] Sherlock installed${NC}" || echo -e "${RED}[FAIL] Sherlock failed${NC}"
pip3 install --user holehe && echo -e "${GREEN}[OK] Holehe installed${NC}" || echo -e "${RED}[FAIL] Holehe failed${NC}"
pip3 install --user theHarvester && echo -e "${GREEN}[OK] theHarvester installed${NC}" || echo -e "${RED}[FAIL] theHarvester failed${NC}"
pip3 install --user sublist3r && echo -e "${GREEN}[OK] Sublist3r installed${NC}" || echo -e "${RED}[FAIL] Sublist3r failed${NC}"
pip3 install --user maigret && echo -e "${GREEN}[OK] Maigret installed${NC}" || echo -e "${RED}[FAIL] Maigret failed${NC}"
pip3 install --user phoneinfoga && echo -e "${GREEN}[OK] PhoneInfoga installed${NC}" || echo -e "${RED}[FAIL] PhoneInfoga failed${NC}"
pip3 install --user h8mail && echo -e "${GREEN}[OK] h8mail installed${NC}" || echo -e "${RED}[FAIL] h8mail failed${NC}"

echo ""
echo -e "${GREEN}Python tools installed${NC}"

# Install additional tools if on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo ""
    echo -e "${YELLOW}Checking for additional Linux tools...${NC}"
    
    # Check if apt is available
    if command -v apt-get &> /dev/null; then
        echo -e "${CYAN}Installing system packages (requires sudo)...${NC}"
        sudo apt-get update
        sudo apt-get install -y dnsrecon whois exiftool
        echo -e "${GREEN}System packages installed${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Configure API keys: ${CYAN}python phineas.py setup${NC}"
echo "  2. Run a scan: ${CYAN}python phineas.py scan --target example@email.com${NC}"
echo "  3. View plugins: ${CYAN}python phineas.py plugins${NC}"
echo ""
echo -e "${YELLOW}Tips:${NC}"
echo "  - Most tools work without API keys"
echo "  - Get free API keys for enhanced features (haveibeenpwned, shodan, etc.)"
echo "  - See README.md for full documentation"
