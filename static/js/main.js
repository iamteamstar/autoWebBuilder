let templatesCache = [];

document.getElementById('generateBtn').addEventListener('click', async () => {
    const topic = document.getElementById('topic').value.trim();
    if (!topic) return alert("Lütfen bir konu girin!");

    const res = await fetch('/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({topic})
    });

    const data = await res.json();
    templatesCache = data.templates; // 🔹 Global cache
    const results = document.getElementById('results');
    results.innerHTML = '';

    data.templates.forEach(t => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h3>${t.name}</h3>
            <p>${t.description}</p>
            <button onclick="previewTemplate(${t.id})">Önizle</button>
        `;
        results.appendChild(card);
    });
});

function previewTemplate(id) {
    const template = templatesCache.find(t => t.id === id);
    const previewWindow = window.open("", "_blank");
    previewWindow.document.write(template.html);
    previewWindow.document.close();

    const downloadBtn = previewWindow.document.createElement('button');
    downloadBtn.innerText = "ZIP Olarak İndir";
    downloadBtn.style.marginTop = "20px";
    downloadBtn.onclick = async () => {
        const res = await fetch('/download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({html: template.html, css: template.css})
        });
        const blob = await res.blob();
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = 'website.zip';
        link.click();
    };
    previewWindow.document.body.appendChild(downloadBtn);
}
