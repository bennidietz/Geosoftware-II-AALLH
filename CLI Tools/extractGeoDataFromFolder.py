"""
@Author Henry Fock
"""
import sys
# add local modules folder
file_path = '../Python_Modules'
sys.path.append(file_path)

import getBoundingBox as box
import getTimeExtent as timeEx
import subprocess
import threading

from os import listdir
from os.path import isfile, join
from osgeo import ogr
import click
from DateTime import DateTime
from tabulate import tabulate

@click.command()
@click.option('--path', prompt="File path", help='Path to file')
def main(path):
    threads = []
    res = []
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

    for name in onlyfiles:
        current = CliTools(path, name)
        threads.append(current)
        current.start()

    for thread in threads:
        thread.join()
        res.append(thread.result)

    click.echo("\nErgebnis:")
    for x in res:
        if x[1][0] == None:
            if x[2][0] == None:
                click.echo((x[0], x[1][1], x[2][1]))
            else:
                click.echo((x[0], x[1][1], x[2][0]))
        else:
            if x[2][0] == None:
                click.echo((x[0], x[1][0], x[2][1]))
            else:
                click.echo((x[0], x[1][0], x[2][0]))

    # Create a geometry collection
    geomcol =  ogr.Geometry(ogr.wkbGeometryCollection)
    lowTime, maxTime = None, None 

    for x in res:
        if x[1][1] == None:
            box = ogr.Geometry(ogr.wkbLineString)
            box.AddPoint(x[1][0][0],x[1][0][1])
            box.AddPoint(x[1][0][0], x[1][0][3])
            box.AddPoint(x[1][0][2],x[1][0][1])
            box.AddPoint(x[1][0][2], x[1][0][3])
            geomcol.AddGeometry(box)
        
        if x[2][1] == None:
            if lowTime == None or DateTime(x[2][0][0]) < lowTime:
                lowTime = DateTime(x[2][0][0])
            
            if maxTime == None or DateTime(x[2][0][1]) > maxTime:
                maxTime = DateTime(x[2][0][1])
    
    env = geomcol.GetEnvelope()
    click.echo("\nFull spatial Extent as Boundingbox: %s" % str((env[0], env[2], env[1], env[3])))
    click.echo("\nFull time Extend as ISO8601: %s" % str((str(lowTime), str(maxTime))))




class CliTools(threading.Thread):
    def __init__(self, path, name): 
        threading.Thread.__init__(self) 
        self.path = path
        self.name = name
        self.result = []

    def run(self):
        bbox = box.getBoundingBox(path=self.path, name=self.name)
        time = timeEx.getTimeExtent(path=self.path, name=self.name)
        self.result.extend([self.name, bbox, time])


if __name__ == '__main__':
    main()