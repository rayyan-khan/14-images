import sys
from PIL import Image
import urllib.request
import io

url = sys.argv[1]
f = io.BytesIO(urllib.request.urlopen(url).read())
img = Image.open(f)


def thirds(color):
    if color < 85: return 0
    elif 85 < color < 170: return 127
    else: return 255


def rgb(r, g, b):
    r = thirds(r)
    g = thirds(g)
    b = thirds(b)
    return (r, g, b)


pix = img.load()

for x in range(img.size[0]):
    for y in range(img.size[1]):
        r, g, b = pix[x, y]
        newColor = rgb(r, g, b)
        pix[x, y] = newColor

img.show()
