#!/bin/bash

# Activate the virtual environment
source /Users/sina/PycharmProjects/DjangoProject1/.venv/bin/activate

# Start the Tryton server
echo "Starting Tryton server..."
trytond -c ./erp/trytond.conf

# Keep the terminal open (optional)
exec bash