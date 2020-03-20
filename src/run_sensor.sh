source /home/random/venv/bin/activate

# Export API-KEYS
./export_secrets.sh

# Run script sensor to collect data
python sensor.py ../data/dataset.csv > ../.log