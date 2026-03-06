// Mermaid init - prosty
mermaid.initialize({ startOnLoad: false, theme: 'default' });

window.addEventListener('load', function() {
    document.querySelectorAll('.mermaid').forEach(function(el) {
        var code = el.textContent;
        code = code.replace(/&gt;/g, '>').replace(/&lt;/g, '<').replace(/&amp;/g, '&');
        el.textContent = code;
    });
    mermaid.init(undefined, '.mermaid');
});
