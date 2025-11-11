import json

ini_json = {
    "setup": {
        "ram_size": 512,
        "disc_size": 262144,
        "target_fps": 120
    },
    "script": {
        "programs": [
            {
                "initialize": {
                    "header": "0b0000000000000001",
                    "data": [
                        "0x0000"
                    ]
                },
                "timestamps": {}
            }
        ]
    }
}

timestamp = ini_json["script"]["programs"][0]["timestamps"]
for i in range(1, 512):
    timestamp[f"{i}"] = {"insert": [f"0x1111"]}
    
        
with open("max_out_script.json", "w") as max_out_json:
    json.dump(ini_json, max_out_json, indent=4)