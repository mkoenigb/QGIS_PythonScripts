### SETTINGS ###
POINT_LAYERNAME = 'Points' # Name of input-point-layer
POLYGON_LAYERNAME = 'Buildings' # Name of input-polygon-layer
OVERLAYDISTANCE = 0 # tolerance-distance (in CRS units) to identify geometric duplicates (0 is an exact duplicate)

"""
This script redistributes points inside a polygon randomly, if there are duplicate-geometry-points.
Tested with QGIS 3.10.12

Hints:
- Both input layer need to be in the same CRS
- Size and shape of the polygons do have a massive impact on performace due to the bruteforce-method of creating random points inside them
- Use the QGIS-Task-Manager to cancel the process at any time
"""

### NO CHANGES NEEDED BELOW ###

import random
from datetime import datetime

from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )
MESSAGE_CATEGORY = 'Redistribute Points in Polygon'

class redistributePoints(QgsTask):
    def __init__(self, description, duration):
        super().__init__(description, QgsTask.CanCancel)
        self.duration = duration
        self.total = 0
        self.iterations = 0
        self.starttime = datetime.now()
        self.exception = None
        self.vl = QgsVectorLayer("Point", "RedistributedPoints", "memory") # create the new output layer

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(
                                     self.description()),
                                 MESSAGE_CATEGORY, Qgis.Info)

        ### RUN ###
        points = QgsProject.instance().mapLayersByName(POINT_LAYERNAME)[0] # get the input-point-layer
        polygons = QgsProject.instance().mapLayersByName(POLYGON_LAYERNAME)[0] # get the input-polygon-layer
        self.total = points.featureCount() # count features for progress bar
        
        if points.sourceCrs() != polygons.sourceCrs(): # Check if both layers are in the same CRS, if not cancel the task
            self.exception = 'Pointlayer and Polygonlayer need to be in the same CRS'
            return False # cancel the process
            
        # Create the new temporary layer
        crs = points.sourceCrs() # read source CRS
        fields = points.fields() # read source Fields
        self.vl.setCrs(crs) # Set outputlayer CRS to source CRS
        pr = self.vl.dataProvider()
        pr.addAttributes(fields) # add source Fields to output layer
        self.vl.updateFields() # update the outputlayer
        #QgsProject.instance().addMapLayer(vl) # we cannot add a layer to the canvas this way when using qgstasks. Need to add them when the task is finished
        
        # Create the spatial indizes
        points_idx = QgsSpatialIndex(points.getFeatures())
        polygons_idx = QgsSpatialIndex(polygons.getFeatures())
        
        with edit(self.vl): # edit the ouput layer
            for i, point in enumerate(points.getFeatures()): # iterate over source layer
                self.setProgress(i/self.total*100) # update the progressbar
                pr.addFeature(point) # copy the current point to the output layer
                self.vl.updateFeature(point) # update it
                
                # create a list of nearest neighbors (their feature ids) from the current point
                nearestneighbors = points_idx.nearestNeighbor(point.geometry(), neighbors=1, maxDistance=OVERLAYDISTANCE)
                
                # if the list has more than one entry, this means that there is another point at the exact same place,
                # so basically a duplicate geometry. Only shift the point if that is the case. If there is no duplicate geometry,
                # leave the point where it is. This will speed up things.
                if len(nearestneighbors) > 1:
                    
                    # iterate over the polygons that intersect with the current point.
                    # Using a spatial index will speed up iterations, as we do not have to make a point-in-polygon-test for all polygons.
                    for id in polygons_idx.intersects(point.geometry().boundingBox()):
                        
                        polygon = polygons.getFeature(id) # get the polygon-feature by its id
                        
                        # get the polygons bounding box and read maxima amd minima
                        ext = polygon.geometry().boundingBox() 
                        xmin = ext.xMinimum()
                        xmax = ext.xMaximum()
                        ymin = ext.yMinimum()
                        ymax = ext.yMaximum()
                        
                        # set the indicator for the new point to find inside the polygon to false
                        inside = False
                        
                        # now brute-force points until we get a random one that is not only inside the polygons boundingbox
                        # but also inside the polygon itself
                        # this is the step needing the most performance currently, so if there is another method, let me know
                        # idea is taken from this answer: https://gis.stackexchange.com/a/259185/107424
                        while inside is False:
                            if self.isCanceled(): # give user the ability to cancel the whole process
                                return False # cancel the process
                            self.iterations += 1 # count iterations for statistical purposes :)
                            x = random.uniform(xmin, xmax) # create a random x coordinate inside the polygons boundingbox
                            y = random.uniform(ymin, ymax) # create a random y coordinate inside the polygons boundingbox
                            pt = QgsPointXY(x, y) # create a QGIS-Point out of the random coordinates
                            if QgsGeometry.fromPointXY(pt).within(polygon.geometry()): # Check if that point is inside the polygon
                                inside = True # if it does, return true and end the while-loop
                        point.setGeometry(QgsGeometry.fromPointXY(pt)) # change the geometry of the current point to the new random location inside the polygon
                        self.vl.updateFeature(point) # update the changes
        return True # done with no errors

    def finished(self, result):
        endtime = datetime.now()
        runtime = endtime - self.starttime
        
        if result:
            # add the outputlayer to the canvas
            QgsProject.instance().addMapLayer(self.vl)
            
            # throwback a log message
            QgsMessageLog.logMessage(
                'Task "{name}" completed\n' \
                'Runtime: {runtime} (with {iterations} '\
                'iterations for {total} points)'.format(
                  name = self.description(),
                  runtime = runtime,
                  iterations = self.iterations,
                  total = self.total),
              MESSAGE_CATEGORY, Qgis.Success)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without '\
                    'exception (probably the task was manually '\
                    'canceled by the user)'.format(
                        name=self.description()),
                    MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.description(),
                        exception=self.exception),
                    MESSAGE_CATEGORY, Qgis.Critical)
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage(
            'Task "{name}" was canceled'.format(
                name=self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()

# start the task as background process to keep QGIS responsive
# see https://docs.qgis.org/3.16/en/docs/pyqgis_developer_cookbook/tasks.html
task = redistributePoints('Redistribute Points in Polygon', 5)
QgsApplication.taskManager().addTask(task)
