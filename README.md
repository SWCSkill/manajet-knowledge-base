# manajet-knowledge-base

Репозиторий скилла **swc-manajet-expert** для AI-ассистента сотрудников SWC.
Содержит и сам скилл, и живую базу знаний (справку ManaJet), к которой
скилл обращается во время работы.

## Хочу установить скилл

Иди в [INSTALL.md](./INSTALL.md). Ссылка на актуальную версию:

**https://github.com/SWCSkill/manajet-knowledge-base/releases/latest/download/swc-manajet-expert.skill**

## Что внутри

```
manajet-knowledge-base/
├── articles/                    ← живая база (221 статья справки ManaJet)
├── INDEX.md                     ← публичный индекс базы
│
├── skill-template/              ← исходники скилла
│   └── SKILL.md.template        ← шаблон с {{VERSION}} и {{BUILD_DATE}}
├── skill-references/            ← локальные референсы скилла
│   ├── INDEX.md                 ← навигационный индекс корпуса для скилла
│   ├── swc_terminology.md       ← словарь терминов ManaJet ↔ SWC
│   └── swc_practice.md          ← SWC-практика поверх справки
│
├── scripts/
│   ├── build_corpus.py          ← пересборка articles/ из JSON-выгрузки справки
│   └── build_skill.py           ← сборка .skill из скилла-шаблона + skill-references
├── .github/workflows/
│   └── build-skill.yml          ← автоматическая сборка релиза при push тега
│
├── VERSION                      ← текущая версия скилла
├── CHANGELOG.md                 ← история версий
├── INSTALL.md                   ← инструкция установки
└── README.md                    ← этот файл
```

## Два слоя

### Слой 1. Живая база знаний (`articles/`)

221 статья справки ManaJet по одной на файл. Скилл во время работы
обращается сюда через curl и подтягивает нужную статью по ID.
Доступ: `https://raw.githubusercontent.com/SWCSkill/manajet-knowledge-base/main/articles/{ID}.md`

### Слой 2. Скилл (`skill-template/`, `skill-references/`)

Файлы, из которых GitHub Actions собирает .skill-архив для загрузки в Claude.ai.
При сборке из шаблона рендерится `SKILL.md` с подставленной версией и датой,
а файлы из `skill-references/` копируются в `references/` внутри пакета.

## Как обновить корпус справки ManaJet

Когда ManaJet выкатил новые статьи или поменял существующие:

1. Получить актуальную JSON-выгрузку справки (через ManaJet или вручную).
2. Прогнать скрипт пересборки:
   ```
   python3 scripts/build_corpus.py manajet_documentation.json .
   ```
   Перепишет `articles/` и `INDEX.md`.
3. Закоммитить и запушить. **Скилл подхватит обновления при следующем
   обращении к репо** - переустанавливать его не нужно.

## Как обновить сам скилл

Когда меняем поведение скилла (правим `SKILL.md.template`, словари, добавляем разделы):

1. Внести правки в `skill-template/SKILL.md.template` и/или файлы в `skill-references/`.
2. Обновить `VERSION` (например, с `1.3.0` на `1.4.0`).
3. Дописать запись в `CHANGELOG.md`.
4. Закоммитить и запушить. GitHub Actions автоматически:
   - Соберёт `.skill`-архив
   - Создаст релиз `v1.4.0`
   - Положит туда `swc-manajet-expert.skill` (стабильное имя для latest)
   - И `swc-manajet-expert-v1.4.0.skill` (с версией в имени)
5. Сотрудники скачают по той же постоянной ссылке - получат уже новую версию.

## Локальная сборка скилла

Без GitHub - на своей машине:

```bash
pip install PyYAML
python3 scripts/build_skill.py --output dist/test.skill
```

## Источник

Корпус получен из официальной справки ManaJet
(https://app.manajet.org/FAQ/Public/Index/0). Раздел 24 «Минутка ManaJet»
отфильтрован: оставлены только статьи о возможностях программы,
общеделовой блог-контент исключён.

## Лицензия и атрибуция

Тексты статей в `articles/` принадлежат правообладателям ManaJet.
Этот репозиторий - локальная копия для использования AI-ассистентом
в работе сотрудников SWC. Сам скилл (SKILL.md, словари, практика) -
авторская работа SWC.
