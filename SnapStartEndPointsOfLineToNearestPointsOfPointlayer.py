points = QgsProject.instance().mapLayersByName('points')[0]
lines = QgsProject.instance().mapLayersByName('lines')[0]
tolerance = 10000 # snapping tolerance in CRS units

# creat the spatial index of the pointlayer
points_idx = QgsSpatialIndex(points.getFeatures())

with edit(lines):
    # enumerate because we need the feature id to use QgsVectorLayerEditUtils
    for i, feat in enumerate(lines.getFeatures()):
        linegeom = feat.geometry().asPolyline()
        i += 1 # adjust the current feature id

        # get start and end point of line
        line_startgeom = QgsPointXY(linegeom[0])
        line_endgeom = QgsPointXY(linegeom[-1])
        
        # find nearest point of point layer to start and endpoint of line
        nearestneighbor_start = points_idx.nearestNeighbor(line_startgeom, neighbors=1, maxDistance=tolerance)
        nearestneighbor_end = points_idx.nearestNeighbor(line_endgeom, neighbors=1, maxDistance=tolerance)
        
        try: # only adjust the startpoint if there is a nearest point within the maxdistance
            nearpoint_startgeom = points.getFeature(nearestneighbor_start[0]).geometry() # get the geometry of the nearest point in pointlayer
            x_start = nearpoint_startgeom.asPoint().x() # extract x value of that point
            y_start = nearpoint_startgeom.asPoint().y() # extract y value of that point
            QgsVectorLayerEditUtils(lines).moveVertex(x_start,y_start,i,0) # use QgsVectorLayerEditUtils to edit the vertex, for more details see https://qgis.org/pyqgis/3.4/core/QgsVectorLayerEditUtils.html#qgis.core.QgsVectorLayerEditUtils
        except: # if there is no nearest point just do nothing
            pass
        try:
            nearpoint_endgeom = points.getFeature(nearestneighbor_end[0]).geometry()
            x_end = nearpoint_endgeom.asPoint().x()
            y_end = nearpoint_endgeom.asPoint().y()
            lastvert = len(feat.geometry().asPolyline())-1 # QgsVectorLayerEditUtils.moveVertex() seems to not accept -1 as index of last vertex, so we need to count for it...
            QgsVectorLayerEditUtils(lines).moveVertex(x_end,y_end,i,lastvert)
        except:
            pass