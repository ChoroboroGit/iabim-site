// Mermaid init
mermaid.initialize({
    startOnLoad: false,
    theme: 'base',
    themeVariables: {
        primaryColor: '#448aff',
        primaryBorderColor: '#2962ff',
        primaryTextColor: '#ffffff',
        lineColor: '#448aff',
        arrowheadColor: '#448aff',
        background: 'transparent',
        mainBkg: 'transparent'
    }
});

window.addEventListener('load', function() {
    document.querySelectorAll('.mermaid').forEach(function(el) {
        var code = el.textContent;
        code = code.replace(/&gt;/g, '>').replace(/&lt;/g, '<').replace(/&amp;/g, '&');
        el.textContent = code;
    });
    mermaid.init(undefined, '.mermaid');
});
