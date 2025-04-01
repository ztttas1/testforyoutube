# by ztttas1
from flask import Flask, request, render_template_string, Response
import requests
import base64
import os
app = Flask(__name__)

# Invidious APIのベースURL（公開インスタンスを使用）
INVIDIOUS_API_URL = "https://" + os.environ.get('INVIDIOUS',) + "/api/v1"

# BASIC認証のユーザー名とパスワード
USERNAME = os.environ.get('USERNAME', 'ztttas1')
PASSWORD = os.environ.get('PASSWORD', 'pas')

def check_auth(username, password):
    """認証情報を確認する関数"""
    return username == USERNAME and password == PASSWORD

def authenticate():
    """認証失敗時に401レスポンスを返す関数"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

@app.before_request
def require_auth():
    """すべてのリクエストに対して認証を要求"""
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

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
                <title>Search</title>
                <style>
                    body { text-align: center; }
                    .result { margin: 20px; text-align: left; display: inline-block; }
                    img { width: 120px; height: auto; float: left; margin-right: 10px; }
                </style>
            </head>
            <body>
                <h1>Search</h1>
                <form method="post">
                    <input type="text" name="query" placeholder="検索キーワードを入力">
                    <input type="submit" value="検索">
                </form>
                <h2>検索結果</h2>
            """
            for video in results[:10]:  # 上位10件を表示
                video_id = video.get('videoId')
                title = video.get('title')
                thumbnails = video.get('videoThumbnails')
                if thumbnails and len(thumbnails) > 0:
                    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                else:
                    thumbnail_url = "https://via.placeholder.com/120"  # デフォルト画像
                html_content += f"""
                <div class="result">
                    <a href="/w?id={video_id}">
                        <img src="{thumbnail_url}" alt="thumbnail">
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
        <title>Home</title>
    </head>
    <body>
        <h1>Search</h1>
        <form method="post">
            <input type="text" name="query" placeholder="Search word">
            <input type="submit" value="検索">
        </form>
        <p>製作:ztttas1<br>動画:わかめtube<br>検索:Invidious</p>
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
            <title>Video</title>
            <style>
                body {{
                    text-align: center;
                }}
                img {{
                    width: 100px;
                    height: auto;
                }}
                .container {{
                    display: inline-block;
                    text-align: left;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <video width="640" height="360" controls>
                <source src="{stream_url}" type="video/mp4">
                お使いのブラウザは動画タグに対応していません。
            </video>
            <div class="container">
                <img src="{channel_image}" alt="Channel Image" style="float:left; margin-right:10px;">
                <p><strong>{video_title}</strong></p>
                <p><strong>{channel_name}</strong></p>
                <p>{video_des}</p>
            </div>
        </body>
        </html>
        """

        return render_template_string(html_content)

    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
