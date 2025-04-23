# recommendation-service/src/utils.py
"""
工具函数与共享资源：
- get_settings()  : 读取并缓存环境变量配置
- get_db()        : 返回 Mongo 数据库实例（单例）
- get_logger(name): 快速获得带格式的 logger
"""
import os
import logging
from functools import lru_cache
from pymongo import MongoClient
from dotenv import load_dotenv

# 自动读取同级目录或上级目录中的 .env 文件
load_dotenv()

# ---------- 配置 ---------- #
@lru_cache
def get_settings() -> dict:
    """读取环境变量并缓存，避免重复 IO。"""
    return {
        "mongo_url": os.getenv("MONGO_URL", "mongodb://localhost:27017"),
        "mongo_db": os.getenv("MONGO_DB", "ecomm"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }

# ---------- 数据库 ---------- #
@lru_cache
def get_db():
    """返回 MongoDB 数据库实例（单例）。"""
    cfg = get_settings()
    client = MongoClient(cfg["mongo_url"])
    return client[cfg["mongo_db"]]

# ---------- 日志 ---------- #
def get_logger(name: str = "app") -> logging.Logger:
    """返回一个预设格式的 logger。"""
    cfg = get_settings()
    level = getattr(logging, cfg["log_level"].upper(), logging.INFO)

    logger = logging.getLogger(name)
    if logger.handlers:  # 已经配置过就直接返回
        return logger

    logger.setLevel(level)
    fmt = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    return logger
