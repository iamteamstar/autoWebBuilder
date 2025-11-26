from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import io
import zipfile
import requests
import json
import re
from datetime import datetime
from ai_generator import generate_ai_templates
import firebase_admin
from firebase_admin import credentials, auth
from flask import session
from flask import redirect, url_for
import pyrebase
from firebase_admin import credentials, initialize_app, auth as admin_auth
from functools import wraps
from functools import wraps
from flask import redirect, url_for, jsonify, request, session
from PIL import Image 
from io import BytesIO
from shutil import copyfile
import requests, re, os, json
from flask import jsonify, request, session


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:  # eğer AJAX çağrısıysa
                return jsonify({"error": "not_authenticated"}), 401
            else:
                return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function




app = Flask(__name__)
app.secret_key = "supersecretkey_123456"
cred = credentials.Certificate("firebase_admin_key.json")
firebase_admin.initialize_app(cred)

firebase_config = {
    "apiKey": "AIzaSyDvlVVx0X2iaTkI2CBHdBnRRDSdl62tAU4",
    "authDomain": "aidestekliwebsiteolusturma.firebaseapp.com",
    "databaseURL": "",
    "projectId": "aidestekliwebsiteolusturma",
    "storageBucket": "aidestekliwebsiteolusturma.appspot.com",
    "messagingSenderId": "463394196191",
    "appId": "1:463394196191:web:23557bfdd953f4b1acb76a",
}
firebase = pyrebase.initialize_app(firebase_config)
firebase_auth = firebase.auth()

app.config['GENERATED_DIR'] = 'generated_sites'

# Klasör yoksa oluştur
if not os.path.exists(app.config['GENERATED_DIR']):
    os.makedirs(app.config['GENERATED_DIR'])
 




@app.route('/')
def index():
    user_email = session.get('email')
    return render_template('index.html', user_email=user_email)

def generate_images_for_site(folder_path: str, topic: str, count: int = 5):
    """Her site için konuya özel görseller üretir."""
    images_dir = os.path.join(folder_path, "images")
    os.makedirs(images_dir, exist_ok=True)
    saved_images = []

    for i in range(count):
        img_url = f"https://source.unsplash.com/600x400/?{topic},{i}"
        try:
            resp = requests.get(img_url, timeout=5)
            if resp.status_code == 200:
                img_path = os.path.join(images_dir, f"image_{i+1}.jpg")
                with open(img_path, "wb") as f:
                    f.write(resp.content)
                saved_images.append(f"images/image_{i+1}.jpg")
        except Exception as e:
            print(f"⚠️ Görsel indirilemedi ({img_url}): {e}")

    # Eğer hiç görsel alınamadıysa placeholder ekle
    if not saved_images:
        placeholder_src = os.path.join("static", "default_placeholder.jpg")
        placeholder_tgt = os.path.join(images_dir, "placeholder.jpg")
        if os.path.exists(placeholder_src):
            copyfile(placeholder_src, placeholder_tgt)
            saved_images.append("images/placeholder.jpg")
        else:
            print("⚠️ default_placeholder.jpg bulunamadı.")

    return saved_images


@app.route("/saved_sites")
@login_required
def saved_sites():
    import os, json
    from flask import session, render_template

    user_id = session.get("user_id")
    if not user_id:
        return "Oturum bulunamadı", 401

    # Kullanıcının kendi edited klasörü
    user_base = os.path.join(app.config["GENERATED_DIR"], str(user_id), "edited")

    sites = []
    if os.path.exists(user_base):
        for folder in os.listdir(user_base):
            meta_path = os.path.join(user_base, folder, "metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, encoding="utf-8") as f:
                    meta = json.load(f)
                sites.append({
                    "id": folder,
                    "saved_at": meta.get("saved_at"),
                    "original_id": meta.get("original_id"),
                    "edited": meta.get("edited", False)
                })

    return render_template("saved_sites.html", sites=sites)

@app.route("/preview_saved/<site_id>")
@login_required
def preview_saved(site_id):
    import os
    from flask import send_from_directory, session, abort

    user_id = session.get("user_id")
    if not user_id:
        return abort(401, "Oturum bulunamadı")

    # Kullanıcının düzenlenmiş site dizini
    edited_path = os.path.join(app.config["GENERATED_DIR"], str(user_id), "edited", site_id)

    # index.html dosyasını kontrol et
    index_path = os.path.join(edited_path, "index.html")
    if not os.path.exists(index_path):
        return abort(404, "Site bulunamadı veya silinmiş")

    # index.html dosyasını gönder
    return send_from_directory(edited_path, "index.html")

@app.route("/preview_saved/<site_id>/<path:filename>")
@login_required
def preview_saved_assets(site_id, filename):
    import os
    from flask import send_from_directory, session, abort

    user_id = session.get("user_id")
    edited_path = os.path.join(app.config["GENERATED_DIR"], str(user_id), "edited", site_id)

    file_path = os.path.join(edited_path, filename)
    if not os.path.exists(file_path):
        return abort(404)

    return send_from_directory(edited_path, filename)


@app.route('/generated_sites/<path:filename>')
def serve_generated_site(filename):
    base_dir = app.config['GENERATED_DIR']
    return send_from_directory(base_dir, filename)


@app.route('/generate', methods=['POST'])
@login_required
def generate():
    from PIL import Image
    from io import BytesIO

    data = request.get_json()
    topic = data.get('topic', '').strip()
    if not topic:
        return jsonify({"error": "Konu belirtilmedi."}), 400

    try:
        templates = generate_ai_templates(topic)
        saved_sites = []

        user_id = session.get("user_id", "guest")
        user_folder = os.path.join(app.config['GENERATED_DIR'], user_id)
        os.makedirs(user_folder, exist_ok=True)

        #  Görselleri üreten yardımcı fonksiyon (generate_images_for_site)
        def generate_images_for_site(folder_path: str, topic: str, count: int = 5):
            """Her site için konuya özel görseller üretir."""
            images_dir = os.path.join(folder_path, "images")
            os.makedirs(images_dir, exist_ok=True)
            saved_images = []

            for i in range(count):
                img_url = f"https://source.unsplash.com/600x400/?{topic},{i}"
                try:
                    resp = requests.get(img_url, timeout=5)
                    if resp.status_code == 200:
                        img_path = os.path.join(images_dir, f"image_{i+1}.jpg")
                        with open(img_path, "wb") as f:
                            f.write(resp.content)
                        saved_images.append(f"/generated_sites/{user_id}/{os.path.basename(folder_path)}/images/image_{i+1}.jpg")

                except Exception as e:
                    print(f"⚠️ Görsel indirilemedi: {e}")

            # Eğer hiç görsel alınamadıysa placeholder ekle
            if not saved_images:
                placeholder_src = os.path.join("static", "default_placeholder.jpg")
                placeholder_tgt = os.path.join(images_dir, "placeholder.jpg")
                if os.path.exists(placeholder_src):
                    copyfile(placeholder_src, placeholder_tgt)
                    saved_images.append("images/placeholder.jpg")
                else:
                    print("⚠️ default_placeholder.jpg bulunamadı.")

            return saved_images

        #  Şablonlara göre site klasörlerini oluştur
        for idx, t in enumerate(templates):
            folder_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}"
            folder_path = os.path.join(user_folder, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # 🔹 Her site için görselleri oluştur (doğru yer burası)
            image_list = generate_images_for_site(folder_path, topic)

            html = t.get('html', '')
            css = t.get('css', '')

            # 🔹 <img> etiketlerini güncelle
            # 🔹 <img> etiketlerini güncelle (mutlak URL ile)
            html = re.sub(
    r'<img([^>]*?)src=["\'](?!https?://)([^"\']+)["\']',
    lambda m: f'<img{m.group(1)}src="/generated_sites/{user_id}/{folder_name}/images/{os.path.basename(image_list[len(saved_sites) % len(image_list)])}"',
    html
)



            # 🔹 CSS dosyasını kaydet
            css_path = f"/generated_sites/{user_id}/{folder_name}/style.css"
            with open(os.path.join(folder_path, 'style.css'), 'w', encoding='utf-8') as f:
                f.write(css)

            # 🔹 CSS linkini ekle (eksikse)
            if '<link rel="stylesheet"' not in html and '<style' not in html:
                if '</head>' in html:
                    html = html.replace('</head>', f'<link rel="stylesheet" href="{css_path}">\n</head>')
                else:
                    html = f'<head><link rel="stylesheet" href="{css_path}"></head>\n' + html

            # 🔹 HTML dosyasını kaydet
            with open(os.path.join(folder_path, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html)

            # 🔹 Metadata oluştur
            title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
            title = title_match.group(1) if title_match else "Adsız Site"

            metadata = {
                "id": folder_name,
                "title": title,
                "topic": topic,
                "user_id": user_id,
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            #  Girintisi düzeltilmiş metadata kaydı
            with open(os.path.join(folder_path, "metadata.json"), "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            #  saved_sites append de aynı seviye
            saved_sites.append({
                "id": folder_name,
                "title": title,
                "description": t.get('description', 'Açıklama bulunamadı.')
            })

        #  Döngü dışına alınmış return
        return jsonify({"templates": saved_sites})

    except Exception as e:
        print(f"❌ Hata: {e}")
        return jsonify({"error": str(e)})




@app.route("/get_metadata/<site_id>", methods=["GET"])
def get_metadata(site_id):
    user_id = session.get("user_id", "guest")
    folder_path = os.path.join("generated_sites", str(user_id), site_id)
    meta_path = os.path.join(folder_path, "metadata.json")

    print("🔎 Metadata isteniyor:", meta_path)  # kontrol logu

    if not os.path.exists(meta_path):
        print("❌ Metadata bulunamadı:", meta_path)
        return jsonify({"error": "metadata bulunamadı"}), 404

    with open(meta_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("✅ Metadata bulundu:", data.keys())
    return jsonify(data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        try:
            # 🔹 Firebase kullanıcı doğrulaması
            user = firebase_auth.sign_in_with_email_and_password(email, password)
            id_token = user['idToken']

            # 🔹 ID token'ı doğrula ve UID al
            decoded_token = admin_auth.verify_id_token(id_token)
            uid = decoded_token['uid']

            # 🔹 Oturum kaydı
            session.permanent = True #login kalıcı
            session['user_id'] = uid
            session['email'] = email

            print(f"✅ Giriş başarılı: {email} (UID: {uid})")

            # 🔹 Başarılı yanıt
            return jsonify({
                "success": True,
                "message": "Giriş başarılı!",
                "user_id": uid,
                "email": email
            })

        except Exception as e:
            print("❌ Giriş hatası:", e)
            return jsonify({
                "success": False,
                "error": "Giriş başarısız. Lütfen e-posta ve şifrenizi kontrol edin."
            }), 401

    # Eğer GET isteğiyle çağrıldıysa HTML sayfasını render et
    return render_template('login.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        try:
            user = firebase_auth.create_user_with_email_and_password(email, password)
            # UID almak için admin tarafını kullan
            firebase_user = admin_auth.get_user_by_email(email)
            print(f"✅ Yeni kullanıcı oluşturuldu: {email} (UID: {firebase_user.uid})")

            return jsonify({"message": "Kayıt başarılı!", "uid": firebase_user.uid})
        except Exception as e:
            print("❌ Kayıt hatası:", e)
            return jsonify({"error": str(e)}), 400

    return render_template('register.html')


@app.route('/logout')
def logout():
    email = session.get('email', '')
    session.clear()
    print(f"👋 Kullanıcı çıkış yaptı: {email}")
    return redirect(url_for('login'))

# BU KISMI DENE DAHA DENENMEDİ
# Kullanıcı bazlı önizleme (index.html, style.css, images/* vs. hepsi için)
@app.route('/generated_sites/<user_id>/<site_id>/<path:filename>')
def serve_generated_file(user_id, site_id, filename):
    base_path = os.path.join(app.config['GENERATED_DIR'], user_id, site_id)
    full_path = os.path.join(base_path, filename)
    if not os.path.exists(base_path):
        return "Klasör bulunamadı.", 404
    if not os.path.exists(full_path):
        # Hataları görmek istersen:
        print("❌ Önizleme dosyası yok:", full_path)
    return send_from_directory(base_path, filename)


@app.route("/save_edits", methods=["POST"])
@login_required
def save_edits():
    import os, shutil, json
    from datetime import datetime
    from flask import request, jsonify, session

    data = request.get_json()
    site_id = data.get("site_id")
    html_content = data.get("html_content")

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Oturum bulunamadı"}), 401

    if not site_id or not html_content:
        return jsonify({"error": "Eksik veri"}), 400

    # 🔹 Kullanıcıya özel site dizinini oluştur
    user_base = os.path.join(app.config['GENERATED_DIR'], str(user_id))
    base_dir = os.path.join(user_base, site_id)

    if not os.path.exists(base_dir):
        return jsonify({"error": "Orijinal site bulunamadı"}), 404

    # 🔹 Düzenlenmiş siteyi kaydedeceğimiz ana klasör
    edited_root = os.path.join(user_base, "edited")
    os.makedirs(edited_root, exist_ok=True)

    # 🔹 Yeni düzenlenmiş klasör ismi
    edited_dir = os.path.join(edited_root, f"{site_id}_edited")

    # Eski düzenleme varsa sil
    if os.path.exists(edited_dir):
        shutil.rmtree(edited_dir)

    shutil.copytree(base_dir, edited_dir)

    # index.html üzerine yaz
    index_path = os.path.join(edited_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # metadata oluştur
    metadata = {
        "original_id": site_id,
        "edited": True,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    meta_path = os.path.join(edited_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return jsonify({"message": "Değişiklikler kaydedildi", "folder": f"{site_id}_edited"})




@app.route('/download/<site_id>', methods=['GET'])
@login_required
def download(site_id):
    import io, os, zipfile
    from flask import send_file, jsonify, session

    user_id = session.get('user_id')

    # Kullanıcının ana site dizini
    user_base = os.path.join(app.config['GENERATED_DIR'], user_id)

    # 1️⃣ Düzenlenmiş (edited) site mi kontrol et
    if "_edited" in site_id:
        folder_path = os.path.join(user_base, "edited", site_id)
    else:
        folder_path = os.path.join(user_base, site_id)

    # 2️⃣ Klasör gerçekten var mı kontrol et
    if not os.path.exists(folder_path):
        return jsonify({"error": "Site bulunamadı."}), 404

    # 3️⃣ ZIP arabelleği oluştur
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zf.write(file_path, arcname=arcname)

    zip_buffer.seek(0)

    # 4️⃣ Dosya adını dinamik belirle
    zip_name = f"{site_id}.zip"
    if not zip_name.endswith(".zip"):
        zip_name = f"{site_id}.zip"

    # 5️⃣ ZIP'i döndür
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name=zip_name,
        mimetype='application/zip'
    )


# 🔹 Geçmiş site listesi (metadata destekli)
@app.route('/history', methods=['GET'])
@login_required
def history():
    import os, json
    from datetime import datetime
    from flask import jsonify, session

    sites = []
    user_id = session.get("user_id", "guest")
    user_folder = os.path.join(app.config['GENERATED_DIR'], user_id)
    edited_folder = os.path.join(user_folder, "edited")

    # 🔹 Orijinal siteler
    if os.path.exists(user_folder):
        for folder_name in sorted(os.listdir(user_folder), reverse=True):
            folder_path = os.path.join(user_folder, folder_name)
            if not os.path.isdir(folder_path) or folder_name == "edited":
                continue

            meta_path = os.path.join(folder_path, "metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                meta.setdefault("description", "Açıklama bulunamadı.")
                meta["type"] = "original"
                meta["id"] = folder_name
                sites.append(meta)
            else:
                created_time = datetime.fromtimestamp(os.path.getctime(folder_path)).strftime('%Y-%m-%d %H:%M:%S')
                sites.append({
                    "id": folder_name,
                    "title": folder_name,
                    "description": "Açıklama bulunamadı.",
                    "created": created_time,
                    "type": "original"
                })

    # 🔹 Düzenlenmiş (edited) siteler
    if os.path.exists(edited_folder):
        for folder_name in sorted(os.listdir(edited_folder), reverse=True):
            folder_path = os.path.join(edited_folder, folder_name)
            if not os.path.isdir(folder_path):
                continue
            meta_path = os.path.join(folder_path, "metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                meta.setdefault("description", "Düzenlenmiş site versiyonu.")
                meta["type"] = "edited"
                meta["id"] = folder_name
                sites.append(meta)

    return jsonify({"sites": sites})


@app.route('/profile')
@login_required
def profile():
    user_email = session.get('email')
    user_id = session.get('user_id')

    # 🔹 Kullanıcının oluşturduğu siteleri getir
    user_folder = os.path.join(app.config['GENERATED_DIR'], user_id)
    sites = []
    if os.path.exists(user_folder):
        for folder_name in sorted(os.listdir(user_folder), reverse=True):
            folder_path = os.path.join(user_folder, folder_name)
            meta_path = os.path.join(folder_path, "metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    sites.append(meta)

    return render_template('profile.html', user_email=user_email, user_id=user_id, sites=sites)

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    from firebase_admin import auth as admin_auth
    data = request.get_json()
    new_password = data.get('new_password')
    user_id = session.get('user_id')

    try:
        admin_auth.update_user(user_id, password=new_password)
        return jsonify({"message": "Şifre başarıyla değiştirildi!"})
    except Exception as e:
        print("❌ Şifre değiştirme hatası:", e)
        return jsonify({"error": str(e)}), 400

@app.route('/delete_site/<site_id>', methods=['DELETE'])
@login_required
def delete_site(site_id):
    user_id = session.get('user_id')
    site_path = os.path.join(app.config['GENERATED_DIR'], user_id, site_id)
    try:
        if os.path.exists(site_path):
            import shutil
            shutil.rmtree(site_path)
            print(f"🗑️ Site silindi: {site_path}")
            return jsonify({"message": "Site silindi."})
        else:
            return jsonify({"error": "Site bulunamadı."}), 404
    except Exception as e:
        print("❌ Silme hatası:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/fix_old_images')
def fix_old_images():
    import re, os
    from shutil import copyfile

    base_dir = app.config['GENERATED_DIR']
    placeholder_source = os.path.join("static", "default_placeholder.jpg")

    if not os.path.exists(placeholder_source):
        return "⚠️ static/default_placeholder.jpg bulunamadı. Lütfen oluştur."

    fixed = 0

    for user_folder in os.listdir(base_dir):
        user_path = os.path.join(base_dir, user_folder)
        if not os.path.isdir(user_path):
            continue

        for site_folder in os.listdir(user_path):
            site_path = os.path.join(user_path, site_folder)
            index_file = os.path.join(site_path, "index.html")
            image_folder = os.path.join(site_path, "images")

            if not os.path.exists(index_file):
                continue

            os.makedirs(image_folder, exist_ok=True)

            placeholder_target = os.path.join(image_folder, "placeholder.jpg")
            try:
                copyfile(placeholder_source, placeholder_target)
                print(f"✅ Görsel kopyalandı: {placeholder_target}")
            except Exception as e:
                print(f"⚠️ Kopyalama hatası: {placeholder_target} ({e})")

            with open(index_file, "r", encoding="utf-8") as f:
                html = f.read()

            html = re.sub(
                r'https?://via\.placeholder\.com/[^\s"\']+',
                "images/placeholder.jpg",
                html
            )

            with open(index_file, "w", encoding="utf-8") as f:
                f.write(html)

            fixed += 1

    return f"✅ {fixed} site güncellendi ve placeholder görseller eklendi."



if __name__ == '__main__':
    app.run(debug=True)
