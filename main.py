from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# Invidious APIのベースURL（公開インスタンスを使用）
INVIDIOUS_API_URL = "https://inv.tux.pizza/api/v1"

@app.route('/', methods=['GET', 'POST'])
def search_videos():
    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            return "検索キーワードを入力してください", 400
        
        # Invidious APIで動画を検索
        search_url = f"{INVIDIOUS_API_URL}/search?q={query}&type=video"
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            results = response.json()

            # 検索結果をHTMLで表示
            html_content = """
            <!doctype html>
            <html lang="ja">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>検索結果</title>
                <style>
                    body { text-align: center; }
                    .result { margin: 20px; text-align: left; display: inline-block; }
                    img { width: 120px; height: auto; float: left; margin-right: 10px; }
                </style>
            </head>
            <body>
                <h1>動画検索</h1>
                <form method="post">
                    <input type="text" name="query" placeholder="検索キーワードを入力">
                    <input type="submit" value="検索">
                </form>
                <h2>検索結果</h2>
            """
            for video in results[:5]:  # 上位5件を表示
                video_id = video.get('videoId')
                title = video.get('title')
                # videoThumbnailsが存在するか確認
                thumbnails = video.get('videoThumbnails')
                thumbnail = thumbnails[0].get('url') if thumbnails and len(thumbnails) > 0 else "https://via.placeholder.com/120"  # デフォルト画像
                html_content += f"""
                <div class="result">
                    <a href="/w?id={video_id}">
                        <img src="{thumbnail}" alt="thumbnail">
                        <p><strong>{title}</strong></p>
                    </a>
                </div>
                """
            html_content += """
            </body>
            </html>
            """
            return render_template_string(html_content)

        except requests.exceptions.RequestException as e:
            return f"検索エラー: {str(e)}", 500

    # GETリクエストの場合は検索フォームのみ表示
    html_content = """
    <!doctype html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>動画検索</title>
    </head>
    <body>
        <h1>動画検索</h1>
        <form method="post">
            <input type="text" name="query" placeholder="検索キーワードを入力">
            <input type="submit" value="検索">
        </form>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/w', methods=['GET'])
def get_stream_url():
    param_id = request.args.get('id')

    if not param_id:
        return "id parameter is required", 400

    api_url = f"https://natural-voltaic-titanium.glitch.me/api/{param_id}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()

        stream_url = data.get('stream_url')
        channel_image = data.get('channelImage')
        channel_name = data.get('channelName')
        video_des = data.get('videoDes')
        video_title = data.get('videoTitle')

        html_content = f"""
        <!doctype html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>動画情報</title>
            <style>
                body {{
                    text-align: center;
                }}
                img {{
                    width: 100px;
                    height: auto
