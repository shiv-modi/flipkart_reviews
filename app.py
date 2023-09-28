from flask import Flask , request , jsonify ,render_template
from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as bs
from flask_cors import cross_origin , CORS

import requests
import logging
from pymongo.mongo_client import MongoClient
import json


logging.basicConfig(filename='system.log',level=logging.DEBUG)

app = Flask(__name__)
try :
    @app.route("/" , methods =['GET'])
    @cross_origin()
    def index():
            return render_template('index.html')

except Exception as e:
     logging.info(e)
 
try : 
     @app.route("/review" , methods=['POST','GET'])
     @cross_origin()
     def review():


            if request.method == 'POST':

                try:
                
                    search_product = request.form['content'].replace(" ","")

                    product_name = 'https://www.flipkart.com/search?q=' + search_product

                    product_page_open = ureq(product_name)

                    product_page_read = product_page_open.read()

                    product_page_bs = bs(product_page_read,'html.parser')

                    product_link = product_page_bs.find_all('div',{"class":"_1AtVbE col-12-12"})

                    product_name = product_link[2].find("div",{"class":"_4rR01T"}).text

                    product_page = 'https://www.flipkart.com' + product_link[2].div.div.div.a['href']

                    product = requests.get(product_page)

                    enter_product = bs(product.text,'html.parser')

                    product_reviews = enter_product.find_all("div",{"class":"_16PBlm"})

                    reviews = []

                    for comment in product_reviews:   

                                    
                            try:

                                    rating = comment.div.find('div',{"class":"_3LWZlK _1BLPMq"}).text

                                    logging.info('Rating is fetch properly')

                            except:
                                    rating1 = " No Rating"
                                    logging.info(rating1)
                                
                            try:
                                    headline = comment.div.div.div.p.text
                                    logging.info('headline is fetch properly')
                                
                            except:
                                    headline1 = "No Comment Headline"
                                    logging.info(headline1)

                            try :
                                
                                    review = comment.div.find('div',{"class":""}).div.text
                                    logging.info('review is fetch properly')

                            except:
                                    review1 =  "NO Review"
                                    logging.info(review1)

                            try :
                                    name = comment.find('div',{"class":"row _3n8db9"}).find('p').text
                                    logging.info('name is fetch properly')

                                
                            except :
                                    name1 = "NO Name Found"
                                    logging.info(name1)

                            mydict = {"Product": product_name,"Name" : name ,"Rating" : rating ,"CommentHead" : headline , "Comment" : review }
                            reviews.append(mydict)

                            filename = search_product

                            with open(filename + '.json',"w") as f :
                                  
                                  json.dump(reviews , f)


                    uri = "mongo_db_url"

                    # Create a new client and connect to the server
                    client = MongoClient(uri)

                    # Send a ping to confirm a successful connection
                    try:
                      
                      client.admin.command('ping')
                      logging.info("Pinged your deployment. You successfully connected to MongoDB!")
                       
                      db = client['flipkart_reviews']

                      collection = db['reviews']

                      collection.insert_many(reviews)  

                      for i in collection.find():

                            logging.info(i) 

                    except Exception as e:
                     logging.info(e) 

                      


 
                    return render_template('result.html',reviews = reviews[0:len(reviews)-1],title = product_name)
                except Exception as e:
                    logging.info(e)
                    return 'something is wrong Please try again!'
                
             
          
except Exception as e :
      logging.info(e) 
       


if __name__ == '__main__':
    app.run(host="0.0.0.0")
