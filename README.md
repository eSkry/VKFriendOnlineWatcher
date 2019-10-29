# VKFriendOnlineWatcher

Сервис для мониторинга состояния (онлайн) пользователей в VK.
Данные записываются в локальную БД Sqlite. В таблице `statistics` содержатся все сессии пользователей, 1 строка - 1 сессия пользователя.
Имеется возможность передавать метрики в Pushgatway (Prometheus) для вывода метрик в Grafana.

Сервис настраивается через конфиг `config/config.conf` (содать самому)
Пример конфига лежит: `config/config.conf.template`

По умолчанию сервис проверят состояние друзей, но так же можно проверять состояние отдельно взятых людей, id который перечислен в файле указанном в конфиге `config/config.conf` раздела `Users` переменная `file`

Включить поддержку Prometheus можно так же в конфиге:
Раздел `Prometheus` переменная `active` устанавливается в `true` (по умолчанию `false`)

## Configuration
Раздел ***Auth***
- **vk_login** - Номер телефона аккаунта VK
- **vk_password** - Пароль от аккаунта VK
- **vk_token** - Токен (Необязательно)
- **vk_app_id** - ID Приложения (Необязательно)

Раздел ***Prometheus***
- **active** - Использовать ли отправку в prometheus
- **host** - Адрес сервера Prometheus

Раздел ***Users***
- **file** - Фаил в котором перечислены ID пользоватлей состояние которых необходимо отслеживать

## Grafana dashboard
Запрос дашбоарда: `friends_online_stats{full_name=~\".*\"}`
![Grafana_dashboard](https://github.com/eSkry/VKFriendOnlineWatcher/blob/master/img/dashboard.png)
