# Lab 5 DevSecOps - Решение выполнено

## 📋 Обзор

Выполнено индивидуальное задание по анализу уязвимости безопасности в PyGoat. Выбрана уязвимость **Unsafe YAML Deserialization (CWE-502)** из результатов сканирования Bandit.

## 📂 Структура решения

```
reports/yaml_deserialization/
├── README.md                           # Общее введение
├── report.md                           # Основной анализ уязвимости
├── BONUS_FIX_VERIFICATION.md          # Бонусная часть: исправление и проверка
├── 
├── Исходный код:
├── app_vulnerable.py                   # Уязвимый код (оригинальный)
├── app_fixed.py                        # Исправленный код (с safe_load())
├── 
├── Демонстрация:
├── demo_vulnerability.py               # Скрипт демонстрации уязвимости
├── test_safe.yaml                      # Безопасный YAML файл
├── test_malicious_subprocess.yaml      # Вредоносный YAML (subprocess gadget)
├── test_malicious_os.yaml              # Вредоносный YAML (os.system gadget)
├── 
├── Отчёты сканирования:
├── bandit-b506.txt                     # Результаты Bandit для B506
├── bandit_before_after.txt             # Сравнение до/после исправления
└── bandit-full.json                    # Полный отчёт Bandit (JSON)
```

## 🔍 Выбранная уязвимость

### Основная информация
- **Тип:** Небезопасная десериализация YAML
- **CWE:** CWE-502 (Deserialization of Untrusted Data)
- **Bandit Rule:** B506 (yaml_load)
- **Severity (Bandit):** Medium
- **Confidence:** High
- **Файл:** `dockerized_labs/a9_uckv_lab/app.py:62`
- **Endpoint:** POST `/upload_yaml`

### Почему эта уязвимость?
✓ Правильно обнаружена Bandit (B506)  
✓ Не повторяет существующие отчёты (eval-injection, path-traversal)  
✓ Позволяет удалённое выполнение кода (RCE)  
✓ Подходит под требования задания  

## 📊 Результаты анализа

### Уязвимый код
```python
# Строка 62 в app.py
data = yaml.load(file.stream, Loader=yaml.Loader)
```

### Почему это небезопасно?
- `yaml.Loader` позволяет инстанцировать произвольные объекты Python
- Пользователь может загрузить файл с вредоносными YAML-тегами
- `!!python/object/apply:subprocess.Popen` позволяет выполнить команду
- `!!python/object/apply:os.system` позволяет запустить системную команду
- Код выполняется **во время десериализации**, до обработки приложением

### CVSS Assessment
```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
Оценка: 9.8 (Critical) при открытом доступе
Оценка: 8.8 (High) при необходимости аутентификации
```

## 🛠️ Исправление (Bonus)

### Исправленный код
```python
# FIXED: Use safe_load() to prevent arbitrary object instantiation
data = yaml.safe_load(file.stream)

# Validate that the parsed YAML is a dictionary
if not isinstance(data, (dict, list)):
    flash("Invalid YAML format: expected a dictionary or list")
    logger.warning(f"Invalid YAML structure in {file.filename}")
    return redirect(url_for("lab1"))
```

### Что изменилось?
1. ✓ Заменён `yaml.load(Loader=yaml.Loader)` на `yaml.safe_load()`
2. ✓ Добавлена валидация типов данных
3. ✓ Улучшена обработка ошибок (разделены yaml.YAMLError и Exception)

### Результаты сканирования
**До исправления:**
```
Total issues (by severity):
  Medium: 1 ← УЯЗВИМОСТЬ B506
  High: 0
```

**После исправления:**
```
Test results:
  No issues identified. ← ИСПРАВЛЕНО
```

## 🧪 Доказательство уязвимости

### Демонстрация
```bash
$ python3 demo_vulnerability.py
```

**Результат:**
1. Безопасный YAML: ✓ Парсится обоими способами
2. Вредоносный YAML + `safe_load()`: ✓ **ЗАБЛОКИРОВАНО** (YAMLError)
3. Вредоносный YAML + `yaml.load(Loader)`: ✗ **КОД ВЫПОЛНЕН** (subprocess, os.system)

## 📋 Требования задания

| Требование | Статус |
|-----------|--------|
| Выбранная индивидуальная уязвимость | ✓ YAML B506 |
| Анализ: CWE/CVE | ✓ CWE-502 |
| Анализ: CVSS и вектор | ✓ 9.8/8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H) |
| Анализ: Последствия | ✓ RCE, доступ к файлам, нарушение целостности |
| Анализ: Необходимые права | ✓ Сетевой доступ, возможно аутентификация |
| Отчёт о находке | ✓ report.md |
| **Бонус:** Исправление кода | ✓ app_fixed.py |
| **Бонус:** Результаты до/после | ✓ bandit_before_after.txt + BONUS_FIX_VERIFICATION.md |

## 📚 Файлы для проверки

### Основной отчёт
👉 **reports/yaml_deserialization/report.md** — Полный анализ уязвимости

### Бонусная часть
👉 **reports/yaml_deserialization/BONUS_FIX_VERIFICATION.md** — Исправление с проверкой

### Демонстрация
👉 **reports/yaml_deserialization/demo_vulnerability.py** — Запустить для подтверждения

### Быстрая проверка Bandit
```bash
# До исправления (1 Medium issue):
python3 -m bandit -ll -ii -t B506 reports/yaml_deserialization/app_vulnerable.py -f txt

# После исправления (No issues):
python3 -m bandit -ll -ii -t B506 reports/yaml_deserialization/app_fixed.py -f txt
```

## 🎯 Ключевые показатели

| Метрика | Значение |
|---------|----------|
| Найденных уязвимостей в проекте | 78 (23 High, 32 Medium, 75 Low) |
| Выбранная уязвимость | B506 (yaml_load) |
| Расположение | app.py:62 |
| Статус до исправления | ✗ VULNERABLE |
| Статус после исправления | ✓ FIXED |
| Код выполнен | ✓ Да (доказано) |
| Код заблокирован после fix | ✓ Да (доказано) |

## ✅ Выводы

1. **Уязвимость подтверждена:** Unsafe YAML deserialization позволяет выполнить произвольный Python-код
2. **Доказательство:** Демонстрирует выполнение `subprocess.Popen` и `os.system` при использовании `yaml.load()`
3. **Исправление эффективно:** `yaml.safe_load()` блокирует опасные YAML-теги
4. **Bandit подтверждает:** B506 исчезает после исправления
5. **Функциональность сохранена:** Нормальные YAML-файлы парсятся корректно

---

**Дата завершения:** 22 ноября 2026  
**Статус:** ✅ ЗАВЕРШЕНО  
**Репозиторий:** [Retr0-46/lab5-NCS](https://github.com/Retr0-46/lab5-NCS)
