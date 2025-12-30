import base64
import os

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 自作の関数をインポート
# もし generate_article/generate_article.py が見つからないエラーが出る場合は
# パス構成を確認してください
try:
    from generate_article.generate_article import \
        generate_article_with_system_instruction
except ImportError:
    # Docker化や環境によってはパスの通し方が変わるため、念の為のエラーハンドリング
    raise ImportError("generate_article モジュールが見つかりません。")

# --- ここが重要: コマンドの main:app の 'app' はこれです ---
app = FastAPI()


# リクエストボディのデータ構造を定義 (Pydantic)
class ArticleRequest(BaseModel):
    theme: str
    level: str
    points: str = ""
    problem_text: str = ""
    problem_answer: str = ""
    problem_commentary: str = ""


# --- WordPress投稿用関数 ---
def post_draft_to_wordpress(title: str, content: str):
    wp_base_url = os.environ.get("WP_BASE_URL")
    wp_user = os.environ.get("WP_USERNAME")
    wp_password = os.environ.get("WP_APP_PASSWORD")

    if not all([wp_base_url, wp_user, wp_password]):
        raise ValueError("WordPressの環境変数が設定されていません(.envを確認してください)")

    # 認証情報の作成
    credentials = f"{wp_user}:{wp_password}"
    token = base64.b64encode(credentials.encode()).decode("utf-8")
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    # APIエンドポイント (/wp-json/wp/v2/posts)
    url = f"{wp_base_url}/wp-json/wp/v2/posts"

    # 投稿データ
    post_data = {
        "title": title,
        "content": content,
        "status": "draft"  # いきなり公開せず「下書き」にする
    }

    response = requests.post(url, headers=headers, json=post_data)

    if response.status_code >= 400:
        raise Exception(f"WordPress API Error: {response.status_code} - {response.text}")

    return response.json() # 作成された記事のデータを返す


@app.get("/")
def read_root():
    return {"message": "Bookkeeping Blog API is running!"}


@app.post("/create-article")
def create_article_endpoint(request: ArticleRequest):
    """
    記事生成APIのエンドポイント
    Geminiを使って記事を生成し、ユーザーが確認できるようにMarkdownを返す
    """
    try:
        # 記事本文を生成 (Gemini)
        markdown_text = generate_article_with_system_instruction(
            theme=request.theme,
            level=request.level,
            points=request.points,
            problem_text=request.problem_text,
            problem_answer=request.problem_answer,
            problem_commentary=request.problem_commentary
        )

        if not markdown_text:
            raise HTTPException(status_code=500,
                                detail="Gemini generated empty text.")

        # 記事タイトルを生成
        article_title = f"【{request.level}】{request.theme}の解説と演習問題"

        # 生成された記事を返す (まだWordPressには投稿しない)
        return {
            "article_markdown": markdown_text,
            "article_title": article_title
        }

    except Exception as e:
        print(f"Error: {e}") # ログ用
        raise HTTPException(status_code=500, detail=str(e))


# WordPress投稿用のリクエストボディ定義
class PublishRequest(BaseModel):
    title: str
    content: str


@app.post("/publish-article")
def publish_article_endpoint(request: PublishRequest):
    """
    ユーザーが確認後にボタンを押してWordPressに記事を投稿するエンドポイント
    """
    try:
        # WordPressに下書き投稿
        wp_response = post_draft_to_wordpress(request.title, request.content)

        # WordPressの管理画面（編集ページ）へのURLを取得
        post_id = wp_response.get("id")
        edit_url = f"{os.environ.get('WP_BASE_URL')}/wp-admin/post.php?post={post_id}&action=edit"

        return {
            "message": "Success! Article posted to WordPress as draft.",
            "post_id": post_id,
            "wordpress_url": edit_url
        }

    except Exception as e:
        print(f"Error: {e}") # ログ用
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/create-article")
# def create_article_endpoint(request: ArticleRequest):
#     """
#     記事生成APIのエンドポイント
#     """
#     try:
#         # Geminiを使って記事生成
#         # Pydanticモデルからデータを取り出して関数に渡す
#         markdown_text = generate_article_with_system_instruction(
#             theme=request.theme,
#             level=request.level,
#             points=request.points,
#             problem_text=request.problem_text,
#             problem_answer=request.problem_answer,
#             problem_commentary=request.problem_commentary
#         )

#         if not markdown_text:
#             raise HTTPException(status_code=500, detail="Gemini API returned empty response.")

#         return {"article_markdown": markdown_text}

#     except Exception as e:
#         # エラーが発生した場合は500エラーを返す
#         raise HTTPException(status_code=500, detail=str(e))
