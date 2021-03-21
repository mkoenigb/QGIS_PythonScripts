for layer in QgsProject.instance().mapLayers().values():
    layer.setProviderEncoding(u'UTF-8')
    layer.dataProvider().setEncoding(u'UTF-8')
    print (layer.name(), layer.dataProvider().encoding())