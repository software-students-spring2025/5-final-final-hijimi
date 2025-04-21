def make_recommendations(preferences):
    pool = {
        "laptop": ["laptop-stand", "usb-c-dock"],
        "mouse": ["mouse-pad", "ergonomic-wrist-rest"],
        "keyboard": ["keycap-set", "switch-lubricant"],
        "headphone": ["headphone-case", "dac-amp"]
    }
    recs = []
    for p in preferences:
        recs.extend(pool.get(p, []))
    return recs[:6]

# 在 services.py 或 main.py 中
from utils import get_db, get_logger

db     = get_db()
logger = get_logger(__name__)

logger.info("Connected to MongoDB with %s docs", db.users.count_documents({}))
