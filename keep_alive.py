import os
import requests
import time
import random
from datetime import datetime, timedelta

# ========== 配置 ==========
# 每个 Space 可以单独配置 token（None 表示公共 Space）
SPACE_LIST = [
    {"id": "jpmaThomas/test", "token": os.getenv("HF_TOKEN")},
    # {"id": "jpmaThomas/test1", "token": os.getenv("HF_TOKEN")},
    # 可以继续添加
]

# Hugging Face Space API 地址
API_URL = "https://huggingface.co/api/spaces"

LOG_FILE = "logs/keep_alive.log"

# 日志保留天数
LOG_RETENTION_DAYS = 30

# 随机延迟范围（分钟）
DELAY_MIN = 0
DELAY_MAX = 5
# ========================

def log(msg):
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{time_str}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def cleanup_logs():
    """清理超过保留天数的日志条目"""
    if not os.path.exists(LOG_FILE):
        return
    cutoff = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            for line in lines:
                try:
                    time_str = line.split("]")[0][1:]
                    log_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    if log_time >= cutoff:
                        f.write(line)
                except Exception:
                    f.write(line)
        log(f"日志清理完成，保留最近 {LOG_RETENTION_DAYS} 天的记录")
    except Exception as e:
        log(f"日志清理失败: {e}")

def keep_alive_space(space):
    space_id = space["id"]
    token = space.get("token")

    # 随机延迟
    delay_minutes = random.randint(DELAY_MIN, DELAY_MAX)
    log(f"[{space_id}] 随机延迟 {delay_minutes} 分钟后访问 Space")
    time.sleep(delay_minutes * 60)

    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # 直接调用 Hugging Face Space API 获取状态
    url = f"{API_URL}/{space_id}/runtime"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get("runtime", {}).get("stage")
            log(f"[{space_id}] Space 保活成功，当前状态: {status}")
        else:
            msg = f"[{space_id}] Space 保活失败，状态码: {response.status_code}"
            log(msg)
    except Exception as e:
        msg = f"[{space_id}] Space 保活异常: {e}"
        log(msg)

if __name__ == "__main__":
    for space in SPACE_LIST:
        keep_alive_space(space)
    cleanup_logs()
