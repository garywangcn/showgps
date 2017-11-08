#!/usr/bin/env python
from pexif import JpegFile
import sys
# import the necessary packages
import os
import argparse
import subprocess
import sys
import getopt
import logging

VERSION="V1.4 20170616"

# Global var which will be stored to KML file
global IndextoPath
IndextoPath='1-.;'
global PathIndex
PathIndex=1

def  writeHMTLHeader(fp, outputfileName) :
    header1 = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>"""

    header2="<name>"+outputfileName+"</name>"

    header3="""    <Style id="s_ylw-pushpin_hl">
        <IconStyle>
            <scale>1.3</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>
            </Icon>
            <hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
        </IconStyle>
        <ListStyle>
            <ItemIcon>
                <href>http://maps.google.com/mapfiles/kml/paddle/red-circle-lv.png</href>
            </ItemIcon>
        </ListStyle>
    </Style>
    <Style id="s_ylw-pushpin">
        <IconStyle>
            <scale>1.1</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>
            </Icon>
            <hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
        </IconStyle>
        <ListStyle>
            <ItemIcon>
                <href>http://maps.google.com/mapfiles/kml/paddle/red-circle-lv.png</href>
            </ItemIcon>
        </ListStyle>
    </Style>
    <StyleMap id="m_ylw-pushpin">
        <Pair>
            <key>normal</key>
            <styleUrl>#s_ylw-pushpin</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#s_ylw-pushpin_hl</styleUrl>
        </Pair>
    </StyleMap>"""
    
    fp.write(header1)
    fp.write(header2)
    fp.write(header3)
    
def writeHTMLTail(fp) :
    tail="""</Document>
</kml>"""
    fp.write(tail)
    
def wirtePostion2Kml(fp, postion, fileName) :
    fp.write("    <Placemark>\n")
    strFilename="        <name>" + fileName + "</name>\n"
    fp.write(strFilename)
    fp.write("        <styleUrl>#m_ylw-pushpin</styleUrl>\n")
    fp.write("        <Point>\n")
    fp.write("            <gx:drawOrder>1</gx:drawOrder>\n")
    strPostion="            <coordinates>" + str(postion[1]) + ',' + str(postion[0]) + ',' + str(postion[2]) + "</coordinates>\n"
    fp.write(strPostion)
    fp.write("        </Point>\n")
    fp.write("    </Placemark>\n")
  
# For example: Path=c:/
#              directory=8100D
#              outputFileName=a.kml
#              so we will check the picture under C:/8100D

def getGPSinFolder(path, directory, outputFileName):
    global IndextoPath
    global PathIndex
    tmpPathIndex=PathIndex
    tmpPath=path+'\\'+directory+'\\'
    
    print "Enter folder:", tmpPath
    listfile=os.listdir(tmpPath)
    
    # loop over the input images
    for imagePath in listfile :
        # load the image, convert it to grayscale, and compute the
        # focus measure of the image using the Variance of Laplacian
        # method
        imagefile = tmpPath + '\\' + imagePath
        
        # To check if this is a folder, if yes, handle all files under this folder
        if  os.path.isdir(imagefile):             
            getGPSinFolder(tmpPath, imagePath, outputFileName)
            continue
            
        try:
            ef = JpegFile.fromFile(imagefile)
            a = ef.get_geo1()
               
        except IOError:
            type, value, traceback = sys.exc_info()
            print >> sys.stderr, "Error opening file:", value, imagePath
            continue
        except JpegFile.NoSection:
            type, value, traceback = sys.exc_info()
            print >> sys.stderr, "Error get GPS info:", value, imagePath
            continue
        except JpegFile.InvalidFile:
            type, value, traceback = sys.exc_info()
            print >> sys.stderr, "Error opening file:", value, imagePath
            continue
        
        except AttributeError:
             print >> sys.stderr, "No GPS infor", imagefile
             continue
             
        # Add the index to head of filename, ex: 1_DSC_0001, 2_DSC_0009
        if directory != '.':
            tmpImagePath=directory + ':' + imagePath  # Write directory name + filename of picture
        else:
            tmpImagePath=imagePath  #Just write the filename of picture
            
        wirtePostion2Kml(outputFileName, a, tmpImagePath)
        
    print "Exit  folder:", tmpPath
 
if __name__ == "__main__": 
    
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--images", required=True,
        help="path to input directory of images")
    ap.add_argument("-o", "--output", required=True,
        help="file of output KML file")
        
    args = vars(ap.parse_args())

    kmlfile=args["output"]

    fo = open(kmlfile, "w")
    print "Creating KML file: ", fo.name

    # Write HTML header to file
    writeHMTLHeader(fo, kmlfile) 
     
    print "Starting to get GPS info from photo ..."

    getGPSinFolder(args["images"], '.', fo)

    writeHTMLTail(fo)
    print "done"
    fo.close()