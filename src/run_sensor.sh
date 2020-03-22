source /home/random/venv/bin/activate

# Export API-KEYS
source ./export_secrets.sh

# Run script sensor to collect data
python sensor.py ../data/dataset.csv >> ../.log

git add ../data/dataset.csv
git commit -m "auto: update dataset"
git push