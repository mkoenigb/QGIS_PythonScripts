points = QgsProject.instance().mapLayersByName('points')[0]
lines = QgsProject.instance().mapLayersByName('lines')[0]
tolerance = 10000 # snapping tolerance in CRS units

if QgsWkbTypes.isMultiType(points.wkbType()): # if point-input is of type multigeometry
    res = processing.run("native:multiparttosingleparts",{'INPUT':points,'OUTPUT':'TEMPORARY_OUTPUT'}) # convert to singlepoint
    singlepoints = res['OUTPUT']
else: # if point-input is of type singlegeometry 
    singlepoints = points # leave the inputlayer as it is

# create the spatial index of the pointlayer
points_idx = QgsSpatialIndex(singlepoints.getFeatures())

with edit(lines):
    for feat in lines.getFeatures():
        geom = feat.geometry()
        vert = 0 # reset vertices-count on every new feature
        vert_dict = {} # clear vertices dictionary on every new feature
        for part in geom.parts(): # iterate through all parts of each feature
            for vertex in part.vertices(): # iterate through all vertices of each part
                #if feat.geometry().vertexAt(0) == geom.vertexAt(vert): # if the current vertex is a startpoint of the feature
                if part.startPoint() == geom.vertexAt(vert): # if the current vertex is a startpoint of the features part, then:
                    nearestneighbor_start = points_idx.nearestNeighbor(QgsPointXY(part.startPoint()), neighbors=1, maxDistance=tolerance) # find the closest point to the current startpoint
                    if len(nearestneighbor_start) > 0:# only adjust the startpoint if there is a nearest point within the maxdistance
                        nearpoint_startgeom = singlepoints.getFeature(nearestneighbor_start[0]).geometry() # get the geometry of the nearest point in pointlayer
                        vert_dict[vert] = nearpoint_startgeom.asPoint() # add the index of the current vertex as key and the geometry of the closest point as value to the dictionary
                #elif feat.geometry().vertexAt([i for i, f in enumerate(feat.geometry().vertices())][-1]) == geom.vertexAt(vert): # if the current vertex is an endpoint of the current feature
                elif part.endPoint() == geom.vertexAt(vert): # if the current vertex is an endpoint of the current features part
                    nearestneighbor_end = points_idx.nearestNeighbor(QgsPointXY(part.endPoint()), neighbors=1, maxDistance=tolerance)
                    if len(nearestneighbor_end) > 0:
                        nearpoint_endgeom = singlepoints.getFeature(nearestneighbor_end[0]).geometry()
                        vert_dict[vert] = nearpoint_endgeom.asPoint()
                else:
                    pass # if current vertex is not a start or end point skip it...
                vert += 1 # increase vertices-counter
        for vertindex, newpoint in vert_dict.items(): # for every feature iterate over the just created dictionary (vertindex (=dict key) is the start or endpoint we want to move and newpoint (=dict value) the position we want to move it to)
            QgsVectorLayerEditUtils(lines).moveVertex(newpoint.x(),newpoint.y(),feat.id(),vertindex) # use QgsVectorLayerEditUtils to edit the vertex, for more details see https://qgis.org/pyqgis/3.4/core/QgsVectorLayerEditUtils.html#qgis.core.QgsVectorLayerEditUtils
# https://gis.stackexchange.com/a/411157/107424