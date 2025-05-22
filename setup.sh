#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Daily Word...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error creating virtual environment. Make sure python3 and venv module are installed.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created.${NC}"
else
    echo -e "${GREEN}Virtual environment already exists.${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Error activating virtual environment.${NC}"
    exit 1
fi
echo -e "${GREEN}Virtual environment activated.${NC}"

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Error installing dependencies.${NC}"
    exit 1
fi
echo -e "${GREEN}Dependencies installed.${NC}"

# Install the package in development mode
echo -e "${BLUE}Installing the package in development mode...${NC}"
pip install -e .
if [ $? -ne 0 ]; then
    echo -e "${RED}Error installing the package.${NC}"
    exit 1
fi
echo -e "${GREEN}Package installed.${NC}"

# Create .env file from template if it doesn't exist
if [ ! -f ".env" ] && [ -f "env.example" ]; then
    echo -e "${BLUE}Creating .env file from template...${NC}"
    cp env.example .env
    echo -e "${GREEN}.env file created. Edit it to configure MongoDB connection.${NC}"
else
    echo -e "${GREEN}.env file already exists.${NC}"
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "To start using Daily Word, run: ${BLUE}python daily_word.py${NC} or ${BLUE}python -m dailydose${NC}"
echo -e "To deactivate the virtual environment when done, run: ${BLUE}deactivate${NC}" 