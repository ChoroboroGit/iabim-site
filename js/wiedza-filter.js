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

// Uruchom przy pierwszym załadowaniu
document.addEventListener('DOMContentLoaded', initWiedzaFilter);

// Uruchom przy nawigacji instant (MkDocs Material)
document.addEventListener('DOMContentSwitch', initWiedzaFilter);

// Fallback - obserwuj zmiany w DOM
if (typeof MutationObserver !== 'undefined') {
  const observer = new MutationObserver(function(mutations) {
    if (document.getElementById('kategorie-filter')) {
      initWiedzaFilter();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
}
