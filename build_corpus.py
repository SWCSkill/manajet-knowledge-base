#!/usr/bin/env python3
"""
build_corpus.py - пересобирает корпус справки ManaJet из JSON-выгрузки.

Использование:
    python3 build_corpus.py <input.json> <output_dir>

Где:
    input.json  - выгрузка справки ManaJet в JSON
    output_dir  - папка, куда сложить articles/ и INDEX.md

Что делает скрипт:
- Фильтрует статьи (раздел 24 - только статьи про ManaJet)
- Заменяет внутренние ссылки app.manajet.org/FAQ/Home/Index/{id} на публичные
  app.manajet.org/FAQ/Public/Index/{id}?culture=ru-RU (открываются без авторизации,
  со скриншотами)
- Чистит технический мусор (loading.gif и пр.)
- Добавляет в шапку каждого .md публичную ссылку на статью
- Генерирует articles/{id}.md и INDEX.md
"""

import json
import re
import os
import sys
from collections import defaultdict


PUBLIC_BASE = 'https://app.manajet.org/FAQ/Public/Index'

# Ключевые слова, по которым статьи раздела 24 «Минутка ManaJet»
# считаются относящимися к самому ManaJet (а не общим бизнес-контентом)
MANAJET_KEYWORDS = [
    'ManaJet', 'Поток', 'ЗРС', 'CRM', 'статистик', 'Управленческ', 'Финансов',
    'ФП', 'Контрол', 'Должностн', 'Заявк', 'Счет', 'Ассортимент', 'Рассылк',
    'Канбан', 'канбан', 'Бизнес-процесс', 'программ', 'Отгрузк', 'Шаблон',
]

SECTIONS = {
    '1':  'Начало работы',
    '2':  'Личный кабинет',
    '3':  'Сотрудники',
    '4':  'Статистики',
    '5':  'CRM',
    '6':  'Структура компании',
    '7':  'Воронка продаж',
    '8':  'Плазма',
    '9':  'Должностные инструкции',
    '10': 'Финансовое планирование',
    '11': 'Управление проектами',
    '12': 'Поток (канбан)',
    '13': 'Бизнес-процессы',
    '14': 'Инструменты',
    '15': 'API',
    '16': 'Настройки',
    '17': 'Мобильные устройства',
    '18': 'Интеграция с 1С',
    '19': 'Интеграция с Google',
    '20': 'Интеграция с CallGear',
    '21': 'Интеграция с Shopify',
    '22': 'Глоссарий',
    '23': 'FAQ',
    '24': 'Минутка ManaJet (статьи о возможностях)',
}


def belongs_in_skill(article):
    title = article['title']
    if not title.startswith('24.'):
        return True
    return any(kw in title for kw in MANAJET_KEYWORDS)


def get_section(title):
    m = re.match(r'^(\d+)\.', title)
    return m.group(1) if m else '0'


def build(input_json, output_dir):
    with open(input_json, encoding='utf-8') as f:
        data = json.load(f)

    filtered = [a for a in data['articles'] if belongs_in_skill(a)]
    print(f"Отобрано {len(filtered)} статей из {len(data['articles'])}")

    # Заменяем внутренние ссылки на публичные
    url_pattern = re.compile(
        r'https?://app\.manajet\.org/FAQ/Home/Index/(\d+)(?:\?[^\s\)"]*)?'
    )

    def fix_links(content):
        def replace(match):
            target_id = int(match.group(1))
            return f"{PUBLIC_BASE}/{target_id}?culture=ru-RU"
        return url_pattern.sub(replace, content)

    def clean_content(content):
        content = fix_links(content)
        content = re.sub(r'!\[\]\([^\)]*loading\.gif\)\s*\n?', '', content)
        return content.strip()

    articles_dir = os.path.join(output_dir, 'articles')
    os.makedirs(articles_dir, exist_ok=True)

    for a in filtered:
        body = clean_content(a['content'])
        public_url = f"{PUBLIC_BASE}/{a['id']}?culture=ru-RU"
        md = f"# {a['title']}\n\nПубличная ссылка: {public_url}\n\n{body}\n"
        path = os.path.join(articles_dir, f"{a['id']}.md")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(md)

    print(f"Записано {len(filtered)} файлов в {articles_dir}")

    # INDEX.md с публичными ссылками
    grouped = defaultdict(list)
    for a in filtered:
        grouped[get_section(a['title'])].append(a)

    lines = [
        "# ManaJet Knowledge Base - Индекс статей",
        "",
        f"Справочник ManaJet - {len(filtered)} статей.",
        "",
        "**Публичная справка:** https://app.manajet.org/FAQ/Public/Index/{id}?culture=ru-RU (со скриншотами)",
        "**curl для скилла:** `https://raw.githubusercontent.com/<owner>/<repo>/main/articles/{id}.md`",
        "",
        "## Структура корпуса",
        "",
    ]
    for sect_num in sorted(grouped.keys(), key=int):
        sect_name = SECTIONS.get(sect_num, f"Раздел {sect_num}")
        arts = grouped[sect_num]
        lines.append(f"### {sect_num}. {sect_name} ({len(arts)} статей)")
        lines.append("")
        for a in arts:
            public = f"{PUBLIC_BASE}/{a['id']}?culture=ru-RU"
            lines.append(f"- [`{a['id']}`](./articles/{a['id']}.md) - {a['title']} · [справка]({public})")
        lines.append("")

    index_path = os.path.join(output_dir, 'INDEX.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Записан {index_path}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    build(sys.argv[1], sys.argv[2])
