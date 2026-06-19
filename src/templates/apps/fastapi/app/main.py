from fastapi import FastAPI

app = FastAPI(
    title="$$NAME$$",
    description="$$DESCRIPTION$$",
    version="0.0.1"
)


@app.get("/")
def root():
    return {
        "name": "$$NAME$$",
        "description": "$$DESCRIPTION$$",
        "language": "$$LANGUAGE$$",
        "framework": "$$FRAMEWORK$$",
        "template": "$$TEMPLATE_NAME$$"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
