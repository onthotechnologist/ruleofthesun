# Wiki Netlify

Небольшая статическая вики для деплоя на Netlify. Содержит 6 статей: предыстории (магик, пламярожденный, храмовник гаргаута), сеттинг (порча, состояние мира) и механику порчи (таблицы эффектов и аспектов). Дизайн — тёмная тема с мягкими красными акцентами и шрифтом JetBrains Mono.

## Локальная сборка

```bash
pip install -r requirements.txt
python3 build.py
```

После сборки откройте папку `dist/` в браузере (например, `python3 -m http.server --directory dist 8000` и перейдите на http://localhost:8000).

## Деплой на Netlify

Настройки сборки задаются **в Netlify**, а не в GitHub. GitHub — только источник кода.

1. Зайдите на [netlify.com](https://netlify.com), войдите в аккаунт.
2. **Add new site** → **Import an existing project** → выберите **GitHub** и авторизуйте доступ к репозиторию.
3. Укажите репозиторий и ветку. **Важно:** если вики лежит в подпапке `wiki-netlify` (а не в корне репозитория), обязательно укажите **Base directory**: `wiki-netlify` — иначе сборка пойдёт из корня репо и не найдёт `requirements.txt` и `build.py`.
4. В блоке **Build settings** (или в **Site configuration** → **Build & deploy** → **Build settings**) задайте:
   - **Build command:** `pip install -r requirements.txt && python3 build.py`
   - **Publish directory:** `dist`
   
   Если в корне (или в Base directory) есть файл `netlify.toml`, Netlify подхватит эти значения из него автоматически — тогда вручную можно ничего не вводить.
5. Нажмите **Deploy site**. Дальнейшие пуши в выбранную ветку будут запускать новый деплой.

Готовый сайт будет доступен по вашему домену Netlify. Добавление статей: положите `.md` в `content/` в нужную подпапку (предыстории, сеттинг, порча) и пересоберите/задеплойте.
