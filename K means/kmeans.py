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
    points = set()
    while len(points) < k:
        points.add(pix[random.randint(0, xRange),
                       random.randint(0, yRange)])
    points = [point for point in points]
    return points

randomMeans = randPoints()


### METHODS ###

# DEBUGGING
def roundMeans(means, decimals):
    for m in range(len(means)):
        r, g, b = means[m]
        r = round(r, decimals)
        g = round(g, decimals)
        b = round(b, decimals)
        means[m] = (r, g, b)
    return means


# PART 1 METHODS
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


# PART 2 METHODS

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


def recolor(pixGroups):
    global pix
    for m in pixGroups:
        for x, y in pixGroups[m]:
            r, g, b = m
            r, g, b = round(r), round(g), round(b)
            pix[x, y] = (r, g, b)
    image.show()


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


def newMeans(currentMeans): # currentMeans = list of (r, g, b) tuples
    pixGroups = groupPix(currentMeans)
    newMeans = [averageList(pixGroups[m]) for m in pixGroups]
    return newMeans, pixGroups


def findSwitchedPix(pixGroups, newPixGroups):
    # pixGroups = {(r,g,b): [(x,y),(x,y)...], etc}
    # => dictionary where mean as rgb is key with list of xy tuples as values
    points, newPoints = list(pixGroups.values()), \
                        list(newPixGroups.values())
    switchedPix = [set(points[n]) - set(newPoints[n]) for n
                       in range(len(points))]
    numSwitchedPix = sum(len(s) for s in switchedPix)
    return numSwitchedPix


def kMeans():
    global randomMeans, k
    currentMeans = randomMeans
    switchedPix = True
    counter = 0
    pixGroups = 0
    while switchedPix:
        newMns, newPixGroups = newMeans(currentMeans) # pixGroups = {(r,g,b):[(x,y)...]}
        if counter > 0:
            switchedPix = findSwitchedPix(pixGroups, newPixGroups)
        currentMeans = newMns
        pixGroups = newPixGroups
        #roundedMns = roundMeans(currentMeans, 3)
        #print('ITERATION: {} MEANS: {}'.format(counter, roundedMns))
        #if counter > 0: print('SWITCHED PIX: {}'.format(switchedPix))
        counter += 1
    return currentMeans, pixGroups


# PART 3 METHODS
def floodFill(coord, color, visitedPix): # visitedPix = {(x,y)...}, color = (r,g,b)
    global image, pix # careful, because it only works as intended after using recolor()
    try:
        width, height = image.size
        x, y = coord
        if 0 <= x < width and 0 <= y < height and (x, y) \
                not in visitedPix and pix[x, y] == color:
            visitedPix.add((x, y))
            floodFill((x + 1, y), color, visitedPix)
            floodFill((x - 1, y), color, visitedPix)
            floodFill((x, y + 1), color, visitedPix)
            floodFill((x, y - 1), color, visitedPix)
        return visitedPix
    except:
        print('VISITED PIX: {} {}'.format(len(visitedPix), visitedPix))


def floodFillIter(startCoord, color):
    global image, pix
    width, height = image.size
    x, y = startCoord
    visitedPix = set()
    clusterPix = set()
    toVisit = [(x, y)]
    while toVisit:
        x, y = toVisit.pop(0)
        print('TO VISIT: {} CURRENT POINT: {}'.format(len(toVisit), (x, y)))
        if pix[x, y] == color:
            newPts = [(x + a, y + b) for a in (-1, 0, 1)
                       for b in (-1, 0, 1) if (x + a, y + b) != (x, y)
                       and 0 <= x + a < width and 0 <= y + b < height
                       and (x + a, y + b) not in visitedPix]
            visitedPix = visitedPix.union(set(newPts))
            clusterPix.add((x, y))
            toVisit.extend(newPts)
    return clusterPix


def floodfillCounter(means): # list of rounded means
    global image, pix # careful, because it only works as intended after using recolor()
    width, height = image.size
    skipSet = set()
    clusterCounter = {m: 0 for m in means}
    for x in range(width):
        for y in range(height):
            if (x, y) in skipSet: continue
            else:
                pixColor = pix[x, y]
                skipSet = skipSet.union(floodFillIter((x, y), pixColor))
                clusterCounter[pixColor] += 1
                print('CC', clusterCounter, 'num skips', len(skipSet))
    return clusterCounter



### PART 1: FIND K MEANS ###
printBasicInfo()
means, pixGroups = kMeans()
#print(means)


### PART 2: RECOLOR PHOTO PIXELS TO NEAREST MEAN ###
recolor(pixGroups)
pix = image.load()
print('Final means:')
counter = 1
for m in pixGroups:
    print('{}: {} => {}'.format(counter, m, len(pixGroups[m])))
    counter += 1


### PART 3: COUNT CLUSTERS ###
roundedMeans = roundMeans(means, 0)
clusterCounts = floodfillCounter(roundedMeans)
print(clusterCounts)

### PART 4: SAVE IMAGE ###
#image.save('kmeans/{}.png'.format('2019rkhan'), 'PNG')



