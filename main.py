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
    """Kompresuj obrazek jeśli jest za duży. Duże PNG i BMP konwertuje do JPEG."""
    try:
        file_size_kb = os.path.getsize(img_path) / 1024

        with Image.open(img_path) as img:
            width, height = img.size
            needs_resize = width > MAX_WIDTH or height > MAX_HEIGHT
            needs_compress = file_size_kb > MAX_FILE_SIZE_KB
            is_png = str(img_path).lower().endswith('.png')
            is_bmp = str(img_path).lower().endswith('.bmp')
            has_transparency = img.mode == 'RGBA' and img.getchannel('A').getextrema()[0] < 255

            # BMP zawsze konwertuj do JPEG
            if is_bmp:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                if needs_resize:
                    img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
                new_path = img_path.with_suffix('.jpg')
                img.save(new_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
                os.remove(img_path)
                new_size_kb = os.path.getsize(new_path) / 1024
                print(f"[macros] Skompresowano: {img_path.name} -> {new_path.name} ({file_size_kb:.0f}KB -> {new_size_kb:.0f}KB)")
                return True

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
            list(gallery_dir.glob("*.webp")) +
            list(gallery_dir.glob("*.bmp"))
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

def _wyczysc_sieroty(portfolio_dir, img_portfolio_dir, slugs_z_csv):
    """Usuń pliki MD i foldery obrazków bez wpisu w CSV"""
    # Usuń osierocone pliki MD
    for md_file in portfolio_dir.glob("*.md"):
        slug = md_file.stem
        if slug not in slugs_z_csv:
            md_file.unlink()
            print(f"[macros] Usunięto sierotę: {md_file.name}")

    # Usuń puste foldery obrazków
    for img_dir in img_portfolio_dir.iterdir():
        if img_dir.is_dir() and img_dir.name not in slugs_z_csv:
            if not any(img_dir.iterdir()):  # pusty folder
                img_dir.rmdir()
                print(f"[macros] Usunięto pusty folder: {img_dir.name}")

def _kompresuj_obrazki_wiedza(project_dir):
    """Kompresuj wszystkie obrazki w folderach wiedzy"""
    img_wiedza_dir = Path(project_dir) / "docs" / "img" / "wiedza"
    if not img_wiedza_dir.exists():
        return

    for slug_dir in img_wiedza_dir.iterdir():
        if not slug_dir.is_dir():
            continue
        for img_path in slug_dir.glob("*"):
            if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                _kompresuj_obrazek(img_path)


def _generuj_podstrony(project_dir):
    """Automatycznie generuj/aktualizuj podstrony projektów z CSV"""
    docs_dir = Path(project_dir) / "docs"
    csv_path = docs_dir / "projekty.csv"
    portfolio_dir = docs_dir / "portfolio"
    img_portfolio_dir = docs_dir / "img" / "portfolio"

    if not csv_path.exists():
        return

    portfolio_dir.mkdir(exist_ok=True)

    slugs_z_csv = set()
    with open(csv_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            link = row['link'].strip('/')
            slug = link.replace('portfolio/', '')
            slugs_z_csv.add(slug)
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

            # Zespół autorski
            zespol = row.get('zespol_autorski', '')
            zespol_html = f"\n\n**Zespół autorski:** {zespol}\n" if zespol else ""

            # Generuj galerię (hero + pozostałe obrazki)
            gallery_html = ""
            all_images = [hero_image] + gallery_images if hero_image else gallery_images
            if all_images:
                gallery_html = '\n\n## Galeria\n\n<div class="gallery">\n'
                for img in all_images:
                    img_name = img.stem.replace('_', ' ').replace('-', ' ').title()
                    img_path = f"../../img/portfolio/{slug}/{img.name}"
                    gallery_html += f'''  <figure class="gallery-item">
    <a href="{img_path}" class="glightbox" data-gallery="portfolio-{slug}">
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
  <a href="{hero_path}" class="glightbox" data-gallery="portfolio-{slug}">
    <img src="{hero_path}" alt="{row['nazwa']}">
  </a>
</div>

<div class="project-meta">
  <div class="meta-item">
    <strong>Klient</strong>
    <span><b>{row.get('klient', '-')}</b></span>
  </div>
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
  <div class="meta-item">
    <strong>Realizacja</strong>
    <span>{row.get('realizacja', '')}</span>
  </div>
  <div class="meta-item">
    <strong>Wykonawca</strong>
    <span><b>{row.get('wykonawca', '-')}</b></span>
  </div>
</div>

---

## O projekcie

{opis_pelny}
{zespol_html}
## Zakres prac pracowni IA

{zakres_html}
{gallery_html}

---

<p style="text-align: center; margin-top: 2rem;">
  <a href="../" class="kategoria-link wiedza-back">Powrót do portfolio</a>
</p>
'''
            # Zapisz tylko jeśli treść się zmieniła
            if md_path.exists():
                existing = md_path.read_text(encoding='utf-8')
                if existing == content:
                    continue  # Bez zmian, nie zapisuj
            md_path.write_text(content, encoding='utf-8')
            print(f"[macros] Zaktualizowano: {md_path.name}")

    # Wyczyść sieroty (pliki bez wpisu w CSV)
    _wyczysc_sieroty(portfolio_dir, img_portfolio_dir, slugs_z_csv)

def define_env(env):
    """Define variables and macros for MkDocs"""

    # Generuj/aktualizuj podstrony projektów z CSV przy każdym buildzie
    _generuj_podstrony(env.project_dir)

    # Kompresuj obrazki w folderach wiedzy
    _kompresuj_obrazki_wiedza(env.project_dir)

    # Kompresuj obrazki oferty i o_nas
    for folder in ["oferta", "o_nas"]:
        img_dir = Path(env.project_dir) / "docs" / "img" / folder
        if img_dir.exists():
            for img in img_dir.glob("*"):
                if img.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                    _kompresuj_obrazek(img)

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

        # Sortuj po roku realizacji (malejąco - najnowsze pierwsze)
        projects.sort(key=lambda p: int(p.get('realizacja', 0) or 0), reverse=True)
        return projects

    @env.macro
    def portfolio_karty():
        """Generuj karty portfolio jako HTML"""
        projects = projekty()
        html = '<div class="portfolio-preview" id="portfolio-grid">\n'

        for p in projects:
            link = p['link'].replace('portfolio/', '')
            typ = p.get('typ', '').replace(' ', '-').lower()
            html += f'''
  <a class="portfolio-card" href="{link}" data-typ="{typ}">
    <img src="../{p['obrazek']}" alt="{p['nazwa']}">
    <div class="portfolio-info">
      <h4>{p['nazwa']}</h4>
      <p><strong>{p.get('klient') or p['typ']}</strong></p>
      <p>{p['typ']} &bull; {p['powierzchnia']} &bull; {p['stadium']}</p>
      <p>{p.get('realizacja', '')}</p>
    </div>
  </a>
'''

        html += '</div>\n'

        # Dodaj przycisk "Pokaż więcej" jeśli więcej niż 8 projektów
        if len(projects) > 8:
            html += '''
<div class="portfolio-toggle">
  <button class="kategoria-link wiedza-back" onclick="document.getElementById('portfolio-grid').classList.add('expanded'); this.style.display='none';">Pokaż więcej</button>
</div>
'''
        return html

    @env.macro
    def portfolio_typy():
        """Generuj przyciski filtra typów budynków"""
        projects = projekty()
        typy = sorted(set(p.get('typ', '') for p in projects if p.get('typ')))

        html = '<nav class="kategorie-nav portfolio-filter">\n'
        html += '  <button class="kategoria-link active" data-filter="all">Wszystkie</button>\n'
        for typ in typy:
            typ_slug = typ.replace(' ', '-').lower()
            html += f'  <button class="kategoria-link" data-filter="{typ_slug}">{typ}</button>\n'
        html += '</nav>\n'
        return html

    @env.macro
    def portfolio_karty_index():
        """Generuj karty portfolio dla strony głównej"""
        projects = projekty()
        html = '<div class="portfolio-preview">\n'

        for p in projects:
            html += f'''
  <a class="portfolio-card" href="{p['link']}">
    <img src="{p['obrazek']}" alt="{p['nazwa']}">
    <div class="portfolio-info">
      <h4>{p['nazwa']}</h4>
      <p>{p.get('klient') + ' · ' if p.get('klient') else ''}{p['typ']} · {p['powierzchnia']}</p>
    </div>
  </a>
'''

        html += '</div>'
        return html

    @env.macro
    def artykuly():
        """Wczytaj artykuły z pliku CSV"""
        csv_path = Path(env.project_dir) / "docs" / "artykuly.csv"
        articles = []

        if csv_path.exists():
            with open(csv_path, encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                # Pokaż drafty tylko przy serve (lokalny podgląd)
                import sys
                show_drafts = 'serve' in sys.argv
                for row in reader:
                    status = row.get('status')
                    if status == 'published' or (show_drafts and status == 'draft'):
                        articles.append(row)

        return articles

    @env.macro
    def has_hero(slug):
        """Sprawdź czy artykuł ma hero.jpg"""
        docs_dir = Path(env.project_dir) / "docs"
        hero_path = docs_dir / 'img' / 'wiedza' / slug / 'hero.jpg'
        return hero_path.exists()

    @env.macro
    def wiedza_hero(slug):
        """Wyświetl hero jeśli istnieje"""
        if has_hero(slug):
            return f'<img src="/img/wiedza/{slug}/hero.jpg" alt="" class="article-hero">'
        return ''

    @env.macro
    def wiedza_karty(from_index=False):
        """Generuj karty artykułów jako HTML"""
        articles = artykuly()

        if not articles:
            return '<p class="empty-state">Wkrótce pojawią się artykuły eksperckie.</p>'

        html = '<div class="wiedza-grid" id="wiedza-grid">\n'

        for a in articles:
            problem = a.get('problem', '')
            slug = a['slug']
            has_hero_img = has_hero(slug)

            # Różne ścieżki dla głównej vs /wiedza/
            if from_index:
                link = f"wiedza/{slug}/"
                img_src = f"img/wiedza/{slug}/hero.jpg"
            else:
                link = f"{slug}/"
                img_src = f"../img/wiedza/{slug}/hero.jpg"

            hero_img = f'<img src="{img_src}" alt="{a["title"]}" class="wiedza-hero">' if has_hero_img else ''
            hero_class = ' has-hero' if has_hero_img else ''

            html += f'''
  <a class="wiedza-card{hero_class}" href="{link}" data-problem="{problem}">
    {hero_img}
    <div class="wiedza-info">
      <span class="wiedza-category">{a.get('category', '')}</span>
      <h3>{a['title']}</h3>
      <p>{a.get('description', '')}</p>
    </div>
  </a>
'''

        html += '</div>\n'
        return html

    @env.macro
    def wiedza_karty_index():
        """Generuj 3 najnowsze artykuły dla strony głównej"""
        articles = artykuly()[:3]

        if not articles:
            return ''

        html = '<div class="wiedza-preview">\n'

        for a in articles:
            html += f'''
  <a class="wiedza-card" href="wiedza/{a['slug']}/">
    <div class="wiedza-info">
      <h4>{a['title']}</h4>
      <p>{a.get('description', '')}</p>
    </div>
  </a>
'''

        html += '</div>'
        return html

    @env.macro
    def wiedza_powiazane(current_slug, limit=3):
        """Generuj powiązane artykuły (ta sama kategoria lub problem)"""
        all_articles = artykuly()

        # Znajdź aktualny artykuł
        current = None
        for a in all_articles:
            if a['slug'] == current_slug:
                current = a
                break

        if not current:
            return ''

        # Szukaj powiązanych (ta sama kategoria lub problem)
        related = []
        for a in all_articles:
            if a['slug'] == current_slug:
                continue
            # Dopasowanie po kategorii lub problemie
            if (a.get('category') == current.get('category') or
                a.get('problem') == current.get('problem')):
                related.append(a)

        if not related:
            return ''

        # Ogranicz liczbę
        related = related[:limit]

        html = '<div class="wiedza-powiazane">\n'
        html += '<h3>Powiązane artykuły</h3>\n'
        html += '<div class="wiedza-grid wiedza-grid-powiazane">\n'

        for a in related:
            slug = a['slug']
            if has_hero(slug):
                # Karta z hero jako tło + overlay
                html += f'''
  <a class="wiedza-card wiedza-card-hero" href="/wiedza/{slug}/" style="background-image: url('/img/wiedza/{slug}/hero.jpg');">
    <div class="wiedza-overlay">
      <span class="wiedza-category">{a.get('category', '')}</span>
      <h4>{a['title']}</h4>
    </div>
  </a>
'''
            else:
                # Karta bez hero
                html += f'''
  <a class="wiedza-card" href="/wiedza/{slug}/">
    <div class="wiedza-info">
      <span class="wiedza-category">{a.get('category', '')}</span>
      <h4>{a['title']}</h4>
    </div>
  </a>
'''

        html += '</div>\n</div>'
        return html

    @env.macro
    def wiedza_kategoria(problem):
        """Generuj listę artykułów dla danej kategorii/problemu"""
        all_articles = artykuly()
        filtered = [a for a in all_articles if a.get('problem') == problem]

        if not filtered:
            return '<p class="empty-state">Brak artykułów w tej kategorii.</p>'

        html = '<div class="wiedza-grid">\n'

        for a in filtered:
            html += f'''
  <a class="wiedza-card" href="/wiedza/{a['slug']}/">
    <div class="wiedza-info">
      <span class="wiedza-category">{a.get('category', '')}</span>
      <h3>{a['title']}</h3>
      <p>{a.get('description', '')}</p>
    </div>
  </a>
'''

        html += '</div>\n'
        return html

    @env.macro
    def wiedza_wszystkie_kategorie():
        """Zwróć unikalne kategorie problemów"""
        all_articles = artykuly()
        problems = set()
        for a in all_articles:
            if a.get('problem'):
                problems.add(a['problem'])
        return sorted(problems)