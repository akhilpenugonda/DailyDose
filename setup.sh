#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Daily Word environment...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 before continuing.${NC}"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}Using Python ${PYTHON_VERSION}${NC}"

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
if python3 -m venv env; then
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
else
    echo -e "${RED}Failed to create virtual environment. Please check your Python installation.${NC}"
    echo -e "${YELLOW}You can still run the script with your system Python.${NC}"
    echo -e "${YELLOW}Install dependencies by running: pip3 install -r requirements.txt${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source env/bin/activate || {
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
}

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo -e "${RED}pip is not available in the virtual environment.${NC}"
    deactivate
    exit 1
fi

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
if pip install -r requirements.txt; then
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
else
    echo -e "${RED}Failed to install dependencies.${NC}"
    deactivate
    exit 1
fi

# Create .env file from template if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${BLUE}Creating .env file from template...${NC}"
    cp env.example .env
    echo -e "${GREEN}Created .env file. Please edit it with your MongoDB connection details.${NC}"
    echo -e "${YELLOW}You need to update the .env file with your actual MongoDB connection string for MongoDB functionality.${NC}"
else
    echo -e "${YELLOW}The .env file already exists. If you need to reset it, you can copy from env.example.${NC}"
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${GREEN}To activate the environment in the future, run:${NC}"
echo -e "    source env/bin/activate"
echo -e "${GREEN}To run the application:${NC}"
echo -e "    python daily_word.py"
echo -e "${YELLOW}Note: If MongoDB connection fails, the application will automatically use local file storage.${NC}" 