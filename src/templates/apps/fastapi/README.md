# $$NAME$$

$$DESCRIPTION$$

## Info

Language: $$LANGUAGE$$
Framework: $$FRAMEWORK$$
Template: $$TEMPLATE_NAME$$
Template Version: $$TEMPLATE_VERSION$$

## Run

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host $$HOST$$ --port $$PORT$$ --reload

URL:

http://$$HOST$$:$$PORT$$
