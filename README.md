# VKFriendOnlineWatcher

Сервис для мониторинга состояния (онлайн) пользователей в VK.
Данные записываются в локальную БД Sqlite.
Имеется возможность передавать метрики в Pushgatway (Prometheus) для вывода метрик в Grafana.

Сервис настраивается через конфиг `config/config.conf` (содать самому)
Пример конфига лежит: `config/config.conf.template`

По умолчанию сервис проверят состояние друзей, но так же можно проверять состояние отдельно взятых людей, id который перечислен в файле указанном в конфиге `config/config.conf` раздела `Users` переменная `file`

Включить поддержку Prometheus можно так же в конфиге:
Раздел `Prometheus` переменная `active` устанавливается в `true` (по умолчанию `false`)

## TODO

- Добавить возможность отправки метрик на PostgreSQL сервер БД
- Дружественные связи между людьми (граф друзей и перечисленных людей)

## Grafana dashboard

![Grafana_dashboard](https://github.com/eSkry/VKFriendOnlineWatcher/blob/master/img/dashboard.png)
