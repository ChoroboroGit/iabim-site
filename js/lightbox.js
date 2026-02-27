// Czekaj na pełne załadowanie strony
window.addEventListener('load', function() {
  if (typeof GLightbox !== 'undefined') {
    GLightbox({
      selector: '.glightbox',
      touchNavigation: true,
      loop: true,
      closeButton: true,
      zoomable: true,
      draggable: true
    });
  }
});

// Dla nawigacji SPA (Material theme)
document.addEventListener('DOMContentLoaded', function() {
  if (typeof GLightbox !== 'undefined') {
    GLightbox({
      selector: '.glightbox',
      touchNavigation: true,
      loop: true,
      closeButton: true,
      zoomable: true,
      draggable: true
    });
  }
});
