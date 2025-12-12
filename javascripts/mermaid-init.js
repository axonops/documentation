// Initialize mermaid diagrams
document.addEventListener("DOMContentLoaded", function () {
    mermaid.initialize({
        startOnLoad: true,
        theme: "default",
        securityLevel: "loose",
        flowchart: {
            useMaxWidth: true,
            htmlLabels: true
        },
        sequence: {
            useMaxWidth: true,
            wrap: true
        }
    });

    // Re-render mermaid diagrams when content changes (for instant loading)
    if (typeof document$ !== "undefined") {
        document$.subscribe(function () {
            mermaid.contentLoaded();
        });
    }
});
