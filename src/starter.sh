git pull
cd ./src/
host_ip=$(/sbin/ip route|awk '/default/ { print $3 }')
echo 'ip:'
echo $host_ip
python3 main.py $host_ip