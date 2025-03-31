from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

@app.route('/w', methods=['GET'])
def get_stream_url():
    # クエリパラメータから'id'を取得
    param_id = request.args.get('id')

    if not param_id:
        return "id parameter is required", 400

    # 外部APIのURLを設定
    api_url = f"https://natural-voltaic-titanium.glitch.me/api/{param_id}"

    try:
        # 外部APIにリクエストを送信
        response = requests.get(api_url)
        response.raise_for_status()  # ステータスコードが200でない場合は例外を発生させる

        # JSONデータを取得
        data = response.json()

        # 必要な情報を取得
        stream_url = data.get('stream_url')
        channel_image = data.get('channelImage')
        channel_name = data.get('channelName')
        video_des = data.get('videoDes')
        video_title = data.get('videoTitle')

        # HTMLテンプレートを作成
        html_content = f"""
        <!doctype html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>動画情報</title>
            <style>
                body {{
                    text-align: center; /* テキストを中央揃え */
                }}
                img {{
                    width: 100px; /* 画像サイズを小さくする */
                    height: auto;
                }}
                .container {{
                    display: inline-block; /* 中央寄せのためにインラインブロックにする */
                    text-align: left; /* 左寄せにする */
                    margin-top: 20px; /* 上部のマージンを追加 */
                }}
            </style>
        </head>
        <body>
            <h1>動画情報</h1>
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

@app.route('/s', methods=['GET'])
def search_videos():
    search_word = request.args.get('word')

    if not search_word:
        return "word parameter is required", 400

    api_url = f"https://invidious.f5.si/api/v1/search?q={search_word}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        results = response.json()

        # 検索結果のHTMLを生成
        html_content = """
        <!doctype html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>検索結果</title>
            <style>
                body {{
                    text-align: center;
                }}
                .results {{
                    display: inline-block;
                    text-align: left;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>検索結果</h1>
            <div class="results">
        """

        for item in results.get('videos', []):
            video_title = item.get('title')
            video_id = item.get('id')
            video_url = f"/w?id={video_id}"

            html_content += f"""
                <p><a href="{video_url}">{video_title}</a></p>
            """

        html_content += """
            </div>
        </body>
        </html>
        """

        return render_template_string(html_content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,debug=True)
