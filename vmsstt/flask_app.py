from flask import Flask, jsonify
import logging
from vmsstt import config
import vmsstt
from vmsstt.vm import ScreenShot
from vmsstt.ocr import get_text

app = Flask(__name__, static_url_path="/static")


@app.route("/vm_text/<string:name>")
def index(name):
    screen_shot = ScreenShot(
        vm_name=name,
        host=config.VCENTER_HOST,
        user=config.VCENTER_USER,
        password=config.VCENTER_PASSWORD,
        verify=config.VERIFY,
    )
    screen_shot.connect()
    screen_shot.search()
    image = screen_shot.get()
    screen_shot.delete()
    screen_shot.disconnect()
    text = get_text(image)
    return jsonify({"text": text})


if __name__ == "__main__":
    vmsstt.vm.logger.setLevel(logging.DEBUG)
    vmsstt.ocr.logger.setLevel(logging.DEBUG)
    app.run(debug=True)
