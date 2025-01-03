from flask import Flask, request, render_template_string
import requests
import os
html_template = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>リダイレクトサンプル</title>
    <script>
        function redirectToURL() {
            const input = document.getElementById('inputField').value;
            const url = `/s?w=${encodeURIComponent(input)}`;
            window.location.href = url;
        }
    </script>
</head>
<body>
    <h1>リダイレクトページ</h1>
    <input type="text" id="inputField" placeholder="文字列を入力してください">
    <button onclick="redirectToURL()">リダイレクト</button>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)
v1_7 = os.environ['v1_7']
app = Flask(__name__)
@app.route('/ed')
def ed():
    v1_7 = request.args.get('v')
    return f"OK"
@app.route('/')
def home():
    return html_template
@app.route('/w')
def get_video_info():
    videoid = request.args.get('i')
    if not videoid:
        return "Video ID is required", 400
    # 外部APIのURLを作成
    api_url = f'https://yt.bonaire.tk/api/server/v{v1_7}/{videoid}'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # ステータスコードが200以外の場合、エラーを発生させる
        data = response.json()
        # 必要なデータを取得
        channel_image = data.get('channelImage', '画像が見つかりません')
        like_count = data.get('likeCount', '不明')
        video_views = data.get('videoViews', '不明')
        video_title = data.get('videoTitle', '不明')
        channel_name = data.get('channelName', '不明')
        audio_url = data.get('audioUrl', '不明')
        stream_url = data.get('stream_url', '不明')
        
        # HTMLテンプレートの作成
        html_content = f"""
        <h1>{video_title}</h1>
        <img src="{channel_image}" alt="Channel Image">
        <p>Channel Name: {channel_name}</p>
        <p>Likes: {like_count}</p>
        <p>Views: {video_views}</p>
        
        <p>Audio:</p>
        <audio controls src="{audio_url}">このブラウザではオーディオが再生できません。</audio>
        
        <p>Stream:</p>
        <video class="video" controls src="{stream_url}">このブラウザではビデオが再生できません。</video>
        """
        
        return render_template_string(html_content)
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {str(e)}", 500
@app.route('/s')
def search_videos():
    search_word = request.args.get('w')
    if not search_word:
        return "Search word is required", 400
    
    # 検索APIのURL
    api_url = f'https://ytsr.bonaire.tk/apis?q={search_word}'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # ステータスコードが200以外の場合、エラーを発生させる
        data = response.json()
        
        # HTMLテンプレートの作成
        html_content = "<h1>検索結果</h1>"
        
        for item in data:
            if item['type'] == 'video':
                title = item['title']
                video_id = item['id']  # 動画のIDを取得
                thumbnail_url = item['bestThumbnail']['url']
                views = item.get('views', '不明')
                duration = item.get('duration', '不明')
                
                html_content += f"""
                <div>
                    <h2><a href="/w?i={video_id}">{title}</a></h2>
                    <img src="{thumbnail_url}" alt="{title}">
                    <p>Views: {views}</p>
                    <p>Duration: {duration}</p>
                </div>
                """
            elif item['type'] == 'channel':
                channel_name = item['name']
                channel_url = item['url']
                channel_image = item['bestAvatar']['url']
                subscribers = item.get('subscribers', '不明')
                
                html_content += f"""
                <div>
                    <h2><a href="{channel_url}">{channel_name}</a></h2>
                    <img src="{channel_image}" alt="{channel_name}">
                    <p>Subscribers: {subscribers}</p>
                    <p>Description: {item.get('descriptionShort', '不明')}</p>
                </div>
                """
        
        return render_template_string(html_content)

    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,debug=True)
