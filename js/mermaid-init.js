// Inicjalizacja Mermaid dla diagramów
document.addEventListener('DOMContentLoaded', function() {
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
    }
});

// Fallback dla navigation.instant
const observer = new MutationObserver(function() {
    if (typeof mermaid !== 'undefined') {
        mermaid.init(undefined, '.mermaid');
    }
});
observer.observe(document.body, { childList: true, subtree: true });
