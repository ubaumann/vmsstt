# VMSSTT (Virtual Machine ScreenShot to Text)

Small flask app

## Docker deployment

Copy `vmsstt.env.tmpl` to `vmsstt.env` and edit the settings.

```bash
cp vmsstt.env.tmpl vmsstt.env
```

Run docker with your prefered settings. For example like this:

```bash
docker run -it --rm --env-file vmsstt.env -p 5000:5000 vmsstt
```

Build docker image manually

```bash
docker build -t vmsstt .
```

## Setup without docker

This repo uses poetry and **tesseract-ocr**

### Install requirements

```bash
apt-get install tesseract-ocr
poetry install
```

### Open shell with venv and run app

```bash
poetry shell
```

### Run app (first open shell)

```bash
python flask_app.py
```

### Format python document (first open shell)

```bash
black flask_app.py
```
