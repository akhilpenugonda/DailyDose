#!/bin/bash

# Path to the project directory - update this with your actual path
PROJECT_DIR="/home/pi/DailyDose"

# Log file
LOG_FILE="$PROJECT_DIR/cron.log"

# Log start time
echo "=============================" >> $LOG_FILE
echo "Running Daily Word at $(date)" >> $LOG_FILE

# Change to project directory
cd $PROJECT_DIR

# Activate virtual environment
source venv/bin/activate

# Run the application
python daily_word.py >> $LOG_FILE 2>&1

# Log completion
echo "Completed at $(date)" >> $LOG_FILE
echo "=============================" >> $LOG_FILE
echo "" >> $LOG_FILE

# Deactivate virtual environment
deactivate 