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

    # Suche nach den News-Einträgen auf der Seite
    # (Passt auf die typische HTML-Struktur der DZNE News-Karten)
    news_items = soup.find_all("article") or soup.find_all(
        "div", class_="news-list-item"
    )

    for item in news_items:
        # Titel und Link extrahieren
        title_tag = item.find(["h2", "h3", "h4"]) or item.find("a")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)

        # Link finden
        link_tag = item.find("a", href=True)
        if not link_tag:
            continue

        link = urljoin(target_url, link_tag["href"])

        # Beschreibung / Teaser-Text extrahieren (falls vorhanden)
        desc_tag = item.find("p")
        description = (
            desc_tag.get_text(strip=True) if desc_tag else "No description available."
        )

        # Feed-Eintrag erstellen
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
