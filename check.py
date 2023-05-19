import os
from PIL import Image
import base64
import json
from image_data_extraction import extract_data_from_image

image_json_dir = "./image_json/"
def check():
    for file in os.listdir("./images/"):
        im = Image.open("./images/" + file)
        if "chara" in im.info:
            try:
                data = im.info["chara"] # Base64 encoded string
                data = base64.b64decode(data)
                data = data.decode("utf-8")
                data = json.loads(data)
                # print(data)
                with open(image_json_dir + file.split(".")[0] + ".json", "w") as f:
                    json.dump(data, f)
            except:
                print("failed")
        else:
            if im.info != {} and "srgb" not in im.info:
                print(im.info)
            try:
                data = extract_data_from_image("./images/" + file)
            except:
                data = {}
            if data != {}:
                with open(image_json_dir + file.split(".")[0] + ".json", "w") as f:
                    json.dump(data, f)
