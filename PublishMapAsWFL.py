#!/usr/bin/env python

"""PublishMapAsWFL.py: shares a map as a web feature layer to ArcGIS Online."""

import arcpy, json, os
from urllib.request import urlopen
from urllib.parse import urlencode

__author__ = "Chunming Peng, and Shilpi Jain"
__copyright__ = "Copyright 2018, Esri"
__credits__ = ["Chunming Peng", "Shilpi Jain"]
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = "cpeng at esri.com"
__status__ = "Production"

# list the paths for the input aprx, output sddraft and sd files in variables
aprxPath = r'C:\temp\UC2018\PublishingSamples\Project\USCities\USCities.aprx'
serviceName = 'h_USCities_UC2018'
sddraftPath = r"C:\temp\UC2018\PublishingSamples\Output\%s.sddraft" % (serviceName)
sdPath = r"C:\temp\UC2018\PublishingSamples\Output\%s.sd" % (serviceName)
restEndPoint = "https://services.arcgis.com/EguFTd9xPXEoDtC7/arcgis/rest/services/"
queryCriteria = "where=&objectIds=1&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=&returnGeometry=true&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnDistinctValues=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&quantizationParameters=&sqlFormat=none"
baseJSONFile = r'baselines\base_' + serviceName + '_queryResult_Id1.json'

# list the AGO or enterprise url and credentials here
portalURL = r'https://www.arcgis.com'
cred_detail = []
with open("secure/AGO_pass.txt") as f:
        for line in f:
            cred_detail.append(line.splitlines())
username = cred_detail[0][0]
password = cred_detail[1][0]

# Sign into AGO and set as active portal
arcpy.SignInToPortal(portalURL, username, password)

# Maintain a reference of an ArcGISProject object pointing to your project
aprx = arcpy.mp.ArcGISProject(aprxPath)

# Maintain a reference of a Map object pointing to your desired map
m = aprx.listMaps('Map1')[0]

''' the first step to automate the publishing of a map, layer, or list of layers to a hosted web layer using ArcPy, in new object-oriented approach.
   
   Use "getWebLayerSharingDraft" method to create a FeatureSharingDraft object (reference: http://pro.arcgis.com/en/pro-app/arcpy/sharing/featuresharingdraft-class.htm)
   Syntax = getWebLayerSharingDraft (server_type, service_type, service_name, {...})
   
   Then to a Service Definition Draft (.sddraft) file with "exportToSDDraft" method.
   Syntax = exportToSDDraft (out_sddraft)
'''
sharing_draft = m.getWebLayerSharingDraft('HOSTING_SERVER', 'FEATURE', serviceName)
sharing_draft.portalUrl = portalURL
sharing_draft.summary = "My Summary"
sharing_draft.tags = "My Tags"
sharing_draft.description = "My Description"
sharing_draft.credits = "My Credits"
sharing_draft.useLimitations = "My Use Limitations"
sharing_draft.exportToSDDraft(sddraftPath)

''' The Service Definition Draft can then be converted to a fully consolidated Service Definition (.sd) file using the Stage Service tool.
    Staging compiles all the necessary information needed to successfully publish the GIS resource.
    Syntax = StageService_server (in_service_definition_draft, out_service_definition, staging_version)
'''
arcpy.StageService_server(sddraftPath, sdPath)

'''  Finally, the Service Definition file can be uploaded and published as a GIS service to a specified online organization using the Upload Service Definition tool.
    This step takes the Service Definition file, copies it onto the server, extracts required information, and publishes the GIS resource.
    Syntax = UploadServiceDefinition_server (in_sd_file, in_server, {in_service_name}, {in_cluster}, {in_folder_type},
                                                                        {in_folder}, {in_startupType}, {in_override}, {in_my_contents}, {in_public}, {in_organization}, {in_groups})
'''
arcpy.UploadServiceDefinition_server(sdPath, 'My Hosted Services', in_public = "PUBLIC", in_organization = "SHARE_ORGANIZATION")

''' Getting the token
'''
token_url = 'https://www.arcgis.com/sharing/generateToken'
referer = "http://services.arcgis.com"
query_dict1 = {  'username':   username,
                 'password':   password,
                 'expiration': str(1440),
                 'client':     'referer',
                 'referer': referer}
query_string = urlencode(query_dict1)
tokenStr = json.loads(urlopen(token_url + "?f=json", str.encode(query_string)).read().decode('utf-8'))['token']

'''  Validation - Check if the service published contains "city_name" in layers[0]
'''
test_json = restEndPoint + serviceName + "/FeatureServer/0/query?" + queryCriteria + "&f=pjson&token=" + tokenStr
# Get request and store as bytes
response = urlopen(test_json)
# Convert bytes to string type and string type to dict
testdata = json.loads(response.read().decode('utf-8'))
print(testdata)
basedata = json.load(open(baseJSONFile))
if ((testdata[u'features'][0])[u'attributes']['CITY_NAME'] == (basedata[u'features'][0])[u'attributes']['CITY_NAME']):
        print("Test passed. Query request to the feature service is returning correct city name")
else:
        print("Test failed.")

# end
