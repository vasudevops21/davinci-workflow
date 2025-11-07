# main.py
from flask import Flask, render_template, request
from auto_cut_script import run_auto_cut

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_script():
    davinci_path = request.form.get("davinci_path")
    cut_interval = float(request.form.get("cut_interval"))
    remove_duration = float(request.form.get("remove_duration"))
    audio_threshold = float(request.form.get("audio_threshold"))

    result = run_auto_cut(
        DAVINCI_PATH=davinci_path,
        CUT_INTERVAL=cut_interval,
        REMOVE_DURATION=remove_duration,
        AUDIO_THRESHOLD_DB=audio_threshold,
    )

    return render_template("index.html", output=result)

if __name__ == "__main__":
    app.run(debug=True)
