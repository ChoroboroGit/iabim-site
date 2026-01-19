"""
MkDocs Macros - moduł do wczytywania projektów z CSV
Obrazki zarządzane przez foldery img/portfolio/{slug}/
- Pierwszy obrazek (alfabetycznie) = hero + miniaturka
- Reszta = galeria
- Automatyczna kompresja dużych obrazków
"""
import csv
from pathlib import Path
from PIL import Image, ImageFile
import os

# Pozwól na ładowanie uszkodzonych/niekompletnych obrazów
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Ustawienia kompresji
MAX_WIDTH = 1920       # maksymalna szerokość w px
MAX_HEIGHT = 1080      # maksymalna wysokość w px
JPEG_QUALITY = 85      # jakość JPEG (1-100)
MAX_FILE_SIZE_KB = 500 # maksymalny rozmiar pliku w KB

def _kompresuj_obrazek(img_path):
    """Kompresuj obrazek jeśli jest za duży. Duże PNG konwertuje do JPEG."""
    try:
        file_size_kb = os.path.getsize(img_path) / 1024

        with Image.open(img_path) as img:
            width, height = img.size
            needs_resize = width > MAX_WIDTH or height > MAX_HEIGHT
            needs_compress = file_size_kb > MAX_FILE_SIZE_KB
            is_png = str(img_path).lower().endswith('.png')
            has_transparency = img.mode == 'RGBA' and img.getchannel('A').getextrema()[0] < 255

            # Nie kompresuj jeśli nie trzeba lub to już JPEG pod limitem
            is_jpeg = str(img_path).lower().endswith(('.jpg', '.jpeg'))
            if not needs_resize:
                if not needs_compress:
                    return False
                # JPEG już skompresowany - nie da się bardziej
                if is_jpeg and file_size_kb < 700:
                    return False

            # Zmień rozmiar zachowując proporcje
            if needs_resize:
                img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)

            # Dla dużych PNG bez przezroczystości - konwertuj do JPEG
            if is_png and file_size_kb > MAX_FILE_SIZE_KB and not has_transparency:
                # Konwertuj do RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Zmień rozszerzenie na .jpg
                new_path = img_path.with_suffix('.jpg')
                img.save(new_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)

                # Usuń stary PNG
                os.remove(img_path)

                new_size_kb = os.path.getsize(new_path) / 1024
                print(f"[macros] Skompresowano: {img_path.name} -> {new_path.name} ({file_size_kb:.0f}KB -> {new_size_kb:.0f}KB)")
                return True

            # Standardowa kompresja
            if img.mode == 'P':
                img = img.convert('RGBA' if 'transparency' in img.info else 'RGB')

            save_kwargs = {}
            if str(img_path).lower().endswith(('.jpg', '.jpeg')):
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                save_kwargs = {'quality': JPEG_QUALITY, 'optimize': True}
            elif str(img_path).lower().endswith('.png'):
                save_kwargs = {'optimize': True}
            elif str(img_path).lower().endswith('.webp'):
                save_kwargs = {'quality': JPEG_QUALITY, 'optimize': True}

            img.save(img_path, **save_kwargs)

            new_size_kb = os.path.getsize(img_path) / 1024
            print(f"[macros] Skompresowano: {img_path.name} ({file_size_kb:.0f}KB -> {new_size_kb:.0f}KB)")
            return True

    except Exception as e:
        print(f"[macros] Blad kompresji {img_path.name}: {e}")
        return False

def _pobierz_obrazki(img_portfolio_dir, slug, kompresuj=True):
    """Pobierz listę obrazków z folderu projektu"""
    gallery_dir = img_portfolio_dir / slug
    if not gallery_dir.exists():
        return [], None

    def _skanuj_obrazki():
        return sorted(
            list(gallery_dir.glob("*.jpg")) +
            list(gallery_dir.glob("*.jpeg")) +
            list(gallery_dir.glob("*.png")) +
            list(gallery_dir.glob("*.webp"))
        )

    images = _skanuj_obrazki()
    if not images:
        return [], None

    # Kompresuj obrazki jeśli potrzeba
    if kompresuj:
        for img_path in images:
            _kompresuj_obrazek(img_path)
        # Po kompresji odśwież listę (PNG mogły zostać zamienione na JPG)
        images = _skanuj_obrazki()

    if not images:
        return [], None

    # Pierwszy obrazek = hero, reszta = galeria
    hero = images[0]
    gallery = images[1:] if len(images) > 1 else []

    return gallery, hero

def _generuj_podstrony(project_dir):
    """Automatycznie generuj/aktualizuj podstrony projektów z CSV"""
    docs_dir = Path(project_dir) / "docs"
    csv_path = docs_dir / "projekty.csv"
    portfolio_dir = docs_dir / "portfolio"
    img_portfolio_dir = docs_dir / "img" / "portfolio"

    if not csv_path.exists():
        return

    portfolio_dir.mkdir(exist_ok=True)

    with open(csv_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            link = row['link'].strip('/')
            slug = link.replace('portfolio/', '')
            md_path = portfolio_dir / f"{slug}.md"

            # Utwórz folder na obrazki jeśli nie istnieje
            gallery_dir = img_portfolio_dir / slug
            gallery_dir.mkdir(parents=True, exist_ok=True)

            # Pobierz obrazki z folderu
            gallery_images, hero_image = _pobierz_obrazki(img_portfolio_dir, slug)

            # Ścieżka do hero image
            if hero_image:
                hero_path = f"../../img/portfolio/{slug}/{hero_image.name}"
            else:
                hero_path = "../../img/placeholder.png"  # fallback

            # Pobierz pełny opis lub użyj krótkiego
            opis_pelny = row.get('opis_pelny', '') or row.get('opis', '')

            # Parsuj zakres BIM (separator: |)
            zakres_bim = row.get('zakres_bim', '')
            if zakres_bim:
                zakres_items = [f"- {item.strip()}" for item in zakres_bim.split('|') if item.strip()]
                zakres_html = '\n'.join(zakres_items)
            else:
                zakres_html = "- Model architektoniczny\n- Dokumentacja wykonawcza\n- Koordynacja międzybranżowa"

            # Generuj galerię z pozostałych obrazków
            gallery_html = ""
            if gallery_images:
                gallery_html = '\n\n## Galeria\n\n<div class="gallery">\n'
                for img in gallery_images:
                    img_name = img.stem.replace('_', ' ').replace('-', ' ').title()
                    img_path = f"../../img/portfolio/{slug}/{img.name}"
                    gallery_html += f'''  <figure class="gallery-item">
    <a href="{img_path}" target="_blank">
      <img src="{img_path}" alt="{img_name}">
      <figcaption>{img_name}</figcaption>
    </a>
  </figure>
'''
                gallery_html += '</div>'

            content = f'''---
name: "{row['nazwa']}"
type: "{row['typ']}"
area: "{row['powierzchnia']}"
stage: "{row['stadium']}"
---

# {row['nazwa']}

<div class="project-hero">
  <img src="{hero_path}" alt="{row['nazwa']}">
</div>

<div class="project-meta">
  <div class="meta-item">
    <strong>Typ</strong>
    <span>{row['typ']}</span>
  </div>
  <div class="meta-item">
    <strong>Powierzchnia</strong>
    <span>{row['powierzchnia']}</span>
  </div>
  <div class="meta-item">
    <strong>Stadium</strong>
    <span>{row['stadium']}</span>
  </div>
  <div class="meta-item">
    <strong>Lokalizacja</strong>
    <span>{row['lokalizacja']}</span>
  </div>
</div>

---

## O projekcie

{opis_pelny}

## Zakres prac BIM

{zakres_html}
{gallery_html}

---

<p style="text-align: center; margin-top: 2rem;">
  <a href="../" class="btn btn-outline">Powrót do portfolio</a>
</p>
'''
            # Zapisz tylko jeśli treść się zmieniła
            if md_path.exists():
                existing = md_path.read_text(encoding='utf-8')
                if existing == content:
                    continue  # Bez zmian, nie zapisuj
            md_path.write_text(content, encoding='utf-8')
            print(f"[macros] Zaktualizowano: {md_path.name}")

def define_env(env):
    """Define variables and macros for MkDocs"""

    # Generuj/aktualizuj podstrony projektów z CSV przy każdym buildzie
    _generuj_podstrony(env.project_dir)

    docs_dir = Path(env.project_dir) / "docs"
    img_portfolio_dir = docs_dir / "img" / "portfolio"

    @env.macro
    def projekty():
        """Wczytaj projekty z pliku CSV"""
        csv_path = Path(env.project_dir) / "docs" / "projekty.csv"
        projects = []

        if csv_path.exists():
            with open(csv_path, encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    # Dodaj ścieżkę do hero image z folderu
                    link = row['link'].strip('/')
                    slug = link.replace('portfolio/', '')
                    _, hero = _pobierz_obrazki(img_portfolio_dir, slug)
                    if hero:
                        row['obrazek'] = f"img/portfolio/{slug}/{hero.name}"
                    else:
                        row['obrazek'] = "img/placeholder.png"
                    projects.append(row)

        return projects

    @env.macro
    def portfolio_karty():
        """Generuj karty portfolio jako HTML"""
        projects = projekty()
        html = '<div class="portfolio-preview">\n'

        for p in projects:
            link = p['link'].replace('portfolio/', '')
            html += f'''
  <div class="portfolio-card">
    <img src="../{p['obrazek']}" alt="{p['nazwa']}">
    <div class="portfolio-info">
      <h4>{p['nazwa']}</h4>
      <p><strong>{p['typ']}</strong></p>
      <p>{p['powierzchnia']} &bull; {p['stadium']}</p>
      <a href="{link}">Zobacz szczegóły</a>
    </div>
  </div>
'''

        html += '</div>'
        return html

    @env.macro
    def portfolio_karty_index():
        """Generuj karty portfolio dla strony głównej"""
        projects = projekty()
        html = '<div class="portfolio-preview">\n'

        for p in projects:
            html += f'''
  <div class="portfolio-card">
    <img src="{p['obrazek']}" alt="{p['nazwa']}">
    <div class="portfolio-info">
      <h4>{p['nazwa']}</h4>
      <p>{p['typ']} &bull; {p['powierzchnia']}</p>
      <a href="{p['link']}">Zobacz projekt</a>
    </div>
  </div>
'''

        html += '</div>'
        return html