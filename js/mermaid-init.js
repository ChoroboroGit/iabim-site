// Inicjalizacja Mermaid dla diagramów
function initMermaid() {
    if (typeof mermaid === 'undefined') return;

    // Dekoduj HTML entities przed renderowaniem
    document.querySelectorAll('.mermaid').forEach(function(el) {
        if (!el.dataset.processed) {
            var text = el.innerHTML;
            text = text.replace(/&gt;/g, '>');
            text = text.replace(/&lt;/g, '<');
            text = text.replace(/&amp;/g, '&');
            el.innerHTML = text;
            el.dataset.processed = 'true';
        }
    });

    mermaid.initialize({ startOnLoad: false, theme: 'neutral' });
    mermaid.init(undefined, '.mermaid');
}

document.addEventListener('DOMContentLoaded', initMermaid);

// Fallback dla navigation.instant
var defined = false;
document.addEventListener('DOMContentLoaded', function() {
    if (defined) return;
    defined = true;
    var observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(m) {
            if (m.addedNodes.length) initMermaid();
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
