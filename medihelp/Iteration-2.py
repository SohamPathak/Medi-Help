
# coding: utf-8

# In[ ]:


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
import os


def by_size(words, size):
    return [word for word in words if len(word) >= size]
def Remove(duplicate): 
    final_list = [] 
    for num in duplicate: 
        if num not in final_list: 
            final_list.append(num) 
    return final_list 

img = cv2.imread("mupir.jpeg")
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

for l in lst3:
    str1 = str1+'+'+l

#str1 = str1.lower()    
url = str1+str2  

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


print(summary)  

pygame.mixer.init()
language = 'en'

tts = gTTS(text=summary, lang=language, slow=False)
tts.save("voice.mp3")
os.system("voice.mp3")

