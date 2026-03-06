// Mermaid init - styl jak info/definicja
mermaid.initialize({
    startOnLoad: false,
    theme: 'base',
    themeVariables: {
        primaryColor: '#e1f5fe',
        primaryBorderColor: '#00b8d4',
        primaryTextColor: '#01579b',
        lineColor: '#00b8d4',
        arrowheadColor: '#00b8d4',
        nodeBorderRadius: '4px'
    },
    flowchart: {
        nodeSpacing: 50,
        rankSpacing: 50,
        curve: 'basis'
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
