let templatesCache = [];
const USER_ID = document.querySelector('meta[name="user-id"]')?.content || "guest";

// 🔹 Site oluşturma butonu
document.getElementById('generateBtn').addEventListener('click', async () => {
    const topic = document.getElementById('topic').value.trim();
    if (!topic) return alert("Lütfen bir konu girin!");

    const res = await fetch('/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ topic })
    });

    if (res.status === 401) {
        alert("Lütfen giriş yaparak site oluşturun.");
        window.location.href = "/login";
        return;
    }

    const data = await res.json();
    if (data.error) {
        alert("Bir hata oluştu: " + data.error);
        return;
    }

    templatesCache = data.templates || [];
    const results = document.getElementById('results');
    results.innerHTML = "<h2>Yeni Oluşturulan Siteler</h2>";

    data.templates.forEach(t => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h3>${t.title}</h3>
            <p>${t.description}</p>
            <button onclick="previewSite('${t.id}')">Önizle</button>
            <button onclick="downloadSite('${t.id}')">ZIP Olarak İndir</button>
        `;
        results.appendChild(card);
    });
});


// 🔹 Önizleme fonksiyonu (her zaman dosyadan yükle)
async function previewSite(siteId) {
    try {
        // 🟢 Global değişkene atama (kaydetme işlemi için gerekli)
        window.currentSiteId = siteId;

        const htmlUrl = `/generated_sites/${USER_ID}/${siteId}/index.html`;
        const cssUrl = `/generated_sites/${USER_ID}/${siteId}/style.css`;

        console.log("🧩 Önizleme başlıyor:", htmlUrl);

        const htmlRes = await fetch(htmlUrl);
        if (!htmlRes.ok) throw new Error("HTML dosyası bulunamadı");
        const html = await htmlRes.text();

        const cssRes = await fetch(cssUrl);
        const css = cssRes.ok ? await cssRes.text() : "";

        // 🔹 Modal elemanlarını seç
        const modal = document.getElementById("previewModal");
        const iframe = document.getElementById("previewFrame");

        // 🔹 HTML + CSS'i iframe içine yaz
        const fullHtml = html.replace("</head>", `<style>${css}</style></head>`);
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        doc.open();
        doc.write(fullHtml);
        doc.close();

        // 🔹 Modalı göster
        modal.style.display = "flex";

        // 🔹 iframe içeriği yüklenince düzenlenebilir hale getir
        iframe.onload = () => {
            const innerDoc = iframe.contentDocument || iframe.contentWindow.document;

            // 🧠 Metinleri düzenlenebilir hale getir
            innerDoc.querySelectorAll("h1, h2, h3, p, a, span, li").forEach(el => {
                el.contentEditable = true;
                el.style.outline = "1px dashed rgba(0,0,0,0.2)";
                el.addEventListener("focus", () => el.style.outline = "2px solid #0078ff");
                el.addEventListener("blur", () => el.style.outline = "1px dashed rgba(0,0,0,0.2)");
            });

            // 🧠 Görselleri tıklayarak değiştirme
            innerDoc.querySelectorAll("img").forEach(img => {
                img.style.cursor = "pointer";
                img.addEventListener("click", () => {
                    const upload = document.createElement("input");
                    upload.type = "file";
                    upload.accept = "image/*";
                    upload.onchange = e => {
                        const file = e.target.files[0];
                        const reader = new FileReader();
                        reader.onload = ev => img.src = ev.target.result;
                        reader.readAsDataURL(file);
                    };
                    upload.click();
                });
            });

            // Eğer başka text edit fonksiyonun varsa onu çağır
            if (typeof enableTextEditing === "function") {
                enableTextEditing(innerDoc);
            }
        };

    } catch (err) {
        console.error("❌ Önizleme hatası:", err);
        alert("Önizleme başarısız. Site bulunamadı veya yüklenemedi.");
    }
}



// 🔹 ZIP indirme fonksiyonu
function downloadSite(siteId) {
    window.location.href = `/download/${siteId}`;
}


// 🔹 Geçmiş siteleri gösterme
document.getElementById('historyBtn').addEventListener('click', async () => {
    const res = await fetch('/history');
    const data = await res.json();

    const results = document.getElementById('results');
    results.innerHTML = "<h2>Geçmiş Oluşturulan Siteler</h2>";

    if (!data.sites.length) {
        results.innerHTML += "<p>Henüz oluşturulmuş site bulunmuyor.</p>";
        return;
    }

    data.sites.forEach(s => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h3>${s.title}</h3>
            <p>Oluşturulma Tarihi: ${s.created}</p>
            <button onclick="previewSite('${s.id}')">Önizle</button>
            <button onclick="downloadSite('${s.id}')">ZIP Olarak İndir</button>
        `;
        results.appendChild(card);
    });
});

// 🔹 Modal kontrol
function openModal(siteId) {
  const modal = document.getElementById('previewModal');
  const frame = document.getElementById('previewFrame');
  frame.src = `/generated_sites/${USER_ID}/${siteId}/index.html`;
  modal.style.display = 'flex';
}

function closeModal() {
  document.getElementById('previewModal').style.display = 'none';
}

// ---- Tema: seçilen renkten tonlar üret ve sayfaya uygula ----
function applyTheme() {
  const colorHex = document.getElementById("themeColor").value || "#3b82f6";
  const iframe = document.getElementById("previewFrame");
  const doc = iframe.contentDocument || iframe.contentWindow.document;

  // Yardımcılar
  const hexToHsl = (hex) => {
    let r = 0, g = 0, b = 0;
    const s = hex.replace("#","").toLowerCase();
    if (s.length === 3) {
      r = parseInt(s[0]+s[0],16); g = parseInt(s[1]+s[1],16); b = parseInt(s[2]+s[2],16);
    } else {
      r = parseInt(s.substr(0,2),16); g = parseInt(s.substr(2,2),16); b = parseInt(s.substr(4,2),16);
    }
    r/=255; g/=255; b/=255;
    const max = Math.max(r,g,b), min = Math.min(r,g,b);
    let h, s2, l = (max+min)/2;
    if (max===min) { h=0; s2=0; }
    else {
      const d = max-min;
      s2 = l>0.5 ? d/(2-max-min) : d/(max+min);
      switch(max){
        case r: h=(g-b)/d + (g<b?6:0); break;
        case g: h=(b-r)/d + 2; break;
        case b: h=(r-g)/d + 4; break;
      }
      h/=6;
    }
    return { h: Math.round(h*360), s: Math.round(s2*100), l: Math.round(l*100) };
  };
  const hsl = hexToHsl(colorHex);
  const make = (h, s, l, a=1) => `hsla(${h}, ${s}%, ${l}%, ${a})`;

  // Ana tonlar
  const primary     = make(hsl.h, hsl.s, Math.min(hsl.l, 48)); // navbar/btn
  const bgSoft      = make(hsl.h, Math.max(hsl.s-20, 10), Math.min(hsl.l+40, 96)); // sayfa bg
  const bgSection   = make(hsl.h, Math.max(hsl.s-25, 8),  Math.min(hsl.l+30, 92)); // section/card
  const accent      = make(hsl.h, Math.min(hsl.s+10, 95), Math.max(hsl.l-10, 25)); // başlık vurgusu
  const btnHover    = make(hsl.h, hsl.s, Math.max(hsl.l-8, 20));
  const borderSoft  = make(hsl.h, Math.max(hsl.s-35, 5), Math.min(hsl.l+20, 85));

  // CSS değişkenlerini head'e enjekte et (tekrar çağrılırsa güncelle)
  let vars = doc.getElementById("builder-theme-vars");
  const cssVars = `
    :root{
      --primary:${primary};
      --bg-page:${bgSoft};
      --bg-section:${bgSection};
      --accent:${accent};
      --btn-hover:${btnHover};
      --border-soft:${borderSoft};
      --text-on-primary:#fff;
    }
  `;
  if (!vars) {
    vars = doc.createElement("style");
    vars.id = "builder-theme-vars";
    vars.textContent = cssVars;
    doc.head.appendChild(vars);
  } else {
    vars.textContent = cssVars;
  }

  // Evrensel override stili (var'ları kullanan kurallar)
  let override = doc.getElementById("builder-theme-override");
  const cssOverride = `
    body{ background: var(--bg-page) !important; }
    header, nav, .navbar, .site-header{ background-color: var(--primary) !important; color: var(--text-on-primary) !important; }
    header a, nav a, .navbar a{ color: var(--text-on-primary) !important; }
    .btn, button, input[type="submit"]{
      background-color: var(--primary) !important; color: var(--text-on-primary) !important; border: none !important;
    }
    .btn:hover, button:hover, input[type="submit"]:hover{ background-color: var(--btn-hover) !important; }
    section, .section, .hero, .card, .feature, .panel, .content-block{
      background-color: var(--bg-section) !important; border-color: var(--border-soft) !important;
    }
    h1, h2, h3, .title, .heading{ color: var(--accent) !important; }
  `;
  if (!override) {
    override = doc.createElement("style");
    override.id = "builder-theme-override";
    override.textContent = cssOverride;
    doc.head.appendChild(override);
  } else {
    override.textContent = cssOverride;
  }
}


// 🔹 Logo yükleme
function updateLogo(retry = 0) {
  const fileInput = document.getElementById("logoUpload");
  const file = fileInput.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    const iframe = document.getElementById("previewFrame");
    const doc = iframe.contentDocument || iframe.contentWindow.document;

    // DOM yüklenmesini bekle
    if (!doc.body || doc.body.innerHTML.trim().length < 100) {
      if (retry < 5) {
        console.log("⏳ DOM yüklenmedi, tekrar denenecek...");
        setTimeout(() => updateLogo(retry + 1), 500);
      } else {
        alert("⚠️ Sayfa içeriği bulunamadı. Lütfen tekrar deneyin.");
      }
      return;
    }

    // 🎯 Tüm tema türlerini kapsayan logo seçiciler
    const logoSelectors = [
      ".logo",
      ".logo-urban",
      ".logo-farm",
      ".site-logo",
      "header .logo",
      "header .logo-urban",
      "header .logo-farm",
      ".navbar .logo",
      ".navbar-urban .logo-urban",
      ".navbar-farm .logo-farm",
    ];

    let logoEl = null;
    for (let sel of logoSelectors) {
      logoEl = doc.querySelector(sel);
      if (logoEl) break;
    }

    if (logoEl) {
      // 🧹 Var olan metni temizle
      logoEl.innerHTML = "";

      // 🖼 Yeni görsel logoyu oluştur
      const newLogo = doc.createElement("img");
      newLogo.src = e.target.result;
      newLogo.alt = "Site Logosu";
      newLogo.style.objectFit = "contain";
      newLogo.style.maxHeight = "55px";
      newLogo.style.maxWidth = "180px";
      newLogo.style.display = "inline-block";
      newLogo.style.verticalAlign = "middle";

      // 🩸 Tarz uyumlu margin
      newLogo.style.margin = "4px 8px";

      logoEl.appendChild(newLogo);

      console.log("✅ Logo başarıyla değiştirildi:", logoEl.className);
    } else {
      alert("⚠️ Bu şablonda tanımlı bir logo alanı bulunamadı.");
    }
  };

  reader.readAsDataURL(file);
}

// 🔹 Başlık güncelleme
function updateTitle() {
  const newTitle = document.getElementById("siteTitle").value;
  const iframe = document.getElementById("previewFrame");
  const doc = iframe.contentDocument || iframe.contentWindow.document;

  const h1 = doc.querySelector("h1, .hero-title, .main-title");
  if (h1) h1.textContent = newTitle;
  else doc.title = newTitle;
}

// 🔹 Favorilere kaydet (örnek olarak localStorage)
function saveFavorite() {
  const title = document.getElementById("siteTitle").value || "Adsız Site";
  const color = document.getElementById("themeColor").value;
  const favs = JSON.parse(localStorage.getItem("favorites") || "[]");
  favs.push({ title, color, date: new Date().toLocaleString() });
  localStorage.setItem("favorites", JSON.stringify(favs));
  alert("⭐ Site favorilere eklendi!");
}

let activeTextElement = null;

// 🧠 Site içindeki metinlere tıklanabilirlik kazandır
function enableTextEditing(previewDoc) {
  // 🔹 Düzenlenebilir tüm metin öğeleri
  const textEls = previewDoc.querySelectorAll(
    "h1, h2, h3, h4, h5, h6, p, span, a, li, strong, em, blockquote, figcaption, button"
  );

  textEls.forEach(el => {
    el.style.cursor = "text"; // Hover'da kullanıcıya düzenlenebilir hissi ver
    el.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      activeTextElement = el;
      showTextToolbar(e.pageX, e.pageY);
    });
  });

  console.log(`🧩 ${textEls.length} metin öğesi düzenlenebilir hale getirildi.`);
}


// 🎨 Araç çubuğunu konumlandır
function showTextToolbar(x, y) {
  const toolbar = document.getElementById("textToolbar");
  toolbar.style.display = "flex";
  toolbar.style.position = "fixed";
  toolbar.style.top = `${Math.min(y + 15, window.innerHeight - 60)}px`;
  toolbar.style.left = `${Math.min(x, window.innerWidth - 300)}px`;
  toolbar.style.background = "#fff";
  toolbar.style.border = "1px solid #ccc";
  toolbar.style.borderRadius = "8px";
  toolbar.style.padding = "6px 8px";
  toolbar.style.gap = "6px";
  toolbar.style.boxShadow = "0 2px 6px rgba(0,0,0,0.2)";
  toolbar.style.zIndex = "9999";
}


// 🧩 Stil uygulama fonksiyonu
function applyTextStyle(type) {
  if (!activeTextElement) return;
  switch (type) {
    case "bold":
      activeTextElement.style.fontWeight =
        activeTextElement.style.fontWeight === "bold" ? "normal" : "bold";
      break;
    case "italic":
      activeTextElement.style.fontStyle =
        activeTextElement.style.fontStyle === "italic" ? "normal" : "italic";
      break;
    case "underline":
      activeTextElement.style.textDecoration =
        activeTextElement.style.textDecoration === "underline" ? "none" : "underline";
      break;
  }
}

// 🎨 Yazı rengi, font tipi ve boyutu değiştiriciler
document.getElementById("textColor").addEventListener("input", (e) => {
  if (activeTextElement) activeTextElement.style.color = e.target.value;
});

document.getElementById("fontFamily").addEventListener("change", (e) => {
  if (activeTextElement) activeTextElement.style.fontFamily = e.target.value;
});

document.getElementById("fontSize").addEventListener("change", (e) => {
  if (activeTextElement) activeTextElement.style.fontSize = e.target.value;
});

// 🧹 Araç çubuğunu kapat
function closeTextToolbar() {
  document.getElementById("textToolbar").style.display = "none";
  activeTextElement = null;
}

// 🧩 Yeni içerik ekleme fonksiyonu (güncel)
async function addNewSection() {
  const iframe = document.getElementById("previewFrame");
  const doc = iframe.contentDocument || iframe.contentWindow.document;

  // Form alanlarını al
  const title = document.getElementById("newSectionTitle").value.trim();
  const desc = document.getElementById("newSectionDesc").value.trim();
  const imgFile = document.getElementById("newSectionImage").files[0];
  const imgPos = document.getElementById("imagePosition").value; // ✅ doğru id

  if (!title && !desc) {
    alert("⚠️ Lütfen en az başlık veya açıklama girin!");
    return;
  }

  // Görsel varsa yükle
  let imgSrc = null;
  if (imgFile) {
    const reader = new FileReader();
    imgSrc = await new Promise((resolve) => {
      reader.onload = (e) => resolve(e.target.result);
      reader.readAsDataURL(imgFile);
    });
  }

  // Yeni section oluştur
  const section = doc.createElement("section");
  section.style.display = "flex";
  section.style.alignItems = "center";
  section.style.justifyContent = "space-between";
  section.style.margin = "40px 0";
  section.style.gap = "20px";

  const textHTML = `
    <div>
      <h2>${title}</h2>
      <p>${desc}</p>
    </div>
  `;
  const imgHTML = imgSrc
    ? `<img src="${imgSrc}" style="width:40%;border-radius:10px;max-height:300px;object-fit:cover;">`
    : "";

  section.innerHTML =
    imgPos === "left" ? imgHTML + textHTML : textHTML + imgHTML;

  // Eklenme yeri
  const container =
    doc.querySelector("main, section, body") || doc.body;
  container.appendChild(section);

  alert("✅ Yeni içerik eklendi!");
}

function insertSection(doc, section) {
  const footer = doc.querySelector("footer");
  const main = doc.querySelector("main") || doc.body;
  const motto = main.querySelector("h1, h2");

  if (footer) {
    footer.insertAdjacentElement("beforebegin", section);
  } else if (motto && motto.parentElement) {
    motto.parentElement.insertAdjacentElement("afterend", section);
  } else {
    main.appendChild(section);
  }

  // Yeni metin alanları da düzenlenebilir olsun
  enableTextEditing(doc);

  alert("✅ Yeni içerik eklendi!");
}

// 🧩 Yeni içerik ekleme fonksiyonu (güncel)

document.getElementById("addSectionBtn").addEventListener("click", async () => {
  const title = document.getElementById("newSectionTitle").value.trim();
  const desc = document.getElementById("newSectionDesc").value.trim();
  const imgInput = document.getElementById("newSectionImage");
  const imgPos = document.getElementById("imagePosition").value;
  const iframe = document.getElementById("previewFrame");
  const doc = iframe.contentDocument || iframe.contentWindow.document;

  if (!title && !desc && !imgInput.files.length) {
    alert("⚠️ En az bir içerik girin.");
    return;
  }

  // Yeni bölüm elemanı oluştur
  const section = doc.createElement("section");
  section.style.display = "flex";
  section.style.alignItems = "center";
  section.style.gap = "20px";
  section.style.margin = "30px 0";
  section.style.padding = "20px";
  section.style.background = "#fafafa";
  section.style.borderRadius = "10px";
  section.style.boxShadow = "0 2px 6px rgba(0,0,0,0.1)";

  // Görsel seçildiyse yükle
  if (imgInput.files.length > 0) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = doc.createElement("img");
      img.src = e.target.result;
      img.style.width = "45%";
      img.style.borderRadius = "10px";

      const content = doc.createElement("div");
      content.style.width = "55%";
      content.innerHTML = `<h2>${title}</h2><p>${desc}</p>`;

      if (imgPos === "left") {
        section.appendChild(img);
        section.appendChild(content);
      } else {
        section.appendChild(content);
        section.appendChild(img);
      }

      insertSection(doc, section);
    };
    reader.readAsDataURL(imgInput.files[0]);
  } else {
    // Görsel yoksa sade metin bölümü
    const content = doc.createElement("div");
    content.style.width = "100%";
    content.innerHTML = `<h2>${title}</h2><p>${desc}</p>`;
    section.appendChild(content);
    insertSection(doc, section);
  }

  // Alanı sıfırla
  document.getElementById("newSectionTitle").value = "";
  document.getElementById("newSectionDesc").value = "";
  imgInput.value = "";
});

document.getElementById("saveEditedSiteBtn").addEventListener("click", async () => {
  const frame = document.getElementById("previewFrame");
  const siteHtml = frame.contentWindow.document.documentElement.outerHTML;

  if (!window.currentSiteId) {
    alert("❌ Kaydedilecek site bulunamadı!");
    return;
  }

  const payload = {
    site_id: window.currentSiteId,
    html_content: siteHtml
  };

  const res = await fetch("/save_edits", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  if (res.ok) {
    alert("✅ Değişiklikler kaydedildi: " + data.folder);
  } else {
    alert("❌ Hata: " + data.error);
  }
});
