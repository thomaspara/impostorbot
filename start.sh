while [ -z "$(fping google.com | grep alive)" ]
do
    echo "waiting for internet ..."
    sleep 3
done
echo "Internet is now online"
script_full_path=$(dirname "$(realpath "$0")")
cd $script_full_path
source ./venv/bin/activate
python3 impostor_bot.py
sleep 3000000