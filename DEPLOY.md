# 🚀 Инструкции по развёртыванию

## Локальное развёртывание

### Требования:
- Python 3.8+
- pip (пакетный менеджер Python)

### Шаги:

1. **Клонировать или скопировать проект:**
```bash
cd /path/to/project
```

2. **Создать виртуальную среду (рекомендуется):**
```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. **Установить зависимости:**
```bash
pip install -r requirements.txt
```

4. **Создать файл `.env`:**
```bash
cp .env.example .env
# Отредактировать .env и добавить TELEGRAM_BOT_TOKEN
```

5. **Запустить бота:**
```bash
python bot.py
```

## Развёртывание на Linux сервере (systemd)

### 1. Установить Python и зависимости:
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

### 2. Скопировать проект на сервер:
```bash
scp -r . user@server:/home/user/telegram-bot
```

### 3. Настроить на сервере:
```bash
ssh user@server
cd /home/user/telegram-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Отредактировать .env
```

### 4. Создать systemd сервис:
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Добавить:
```ini
[Unit]
Description=Telegram Price Search Bot
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/telegram-bot
Environment="PATH=/home/user/telegram-bot/venv/bin"
ExecStart=/home/user/telegram-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5. Запустить сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### 6. Проверить статус:
```bash
sudo systemctl status telegram-bot
```

## Развёртывание на PythonAnywhere

### 1. Создать аккаунт на pythonanywhere.com

### 2. Загрузить файлы проекта

### 3. Создать консоль и установить зависимости:
```bash
pip install --user -r requirements.txt
```

### 4. Добавить в конфигурацию расписание (Tasks):
- Command: `/home/username/.local/bin/python /home/username/telegram-bot/bot.py`
- Schedule: Always (для постоянного запуска)

## Развёртывание на Heroku

### 1. Создать Procfile:
```
worker: python bot.py
```

### 2. Создать app.json для переменных окружения

### 3. Развернуть на Heroku:
```bash
heroku login
heroku create your-app-name
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set DEMO_MODE=true
git push heroku main
```

## Отладка

### Просмотр логов (systemd):
```bash
sudo journalctl -u telegram-bot -f
```

### Просмотр файла логов:
```bash
tail -f logs/bot_*.log
```

### Проверка соединения с Telegram API:
```bash
python3 -c "import requests; print(requests.get('https://api.telegram.org/').status_code)"
```

## Обновление бота

### На сервере с systemd:
```bash
cd /home/user/telegram-bot
git pull origin main
# или скопировать новые файлы
sudo systemctl restart telegram-bot
```

## Мониторинг

### Добавить мониторинг в crontab:
```bash
crontab -e
```

Добавить строку:
```
*/5 * * * * systemctl is-active --quiet telegram-bot || systemctl start telegram-bot
```

Это перезапустит бота, если он упадёт.

## Переменные окружения для продакшена

Рекомендуемые установки для продакшена:
```bash
TELEGRAM_BOT_TOKEN=your_production_token
LOG_LEVEL=WARNING
DEMO_MODE=false
```

## Безопасность

⚠️ **Важно:**
- Не коммитьте файл `.env` в git
- Используйте `python-telegram-bot` вместо `aiogram` если встречаете проблемы
- Регулярно обновляйте зависимости: `pip install --upgrade -r requirements.txt`
- Используйте для хранения токена переменные окружения или менеджеры секретов

---

Для вопросов и проблем смотрите README.md
