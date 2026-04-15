# Integral Build System

Проект для построения интегрального показателя по загруженным табличным данным.

Система позволяет:
- загрузить табличные показатели;
- создать проект;
- выбрать, какие показатели участвуют в расчете;
- добавить пользовательские показатели по формуле;
- настроить нормализацию;
- задать веса вручную;
- рассчитать интегральный показатель аддитивной сверткой.

Сейчас основной рабочий сценарий реализован в backend. Математический блок находится в `backend/src/math_part` и используется через адаптер, без изменений внутри самого блока.

## Как устроен процесс

Работа с системой идет в таком порядке:

1. Пользователь регистрируется и логинится.
2. Пользователь загружает исходные показатели как таблицы.
3. Пользователь создает проект.
4. В проекте выбираются нужные показатели.
5. При необходимости добавляются пользовательские показатели по формуле.
6. Для показателей задаются методы нормализации.
7. Для показателей задаются веса.
8. Запускается расчет интегрального показателя.

## Что считается показателем

Один показатель это одна таблица вида:

```text
region | 2019 | 2020 | 2021
Tomsk  | 10   | 12   | 13
Omsk   | 8    | 9    | 11
```

Правила:
- первая строка содержит годы;
- первый столбец содержит регионы;
- каждая строка после первой это один регион;
- каждая колонка после первой это один год;
- внутри таблицы должны быть числовые значения.

После загрузки backend сохраняет показатель в MongoDB в виде:
- `regions`
- `years`
- `values`

## Поддерживаемые операции

### Исходные показатели

Можно:
- загрузить показатель из `.csv`
- загрузить показатель из `.xls`
- загрузить показатель из `.xlsx`
- создать показатель вручную JSON-ом

### Пользовательские показатели

Можно создать производный показатель по формуле на основе уже выбранных показателей.

Пример:

```text
"Рождаемость"/"Смертность"
```

Или:

```text
("Доходы"*"Занятость")/"Население"
```

Важно:
- названия показателей в формуле должны быть в двойных кавычках;
- формула опирается на имена показателей внутри проекта;
- формула считается через математический блок `math_part`.

### Нормализация

Сейчас поддерживаются методы:
- `minmax`
- `z-score`
- `robust`

Если настройки нормализации не заданы, backend по умолчанию применяет `minmax` ко всем показателям проекта.

### Веса

Веса можно задать вручную.

Если веса не заданы, backend автоматически проставляет равные веса для всех нормализованных показателей проекта.

### Свертка

Сейчас поддерживается только один способ свертки:
- `sum`

То есть интегральный показатель считается аддитивно как сумма взвешенных компонент.

## Структура backend

Основные части:

- `backend/src/user`
  Отвечает за регистрацию, логин, пользователя и cookie-аутентификацию.

- `backend/src/indicator`
  Отвечает за загрузку и хранение исходных показателей.

- `backend/src/project`
  Отвечает за состав проекта, пользовательские показатели, настройки расчета и финальный результат.

- `backend/src/math_part`
  Математический блок. Его код не редактируется, он подключен через сервис-адаптер.

Ключевые файлы:

- [README.md](/home/t0mb/projects/integral_build_system/README.md)
- [main.py](/home/t0mb/projects/integral_build_system/backend/src/main.py)
- [config.py](/home/t0mb/projects/integral_build_system/backend/src/config.py)
- [indicator/router.py](/home/t0mb/projects/integral_build_system/backend/src/indicator/router.py)
- [project/router.py](/home/t0mb/projects/integral_build_system/backend/src/project/router.py)
- [user/router.py](/home/t0mb/projects/integral_build_system/backend/src/user/router.py)
- [calculation_service.py](/home/t0mb/projects/integral_build_system/backend/src/project/calculation_service.py)

## Запуск backend

### 1. Поднять MongoDB

В проекте есть `docker-compose` только для MongoDB и Mongo Express:

[docker-compose.yml](/home/t0mb/projects/integral_build_system/backend/docker-compose.yml)

Запуск:

```bash
cd backend
docker compose up -d
```

После этого:
- MongoDB будет доступна на `localhost:27017`
- Mongo Express будет доступен на `http://localhost:8081`


### 3. Установить зависимости

```bash
cd backend
source ../.venv/bin/activate
pip install -r requirements.txt
```

### 4. Запустить сервер

```bash
cd backend
python -m src.main
```

Backend стартует на:

```text
http://0.0.0.0:9000
```

Swagger:

```text
http://127.0.0.1:9000/docs
```

## Аутентификация

Backend использует cookie-аутентификацию.

После логина сервер выставляет cookie:

```text
access_user_token
```

Эта cookie автоматически используется защищенными ручками:
- `/indicator/*`
- `/project/*`
- `/user/check/`
- `/user/me/`
- `/user/list/`

## Основные API ручки

## Пользователь

### `POST /user/register/`

Регистрация пользователя.

Тело:

```json
{
  "email": "user@example.com",
  "username": "user1",
  "password": "secret123"
}
```

Ответ:

```json
{
  "id": "mongo_id",
  "email": "user@example.com",
  "username": "user1"
}
```

### `POST /user/login/`

Логин пользователя.

Тело:

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

Ответ:

```json
{
  "ok": true,
  "access_token": "jwt_token",
  "message": "Авторизация успешна!"
}
```

Дополнительно сервер выставляет cookie `access_user_token`.

### `GET /user/check/`

Проверка авторизации.

Ответ:

```json
{
  "ok": true,
  "user": {
    "id": "mongo_id",
    "username": "user1",
    "email": "user@example.com"
  }
}
```

## Показатели

### `GET /indicator/`

Получить все показатели текущего пользователя.

### `GET /indicator/{id}`

Получить один показатель.

### `POST /indicator/upload`

Загрузить показатель из файла.

Формат запроса: `multipart/form-data`

Поля:
- `file` обязательное, файл `.csv`, `.xls` или `.xlsx`
- `name` обязательное, имя показателя в системе
- `description` необязательное
- `sheet_name` необязательное, имя листа для Excel

Пример:

```bash
curl -X POST http://127.0.0.1:9000/indicator/upload \
  -b cookies.txt -c cookies.txt \
  -F "file=@birth_rate.csv" \
  -F "name=Рождаемость" \
  -F "description=Коэффициент рождаемости"
```

Пример ответа:

```json
{
  "id": "mongo_id",
  "name": "Рождаемость",
  "description": "Коэффициент рождаемости",
  "table": {
    "regions": ["Tomsk", "Omsk"],
    "years": ["2019", "2020"],
    "values": [[10.0, 12.0], [8.0, 9.0]]
  },
  "source_file_name": "birth_rate.csv",
  "source_sheet_name": null,
  "created_at": "2026-04-15T08:42:23.302792Z",
  "updated_at": "2026-04-15T08:42:23.302797Z",
  "preview_region_count": 2,
  "preview_year_count": 2
}
```

### `POST /indicator/`

Создать показатель вручную JSON-ом.

Тело:

```json
{
  "name": "Рождаемость",
  "description": "Коэффициент рождаемости",
  "table": {
    "regions": ["Tomsk", "Omsk"],
    "years": ["2019", "2020"],
    "values": [
      [10.0, 12.0],
      [8.0, 9.0]
    ]
  }
}
```

### `PUT /indicator/{id}`

Изменить:
- `name`
- `description`

### `DELETE /indicator/{id}`

Удалить показатель.

## Проекты

### `GET /project/`

Список проектов текущего пользователя.

### `GET /project/{id}`

Получить проект целиком.

### `POST /project/`

Создать проект.

Можно создать:
- пустой проект;
- проект сразу с выбранными показателями;
- проект сразу с пользовательскими формулами;
- проект сразу с настройками нормализации и весов.

Минимальный вариант:

```json
{
  "name": "Демография регионов",
  "description": "Пилотный проект"
}
```

Полный вариант:

```json
{
  "name": "Демография регионов",
  "description": "Интегральный демографический показатель",
  "indicators": [
    {
      "indicator_id": "INDICATOR_ID_1",
      "name": "Рождаемость"
    },
    {
      "indicator_id": "INDICATOR_ID_2",
      "name": "Смертность"
    }
  ],
  "custom_indicators": [
    {
      "name": "Коэффициент воспроизводства",
      "formula": "\"Рождаемость\"/\"Смертность\"",
      "description": "Пользовательский показатель"
    }
  ],
  "normalization_settings": [
    {
      "indicator_name": "Рождаемость",
      "method": "minmax",
      "output_name": "Рождаемость"
    },
    {
      "indicator_name": "Смертность",
      "method": "minmax",
      "output_name": "Смертность"
    },
    {
      "indicator_name": "Коэффициент воспроизводства",
      "method": "minmax",
      "output_name": "Коэффициент воспроизводства"
    }
  ],
  "weight_settings": [
    {
      "indicator_name": "Рождаемость",
      "weight": 0.3
    },
    {
      "indicator_name": "Смертность",
      "weight": 0.2
    },
    {
      "indicator_name": "Коэффициент воспроизводства",
      "weight": 0.5
    }
  ],
  "calculation_year": "2020",
  "aggregation_method": "sum"
}
```

### `PUT /project/{id}`

Изменить:
- `name`
- `description`
- `indicators`
- `custom_indicators`
- `normalization_settings`
- `weight_settings`
- `calculation_year`
- `aggregation_method`

### `POST /project/{id}/indicators`

Добавить один показатель в уже существующий проект.

Тело:

```json
{
  "indicator_id": "INDICATOR_ID",
  "name": "Рождаемость",
  "description": "Опциональное описание"
}
```

### `POST /project/{id}/calculate`

Запустить расчет проекта.

Можно вызвать пустым телом:

```json
{}
```

Тогда backend возьмет настройки, которые уже сохранены в проекте.

Можно передать временные настройки в теле:

```json
{
  "year": "2020",
  "normalization_settings": [
    {
      "indicator_name": "Рождаемость",
      "method": "z-score",
      "output_name": "Рождаемость"
    },
    {
      "indicator_name": "Смертность",
      "method": "robust",
      "output_name": "Смертность"
    }
  ],
  "weight_settings": [
    {
      "indicator_name": "Рождаемость",
      "weight": 0.6
    },
    {
      "indicator_name": "Смертность",
      "weight": 0.4
    }
  ]
}
```

Ответом будет обновленный проект, в котором поле `last_result` заполнено.

## Что находится в `last_result`

После расчета в проекте появляется поле:

```json
{
  "last_result": {
    "year": "2020",
    "normalized_indicators": [],
    "weights": [],
    "weighted_components": [],
    "integral_values": [],
    "ranking": [],
    "aggregation_method": "sum",
    "calculated_at": "2026-04-15T08:48:59.059000"
  }
}
```

Расшифровка:

- `year`
  Год, по которому считался итог.

- `normalized_indicators`
  Нормализованные таблицы показателей.

- `weights`
  Итоговые веса, использованные в расчете.

- `weighted_components`
  Взвешенные значения каждого показателя по выбранному году.

- `integral_values`
  Интегральный показатель по регионам.

- `ranking`
  Регионы, отсортированные по убыванию интегрального показателя.

- `aggregation_method`
  Сейчас всегда `sum`.

- `calculated_at`
  Время расчета.

## Какой сейчас рабочий happy path

Полный рабочий сценарий:

1. `POST /user/register/`
2. `POST /user/login/`
3. `POST /indicator/upload` несколько раз
4. `POST /project/`
5. `POST /project/{id}/calculate`
6. `GET /project/{id}` при необходимости

Этот сценарий проверен живым HTTP-тестом:
- с двумя исходными показателями;
- без пользовательских показателей;
- с пользовательским показателем через `custom_indicators`.

## Что уже проверено

Живыми HTTP-проверками подтверждено, что работает:
- регистрация;
- логин;
- cookie-аутентификация;
- загрузка показателей;
- создание показателей вручную;
- создание проекта;
- расчет проекта;
- пользовательские показатели по формуле;
- нормализация;
- ручные веса;
- аддитивная свертка.

## Ограничения текущей версии

- Поддерживается только `aggregation_method = "sum"`.
- Формулы пользовательских показателей должны содержать названия показателей в двойных кавычках.
- CORS сейчас настроен на `http://localhost:5173`.
- В проекте остались старые модули `level`, `module`, `function`, но текущий расчетный сценарий на них не опирается.

## Откуда backend берет расчеты

Основная вычислительная логика подключена из:

- [base_indicator.py](/home/t0mb/projects/integral_build_system/backend/src/math_part/program_math/base_indicator.py)
- [norm_indicator.py](/home/t0mb/projects/integral_build_system/backend/src/math_part/program_math/norm_indicator.py)
- [weight_indicator.py](/home/t0mb/projects/integral_build_system/backend/src/math_part/program_math/weight_indicator.py)

Адаптер, который связывает API и `math_part`:

- [calculation_service.py](/home/t0mb/projects/integral_build_system/backend/src/project/calculation_service.py)

## Что писать на frontend

Frontend должен работать так:

1. Пользователь логинится через `POST /user/login/`.
2. Браузер получает cookie `access_user_token`.
3. Дальше frontend вызывает защищенные ручки с `credentials: "include"`.
4. Для загрузки таблиц используется `multipart/form-data` на `/indicator/upload`.
5. Для создания проекта используется JSON на `/project/`.
6. Для запуска расчета используется JSON на `/project/{id}/calculate`.
7. Итог нужно читать из `project.last_result`.

## Что ожидать от backend

Если все хорошо:
- успешные ответы возвращаются с кодом `200`.

Если пользователь не авторизован:
- backend вернет `401`.

Если проект или показатель не найдены:
- backend вернет `404`.

Если есть ошибка в настройках расчета:
- backend вернет `400`.

Если внутри проекта формула написана неверно:
- backend вернет `400` с текстом ошибки.

## Быстрая памятка

Если коротко:

- таблицу загружать в `/indicator/upload`
- проект создавать в `/project/`
- формулы писать в `custom_indicators`
- методы нормализации писать в `normalization_settings`
- веса писать в `weight_settings`
- итог расчета читать из `last_result`
- свертка сейчас только `sum`

