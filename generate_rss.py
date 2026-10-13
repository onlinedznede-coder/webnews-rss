import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator


def generate_dzne_rss():
  target_url = "https://www.dzne.de/en/news/webnews/"

  # Headers mitsenden, damit die Anfrage nicht blockiert wird
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

  # RSS-Feed Initialisierung
  fg = FeedGenerator()
  fg.title("DZNE Webnews (English)")
  fg.link(href=target_url, rel="alternate")
  fg.description("Latest news and updates from the DZNE.")
  fg.language("en")

  # Suche flexibel nach allen möglichen News-Containern oder Teasern auf der DZNE-Seite
  news_items = soup.find_all(
      ["article", "div", "li"],
      class_=lambda x: x
      and any(term in x.lower() for term in ["news", "teaser", "item", "card"]),
  )

  # Fallback: Wenn keine Container gefunden werden, suchen wir nach allen Links mit Überschriften
  if not news_items:
    news_items = soup.find_all(["h2", "h3"], limit=15)

  for item in news_items:
    # Versuche Titel und Link zu extrahieren
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

    # Beschreibung / Teaser-Text (falls vorhanden)
    desc_tag = item.find("p")
    description = (
        desc_tag.get_text(strip=True) if desc_tag else "DZNE Webnews Update"
    )

    # Doppelte Einträge vermeiden
    if any(e.link() == link for e in fg.entry()):
      continue

    # Feed-Eintrag hinzufügen
    fe = fg.add_entry()
    fe.id(link)
    fe.title(title)
    fe.link(href=link)
    fe.description(description)

  # XML-Datei speichern
  output_file = "dzne_news_feed.xml"
  fg.rss_file(output_file)
  print(
      f"Erfolgreich ausgeführt! Der RSS-Feed wurde in '{output_file}' gespeichert."
  )


if __name__ == "__main__":
  generate_dzne_rss()
