import google.generativeai as genai
import config
import os
import drive_manager
import time

# Configure Gemini
genai.configure(api_key=config.GEMINI_API_KEY)

def generate_intermediate_draft(articles, keyword):
    """
    Summarize articles into an intermediate draft.
    Preserve facts and sources.
    """
    if not articles:
        return "No articles found."

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Construct context
    context = ""
    for art in articles:
        context += f"Source: {art['link']}\nTitle: {art['title']}\nContent: {art['content']}\n\n"
        
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
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    あなたは「公平・中立」を旨とする、優秀なプロの政治担当記者です。
    以下の「中間レポート」を元に、Discordで配信するための最終ニュースレポートを作成してください。
    
    【トーン設定: {user_tone}（ビジネスライクかつ読みやすい文体）】
    
    【重要: 構成ルール - 動画ファースト】
    1. **動画解析情報の優先**: 「YouTube動画（高精度解析済み）」の情報が含まれている場合、それをレポートの**トップニュース**として扱い、詳細（誰が・何を・どう述べたか）を厚く記述すること。
    2. **Webニュースは概要**: テキストニュース（Web記事）は、Google Newsの仕様上、概要のみの場合があります。これらは「関連トピック / ヘッドライン」として簡潔にまとめ、「詳細はリンク先へ」と誘導する形式にすること。
    3. **出典の明記**: 記事・動画ともに、必ず情報の末尾に `[Source](url)` を付記すること。
    4. **中立性の維持**: 感情的な煽りを避け、事実ベースで記述すること。
    
    【中間レポート】
    {drafts_content}
    """
    
    response = model.generate_content(prompt)
    return response.text

def process_video_audio(audio_path, title, context_text=""):
    """
    Uploads audio to Gemini, waits for processing, and generates a summary.
    Returns a dictionary with 'summary' and 'key_points'.
    """
    if not audio_path or not os.path.exists(audio_path):
        return {"summary": "Audio file not found.", "key_points": []}

    print(f"DEBUG: Uploading audio {audio_path} to Gemini...")
    try:
        # Upload the file
        audio_file = genai.upload_file(path=audio_path, mime_type="audio/mp3")
        
        # Wait for processing
        print(f"DEBUG: Waiting for audio processing...")
        while audio_file.state.name == "PROCESSING":
            time.sleep(2)
            audio_file = genai.get_file(audio_file.name)
            
        if audio_file.state.name == "FAILED":
            print("DEBUG: Gemini Audio Processing Failed.")
            return {"summary": "Audio processing failed.", "key_points": []}
            
        print(f"DEBUG: Audio Ready. Generating content...")
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        あなたは政治ニュースの分析官です。
        以下の音声ファイル（動画タイトル: {title}）を聴取し、詳細なレポートを作成してください。
        
        【参考情報（過去の経緯・背景）】
        {context_text}
        
        【タスク】
        1. **内容の完全な理解**: 音声を最初から最後まで聞き取り、議論の流れや発言の意図を正確に把握してください。
        参考情報と重複する内容は簡潔にし、**「今回の新しい発言・進展」**に焦点を当ててください。
        2. **詳細な要約**: ニュース記事として成立するレベルで、誰が、いつ、何を、どのように発言したか（5W1H）を具体的に記述してください。
        3. **重要発言の抜粋**: キーとなる発言は「」で引用し、誰の発言かを明記してください。
        
        【出力形式】
        以下のJSON形式のみを出力してください。
        {{
            "summary": "ニュース記事形式の詳細な要約テキスト（400文字以上 recommended）...",
            "key_points": ["重要な事実1", "重要な事実2", "重要な事実3"]
        }}
        """
        
        response = model.generate_content([prompt, audio_file], generation_config={"response_mime_type": "application/json"})
        
        import json
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Gemini Audio Processing Error: {e}")
        return {"summary": f"Error: {e}", "key_points": []}

if __name__ == "__main__":
    # Test
    sample_articles = [
        {"link": "http://example.com/1", "title": "Test 1", "content": "首相は本日、増税を否定した。"},
        {"link": "http://example.com/2", "title": "Test 2", "content": "首相は会見で、経済対策に注力すると述べた。"}
    ]
    print(generate_intermediate_draft(sample_articles, "首相"))
