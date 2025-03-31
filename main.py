from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

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

@app.route('/s')
def search_videos():
    search_word = request.args.get('word')
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
    app.run(host='0.0.0.0', port=8080, debug=True)
