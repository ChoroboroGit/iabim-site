// Inicjalizacja GLightbox
function initGLightbox() {
  if (typeof GLightbox !== 'undefined') {
    GLightbox({
      selector: '.glightbox',
      touchNavigation: true,
      loop: true,
      closeButton: true,
      zoomable: true,
      draggable: true,
      openEffect: 'fade',
      closeEffect: 'fade',
      slideEffect: 'slide'
    });
  }
}

// Przy pierwszym załadowaniu
document.addEventListener('DOMContentLoaded', initGLightbox);

// Przy nawigacji instant (Material theme)
document.addEventListener('DOMContentSwitch', initGLightbox);

// Alternatywna metoda dla Material
if (typeof document$ !== 'undefined') {
  document$.subscribe(initGLightbox);
}
