# Инструкция по сборке exe файла

## Требования

- Python 3.7 или выше
- Все зависимости из `requirements.txt`

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Сборка exe файла

### Вариант 1: Использование готового скрипта

**Windows:**
```bash
build_exe.bat
```

**Linux/Mac:**
```bash
chmod +x build_exe.sh
./build_exe.sh
```

### Вариант 2: Ручная сборка

1. Убедитесь, что PyInstaller установлен:
```bash
pip install pyinstaller
```

2. Запустите сборку:
```bash
pyinstaller pacman_remastered.spec
```

3. Готовый exe файл будет в папке `dist/PacmanRemastered.exe`

## Настройки сборки

### Изменить имя файла

Отредактируйте `pacman_remastered.spec` и измените параметр `name` в секции `EXE`:
```python
name='PacmanRemastered',  # Измените на желаемое имя
```

### Скрыть консольное окно

В файле `pacman_remastered.spec` измените:
```python
console=True,  # Измените на False
```

### Добавить иконку

1. Создайте файл `icon.ico` в корне проекта
2. В `pacman_remastered.spec` измените:
```python
icon='icon.ico',  # Вместо None
```

## Структура после сборки

После сборки в папке `dist/` будет:
- `PacmanRemastered.exe` - исполняемый файл
- Все необходимые ресурсы (Assets, pac-man-1) будут включены в exe

## Решение проблем

### Ошибка "Module not found"

Если при запуске exe возникает ошибка о недостающих модулях:
1. Добавьте модуль в `hiddenimports` в `pacman_remastered.spec`
2. Пересоберите проект

### Ошибка "File not found" для ресурсов

Убедитесь, что все папки с ресурсами указаны в секции `datas` в `pacman_remastered.spec`:
```python
datas=[
    ('Assets', 'Assets'),
    ('pac-man-1', 'pac-man-1'),
],
```

**Важно:** Если возникает ошибка "Failed to execute script", это обычно связано с путями к ресурсам. Убедитесь, что:
1. Файл `pyi_rth_paths.py` находится в корне проекта
2. Все модули используют `path_helper` для получения путей
3. Пересоберите проект после изменений

### Большой размер exe файла

Это нормально для игр на Pygame. Размер может быть 50-200 МБ в зависимости от включенных ресурсов.

## Тестирование

После сборки протестируйте exe файл:
1. Запустите `dist/PacmanRemastered.exe`
2. Проверьте все функции игры
3. Убедитесь, что все ресурсы загружаются корректно

