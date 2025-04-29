#!/bin/bash

# 安装 Docker 和 Docker Compose (如果需要)
echo "检查 Docker 安装..."
if ! command -v docker &> /dev/null; then
    echo "安装 Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker 安装完成"
else
    echo "Docker 已安装"
fi

echo "检查 Docker Compose 安装..."
if ! command -v docker-compose &> /dev/null; then
    echo "安装 Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker-compose
    echo "Docker Compose 安装完成"
else
    echo "Docker Compose 已安装"
fi

# 拉取最新的镜像
echo "拉取最新的 Docker 镜像..."
docker pull scottz1234/ecommerce-mongodb:latest
docker pull scottz1234/ecommerce-recommender:latest
docker pull scottz1234/ecommerce-api:latest
docker pull scottz1234/ecommerce-frontend:latest

# 停止并移除旧容器
echo "停止并移除旧容器..."
docker-compose down

# 启动新容器
echo "启动容器..."
docker-compose up -d

echo "部署完成！应用程序现已可用"
echo "前端: http://$(hostname -I | awk '{print $1}')/"
echo "API: http://$(hostname -I | awk '{print $1}'):8000/" 