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

// Automatyczne podpisy pod obrazkami (z alt)
function addImageCaptions() {
  document.querySelectorAll('article img[alt]').forEach(function(img) {
    // Pomijaj hero, miniaturki i karty
    if (img.classList.contains('article-hero') ||
        img.classList.contains('wiedza-hero') ||
        img.closest('.wiedza-card') ||
        img.closest('.portfolio-card') ||
        img.closest('.project-hero')) {
      return;
    }
    if (img.alt && img.alt.trim() !== '' && !img.closest('figure')) {
      var figure = document.createElement('figure');
      var figcaption = document.createElement('figcaption');
      figcaption.textContent = img.alt;
      img.parentNode.insertBefore(figure, img);
      figure.appendChild(img);
      figure.appendChild(figcaption);
    }
  });
}

// Przy pierwszym załadowaniu
document.addEventListener('DOMContentLoaded', function() {
  addImageCaptions();
  initGLightbox();
});

// Przy nawigacji instant (Material theme)
document.addEventListener('DOMContentSwitch', function() {
  addImageCaptions();
  initGLightbox();
});

// Alternatywna metoda dla Material
if (typeof document$ !== 'undefined') {
  document$.subscribe(function() {
    addImageCaptions();
    initGLightbox();
  });
}
