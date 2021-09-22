def display_point(pointTool): 
    #print ('({:.4f}, {:.4f})'.format(pointTool[0], pointTool[1]))
    point = QgsPointXY(pointTool) # convert QgsPoint to QgsPointXY
    reprojectedpoint = tr.transform(point) # Reproject the clicked point from canvas CRS to layers CRS
    nearestneighbors = spatial_idx.nearestNeighbor(reprojectedpoint, neighbors=1) # build a list of the nearest 1 neigbors
    layer.selectByIds(nearestneighbors) # select the x nearest neighbors

canvas = iface.mapCanvas() # a reference to our map canvas 
layer = iface.activeLayer() # get layer to select features from
sourceCrs = QgsCoordinateReferenceSystem(canvas.mapSettings().destinationCrs().authid()) # get CRS of map canvas
destCrs = QgsCoordinateReferenceSystem(layer.crs()) # get CRS of layer
tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance()) # setup reprojection
spatial_idx = QgsSpatialIndex(layer.getFeatures()) # build a spatial index for the layer
# this QGIS tool emits as QgsPoint after each click on the map canvas
pointTool = QgsMapToolEmitPoint(canvas)
pointTool.canvasClicked.connect(display_point)
canvas.setMapTool(pointTool)