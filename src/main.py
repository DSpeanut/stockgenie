from flask import Flask, render_template, jsonify, Response
from fastapi import Request
from stockgenie import run_agent
import time
import json
from config.config import TEMPLATE_DIR 
import os
from flask import request
app = Flask(__name__)

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
            
            # Stream the answer word by word
            words = answer.split()
            for word in words:
                data = json.dumps({"word": word + " ", "done": False})
                yield f"data: {data}\n\n"  # SSE format
                time.sleep(0.05)
            
            yield f"data: {json.dumps({'word': '', 'done': True})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"answer": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, threaded=True)