"""Application entrypoint: Flask web server with chat endpoint."""

from flask import Flask, jsonify, render_template, request

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

        answer = run_agent(question, thread_id)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error: {e!s}"}), 500


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
