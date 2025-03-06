# VK-PARSE

## Содержание

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Limitations](#limitations)

## About <a name = "about"></a>

Этот скрипт позволяет извлекать данные из ВКонтакте, включая информацию о постах, их вложениях (например, фотографии) и комментариях. Скрипт также поддерживает обработку ссылок на профили и группы ВКонтакте.

## Getting Started <a name = "getting_started"></a>

1. Убедитесь, что у вас установлен Python 3.7 или выше.

2. Установите необходимые зависимости:

```bash
pip install -r requirements.txt
```

3. Переименуйте файл '.env-sample' в '.env' и добавьте туда ваш токен доступа к API ВКонтакте:

```
ACCESS_TOKEN=ваш_токен_доступа
```

4. Создайте файл Destructive.txt в корневой директории проекта и добавьте туда ссылки на посты или профили ВКонтакте, которые вы хотите обработать. Например:

```
https://vk.com/wall-123456_7890
https://vk.com/club123456
https://vk.com/id123456
```

## Usage <a name="usage"></a>

Запустите скрипт (_скрипт запускать из папки \src_):

```bash
python3 main.py
```

### Limitations <a name="limitations"></a>

Для работы скрипта требуется токен доступа к API ВКонтакте. Вы можете получить его через VK API.
https://dev.vk.com/ru/api/access-token/getting-started?ref=old_portal

Или используйте эту ссылку:
https://vkhost.github.io/

