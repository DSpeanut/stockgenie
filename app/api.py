"""Application entrypoint: Flask web server with SSE chat endpoint."""

import json
import time

from flask import Flask, Response, jsonify, render_template, request

from core.agent import run_agent

app = Flask(
    __name__,
    template_folder="web/templates",
)


@app.route("/")
def home():
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        question = data.get("question", "")
        thread_id = data.get("thread_id", "web_session")

        if not question:
            return jsonify({"answer": "Please provide a question."})

        def generate():
            answer = run_agent(question, thread_id)
            words = answer.split()
            for word in words:
                payload = json.dumps({"word": word + " ", "done": False})
                yield f"data: {payload}\n\n"
                time.sleep(0.05)
            yield f"data: {json.dumps({'word': '', 'done': True})}\n\n"

        return Response(generate(), mimetype="text/event-stream")
    except Exception as e:
        return jsonify({"answer": f"Error: {e!s}"}), 500


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
