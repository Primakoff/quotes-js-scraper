from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

START_URL = "https://quotes.toscrape.com/js/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


@dataclass
class Quote:
    """Одна цитата. tags хранится строкой, удобной для CSV."""
    text: str
    author: str
    tags: str


def fetch_page(session: requests.Session, url: str, retries: int = 3,
               delay: float = 1.0) -> str | None:
    """Загружает страницу с повторными попытками при сбое сети."""
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            print(f"  попытка {attempt}/{retries} не удалась: {exc}")
            if attempt < retries:
                time.sleep(delay * attempt)
    return None


def extract_quotes(html: str) -> list[Quote]:
    """
    Главная функция "починки": достаёт цитаты из встроенного JS.

    Логика по шагам:
      1) находим <script>, в котором объявлен массив `var data = [...]`;
      2) вырезаем сам массив (он — валидный JSON);
      3) парсим JSON и превращаем каждый элемент в объект Quote.
    """
    soup = BeautifulSoup(html, "html.parser")

    # (1) среди всех <script> ищем тот, где есть "var data"
    script = next(
        (s.string for s in soup.find_all("script")
         if s.string and "var data" in s.string),
        None,
    )
    if not script:
        return []

    match = re.search(r"var data\s*=\s*(\[.*?\]);", script, re.DOTALL)
    if not match:
        return []

    raw_quotes = json.loads(match.group(1))

    quotes: list[Quote] = []
    for q in raw_quotes:
        quotes.append(Quote(
            text=q["text"].strip("\u201c\u201d\"").strip(),
            author=q["author"]["name"],
            tags="; ".join(q.get("tags", [])),
        ))
    return quotes


def find_next_url(html: str, current_url: str) -> str | None:
    """Ссылка на следующую страницу (кнопка Next) или None, если её нет."""
    soup = BeautifulSoup(html, "html.parser")
    nxt = soup.select_one("li.next a")
    return urljoin(current_url, nxt["href"]) if nxt else None


def scrape_all(start_url: str, delay: float, max_pages: int | None) -> list[Quote]:
    """Обходит все страницы по кнопке Next и собирает цитаты."""
    session = requests.Session()
    session.headers.update(HEADERS)

    all_quotes: list[Quote] = []
    url: str | None = start_url
    page = 0

    while url:
        page += 1
        if max_pages and page > max_pages:
            print(f"Достигнут лимит страниц ({max_pages}).")
            break

        print(f"Страница {page}: {url}")
        html = fetch_page(session, url, delay=delay)
        if html is None:
            break

        quotes = extract_quotes(html)
        all_quotes.extend(quotes)
        print(f"  собрано цитат: {len(quotes)} (всего {len(all_quotes)})")

        url = find_next_url(html, url)
        if url:
            time.sleep(delay) 

    return all_quotes


def save_csv(quotes: list[Quote], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(quotes[0]).keys()))
        writer.writeheader()
        for q in quotes:
            writer.writerow(asdict(q))
    print(f"CSV сохранён: {path} ({len(quotes)} строк)")


def save_json(quotes: list[Quote], path: Path) -> None:
    data = [asdict(q) for q in quotes]
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON сохранён: {path} ({len(quotes)} записей)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Парсер динамического сайта quotes.toscrape.com/js"
    )
    parser.add_argument("--output-dir", default="data")
    parser.add_argument("--format", choices=["csv", "json", "both"], default="both")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--max-pages", type=int, default=None)
    args = parser.parse_args(argv)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    quotes = scrape_all(START_URL, delay=args.delay, max_pages=args.max_pages)
    if not quotes:
        print("Данные не собраны — проверь подключение к сети.")
        return 1

    print(f"\nГотово. Всего цитат: {len(quotes)}")
    if args.format in ("csv", "both"):
        save_csv(quotes, out_dir / "quotes.csv")
    if args.format in ("json", "both"):
        save_json(quotes, out_dir / "quotes.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
