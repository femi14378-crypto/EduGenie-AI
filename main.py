from flask import Flask, render_template, request, jsonify

from explanation_module import explain_topic
from learning_path import create_learning_path
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/explain", methods=["POST"])
def explain():
    data = request.get_json()
    topic = data.get("topic", "")

    result = explain_topic(topic)

    return jsonify({
        "result": result
    })


@app.route("/learn", methods=["POST"])
def learn():
    data = request.get_json()
    topic = data.get("topic", "")

    result = create_learning_path(topic)

    return jsonify({
        "result": result
    })


@app.route("/qna", methods=["POST"])
def qna():
    data = request.get_json()
    question = data.get("question", "")

    result = answer_question(question)

    return jsonify({
        "result": result
    })


@app.route("/quiz", methods=["POST"])
def quiz():
    data = request.get_json()
    topic = data.get("topic", "")

    result = generate_quiz(topic)

    return jsonify({
        "result": result
    })


@app.route("/summary", methods=["POST"])
def summary():
    data = request.get_json()
    text = data.get("text", "")

    result = summarize_text(text)

    return jsonify({
        "result": result
    })


if __name__ == "__main__":
    app.run(debug=True)