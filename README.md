# check_finedustsensor.py
Check_MK datasource program for luftdaten.info finedustsensors.

Check_MK datasource program for luftdaten.info finedustsensors.
Output will be printed in <<<local>>> section.

Build the finedustsensors with the following instructions
https://luftdaten.info/en/construction-manual/

Check_MK
https://mathias-kettner.com/
Successfully tested on Check_MK RAW version 1.5.0 (stable)

Path:
Place this into /omd/sites/<SITE>/local/bin/
Make this script executable!

Configure:
WATO -> Datasource Programs -> Individual program call instead of agent access -> Command line to execute

If you use host attributes:
check_finedustsensor.py --host $HOSTADDRESS$ --opensenseid $_HOSTOPENSENSE$ --latitude $_HOSTLAT$ --longitude $_HOSTLONG$
Manual usage
check_finedustsensor.py --host $HOSTADDRESS$ --opensenseid 5acd37ce223bd800191aef7b --latitude $_HOSTLAT$ --longitude $_HOSTLONG$

Links service:
If you provide the parameters for latitude and longitude you will get a link to maps.luftdaten.info.
If you provide the parameter --opensenseid you will get a link to opensensemap.org.

Optional host attributes
Name: LAT  Title: latitude
Name: LONG Title: longitude
Name: OPENSENSE Title: Opensense ID

Activate "Add as custom macro" for all attributes!
