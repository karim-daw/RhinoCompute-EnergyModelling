import pandas
# rhino 3dm import
# from rhino3dm import *
import rhino3dm as rhino3dm
import compute_rhino3d.Util
import json
import requests
import base64

# Rhino compute by default launches on port 6500
compute_url = "http://localhost:6500/"

# set the URL
compute_rhino3d.Util.url = compute_url
# no auth token required
compute_rhino3d.Util.authToken = ""

# test, should return version object
version_test = requests.get(compute_url + '/version')
pload = json.loads(version_test.content)

print(pload)

gh_energy = open(r"./Rhino/single_zone_energy_model_v0.1.ghx", mode="r", encoding="utf-8-sig").read()
gh_energy_bytes = gh_energy.encode("utf-8")
gh_energy_encoded = base64.b64encode(gh_energy_bytes)
gh_energy_decoded = gh_energy_encoded.decode("utf-8")


'''
Rhino 3dm Encoder
'''

class __Rhino3dmEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "Encode"):
            return o.Encode()
        return json.JSONEncoder.default(self, o)

def getCurves(objs):
    curves = [item.Geometry for item in objs if item.Geometry.ObjectType == rhino3dm.ObjectType.Curve]
    return json.dumps(curves, cls=__Rhino3dmEncoder)

def getBreps(objs):
    breps = [item.Geometry for item in objs if item.Geometry.ObjectType == rhino3dm.ObjectType.Brep]
    return list(map(lambda x: {"type":"Rhino.Geometry.Brep","data":json.dumps(x, cls=__Rhino3dmEncoder)}, breps))

'''
Load Rhino 3dm model via File3dm.Read
'''

rhino_dir = "./Rhino/"
model_path = "singleZone.3dm"
gh_path = "geometry"
file_path = rhino_dir + model_path
print(file_path)

# read the 3dm file and encode the geometry for transit
rhFile = rhino3dm.File3dm.Read(file_path)
modelBreps = getBreps(rhFile.Objects)

roomGeometry = json.loads(modelBreps[0]["data"])
roomGeometry = json.dumps(roomGeometry)

print('Geometry encoded ready to go!')

# # Inputs

# # adjust between 0 and 0.9
roomName = "MyPythonRoom"
climateZoneNumber = 4 # mixed
modelName = "MyPythonModel"
apertureFromInput = True
wwr = 0.5
runSimulation = True


#print((roomGeometry))

# payload
geo_payload = {
    "algo": gh_energy_decoded,
    "pointer": None,
    "values": [
        {
            "ParamName": "RoomGeometry",
            "InnerTree": {
                "{ 0; }": [
                    {
                        "type": "Rhino.Geometry.Brep",
                        "data": roomGeometry
                    }
                ]
            }
        },
        {
            "ParamName": "RoomName",
            "InnerTree":{
                "{ 0; }": [
                    {
                        "type": "System.String",
                        "data": roomName
                    }
                ]
            }
        },
        {
            "ParamName": "ClimateZoneNumber",
            "InnerTree":{
                "{ 0; }": [
                    {
                        "type": "System.Double",
                        "data": climateZoneNumber
                    }
                ]
            }
        },
        {
            "ParamName": "ModelName",
            "InnerTree":{
                "{ 0; }": [
                    {
                        "type": "System.String",
                        "data": modelName
                    }
                ]
            }
        },
        {
            "ParamName": "ApertureFromInput",
            "InnerTree":{
                "{ 0; }": [
                    {
                        "type": "System.Double",
                        "data": apertureFromInput
                    }
                ]
            }
        },
        {
            "ParamName": "WWR",
            "InnerTree":{
                "{ 0; }": [
                    {
                        "type": "System.Double",
                        "data": wwr
                    }
                ]
            }
        },
        {
            "ParamName": "RunSimulation",
            "InnerTree":{
                "{ 0; }": [
                    {
                        "type": "System.Bool",
                        "data": runSimulation
                    }
                ]
            }
        },
    ]
}



# send HTTP request to Rhino Compute Server
res = requests.post(compute_url + "grasshopper", json=geo_payload)

print("status code: {}".format(res.status_code))

# deserialize response object
response_object = json.loads(res.content)['values']

print(len(response_object))
#print(response_object[0])

computed_eui = [result for result in response_object if result['ParamName'] == 'EUI'][0]['InnerTree']['{0}'][0]['data']
print('computed EUI: {}'.format(computed_eui))




#  [result for result in response_object if result['ParamName'] == 'RH_OUT:geometry'][0]['InnerTree']['{0;0;0;0;0}']
# print("Computed EUI: : {}".format(len(geometry_output)))

"""
floor_area = [result for result in response_object if result['ParamName'] == 'RH_OUT:max_area'][0]['InnerTree']['{0}'][0]['data']
print('max floor area: {}'.format(floor_area))

floor_area = [result for result in response_object if result['ParamName'] == 'RH_OUT:max_open'][0]['InnerTree']['{0}'][0]['data']
print('max open area: {}'.format(floor_area))"""