from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/w', methods=['GET'])
def get_stream_url():
    # クエリパラメータから'id'を取得
    param_id = request.args.get('id')

    if not param_id:
        return jsonify({"error": "id parameter is required"}), 400

    # 外部APIのURLを設定
    api_url = f"https://natural-voltaic-titanium.glitch.me/api/{param_id}"

    try:
        # 外部APIにリクエストを送信
        response = requests.get(api_url)
        response.raise_for_status()  # ステータスコードが200でない場合は例外を発生させる

        # JSONデータを取得
        data = response.json()

        # 'stream_url'を取得
        stream_url = data.get('stream_url')
        channel_image = data.get('channelImage')
        channel_name = data.get('channelName')
        video_des = data.get('videoDes')

        # HTMLテンプレートを作成
        html_content = f"""
        <!doctype html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>動画情報</title>
        </head>
        <body>
            <h1>動画情報</h1>
            <video width="640" height="360" controls>
                <source src="{stream_url}" type="video/mp4">
                お使いのブラウザは動画タグに対応していません。
            </video>
            <div>
                <img src="{channel_image}" alt="Channel Image" style="float:left; margin-right:10px;">
                <p><strong>{channel_name}</strong></p>
                <p>{video_des}</p>
            </div>
        </body>
        </html>
        """
        if stream_url:
            return jsonify(html_content)
        else:
            return jsonify({"error": "stream_url not found"}), 404
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,debug=True)
