#!/usr/bin/env python

# Christian Wirtz <doc@snowheaven.de>
#
# Check_MK datasource program for luftdaten.info finedustsensors.
# Output will be printed in <<<local>>> section.

#######################################################################
#  Copyright (C) 2019 Christian Wirtz <doc@snowheaven.de>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#######################################################################

# Build the finedustsensors with the following instructions
# https://luftdaten.info/en/construction-manual/
#
# Check_MK
# https://mathias-kettner.com/
# Successfully tested on Check_MK RAW version 1.5.0 (stable)
# 
# Path:
# Place this into /omd/sites/<SITE>/local/bin/
# Make this script executable!
#
# Configure:
# WATO -> Datasource Programs -> Individual program call instead of agent access -> Command line to execute
# If you use host attributes:
# check_finedustsensor.py --host $HOSTADDRESS$ --opensenseid $_HOSTOPENSENSE$ --latitude $_HOSTLAT$ --longitude $_HOSTLONG$
# Manual usage
# check_finedustsensor.py --host $HOSTADDRESS$ --opensenseid 5acd37ce223bd800191aef7b --latitude $_HOSTLAT$ --longitude $_HOSTLONG$
#
# Links service:
# If you provide the parameters for latitude and longitude you will get a link to maps.luftdaten.info.
# If you provide the parameter --opensenseid you will get a link to opensensemap.org.
#
# Optional host attributes
# Name: LAT  Title: latitude
# Name: LONG Title: longitude
# Name: OPENSENSE Title: Opensense ID
#
# Activate "Add as custom macro" for all attributes!
#

###########################
version      = "1.0"
version_date = "2019-03-24"
###########################


import sys
import getopt
import json
import urllib
from pprint import pprint
try:
    # For Python 3.0 and above
    from urllib.request import urlopen
except ImportError:
    # default: Python 2
    from urllib2 import urlopen


def print_version():
    print "Christian Wirtz <doc@snowheaven.de>"
    print "Date: %s" % (version_date)
    print ""


def print_usage():
    print "Datasource program to get data from Feinstaubsensor for Check_MK."
    print "Output will be printed in <<<local>>> section."
    print ""
    print_version()
    print "-H, --host    -> address/ip (mandatory)"
    print "-h, --help    -> guess what ;-)"
    print "-V, --version -> print version"
    print "-v            -> verbose"
    print "optional:"
    print "--opensenseid -> Opensense ID"
    print "--latitude    -> GPS latitude"
    print "--longitude   -> GPS longitude"


# Process shell arguments
def main(argv):
    #pprint(sys.argv[1:])

    if (sys.argv[1:] == []):
        print "No arguments given!\n"
        print_usage()
        sys.exit(2)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hH:vV", ["help",
                                                          "version",
                                                          "host=",
                                                          "opensenseid=",
                                                          "latitude=",
                                                          "longitude=",
                                                         ])
    except getopt.GetoptError as err:
        print str(err)  # will print something like "option -a not recognized"
        print_usage()
        sys.exit(2)

    global _debug,host,opensenseid,latitude,longitude
    _debug      = False
    host        = None
    opensenseid = None
    latitude    = None
    longitude   = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
            sys.exit()
        if opt in ("-V", "--version"):
            print_version()
            sys.exit()
        elif opt == '-v':
            _debug = True
        elif opt in ("-H", "--host"):
            host = arg
        elif opt == '--opensenseid':
            opensenseid = arg
        elif opt == '--latitude':
            latitude = arg
        elif opt == '--longitude':
            longitude = arg

    if (_debug == True): pprint(sys.argv[1:])

    if ((latitude != None and longitude == None) or (latitude == None and longitude != None)):
        print "Latitude and longitude must be provided together!\n"
        print_usage()
        sys.exit(2)


# Push commandline argument to main function to get parsed
if __name__ == "__main__":
    main(sys.argv[1:])


# Build some values
local_url = "http://%s/" % (host)
url       = "%sdata.json" % (local_url)

if (_debug == True):
    print ""
    print "Host         : %s" % (host)
    print "local_url    : %s" % (local_url)
    print "url          : %s" % (url)

if (opensenseid != None):
    osm_url   = "https://opensensemap.org/explore/%s" % (opensenseid)
else:
    osm_url   = "https://opensensemap.org/"

if (_debug == True):
    print "opensense id : %s" % (opensenseid)
    print "osm_url      : %s" % (osm_url)

if (latitude != None and longitude != None):
    fd_url = "https://duesseldorf.maps.luftdaten.info/#15/%s/%s" % (latitude, longitude)
else:
    fd_url = "https://duesseldorf.maps.luftdaten.info/"
if (_debug == True):
    print "latitude     : %s" % (latitude)
    print "longitude    : %s" % (longitude)
    print "fd_url       : %s" % (fd_url)
    print ""

# Get JSON info from url
output = json.load(urllib.urlopen(url))


# Print agent section
print "<<<check_mk>>>"
print "Version: %s" % (version)
print "AgentOS: arduino"

print "<<<local>>>"

# Build href for links service
links = "<a href='%s' target='_blank'>Luftdaten</a> <a href='%s' target='_blank'>Opensenemap</a> <a href='%s' target='_blank'>Local</a>" % (fd_url, osm_url, local_url)
print "0 Links - %s" % (links)

# Build measurement outputs
print "0 Age - %s sec" % (output['age'])
print "0 Software_Version - %s" % (output['software_version'])

for dict_line in output['sensordatavalues']:
  # map units
  unit = ''
  units = {'SDS_P2'             : 'ug/m3',         # SDS011 PM2.5
           'SDS_P1'             : 'ug/m3',         # SDS011 PM10
           'BME280_temperature' : 'C',             # BME280 Temperatur
           'BME280_humidity'    : '%',             # BME280 rel. Luftfeuchte
           'BME280_pressure'    : 'hPa',           # BME280 Luftdruck
           'samples'            : '',              # ???
           'min_micro'          : '',              # ???
           'max_micro'          : '',              # ???
           'temperature'        : 'C',             # DHT22 Temperatur
           'humidity'           : '%',             # DHT22 rel. Luftfeuchte
           'signal'             : 'dBm',           # WIFI Signal
          }
  unit = units.get(dict_line['value_type'], '')

  # map perflabels
  perflabel = ''
  perflabels = {'SDS_P2'             : 'finedust',    # SDS011 PM2.5
		'SDS_P1'             : 'finedust',    # SDS011 PM10
		'BME280_temperature' : 'temp',        # BME280 Temperatur
		'BME280_humidity'    : 'humidity',    # BME280 rel. Luftfeuchte
		'BME280_pressure'    : 'airpressure', # BME280 Luftdruck
		'samples'            : 'samples',     # ???
		'min_micro'          : 'min_micro',   # ???
		'max_micro'          : 'max_micro',   # ???
		'temperature'        : 'temp',        # DHT22 Temperatur
		'humidity'           : 'humidity',    # DHT22 rel. Luftfeuchte
		'signal'             : 'signal',      # WIFI Signal
	       }
  perflabel = perflabels.get(dict_line['value_type'], 'value')

  # map infotext
  infotext = ''
  infotexts = {'SDS_P2'             : 'finedust PM2.5 concentration', # SDS011 PM2.5
               'SDS_P1'             : 'finedust PM10 concentration',  # SDS011 PM10
               'BME280_temperature' : 'temp',        # BME280 Temperatur
               'BME280_humidity'    : 'humidity',    # BME280 rel. Luftfeuchte
               'BME280_pressure'    : 'airpressure', # BME280 Luftdruck
               'samples'            : 'samples',     # ???
               'min_micro'          : 'min_micro',   # ???
               'max_micro'          : 'max_micro',   # ???
               'temperature'        : 'temp',        # DHT22 Temperatur
               'humidity'           : 'humidity',    # DHT22 rel. Luftfeuchte
               'signal'             : 'signal',      # WIFI Signal
             }
  infotext = infotexts.get(dict_line['value_type'], '')

  # map warnings
  warn = ''
  warnings = {'SDS_P2'             : ';50', # SDS011 PM10
              'SDS_P1'             : ';50', # SDS011 PM2.5
              'BME280_temperature' : '',    # BME280 Temperatur
              'BME280_humidity'    : '',    # BME280 rel. Luftfeuchte
              'BME280_pressure'    : '',    # BME280 Luftdruck
              'samples'            : '',    # ???
              'min_micro'          : '',    # ???
              'max_micro'          : '',    # ???
              'temperature'        : '',    # DHT22 Temperatur
              'humidity'           : '',    # DHT22 rel. Luftfeuchte
              'signal'             : '',    # WIFI Signal
             }
  warn = warnings.get(dict_line['value_type'], '')

  # Build measurement outputs
  print "P %s %s=%s%s %s %s %s" % (
					  dict_line['value_type'],
					  perflabel,
					  dict_line['value'],
					  warn,
					  dict_line['value'],
					  unit,
					  infotext,
				         )

print "<<<>>>"
