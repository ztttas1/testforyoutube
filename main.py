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

        if stream_url:
            return jsonify({"stream_url": stream_url})
        else:
            return jsonify({"error": "stream_url not found"}), 404
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,debug=True)
