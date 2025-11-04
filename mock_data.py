def generate_mock_templates(topic):
    # Gerçek sistemde burada AI çağrısı olacak
    return [
        {
            "id": 1,
            "name": "Minimalist Tema",
            "description": f"{topic} için sade ve modern bir yapı.",
            "html": """<!DOCTYPE html>
<html><head><title>Minimalist Site</title><link rel="stylesheet" href="style.css"></head>
<body><h1>Hoş Geldiniz!</h1><p>Bu site, {topic} konusuna odaklanır.</p></body></html>""".replace("{topic}", topic),
            "css": "body {font-family: sans-serif; background-color: #f5f5f5; text-align:center; color:#333;}"
        },
        {
            "id": 2,
            "name": "Açık Mavi Tema",
            "description": f"{topic} için teknoloji hissi veren mavi tonlar.",
            "html": """<!DOCTYPE html>
<html><head><title>Açık Mavi Site</title><link rel="stylesheet" href="style.css"></head>
<body><h1>{topic}</h1><p>Modern ve ferah bir tema.</p></body></html>""".replace("{topic}", topic),
            "css": "body {background-color: #e8f1ff; color:#004080; font-family:Arial; text-align:center;}"
        },
        {
            "id": 3,
            "name": "Koyu Profesyonel Tema",
            "description": f"{topic} için koyu tonlarda profesyonel bir tasarım.",
            "html": """<!DOCTYPE html>
<html><head><title>Koyu Tema</title><link rel="stylesheet" href="style.css"></head>
<body><h1>{topic}</h1><p>Karanlık, modern ve etkileyici görünüm.</p></body></html>""".replace("{topic}", topic),
            "css": "body {background-color:#111; color:#fff; font-family:'Segoe UI'; text-align:center;}"
        }
    ]
