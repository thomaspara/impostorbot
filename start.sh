script_full_path=$(dirname "$(realpath "$0")")
cd $script_full_path
source venv/bin/activate
python3 impostor_bot.py
