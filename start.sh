script_full_path=$(dirname "$(realpath "$0")")
cd $script_full_path
source venv/bin/activate
pip3 install -r requirements.txt
python3 impostor_bot.py
