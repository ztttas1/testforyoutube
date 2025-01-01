from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

@app.route('/w')
def get_video_info():
    videoid = request.args.get('i')
    if not videoid:
        return "Video ID is required", 400
    
    # APIのバージョンを試行するリスト
    api_versions = [f'https://yt.bonaire.tk/api/server/v{i}/{videoid}' for i in range(1, 8)]
    
    for api_url in api_versions:
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
            # 次のAPIバージョンへ移行
            continue

    # すべてのAPIバージョンで失敗した場合
    return f"Error fetching data: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # ここでホストとポートを指定
