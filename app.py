# importing required modules 
import requests 
import base64
import os
import json
from matplotlib import pyplot as plt
from ibm_watson import VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from flask import Flask, render_template, request, redirect, url_for
  
# Enter your api key 
api_key = "API_KEY"
  
# url variable store url 
url = "https://maps.googleapis.com/maps/api/staticmap?"
  
# center defines the center of the map 
# equidistant from all edges of the mp.  
center = ""
  
# zoom defines the zoom 
# level of the map 
zoom = 17

#IBM cloud config
authenticator = IAMAuthenticator('API_KEY')
visual_recognition = VisualRecognitionV3(
    version='2018-03-19',
    authenticator=authenticator)
visual_recognition.set_service_url('SERVICE_URL') 

  
# get method of requests module 
# return response object 
PEOPLE_FOLDER = os.path.join('static', 'map_image')
  
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

#IndexPage
@app.route('/')
def index():
   chat_img= os.path.join(app.config['UPLOAD_FOLDER'],'chat.png')
   earth_img= os.path.join(app.config['UPLOAD_FOLDER'],'earth.jpg')
   map_html_img=os.path.join(app.config['UPLOAD_FOLDER'],'map_html.png')
   school_img=os.path.join(app.config['UPLOAD_FOLDER'],'school.jpg')
   return render_template("index.html", map_html= map_html_img,chat=chat_img, earth=earth_img, school=school_img)

#ResultPage
@app.route('/image', methods=['GET', 'POST'])
def image():
        center = ""
        
        #Get the userinput(location) 
        comment=request.form.get('location')
        if(comment =='Sipcot'):
                 center = "12.8259,80.21607" #Sipcot lattitude and longitude
                 r = requests.get(url + "center=" + center + "&zoom=" +str(zoom)+ "&size="+"1280x720&scale=2&maptype=satellite&key="+api_key)#get the location image 
                 full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'map.png')
                 f = open(full_filename, 'wb')
                 f.write(r.content)
                 f.close() 
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'map.png') 
        with open(full_filename, 'rb') as images_file:
               classes = visual_recognition.classify(images_file=images_file,threshold='0.6',classifier='color').get_result()#classify the image gives Json output

        #Json to dictionary conversion for retrieving the data
        a=json.dumps(classes, indent=2)
        b=json.loads(a)
        c=b.get('images')
        dict_val=(c[0]['classifiers'][0]['classes'])
        dictt={}
        for x in range(len(dict_val)):
                if 'type_hierarchy' in dict_val[x]:
                        dict_val[x].pop("type_hierarchy")
        for x in range(len(dict_val)):
                key,value=dict_val[x].values()
                if(key=='brick red color'):
                        k='Unoccupied land'
                        dictt[k]=value
                        continue
                if(key=='olive green color'):
                        k = 'Trees'
                        dictt[k]=value
                        continue
                if(key=='tetraskelion'):
                        k = 'Constructed Area'
                        dictt[k]=value
                        continue           
                dictt[key]=value
        labels=dictt.keys()
        sizes=dictt.values()
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%') 
        full_filename_pie = os.path.join(app.config['UPLOAD_FOLDER'], 'piechart.png')
        plt.savefig(full_filename_pie)
        return render_template("image.html", user_image = full_filename , pie_chart=full_filename_pie)


if __name__ == '__main__':
   app.run(debug=True)