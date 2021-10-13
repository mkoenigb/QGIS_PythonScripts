### Imports and Settings
import itertools as it
from random import randrange

layer = iface.activeLayer()
fields = ['crono1','crono2','crono3']

### This is the part to generate a list of all possible combinations
fieldsValuesDict = {}
possibleCombinations = []

# create a dictionary with fieldnames as keys
for field in fields:
    fieldsValuesDict[field] = []

# fill the dictionary with lists of all values in the layer
for feat in layer.getFeatures():
    for field in fields:
        fieldsValuesDict[field].append(feat[field])

# remove duplicate values from the dictionaries values-list
for k, v in fieldsValuesDict.items():
    fieldsValuesDict[k] = list(dict.fromkeys(v))

# create a list of all possible combinations of all value-lists of all keys in the dictionary
allNames = sorted(fieldsValuesDict)
combinations = it.product(*(fieldsValuesDict[Name] for Name in allNames))
for item in list(combinations):
    possibleCombinations.append(''.join(item))

#print(possibleCombinations)

### This is the part to setup the categorized renderer to all possible combinations
categories = []
for combination in possibleCombinations:
    # initialize the default symbol for this geometry type
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())

    # configure a symbol layer
    layer_style = {}
    layer_style['color'] = '%d, %d, %d' % (randrange(0, 256), randrange(0, 256), randrange(0, 256))
    layer_style['outline'] = '#000000'
    symbol_layer = QgsSimpleFillSymbolLayer.create(layer_style)

    # replace default symbol layer with the configured one
    if symbol_layer is not None:
        symbol.changeSymbolLayer(0, symbol_layer)

    # create renderer object
    category = QgsRendererCategory(combination, symbol, str(combination))
    # entry for the list of category items
    categories.append(category)

# create renderer object
mycat = '+'.join(fields)
renderer = QgsCategorizedSymbolRenderer(mycat, categories)

# assign the created renderer to the layer
if renderer is not None:
    layer.setRenderer(renderer)

# refresh
layer.triggerRepaint()