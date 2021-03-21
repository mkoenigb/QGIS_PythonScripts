# Settings:
inputlayer = iface.activeLayer()
polygonSides = 6
bufferLength = 100 # in CRS units

# No changes needed below #
import numpy as np
if inputlayer.wkbType() != QgsWkbTypes.Point: # Only execute script if selected layer is of type point
    print("Error: Selected layer is not of type Point! - Script wont work with other geometry types or MultiPoints!")
else: # run script
    if polygonSides == 6: # set name of new layer to Hexagons if 6 sides were chosen
        layername = "Hexagons"
    else: # else set layername to generic "polygons"
        layername = "Polygons"
    newlayer = QgsVectorLayer("Polygon", layername, "memory") # Create the new outputlayer
    newlayer.setCrs(inputlayer.crs()) # Set new layers CRS to inputlayers crs
    with edit(newlayer): # edit new layer
        newlayer.dataProvider().addAttributes(inputlayer.fields()) # copy fields from input layer to new layer
        for feat in inputlayer.getFeatures(): # iterate over inputlayer
            point = feat.geometry().asPoint() # get geometry of inputpoint
            geom = [QgsPointXY(point[0]+np.sin(angle)*bufferLength, point[1]+np.cos(angle)*bufferLength)
             for angle in np.linspace(0,2*np.pi,polygonSides, endpoint=False)] # create the vertices of hexagon polygon
            outFeat = QgsFeature() # create new feature
            outFeat.setAttributes(feat.attributes()) # copy attributes of inputfeature to outputfeature
            outFeat.setGeometry(QgsGeometry.fromPolygonXY([geom])) # set new features geometry from vertices-pointlist
            newlayer.dataProvider().addFeature(outFeat) # add the feature
            newlayer.updateFeature(outFeat) # and update it
    QgsProject.instance().addMapLayer(newlayer) # add new layer to canvas