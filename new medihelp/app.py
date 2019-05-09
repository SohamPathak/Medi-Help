import os
from flask import Flask, request, redirect, url_for ,render_template,flash,Response
from werkzeug.utils import secure_filename
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import bs4 as bs  
from urllib.request import Request, urlopen  
import re
from nltk.tokenize import sent_tokenize,word_tokenize,WhitespaceTokenizer
import nltk
import heapq  
import requests
import re
#from lxml.html import fromstring
#%pylab inline 
import cv2
#from IPython.display import clear_output
from gtts import gTTS

#useful links
#https://gist.github.com/hosackm/289814198f43976aff9b :: audio
#https://stackoverflow.com/questions/24892035/how-can-i-get-the-named-parameters-from-a-url-using-flask :: get parameter route capturing
#

UPLOAD_FOLDER = 'C:/Users/nEW u/Desktop/new medihelp/static/images'
UPLOAD_FOLDER2 = 'C:/Users/nEW u/Desktop/new medihelp/static'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

global summary
summary = ''


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'



def by_size(words, size):
    return [word for word in words if len(word) >= size]
def Remove(duplicate): 
    final_list = [] 
    for num in duplicate: 
        if num not in final_list: 
            final_list.append(num) 
    return final_list 


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def process(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = cv2.imread(path)
    #print('Original Dimensions : ',img.shape)
    scale_percent = 200 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    #print('Resized Dimensions : ',resized.shape)

    txt =pytesseract.image_to_string(resized)
    #lst=word_tokenize(txt)
    #lst.sort(key=len) 
    #lst.sort(key=lambda item: (-len(item), item))
    #print(lst)



    result1 = re.sub(r"\W", " ", txt, flags=re.I) 
    #remove digit 
    result2 = re.sub(r"\d", "", result1) 
    lst=word_tokenize(result2)
    lst.sort(key=len) 
    lst.sort(key=lambda item: (-len(item), item))

    lst2= by_size(lst,5)
    lst3=Remove(lst2)
    #lst3
    #str0 = 'https://www.google.com/search?q='
    #str1 = 'lybrate'
    #str2= '&source=lnms'
    #for l in lst3:
    #    str1 = str1+'+'+l
    #u = str1+str2    
    #url = u.encode('utf-8')
    #url = url.decode('utf-8')
    #url = str0 + url 
    #url = url[2:]
    article_text = ''
    str1 = 'https://www.google.com/search?q=lybrate'
    str2= '&source=lnms'

    for l in lst3[:5]:
        str1 = str1+'+'+l

    #str1 = str1.lower()    
    url = str1+str2  
    url = re.sub('é','e', url )
    print(url)

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    parsed_article = bs.BeautifulSoup(webpage,'html')
    containers = parsed_article.select(".r a")
    for cont in containers:
        med = cont['href']
        med = med[7:]
        med = med.split("&")
        med = med[0]
        if med[0]=='h':
            #print(med)
            req1 = Request(med, headers={'User-Agent': 'Mozilla/5.0'})
            webpage1 = urlopen(req1).read()
            parsed_article1 = bs.BeautifulSoup(webpage1,'html')
            #p =parsed_article1.find('div', {'class': 'body'})
            #article_text = p.text
            points =parsed_article1.findAll('div', {'class': 'lybMar-btm--double'})
            for p in points:
                #print(p.text)
                article_text += p.text
                
            break
    print(article_text)
    article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)  
    article_text = re.sub(r'\s+', ' ', article_text)  
    formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )  
    formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)  

    sentence_list = nltk.sent_tokenize(article_text)  
    stopwords = nltk.corpus.stopwords.words('english')

    word_frequencies = {}  
    for word in nltk.word_tokenize(formatted_article_text):  
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
    sentence_scores = {}  
    for sent in sentence_list:  
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]
    summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)
   
    summary = ' '.join(summary_sentences)
    summary = re.sub('Ans:',' ', summary )


    return summary





@app.route('/', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            #global filename
            filename = secure_filename(file.filename)
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect(url_for('getsummary'))
           # return redirect(url_for('upload_file',filename=filename))      
    return render_template('account.html')

@app.route('/getsummary', methods=['GET', 'POST'])
def getsummary():
    summary = ''
    filename = 'testimage.jpeg'
    summary = process(filename)

    
    return render_template('result.html',summary = summary)

#def whichlang():



@app.route('/playaudio',methods=['GET'])
def playaudio():

    #language = whichlang()
    #language = 'en'
    language = request.args.get('language')
    summary = ''
    filename = 'testimage.jpeg'
    summary = process(filename)
    tts = gTTS(text=summary, lang=language, slow=False)
    filename = 'voice.wav'
    #path = os.path.join(app.config['UPLOAD_FOLDE'], filename)
    tts.save(os.path.join(app.config['UPLOAD_FOLDER2'], filename))
    #return render_template('audio.html',summary = summary)
    def generate():
        with open("static/voice.wav", "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return Response(generate(), mimetype="audio/x-wav")

    

    #return '''
    #<!doctype html>
    #<title>Upload new File</title>
    #<h1>Upload new File</h1>
    #<form method=post enctype=multipart/form-data>
    #  <p><input type=file name=file>
    #     <input type=submit value=Upload>
    #</form>
    #'''


if __name__ == '__main__':
    app.run(debug=True)    