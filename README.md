# Работа с long polling API [devman.org](https://dvmn.org)

Скрипт опрашивает сайт [devman.org](https://dvmn.org) на наличие проверенных работ и сообщает с помощью telegram-бота о результатах проверки, а также отправляет логи администратору бота.

## Запуск

- Скачайте код
- Настройте окружение. Для этого выполните следующие действия:
  - установите Python3.x;
  - создайте виртуальное окружение [virtualenv/venv](https://docs.python.org/3/library/venv.html) для изоляции проекта и активируйте его.
  - установите необходимые зависимости:

    ```
    pip install -r requirements.txt
    ```
  - Создайте бота и получите токен. Воспользуйтесь услугами [BotFather](https://telegram.me/BotFather), для этого необходимо
    ввести `/start` и следовать инструкции.
  - Чтобы получить свой `chat_id`, напишите в Telegram специальному боту: `@userinfobot`
  - В директории со скриптом создайте файл `.env`, в котором будут храниться чувствительные данные:
    ```
    TG_TOKEN='токен telegram-бота'
    DEVMAN_TOKEN='токен API devman'
    CHAT_ID='ваш чат-id'
    ```
  - запустите скрипт командой:

    ```
    python main.py
    ```

## Deploy на [Heroku](https://id.heroku.com/login)

- Разместите код в своем репозитории на GitHub.
- Зарегистрируйтесь на Heroku и создайте приложение во вкладке `Deploy`.
- Сохраните чувствительные данные во вкладке `Settings` в `Config Vars`.
- Выберите ветку `main` нажмите `Deploy Branch` во вкладке `Deploy`.
- Активируйте процесс на вкладке `Resources`.
Для просмотра в консоли возможных ошибок при деплое бота используйте [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli#download-and-install).

## Цели проекта
Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).