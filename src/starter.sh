git clone https://github.com/livwvil/food_monitor.git
cp ./food_monitor/src/main.py .
host_ip=$(/sbin/ip route|awk '/default/ { print $3 }')
echo 'ip:'
echo $host_ip
python3 main.py $host_ip