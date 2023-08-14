# FoodGram
## Учебный проект Продуктовый помошник


На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## **Описание проекта**

Проект Kittygram находится по адресу: http://fuagra.hopto.org
Логин и пароль для входа в админ зону: admin45 парроль: flvby1256

## **Стэк технологий**

Django==4.2.3
django-colorfield==0.9.0
mypy==1.4.1
mypy-extensions==1.0.0
python-dotenv==1.0.0
tomli==2.0.1
typing_extensions==4.7.1
asgiref==3.7.2
django-filter==23.2
djangorestframework==3.14.0
djoser==2.1.0
Pillow==10.0.0
drf-extra-fields==3.5.0 
html5lib==1.1
pypdf==3.14.0
xhtml2pdf==0.2.11
psycopg2-binary==2.9.3

## Локальный запуск проекта

Клонировать репозиторий и перейти в него в командной строке:

```bash
git git@github.com:Ivan-Edokov/foodgram-project-react.git
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение, установить зависимости:

```bash
python3 -m venv venv && \ 
    source venv/scripts/activate && \
    python -m pip install --upgrade pip && \
    pip install -r backend/requirements.txt
```
Выполнить миграции:

```bash
python3 manage.py migrate
```

В папке с файлом manage.py выполнить команду:

```bash
python3 manage.py runserver
```

## Запуск с использованием CI/CD

Установить docker, docker-compose на сервер.

```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

Создайте папку foogram:

```
mkdir foogram
```

- Перенести файлы docker-compose.production.yml и nginx.conf на сервер.

```
scp docker-compose.production.yml username@server_ip:/home/<username>/foogram
```
```
scp nginx.conf <username>@<server_ip>:/home/<username>/foogram
```

- Создайте файл .env в дериктории foogram:

```
touch .env
```
- Заполнить в настройках репозитория секреты .env

```python
POSTGRES_USER='имя пользователя БД'
POSTGRES_PASSWORD='пароль пользователя БД'
POSTGRES_DB='имя БД'
DB_HOST='хост БД, напимер localhost или db'
DB_PORT='5432'
```

Для использования Continuous Integration (CI) и Continuous Deployment (CD): в репозитории GitHub Actions `Settings/Secrets/Actions` прописать Secrets - переменные окружения для доступа к сервисам:

```
SECRET_KEY                     # стандартный ключ, который создается при старте проекта

DOCKER_USERNAME                # имя пользователя в DockerHub
DOCKER_PASSWORD                # пароль пользователя в DockerHub
HOST                           # ip_address сервера
USER                           # имя пользователя
SSH_KEY                        # приватный ssh-ключ (~/.ssh/id_rsa)
PASSPHRASE                     # кодовая фраза (пароль) для ssh-ключа

TELEGRAM_TO                    # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN                 # токен бота (получить токен можно у @BotFather, /token, имя бота)
```

При push в ветку main автоматически отрабатывают сценарии:

* *tests* - проверка кода на соответствие стандарту PEP8.
* *build\_backend\_and\_push\_to\_docker\_hub* и *build\_frontend\_and\_push\_to\_docker\_hub* - сборка и доставка докер-образов на DockerHub
* *deploy* - автоматический деплой проекта на боевой сервер.
* *send\_message* - отправка уведомления в Telegram.

Для доступа к контейнеру выполните следующие команды на сервере:

```
sudo docker-compose -f docker-compose.production.yml exec backend python manage.py migrate --noinput
```
```
sudo docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
```

Дополнительно можно наполнить базу данных ингредиентами, тэгами и создать админа:

```
sudo docker-compose -f docker-compose.production.yml exec backend python manage.py loaddata
```

# Запуск проекта через Docker

- В папке infra выполнить команду, чтобы собрать контейнер:

```
sudo docker-compose up -d
```

Для доступа к контейнеру выполните следующие команды:

```
sudo docker-compose -f docker-compose.production.yml exec backend python manage.py migrate --noinput
```
```
sudo docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
```

Дополнительно можно наполнить базу данных ингредиентами, тэгами и создать админа:

```
sudo docker-compose -f docker-compose.production.yml exec backend python manage.py loaddata
```
