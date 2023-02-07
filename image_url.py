from urllib.request import urlretrieve,urlopen
import json
import requests

def fetcher():
    key="QN8PUdf7XPHoSfQptbB7IbrE7nSRkhBqBJDIOLh0"
    date="2015-6-3"
    
    url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?earth_date={date}&api_key={key}"
    response = urlopen(url) 
    data_json = json.loads(response.read())
    image_urls=[]
    for x in data_json["photos"]:
        image_urls.append(x['img_src'])
    i=1
    for x in image_urls:
        print(x)
        r = requests.get(x)
        with open(f"images2/image{i}.png", "wb") as f:
            f.write(r.content)
            i=i+1
fetcher()
    