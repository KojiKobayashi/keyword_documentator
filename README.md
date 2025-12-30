### 設定

.envファイル作成

'''
GEMINI_API_KEY="your_actual_api_key_here"
WP_BASE_URL="your_wordpress_site_url_here"
WP_USERNAME="your_wordpress_username_here"
WP_APP_PASSWORD="your_wordpress_app_password_here"
'''

### 実行

WP起動
docker compose up -d

uvicorn実行
uv run --env-file .env uvicorn main:app --reload

streamlit起動
uv run --env-file .env streamlit run app.py
