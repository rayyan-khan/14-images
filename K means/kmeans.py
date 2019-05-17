import sys
import re
import random
import urllib.request
import io
from PIL import Image


### INPUTS & GLOBALS ###

input = sys.argv[1:]
image = ''
k = 0
for arg in input:
    isInt = re.search(r'^\d+$', arg, re.I)
    if isInt: k = int(arg)
    else: image = arg.strip()

if 'http' in image:
    f = io.BytesIO(urllib.request.urlopen(image).read())
    image = Image.open(f)
else: image = Image.open(image)
pix = image.load()


def randPoints(): # returns list of (r, g, b) tuples
    global k, image, pix
    xRange, yRange = image.size
    points = []
    for n in range(k):
        points.append(pix[random.randint(0, xRange),
                       random.randint(0, yRange)])
    return points

randomMeans = randPoints()


### METHODS ###
def distance(point1, point2): # points as (x, y) or (r, g, b)
    global pix
    if len(point1) == 2:
        x1, y1 = point1
        r1, g1, b1 = pix[x1, y1]
    else:
        r1, g1, b1 = point1
    if len(point2) == 2:
        x2, y2 = point2
        r2, g2, b2 = pix[x2, y2]
    else:
        r2, g2, b2 = point2
    return ((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)**.5


def error(list, target):
    sum = 0
    for point in list:
        sum += distance(point, target)**2
    return sum


def printBasicInfo():
    global pix, image, randomMeans

    width, height = image.size
    print('Size: {} x {}'.format(width, height))
    print('Pixels: {}'.format(int(width*height)))

    distinctColors = {} # (r, g, b): num occurrences
    for x in range(width):
        for y in range(height):
            if pix[x, y] in distinctColors:
                distinctColors[pix[x, y]] += 1
            else:
                distinctColors[pix[x, y]] = 1
    print('Distinct pixel count: {}'.format(len(distinctColors)))

    mostFreqColor = (0, 0, 0)
    maxFreq = 0
    for color in distinctColors:
        if distinctColors[color] > maxFreq:
            maxFreq = distinctColors[color]
            mostFreqColor = color
    print('Most common pixel: {} => {}'.format(mostFreqColor, maxFreq))

    print('Random means: {}'.format(randomMeans))


def groupPix(currentMeans): # takes list of current means as (r, g, b) tuples
    global image            # outputs dictionary with means as keys
    xRange, yRange = image.size  # and closest points as values
    meanPts = {}
    for x in range(xRange):
        for y in range(yRange):
            meansDist = {}
            for m in currentMeans:
                dist = distance((x, y), m)
                meansDist[m] = dist
            minVal = min(meansDist.values())
            minMean = (0, 0)
            for m in meansDist:
                if meansDist[m] == minVal:
                    minMean = m
            if minMean in meanPts:
                meanPts[minMean].append((x, y))
            else:
                meanPts[minMean] = [(x, y)]
    return meanPts


def averageList(pixList): # list of (x, y) pixels
    global pix
    rSum, gSum, bSum = 0, 0, 0
    for p in pixList:
        x, y = p
        r, g, b = pix[x, y]
        rSum += r
        gSum += g
        bSum += b
    return rSum/len(pixList), gSum/len(pixList), bSum/len(pixList)


def newMeans(currentMeans): # currentMeans = list of (r, g, b) tuples
    pixGroups = groupPix(currentMeans)
    newMeans = [averageList(pixGroups[m]) for m in pixGroups]
    return newMeans


def roundMeans(means, decimals):
    for m in range(len(means)):
        r, g, b = means[m]
        r = round(r, decimals)
        g = round(g, decimals)
        b = round(b, decimals)
        means[m] = (r, g, b)
    return means


def kMeans():
    global randomMeans
    currentMeans = randomMeans
    switchingPix = True
    counter = 0
    while switchingPix:
        newMns = newMeans(currentMeans)
        if newMns == currentMeans:
            switchingPix = False
        currentMeans = newMns

        roundedMns = roundMeans(currentMeans, 2)
        counter += 1
        print('ITERATION: {} MEANS: {}'.format(counter, roundedMns))

    return currentMeans


### PART 1 ###
printBasicInfo()
means = kMeans()
print(means)








