echo "RUN SCRIPT AS ROOT"

echo "INSTALLING REDIS FROM SOURCE"

yum -y install wget
wget https://download.redis.io/releases/redis-5.0.8.tar.gz
tar -zxvf redis-5.0.8.tar.gz
cd redis-5.0.8

echo "OPENING FIREWALL RULE FOR REDIS"

firewall-cmd --permanent --new-zone=redis
firewall-cmd --permanent --zone=redis --add-port=6379/tcp
firewall-cmd --permanent --zone=redis --add-source=127.0.0.1
firewall-cmd --reload

echo "All Done"