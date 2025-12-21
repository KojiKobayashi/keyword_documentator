import os

import requests  # FastAPIにリクエストを送るため
import streamlit as st

# os や generate_article のインポートは削除

# --- 2. Streamlit UI (入力画面) の構築 ---

st.set_page_config(page_title="簿記ブログ記事 生成システム", layout="wide")
st.title("📝 簿記ブログ記事 生成システム")
st.markdown("---")

# 入力フォームを2カラムレイアウトにする
col1, col2 = st.columns(2)

# APIのエンドポイントURL（フェーズ1ではローカル、フェーズ2でクラウドURLに変更）
# FastAPIをローカルで動かす場合（デフォルト）
API_ENDPOINT = "http://127.0.0.1:8000/create-article"

# デプロイ後のURL（例）
# API_ENDPOINT = "https://your-api-endpoint-url.a.run.app/create-article"

with col1:
    st.subheader("STEP 1: 記事の基本情報を入力")

    # ① 学習テーマ（必須）
    theme = st.text_input("学習テーマ (必須)", placeholder="例: 三分法")

    # ② ターゲット資格レベル
    level = st.selectbox(
        "ターゲット資格レベル",
        ("簿記3級", "簿記2級", "簿記1級", "その他"),
        index=0 # デフォルトを「簿記3級」に
    )

    # ③ 解説のポイント
    points = st.text_area(
        "解説のポイント (任意)",
        height=150,
        placeholder="例: なぜ期末に「しーくり、くりしー」が必要なのか、その理屈を図で説明したい。"
    )

with col2:
    st.subheader("STEP 2: 演習問題を作成 (任意)")

    # ④ 演習問題
    problem_text = st.text_area("問題文", height=100, placeholder="例: 期首商品が100円...")
    problem_answer = st.text_area("答え", height=100, placeholder="例: 売上原価は400円です。")
    problem_commentary = st.text_area("答えの解説", height=100, placeholder="例: 売上原価は「期首在庫＋...」で計算できます。")


st.markdown("---")

# --- 3. 記事の生成と出力 ---

# ③ 生成ボタン
if st.button("記事を生成する", type="primary"):
    if not theme:
        st.error("「学習テーマ」は必須項目です。入力してください。")
    else:
        # --- ここからが変更点 ---
        # ローカル関数呼び出しの代わりに、FastAPIにリクエストを送る

        # APIに送るデータ（Pydanticモデルに対応）
        article_data = {
            "theme": theme,
            "level": level,
            "points": points,
            "problem_text": problem_text,
            "problem_answer": problem_answer,
            "problem_commentary": problem_commentary
        }

        try:
            with st.spinner("APIサーバーが記事を執筆中です..."):
                # FastAPIのエンドポイントにPOSTリクエスト
                response = requests.post(API_ENDPOINT, json=article_data, timeout=300) # タイムアウトを長めに設定

                # レスポンスのチェック
                response.raise_for_status() # エラーがあれば例外を発生させる

                # APIから返ってきたJSONデータを取得
                result = response.json()
                article_markdown = result.get("article_markdown")

            if article_markdown:
                st.success("記事が完成しました！")

                # --- 出力エリア ---
                st.subheader("生成された記事（プレビュー）")
                st.markdown(f'<div style="border: 1px solid #ccc; padding: 20px; border-radius: 5px;">{article_markdown}</div>', unsafe_allow_html=True)

                st.subheader("コピー用のMarkdownコード")
                st.code(article_markdown, language="markdown")
            else:
                st.error(f"APIからの応答が不正です: {result}")

        except requests.exceptions.ConnectionError:
            st.error(f"APIサーバー({API_ENDPOINT})に接続できません。FastAPIサーバーが起動しているか確認してください。")
        except requests.exceptions.RequestException as e:
            st.error(f"APIリクエスト中にエラーが発生しました: {e}")
        except Exception as e:
            st.error(f"記事の生成中に予期せぬエラーが発生しました: {e}")
        # --- ここまでが変更点 ---
