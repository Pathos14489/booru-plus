import os
import json
import requests
from PIL import Image
from scrape import scrape
from check import check

dirname = "./"
if not os.path.exists(dirname):
    os.mkdir(dirname)
images_dirname = dirname + "images/"
if not os.path.exists(images_dirname):
    os.mkdir(images_dirname)
json_dirname = dirname + "json/"
if not os.path.exists(json_dirname):
    os.mkdir(json_dirname)
source_dirname = dirname + "source_json/"
if not os.path.exists(json_dirname):
    os.mkdir(json_dirname)
image_json_dir = "image_json/"
if not os.path.exists(image_json_dir):
    os.mkdir(image_json_dir)

class BooruPlus:
    def __init__(self):
        # Basic Data - All posts have at least this data
        self.images = []
        self.jsons = []
        
        # Extra Data - Not all posts have this data
        self.source_jsons = []
        self.image_jsons = []
        
        # load the images, jsons, source_jsons, and image_jsons from their respective directories
        for image in os.listdir(images_dirname):
            self.images.append(image)
        for jsn in os.listdir(json_dirname):
            self.jsons.append(jsn)
        for source_json in os.listdir(source_dirname):
            self.source_jsons.append(source_json)
        for image_json in os.listdir(image_json_dir):
            self.image_jsons.append(image_json)
        
        # load the jsons into a list of Post objects
        self.posts = []
        for jsn in self.jsons:
            print(json_dirname+jsn)
            with open(json_dirname + jsn, "r") as f:
                data = json.load(f)
                self.posts.append(Post(data, jsn.split(".")[0]))
                
        # For each post, load the source_json in as JSON data if it exists
        for post in self.posts:
            if post.source_json != None:
                if os.path.exists(source_dirname + post.id + ".json"):
                    with open(source_dirname + post.id + ".json", "r") as f:
                        try:
                            post.source_json = json.load(f)
                        except:
                            print("failed to load " + post.id + ".json")
            else:
                post.source_json = {}    
            # For each post, load the image_json in as JSON data if it exists
            if post.id + ".json" in self.image_jsons:
                with open(image_json_dir + post.id + ".json", "r") as f:
                    post.image_json = json.load(f)
            else:
                post.image_json = {}
                
        print("BooruPlus object created with " + str(len(self.posts)) + " posts.")
        has_image_json = 0
        has_source_json = 0
        has_at_least_one = 0
        has_both = 0
        for post in self.posts:
            add_one = 0
            add_two = 0
            if post.image_json != {}:
                has_image_json += 1
                add_one = 1
                add_two += 1
            if post.source_json != {}:
                has_source_json += 1
                add_one = 1
                add_two += 1
            has_at_least_one += add_one
            if add_two == 2:
                has_both += 1
            if post.image_json != {} or post.source_json != {}:
                post.valid = True
                if post.image_json != {}:
                    post.chara = post.image_json
                if post.source_json != {}:
                    post.chara = post.source_json
            else:
                post.valid = False
            del post.image_json
            del post.source_json
        print(str(has_image_json) + " posts have image_jsons.")
        print(str(has_source_json) + " posts have source_jsons.")
        print(str(has_at_least_one) + " posts have at least one of either image_json or source_json.")
        print(str(has_both) + " posts have both image_json and source_json.")
        self.posts = [post for post in self.posts if post.valid]
        print("BooruPlus object created with " + str(len(self.posts)) + " posts.")
        print(self.posts[0].__dict__)
    
    def scrape(self):
        scrape()
    
    def check(self): # depreciated - Was used to fix the image_jsons, left in because I'm lazy
        check()
    
    def get_by_id(self,id):
        for post in self.posts:
            if post.id == id:
                return post
        return None
             
class Post:
    def __init__(self,data,id):
        self.id = id
        self.bpi = data["bpi"]
        self.date = data["date"]
        self.type = data["type"]
        self.size = data["size"]
        self.dimensions = data["dimensions"]
        self.rating = data["rating"]
        self.metadata_revision = data["metadata_revision"]
        self.timestamp = data["timestamp"]
        self.accredation  = data["accredation"]
        self.tags = data["tags"]
        self.image_url = data["image_url"]
        self.source_json = data["source_json"]
    
    def get_local_image_path(self):
        return images_dirname + self.id + ".png"
    
    def get_local_json_path(self):
        return json_dirname + self.id + ".json"
    
    def get_local_source_json_path(self):
        return source_dirname + self.id + ".json"
    
    def get_local_image_json_path(self):
        return image_json_dir + self.id + ".json"
    
    def download_image(self):
        r = requests.get(self.image_url)
        with open(self.get_local_image_path(), "wb") as f:
            f.write(r.content)
        
    def get_image(self): # returns a PIL Image object
        return Image.open(self.get_local_image_path())