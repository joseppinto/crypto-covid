
# Export API-KEYS
source ../export_secrets.sh

# Run script sensor to collect data
python3 sensor.py ../data/dataset.csv >> .log_sensor 2>&1
