🛒 Megano Shop 

Megano Shop — это полнофункциональное веб-приложение для электронной коммерции, разработанное с использованием Python и JavaScript.

🚀 Начало работы

📦 Клонирование репозитория

```bash
git clone https://github.com/Monge-Bayir/megano_shop_origin.git
cd megano_shop_origin


🐳 Запуск с помощью Docker

1.	Соберите Docker-образ:
    docker build -t megano_shop .

2. Запустите контейнер:
    docker run -p 8000:8000 megano_shop

3. Откройте браузер и перейдите по адресу http://localhost:8000

⚙️ Переменные окружения

Если необходимо, создайте файл .env и определите следующие переменные:
env
  DEBUG=True
  SECRET_KEY=your_secret_key
  ALLOWED_HOSTS=localhost,127.0.0.1

📁 Структура проекта
	•	backend/ — серверная часть на Python
	•	diploma-frontend/ — клиентская часть на JavaScript
	•	requirements.txt — список зависимостей Python

🧪 Тестирование

Для запуска тестов выполните:
  python manage.py test
