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

        # Invidious APIで動画とチャンネルを検索（type=allで両方を含む）
        search_url = f"{INVIDIOUS_API_URL}/search?q={query}&type=all&page={page}"
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

            for item in results[:40]:  # 最大40件表示
                item_type = item.get('type')
                
                if item_type == 'video':
                    # 動画の場合
                    video_id = item.get('videoId')
                    title = item.get('title')
                    thumbnails = item.get('videoThumbnails')
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
                elif item_type == 'channel':
                    # チャンネルの場合
                    channel_id = item.get('authorId')
                    channel_name = item.get('author')
                    thumbnails = item.get('authorThumbnails')
                    if thumbnails and len(thumbnails) > 0:
                        # 最大のサムネイルを選択（最後の要素が通常高解像度）
                        thumbnail_url = thumbnails[-1].get('url', 'https://via.placeholder.com/120')
                    else:
                        thumbnail_url = "https://via.placeholder.com/120"  # デフォルト画像
                    html_content += f"""
                    <div class="result">
                        <a href="/c?id={channel_id}">
                            <img src="{thumbnail_url}" alt="channel thumbnail">
                            <p><strong>{channel_name}</strong></p>
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
        if response in "highstreamUrl":
            stream_url = data.get('highstreamUrl')
        else:
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
                <source src="{stream_url}">
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
            <p>{stream_url}</p>
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
@app.route('/c', methods=['GET'])
def get_channel_info():
    channel_id = request.args.get('id')
    page = request.args.get('page', '1')  # ページネーション用のパラメータ

    if not channel_id:
        return "Channel ID is required", 400

    try:
        page = int(page)
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    # Invidious APIでチャンネル情報を取得
    channel_url = f"{INVIDIOUS_API_URL}/channels/{channel_id}"
    videos_url = f"{INVIDIOUS_API_URL}/channels/{channel_id}/videos?page={page}"

    try:
        # チャンネル情報の取得
        channel_response = requests.get(channel_url)
        channel_response.raise_for_status()
        channel_data = channel_response.json()

        # チャンネル動画の取得
        videos_response = requests.get(videos_url)
        videos_response.raise_for_status()
        videos_data = videos_response.json()

        # チャンネル情報の抽出
        channel_name = channel_data.get('author', 'Unknown Channel')
        channel_description = channel_data.get('description', 'No description available')
        banner_url = channel_data.get('authorBanners', [{}])[0].get('url', 'https://via.placeholder.com/1200x200')
        thumbnail_url = channel_data.get('authorThumbnails', [{}])[-1].get('url', 'https://via.placeholder.com/100')

        # HTMLテンプレート
        html_content = f"""
        <!doctype html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{channel_name}</title>
            <style>
                body {{ text-align: center; font-family: Arial, sans-serif; }}
                .container {{ max-width: 1200px; margin: 0 auto; text-align: left; }}
                .banner {{ width: 100%; max-height: 200px; object-fit: cover; }}
                .channel-info {{ display: flex; align-items: center; margin: 20px 0; }}
                .channel-info img {{ width: 100px; height: 100px; border-radius: 50%; margin-right: 20px; }}
                .videos {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }}
                .video {{ text-align: left; }}
                .video img {{ width: 100%; height: auto; }}
                .pagination {{ margin: 20px 0; text-align: center; }}
                .pagination button {{ margin: 0 10px; padding: 10px 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <img src="{banner_url}" alt="Channel Banner" class="banner">
                <div class="channel-info">
                    <img src="{thumbnail_url}" alt="Channel Thumbnail">
                    <div>
                        <h1>{channel_name}</h1>
                        <p>{channel_description}</p>
                    </div>
                </div>
                <h2>動画</h2>
                <div class="videos">
        """

        # 動画リストの追加
        for video in videos_data.get('videos', [])[:40]:  # 最大40件表示
            video_id = video.get('videoId')
            title = video.get('title', 'No Title')
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
            html_content += f"""
            <div class="video">
                <a href="/w?id={video_id}">
                    <img src="{thumbnail_url}" alt="Video Thumbnail">
                    <p><strong>{title}</strong></p>
                </a>
            </div>
            """

        # ページネーション
        html_content += f"""
                </div>
                <div class="pagination">
                    <form method="get" style="display:inline;">
                        <input type="hidden" name="id" value="{channel_id}">
                        <input type="hidden" name="page" value="{page - 1}">
                        <button type="submit" {"disabled" if page == 1 else ""}>前のページ</button>
                    </form>
                    <span>ページ {page}</span>
                    <form method="get" style="display:inline;">
                        <input type="hidden" name="id" value="{channel_id}">
                        <input type="hidden" name="page" value="{page + 1}">
                        <button type="submit">次のページ</button>
                    </form>
                </div>
            </div>
        </body>
        </html>
        """

        return render_template_string(html_content)

    except requests.exceptions.RequestException as e:
        return f"Error fetching channel data: {str(e)}", 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
