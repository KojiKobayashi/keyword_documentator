import os

import google.generativeai as genai

# APIキーの設定（環境変数から読み込むことを推奨）
# 例: os.environ['GEMINI_API_KEY'] = "YOUR_API_KEY"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])


# 1. システムインストラクションとして「長い命令書」を定義
system_prompt = f"""
# 命令書: あなたは簿記教育を専門とするプロのブログライターです。

以下の入力情報と出力形式に従って、簿記学習者向けのブログ記事を生成してください。

# 出力形式
* 全体をMarkdown形式で出力してください。
* 記事のタイトルは`# 見出し1`としてください。
* 読者の興味を引くキャッチーな導入文から始めてください。
* 記事の冒頭（導入文の直後）に、テーマに関連する主要な勘定科目をまとめた「### この記事の主役たち（勘定科目サマリー）」を必ず含めてください。勘定科目の選定は、テーマと解説のポイントからあなた自身で判断してください。
* 見出しは`## 見出し2`、小見出しは`### 見出し3`を使用してください。
* 「### 【演習問題にチャレンジ！】」というセクションを設けてください。
*  **【最重要】** 演習問題の答えは、読者がすぐに見えないように、必ずトグルの中に書いてください。そして初期状態で閉じてください。他の形式は認められません。
* 記事の最後には、学習のポイントをまとめた「## まとめ」セクションを設けてください。
* 専門用語は避け、ターゲットレベルの学習者が理解できる、丁寧で親しみやすいトーンで執筆してください。
"""

# 2. モデルを「System Instruction」付きで初期化
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction=system_prompt
)


# 3. 記事を生成する（毎回、可変部分のプロンプトだけを送る）
#    毎回チャットを続ける必要はない

def generate_article_with_system_instruction(
        theme,
        level="",
        points="",
        problem_text="",
        problem_answer="",
        problem_commentary=""):
    """毎回可変部分だけの短いプロンプトを作成して記事を生成"""

    user_prompt = f"""
# 入力情報
* テーマ: {theme}
* ターゲットレベル: {level}
* 解説のポイント: {points}
* 演習問題:
    * 問題文: {problem_text}
    * 答え: {problem_answer}
    * 解説: {problem_commentary}
"""
    response = model.generate_content(user_prompt)
    return response.text


if __name__ == "__main__":
    # --- 実行 ---
    print("--- 1回目の記事生成 ---")
    article1 = generate_article_with_system_instruction(
        "三分法", "簿記3級", "しーくりの部分を重点的に")
    print(article1)

    print("\n--- 2回目の記事生成 ---")
    article2 = generate_article_with_system_instruction(
        "固定資産の売却", "簿記2級", "間接法と直接法の違いが分かるように")
    print(article2)
