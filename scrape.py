import requests
import bs4
import re
from PIL import Image
import base64
import os
import json
from image_data_extraction import extract_data_from_image

url = "https://booru.plus/+pygmalion/_pages"
total_posts = []

def get_pages(url):
    pages = []
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    page_as = soup.body.find("div", class_="pages").contents[3].contents
    print(page_as)
    for page_a in page_as[1:]:
        if page_a == "\n":
            continue
        print(page_a)
        try:
            pages.append(page_a["href"])
        except:
            pass
    return pages

def get_page(page_url = "+pygmalion"):
    page_url = "https://booru.plus" + page_url
    posts = []
    r = requests.get(page_url)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    post_as = []
    post_list = soup.find_all("div", class_="post-list")
    for post in post_list:
        p_as = post.find_all("a", class_="post-a")
        for p_a in p_as:
            post_as.append(p_a)
            
    for post_a in post_as:
        post = {}
        post["href"] = post_a["href"]
        post["id"] = post_a["id"]
        posts.append(post)
    return posts
    
def get_post_info(url):
    url = "https://booru.plus/_postviewmenu/"+"+"+url.split("#")[0].split("+")[1]
    print(url)
    post_info = {}
    # request the page with a user agent that pretends to be a browser
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    # print(soup)
    sections = soup.find_all("section")
    information_lis = sections[0].find("ul").find_all("li")
    for information_li in information_lis:
        information = information_li.text
        information = information.split(":")
        if len(information) > 2:
            information[1] = ":".join(information[1:])
        information[0] = information[0].strip()
        information[1] = information[1].strip()
        information[0] = information[0].lower()
        remove_multiple_spaces = re.compile(r"\s+")
        information[0] = remove_multiple_spaces.sub(" ", information[0])
        information[0] = information[0].replace(" ", "_")
        information[0] = information[0].replace("\\n_", "")
        post_info[information[0]] = information[1].strip().replace("\\n", "")
    
    # print(post_info)
        
    accredation_lis = sections[1].find("ul").find_all("li")
    posted_li = accredation_lis[0]
    posted_li = str(posted_li) # convert to string to clean it up and then send it back to bs4
    # remove all text outside of the tags 
    posted_li = re.sub(r">[^<>]+<", "><", posted_li)
    # remove all newlines
    posted_li = posted_li.replace("\n", "")
    posted_li = posted_li.replace("\\n", "")
    
    posted_li = bs4.BeautifulSoup(posted_li, "html.parser")
    # find time tag
    time = posted_li.find("time")
    posted = time["datetime"] # get the datetime attribute
    # print the first element of time
    # print(time.contents[0])
    poster_href = posted_li.find("a")["href"]
    post_approval = accredation_lis[1].text
    if "not" in post_approval:
        post_approval = False
    else:
        post_approval = True
    content_approval = accredation_lis[2].text
    if "not" in content_approval:
        content_approval = False
    else:
        content_approval = True
    post_info["accredation"] = {}
    post_info["accredation"]["posted"] = posted.strip().replace("\"", "").replace("\\", "")
    post_info["accredation"]["poster_href"] = poster_href.strip().replace("\"", "").replace("\\", "")
    post_info["accredation"]["post_approval"] = post_approval
    post_info["accredation"]["content_approval"] = content_approval
    
    # print(post_info)
    try:
        tags_lis = sections[4].find("ul").find_all("li")
        tag_as = []
        for tag_li in tags_lis:
            tag_as.append(tag_li.find_all("a")[2])
        tags = []
        for tag_a in tag_as:
            # print(len(tag_a.contents))
            # print(tag_a.contents)
            if len(tag_a.contents) >= 6:
                tag_type = tag_a.contents[0].text.split(":")[0]
                tag_name = tag_a.contents[2].text.strip()
                if tag_type == "tags":
                    tag_type = "general"
            else:
                tag_type = "general"
                tag_name = tag_a.contents[1].text.strip()
            tags.append({"type": tag_type, "name": tag_name})
    except:
        tags = []
    post_info["tags"] = tags
    # print(post_info)
    
    # comments_lis = sections[7].find("ul")
    # comments_lis = str(comments_lis)
    # # remove all text outside of the tags
    # comments_lis = re.sub(r">[^<>]+<", "><", comments_lis)
    # # remove all newlines
    # comments_lis = comments_lis.replace("\n", "")
    # comments_lis = comments_lis.replace("\\n", "")
    # comments_lis = bs4.BeautifulSoup(comments_lis, "html.parser")
    # comments_lis = comments_lis.contents[0]
    # comments_lis = comments_lis.contents[0]
    # print(comments_lis, len(comments_lis.contents))
    # comments = []
    # comment_index = 0
    # for comment_li in comments_lis.contents:
    #     comment = {}
    #     print(comment_li)
    #     comment["id"] = comment_index
    #     comment["content"] = comment_li.contents[0].text
    #     comment["author"] = comment_li.contents[1].contents[0].text
    #     comment["comment_date"] = comment_li.contents[1].contents[1].text
    #     comments.append(comment)
    #     comment_index += 1
    # post_info["comments"] = comments
    
    actions = sections[3].find("p").find_all("a")
    image_url = actions[4]["href"]
    post_info["image_url"] = image_url.strip().replace("\"", "").replace("\\", "")
    
    try:
        source_json = sections[5].find("ul").find_all("li")
        for li in source_json:
            if ".json" in li.text:
                source_json = "http"+li.text.split("http")[1].split(".json")[0] + ".json"
                break
        if type(source_json) != str:
            source_json = None
    except:
        source_json = None
    post_info["source_json"] = source_json
    print(source_json)
    
    return post_info

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

def scrape():
    all_pages = get_pages(url)
    print(all_pages)

    for page in all_pages:
        print(page)
        psts = get_page(page)
        for pst in psts:
            total_posts.append(pst)
    # break_limit = 3
    for post in total_posts:
        data = {
            "image_url": "",
            "source_json": None
        }
        # break
        # break_limit -= 1
        if os.path.exists(json_dirname + post["href"].split("#")[0].split("+")[1] + ".json") == False:
            data = get_post_info(post["href"])
            print(data)
            with open(json_dirname + post["href"].split("#")[0].split("+")[1] + ".json", "w") as f:
                f.write(json.dumps(data))
        if os.path.exists(images_dirname + post["href"].split("#")[0].split("+")[1] + ".png") == False and data["image_url"] != "":
            r = requests.get(data["image_url"], headers={'User-Agent': 'Mozilla/5.0'})
            with open(images_dirname + post["href"].split("#")[0].split("+")[1] + ".png", "wb") as f:
                f.write(r.content)
            im = Image.open(images_dirname + post["href"].split("#")[0].split("+")[1] + ".png")
            print(im.info)
            if "chara" in im.info:
                try:
                    data = im.info["chara"] # Base64 encoded string
                    data = base64.b64decode(data)
                    data = data.decode("utf-8")
                    data = json.loads(data)
                    print(data)
                    with open(image_json_dir + post["href"].split("#")[0].split("+")[1] + ".json", "w") as f:
                        json.dump(data, f)
                except:
                    print("failed")
            else:
                if im.info != {} and "srgb" not in im.info:
                    print(im.info)
                try:
                    data = extract_data_from_image(images_dirname + post["href"].split("#")[0].split("+")[1] + ".png")
                except:
                    data = {}
                if data != {}:
                    with open(image_json_dir + post["href"].split("#")[0].split("+")[1] + ".json", "w") as f:
                        json.dump(data, f)
        if data != None:
            print(data)
            try:
                if "source_json" in data: 
                    if len(data["source_json"]) > 0:
                        if os.path.exists(source_dirname + post["href"].split("#")[0].split("+")[1] + ".json") == False:
                            r = requests.get(data["source_json"], headers={'User-Agent': 'Mozilla/5.0'})
                            with open(source_dirname + post["href"].split("#")[0].split("+")[1] + ".json", "wb") as f:
                                f.write(r.content)
            except:
                pass