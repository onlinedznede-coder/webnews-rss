import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator


def generate_dzne_rss():
  target_url = "https://www.dzne.de/en/im-fokus/meldungen"

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/120.0.0.0 Safari/537.36"
      )
  }

  response = requests.get(target_url, headers=headers)
  if response.status_code != 200:
    print(f"Fehler beim Abrufen der Seite: {response.status_code}")
    return

  soup = BeautifulSoup(response.text, "html.parser")

  # 1. Störende Bereiche (Footer, Navigation, Header etc.) komplett entfernen,
  # damit sie nicht in den Feed geraten.
  for unwanted in soup.find_all(
      ["footer", "nav", "aside", "header"],
      class_=lambda x: x
      and any(
          term in x.lower() for term in ["footer", "nav", "cookie", "meta"]
      ),
  ):
    unwanted.decompose()

  # 2. Versuche, den Hauptinhalt (<main> oder Content-Container) zu finden
  main_area = soup.find("main") or soup.find(
      "div",
      class_=lambda x: x
      and any(term in x.lower() for term in ["content", "main", "list", "grid"]),
  )
  search_context = main_area if main_area else soup

  # RSS-Feed Initialisierung
  fg = FeedGenerator()
  fg.title("DZNE Meldungen (English)")
  fg.link(href=target_url, rel="alternate")
  fg.description("Latest news and updates from DZNE Im Fokus / Meldungen.")
  fg.language("en")

  # Suche nur im bereinigten Bereich nach Artikeln/Teasern
  news_items = search_context.find_all(
      ["article", "div", "li", "item"],
      class_=lambda x: x
      and any(
          term in x.lower()
          for term in ["news", "teaser", "item", "card", "list-item", "row"]
      ),
  )

  # Fallback falls keine passenden Klassen gefunden werden
  if not news_items:
    news_items = search_context.find_all(["h2", "h3"], limit=15)

  for item in news_items:
    if item.name in ["h2", "h3"]:
      title_tag = item
      link_tag = item.find("a") or item.find_parent("a")
    else:
      title_tag = item.find(["h2", "h3", "h4", "a"])
      link_tag = item.find("a", href=True)

    if not title_tag or not link_tag:
      continue

    title = title_tag.get_text(strip=True)
    link = urljoin(target_url, link_tag["href"])

    # Beschreibung / Teaser-Text
    desc_tag = item.find("p")
    description = (
        desc_tag.get_text(strip=True) if desc_tag else "DZNE Meldungen Update"
    )

    # Doppelte Einträge vermeiden
    if any(e.link() == link for e in fg.entry()):
      continue

    fe = fg.add_entry()
    fe.id(link)
    fe.title(title)
    fe.link(href=link)
    fe.description(description)

  output_file = "dzne_news_feed.xml"
  fg.rss_file(output_file)
  print(
      f"Erfolgreich ausgeführt! Der RSS-Feed wurde in '{output_file}' gespeichert."
  )


if __name__ == "__main__":
  generate_dzne_rss()
