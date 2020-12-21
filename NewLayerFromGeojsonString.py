# Define settings:
source_layer = QgsProject.instance().mapLayersByName("mylayer")[0] # Define Source-layer
new_layer = QgsVectorLayer('MultiLineString', "new_geojson_layer", "memory") # Define new layer and its type
source_geojsonfield = 'geojsonstring' # Fieldname containing the GeoJSON

#####
# No Changes needed below #
#####

# Copy fields from old layer to new layer
source_fields = source_layer.fields()
new_layer_pr = new_layer.dataProvider()
new_layer.startEditing()
new_layer_pr.addAttributes(source_fields)
new_layer.commitChanges()

for feature in source_layer.getFeatures():
    # geoj is the string object that contains the GeoJSON
    geoj = feature.attributes()[source_fields.indexFromName(source_geojsonfield)]
    # PyQGIS has a parser class for JSON and GeoJSON
    geojfeats = QgsJsonUtils.stringToFeatureList(geoj, QgsFields(), None)
    # if there are features in the list
    if len(geojfeats) > 0:
        new_geom = geojfeats[0].geometry()
        with edit(new_layer):
            new_feat = QgsFeature(feature)
            new_feat.setGeometry(new_geom)
            new_layer.addFeature(new_feat)
            new_layer.updateExtents()
    else:
        print("No features found in the GeoJSON or no valid GeoJSON-String")

# add this brand new layer
QgsProject.instance().addMapLayer(new_layer)