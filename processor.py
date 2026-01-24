import google.generativeai as genai
import config
import os
import drive_manager

# Configure Gemini
genai.configure(api_key=config.GEMINI_API_KEY)

def generate_intermediate_draft(articles, keyword):
    """
    Summarize articles into an intermediate draft.
    Preserve facts and sources.
    """
    if not articles:
        return "No articles found."

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Construct context
    context = ""
    for art in articles:
        context += f"Source: {art['link']}\nTitle: {art['title']}\nContent: {art['content'][:2000]}\n\n"
        
    prompt = f"""
    あなたは政治ニュースの分析官です。
    以下の記事群（対象キーワードのリスト: {keyword}）から、重要な事実、日付、数値を漏らさずに「中間レポート」を作成してください。
    
    【要件】
    1. 複数の記事で重複する内容は統合するが、出典URLは併記する。
    2. 誰がいつ何をしたか、客観的な事実を中心に記述する。
    3. 感情的な表現は排除する。
    4. 後で最終レポートを作成するための「素材」として機能するように、情報は削ぎ落としすぎないこと。
    
    【記事データ】
    {context}
    """
    
    response = model.generate_content(prompt)
    return response.text

def generate_final_report(drafts_content, user_tone="標準"):
    """
    Generate final report from drafts.
    """
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    あなたは「公平・中立」を旨とする、優秀なプロの政治担当記者です。
    以下の「中間レポート」を元に、Discordで配信するための最終ニュースレポートを作成してください。
    
    【トーン設定: {user_tone}（ビジネスライクかつ読みやすい文体）】
    
    【執筆ルール】
    1. **プロの視点**: 憶測やセンセーショナルな表現を避け、事実に基づいた冷静な筆致で書くこと。
    2. **構造の遵守**: 読み手が短時間で重要事項を把握できるよう、Markdownの箇条書きや見出しを適切に使うこと。
    3. **出典の明記**: 各トピックの末尾には必ず情報源リンクを `[Source](url)` 形式で付記し、裏付けを明確にすること。
    4. **中立性の維持**: 特定の政党や思想に偏らず、両論ある場合は両論を併記すること。
    
    【中間レポート】
    {drafts_content}
    """
    
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    # Test
    sample_articles = [
        {"link": "http://example.com/1", "title": "Test 1", "content": "首相は本日、増税を否定した。"},
        {"link": "http://example.com/2", "title": "Test 2", "content": "首相は会見で、経済対策に注力すると述べた。"}
    ]
    print(generate_intermediate_draft(sample_articles, "首相"))
