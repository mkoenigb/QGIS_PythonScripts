multiPointLayer = QgsProject.instance().mapLayersByName('Dissolved')[0] # get a layer
pr = multiPointLayer.dataProvider()
# Note the change of fieldtypes:
pr.addAttributes([
    QgsField("x_coords", QVariant.String),
    QgsField("y_coords", QVariant.String),
    QgsField("x_coord_centroid", QVariant.Double), 
    QgsField("y_coord_centroid", QVariant.Double),
    QgsField("x_coord_firstpoint", QVariant.Double),
    QgsField("y_coord_firstpoint", QVariant.Double)
])
multiPointLayer.updateFields()

with edit(multiPointLayer):
    for feature in multiPointLayer.getFeatures():
        geom = feature.geometry() # get the geometry of the current feature
        x_arr = [] # create an empty list
        y_arr = [] # create an empty list
        for part in geom.parts(): # loop through the parts of each multipoint feature
            for p in part.vertices(): # now "loop through" each vertex of each part (actually a loop isnt really needed but easier to implement, since each part always has exact one vertex)
                x_arr.append(p.x()) # get the x coordinate of that vertex (p.x()) and append it to the list
                y_arr.append(p.y()) # get the y coordinate of that vertex (p.y()) and append it to the list
        
        # Same as array_to_string(array_foreach(generate_series(0,num_points($geometry)-1),x_at(@element)),','):
        feature['x_coords'] = ','.join(str(x) for x in x_arr) # turn the list of x coordinates into a comma spearated string. Therefore we need to iterate over the list and convert each double value to a string
        feature['y_coords'] = ','.join(str(y) for y in y_arr) # turn the list of y coordinates into a comma spearated string. Therefore we need to iterate over the list and convert each double value to a string
        # Same as x($geometry) and y($geometry):
        feature['x_coord_centroid'] = geom.centroid().asPoint().x() # get the x coordinate of the multipoint features centroid
        feature['y_coord_centroid'] = geom.centroid().asPoint().y() # get the y coordinate of the multipoint features centroid
        # Same as $x and $y:
        feature['x_coord_firstpoint'] = x_arr[0] # get the x coordinate of the first point of each MultiPoint
        feature['y_coord_firstpoint'] = y_arr[0] # get the y coordinate of the first point of each MultiPoint
        
        multiPointLayer.updateFeature(feature)

QgsProject.instance().addMapLayer(multiPointLayer)