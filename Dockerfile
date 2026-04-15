FROM python:3.12-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libdbus-1-3 libxkbcommon0 libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 && \
    rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 构建时预安装 Chromium（避免运行时安装的 60-120s 延迟）
# 这只增加镜像大小，不增加运行时内存（浏览器按需启动+用完释放）
RUN python3 -m patchright install chromium

COPY . .

# 创建数据目录
RUN mkdir -p .crabres/memory .crabres/skills .crabres/crawl .crabres/notifications /data/workspace



CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"]
