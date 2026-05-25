#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 CPU Web Tuner - Установка${NC}"
echo "=============================="

# Проверка ОС
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}❌ Эта программа только для Linux${NC}"
    exit 1
fi

# Установка зависимостей системы
echo -e "${GREEN}📦 Установка системных зависимостей...${NC}"

if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y python3 python3-pip lm-sensors linux-tools-common
    sudo sensors-detect --auto
elif command -v pacman &> /dev/null; then
    sudo pacman -S python python-pip lm_sensors cpupower
elif command -v dnf &> /dev/null; then
    sudo dnf install -y python3 python3-pip lm_sensors kernel-tools
fi

# Установка Python зависимостей
echo -e "${GREEN}📦 Установка Python пакетов...${NC}"
pip3 install -r requirements.txt

# Копирование скриптов
echo -e "${GREEN}🔧 Настройка программы...${NC}"
sudo mkdir -p /opt/cpu-web-tuner
sudo cp -r . /opt/cpu-web-tuner/
sudo chmod +x /opt/cpu-web-tuner/run.py

# Создание systemd сервиса
sudo bash scripts/setup_service.sh

echo -e "${GREEN}✅ Установка завершена!${NC}"
echo -e "${BLUE}🌐 Запустите: sudo systemctl start cpu-web-tuner${NC}"
echo -e "${BLUE}🔗 Откройте браузер: http://localhost:5000${NC}"