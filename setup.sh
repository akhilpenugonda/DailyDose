#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Daily Word environment...${NC}"

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
python -m venv env

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source env/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create .env file from template if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${BLUE}Creating .env file from template...${NC}"
    cp env.example .env
    echo -e "${GREEN}Created .env file. Please edit it with your MongoDB connection details if needed.${NC}"
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${GREEN}To activate the environment in the future, run:${NC}"
echo -e "    source env/bin/activate"
echo -e "${GREEN}To run the application:${NC}"
echo -e "    python daily_word.py" 