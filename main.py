# by ztttas1
from flask import Flask, request, render_template_string, Response
import requests
import base64
import os
app = Flask(__name__)
ver = "1.0"
# Invidious APIのベースURL（公開インスタンスを使用）
INVIDIOUS_API_URL = "https://" + os.environ.get('INVIDIOUS',) + "/api/v1"
SERVER_LIST = ['https://natural-voltaic-titanium.glitch.me','https://wtserver3.glitch.me','https://wtserver1.glitch.me','https://wtserver2.glitch.me','https://watawata8.glitch.me','https://watawata7.glitch.me','https://watawata37.glitch.me','https://wataamee.glitch.me','https://watawatawata.glitch.me','https://amenable-charm-lute.glitch.me','https://battle-deciduous-bear.glitch.me','https://productive-noon-van.glitch.me','https://balsam-secret-fine.glitch.me']
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
        page = request.form.get('page', '1')  # Default to page 1
        if not query:
            return "検索キーワードを入力してください", 400

        try:
            page = int(page)
            if page < 1:
                page = 1
        except ValueError:
            page = 1

        # Invidious APIで動画を検索（ページ番号を追加）
        search_url = f"{INVIDIOUS_API_URL}/search?q={query}&type=video&page={page}"
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
                    .pagination { margin-top: 20px; }
                    .pagination button { margin: 0 10px; }
                </style>
            </head>
            <body>
                <h1>Search</h1>
                <form method="post">
                    <input type="text" name="query" placeholder="検索キーワードを入力" value="{{query}}">
                    <input type="submit" value="検索">
                </form>
                <h2>検索結果</h2>
            """.replace("{{query}}", query)

            for video in results[:40]:
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

            # ページネーション用のボタンを追加
            html_content += """
            <div class="pagination">
                <form method="post" style="display:inline;">
                    <input type="hidden" name="query" value="{{query}}">
                    <input type="hidden" name="page" value="{{prev_page}}">
                    <button type="submit" {{prev_disabled}}>前のページ</button>
                </form>
                <span>ページ {{current_page}}</span>
                <form method="post" style="display:inline;">
                    <input type="hidden" name="query" value="{{query}}">
                    <input type="hidden" name="page" value="{{next_page}}">
                    <button type="submit">次のページ</button>
                </form>
            </div>
            </body>
            </html>
            """.replace("{{query}}", query)\
               .replace("{{prev_page}}", str(page - 1))\
               .replace("{{next_page}}", str(page + 1))\
               .replace("{{current_page}}", str(page))\
               .replace("{{prev_disabled}}", 'disabled' if page == 1 else '')

            return render_template_string(html_content)

        except requests.exceptions.RequestException as e:
            return f"検索エラー: {str(e)}", 500

    # GETリクエストの場合は検索フォームのみ表示
    html_content = f"""
    <!doctype html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Home</title>
    </head>
    <body>
        <h1>YouTubeViewer Search</h1>
        <form method="post">
            <input type="text" name="query" placeholder="Search word">
            <input type="submit" value="検索">
        </form>
        <p>製作:ztttas1<br>動画:わかめtube<br>検索:Invidious<br>Version:{ver}</p>
    </body>
    </html>
    """
    return render_template_string(html_content)
@app.route('/w', methods=['GET', 'POST'])
def get_stream_url():
    param_id = request.args.get('id')

    if not param_id:
        return "id parameter is required", 400

    if request.method == 'POST':
        server_index = request.form.get('server_index')
        try:
            server_index = int(server_index)
            if 0 <= server_index < len(SERVER_LIST):
                selected_server = SERVER_LIST[server_index]
            else:
                return "Invalid server index", 400
        except (ValueError, TypeError):
            return "Server index must be a number", 400

        api_url = f"{selected_server}/api/{param_id}"

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
                    body {{ text-align: center; }}
                    img {{ width: 100px; height: auto; }}
                    .container {{ display: inline-block; text-align: left; margin-top: 20px; }}
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
                <h3>サーバー選択</h3>
                <form method="post">
                    <select name="server_index">
                        {''.join(f'<option value="{i}">{i}: {server}</option>' for i, server in enumerate(SERVER_LIST))}
                    </select>
                    <input type="hidden" name="id" value="{param_id}">
                    <input type="submit" value="サーバー変更">
                </form>
            </body>
            </html>
            """
            return render_template_string(html_content)

        except requests.exceptions.RequestException as e:
            er = f'''
        <form method="post">
                <select name="server_index">
                    {''.join(f'<option value="{i}">{i}: {server}</option>' for i, server in enumerate(SERVER_LIST))}
                </select>
                <input type="hidden" name="id" value="{param_id}">
                <input type="submit" value="サーバー変更">
            </form>
            '''
            return f'Error: {str(e)}<br>{er}', 500

    # GETリクエストの場合はデフォルトサーバー（0番目）を使用
    api_url = f"{SERVER_LIST[0]}/api/{param_id}"

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
                body {{ text-align: center; }}
                img {{ width: 100px; height: auto; }}
                .container {{ display: inline-block; text-align: left; margin-top: 20px; }}
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
            <h3>サーバー選択</h3>
            <form method="post">
                <select name="server_index">
                    {''.join(f'<option value="{i}">{i}: {server}</option>' for i, server in enumerate(SERVER_LIST))}
                </select>
                <input type="hidden" name="id" value="{param_id}">
                <input type="submit" value="サーバー変更">
            </form>
        </body>
        </html>
        """
        return render_template_string(html_content)

    except requests.exceptions.RequestException as e:
        er = f'''
        <form method="post">
                <select name="server_index">
                    {''.join(f'<option value="{i}">{i}: {server}</option>' for i, server in enumerate(SERVER_LIST))}
                </select>
                <input type="hidden" name="id" value="{param_id}">
                <input type="submit" value="サーバー変更">
            </form>
        '''
        return f'Error: {str(e)}<br>{er}', 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

