FROM mongo:latest

# 创建数据目录
COPY init_data.json /data/init_data.json
COPY init.sh /docker-entrypoint-initdb.d/init.sh

RUN chmod +x /docker-entrypoint-initdb.d/init.sh
