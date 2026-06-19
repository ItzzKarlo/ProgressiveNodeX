from flask import Flask, render_template


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            project_name="$$NAME$$",
            description="$$DESCRIPTION$$",
            framework="$$FRAMEWORK$$"
        )

    @app.route("/health")
    def health():
        return {
            "status": "ok",
            "name": "$$NAME$$"
        }

    return app
