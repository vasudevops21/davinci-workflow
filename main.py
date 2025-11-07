from flask import Flask, render_template, request, jsonify
from auto_cut_script import auto_cut_and_keep_gaps

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_script():
    try:
        segment_seconds = int(request.form.get('segment_seconds', 10))
        remove_seconds = int(request.form.get('remove_seconds', 1))

        result = auto_cut_and_keep_gaps(segment_seconds, remove_seconds)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
