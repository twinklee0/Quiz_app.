from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIMULATOR = os.path.join(BASE_DIR, "quiz.vvp")

questions = [
    {
        "question": "Which language is used to structure a web page?",
        "options": ["Python", "HTML", "Java", "C++"]
    },
    {
        "question": "Which symbol is used for comments in Python?",
        "options": ["//", "#", "<!-- -->", "/* */"]
    },
    {
        "question": "Which data type stores True or False?",
        "options": ["Integer", "String", "Boolean", "Float"]
    },
    {
        "question": "Which keyword defines a function in Python?",
        "options": ["function", "define", "func", "def"]
    },
    {
        "question": "Which language is commonly used for styling web pages?",
        "options": ["CSS", "SQL", "C", "Verilog"]
    },
    {
        "question": "Which operator checks equality in Python?",
        "options": ["==", "=", "!=", ">"]
    },
    {
        "question": "Which language describes digital hardware?",
        "options": ["HTML", "CSS", "Verilog", "SQL"]
    },
    {
        "question": "Which loop repeats while a condition is true?",
        "options": ["if", "switch", "case", "while"]
    },
    {
        "question": "Which HTML tag creates a hyperlink?",
        "options": ["<a>", "<p>", "<h1>", "<img>"]
    },
    {
        "question": "Which tool compiles and simulates Verilog?",
        "options": [
            "Flask",
            "Icarus Verilog",
            "HTML",
            "CSS"
        ]
    }
]


@app.route("/")
def home():
    return render_template("index.html", questions=questions)


@app.route("/check", methods=["POST"])
def check_answer():
    try:
        data = request.get_json()

        q = int(data["question"])
        a = int(data["answer"])

        if not (0 <= q < len(questions)):
            return jsonify({"error": "Invalid question"}), 400

        if not (0 <= a < 4):
            return jsonify({"error": "Invalid answer"}), 400

        if not os.path.exists(SIMULATOR):
            return jsonify({
                "error": "quiz.vvp is missing. Compile quiz.v first."
            }), 500

        result = subprocess.run(
            [
                "vvp",
                SIMULATOR,
                f"+Q={q}",
                f"+A={a}"
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=5
        )

        print("Simulator output:", result.stdout)
        print("Simulator errors:", result.stderr)

        if result.returncode != 0:
            return jsonify({
                "error": "Verilog simulation failed: " + result.stderr
            }), 500

        output = result.stdout.strip().splitlines()

        result_lines = [
            line.strip()
            for line in output
            if line.strip().startswith("RESULT=")
        ]

        if not result_lines:
            return jsonify({
                "error": "Verilog did not return a valid result."
            }), 500

        correct = result_lines[-1] == "RESULT=1"

        return jsonify({"correct": correct})

    except Exception as error:
        print("ERROR:", repr(error))

        return jsonify({
            "error": str(error)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)