echo "RUN SCRIPT AS ROOT"

echo "INSTALLING REDIS DEPENDENCIES"
yum -y install wget
yum -y install make
yum -y install gcc

echo "INSTALLING REDIS FROM SOURCE"

wget https://download.redis.io/releases/redis-5.0.8.tar.gz
tar -zxvf redis-5.0.8.tar.gz
cd redis-5.0.8
make MALLOC=libc install
mkdir /etc/redis
cp redis.conf /etc/redis/

echo "INSTALLED REDIS VERSION:"
redis-server -v

echo "You can start redis with:"
echo "redis-server /etc/redis/redis.conf"

echo "OPENING FIREWALL RULE FOR REDIS"

firewall-cmd --permanent --new-zone=redis
firewall-cmd --permanent --zone=redis --add-port=6379/tcp
firewall-cmd --permanent --zone=redis --add-source=127.0.0.1
firewall-cmd --reload

echo "All Done"