#!/bin/bash
echo "Script executed at $(date)" >> /home/grafa/test_work/cron.log
timeout 30s python3 teleth.py
