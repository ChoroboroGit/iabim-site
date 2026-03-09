// Funkcja inicjalizująca filtrowanie
function initWiedzaFilter() {
  const filterContainer = document.getElementById('kategorie-filter');
  const grid = document.getElementById('wiedza-grid');

  if (!filterContainer || !grid) return;

  const buttons = filterContainer.querySelectorAll('.kategoria-link');
  const cards = grid.querySelectorAll('.wiedza-card');

  buttons.forEach(btn => {
    btn.onclick = function() {
      const filter = this.dataset.filter;

      // Aktualizuj aktywny przycisk
      buttons.forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      // Filtruj karty
      cards.forEach(card => {
        if (filter === 'all' || card.dataset.problem === filter) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    };
  });
}

// Funkcja inicjalizująca filtrowanie portfolio
function initPortfolioFilter() {
  const filterContainer = document.querySelector('.portfolio-filter');
  const grid = document.getElementById('portfolio-grid');

  if (!filterContainer || !grid) return;

  const buttons = filterContainer.querySelectorAll('.kategoria-link');
  const cards = grid.querySelectorAll('.portfolio-card');

  buttons.forEach(btn => {
    btn.onclick = function() {
      const filter = this.dataset.filter;

      // Aktualizuj aktywny przycisk
      buttons.forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      // Przy filtrowaniu wyłącz limit nth-child
      grid.classList.toggle('expanded', filter !== 'all');

      // Filtruj karty
      cards.forEach(card => {
        if (filter === 'all' || card.dataset.typ === filter) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    };
  });
}

// Uruchom przy pierwszym załadowaniu
document.addEventListener('DOMContentLoaded', function() {
  initWiedzaFilter();
  initPortfolioFilter();
});

// Uruchom przy nawigacji instant (MkDocs Material)
document.addEventListener('DOMContentSwitch', function() {
  initWiedzaFilter();
  initPortfolioFilter();
});

// Fallback - obserwuj zmiany w DOM
if (typeof MutationObserver !== 'undefined') {
  const observer = new MutationObserver(function(mutations) {
    if (document.getElementById('kategorie-filter')) {
      initWiedzaFilter();
    }
    if (document.querySelector('.portfolio-filter')) {
      initPortfolioFilter();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
}
