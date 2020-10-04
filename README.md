#### Предназначение:
Сервис предназначен для получения и сохранения котировок по инструментам из 
moex api, и расчета процента изменения котировок.

#### Запуск:
1. Клонируем репозиторий
`git clone https://github.com/MikhailKulagin/bks_test.git`
2. Переходим в директорию с проектом
`bks_test`
3. При необходимости правим конфиг
`/bks_test/config.py`
4. Сброка 
`docker build -t bks_test:0.0.1 .`
и запуск контейнера
`docker run --rm -it -p 8005:8005 bks_test:0.0.1`
5. Делаем запрос к методу insert_from_moex, чтобы получить котировки по заданным бордам и инструментам.
Если делаем из коммандной строки curl-ом:
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{
"jsonrpc": "2.0",
"method": "insert_from_moex",
"id": 1,
  "params": {"boards": "SNDX",
  "securities": "IMOEX",
  "date_from": "2020-07-25",
  "date_to": "2020-09-30"}
}' \
 http://localhost:8005/
```
Если пользуемся pycharm, то в файле `.http`:
```
POST http://localhost:8005/
Content-Type: application/json

{
"jsonrpc": "2.0",
"method": "insert_from_moex",
"id": 1,
  "params": {"securities": "IMOEX",
  "date_from": "2020-08-20",
  "date_to": "2020-09-25",
  "boards": "SNDX"}
}
```
6. Делаем запрос к методу get_summary, чтобы получить проценты изменнеий по котировкам
cURL:
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{
"jsonrpc": "2.0",
"method": "get_summary",
"id": 1
}' \
 http://localhost:8005/
```
PyCharm:
```
POST http://localhost:8005/
Content-Type: application/json

{
"jsonrpc": "2.0",
"method": "get_summary",
"id": 1
}
```

#### Структура: 
```
db.app_db.py - инициализация бд и функции добавлоения и выборки записей из бд
service.insert_from_moex.py - наполняем базу приложения данными moex
service.get_summary.py - считаем % на данных moex из базы приложения
service.moex_rest.py - запрос к moex api
service.rest.py - описание функций реста
service.service.py - раннер
service.utils.py - вспомогательные функции
service.config.py - конфиг приложения с env
```