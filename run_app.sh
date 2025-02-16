#!/bin/bash

# Set up env
source .venv/bin/activate

# Start postgresql db
sudo service postgresql start

# Run App
streamlit run app.py --server.headless TRUE
