import io
from PIL import Image



def image_to_byte_array(filename: str) -> bytes:
    image = Image.open(filename)
    # BytesIO is a fake file stored in memory
    imgByteArr = io.BytesIO()
    # image.save expects a file as a argument, passing a bytes io ins
    image.save(imgByteArr, format=image.format)
    # Turn the BytesIO object back into a bytes object
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

