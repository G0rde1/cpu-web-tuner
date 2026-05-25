FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    lm-sensors \
    linux-tools-common \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]