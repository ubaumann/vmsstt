import logging
import pytesseract
from PIL import ImageOps

logger = logging.getLogger(__name__)


def get_text(image) -> str:
    image = ImageOps.invert(image)
    logger.debug("Image inverted")
    image = ImageOps.scale(image, 5)
    logger.debug("Image scale done")
    return pytesseract.image_to_string(image, lang="eng")
