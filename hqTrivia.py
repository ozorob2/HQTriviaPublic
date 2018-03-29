import argparse
import io
import nltk
from nltk.corpus import stopwords

from google.cloud import vision
from google.cloud.vision import types
import pytesseract
import requests

import PIL
from PIL import ImageGrab
from googlesearch.googlesearch import GoogleSearch

from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib

def split(s):
    half, rem = divmod(len(s), 2)
    return s[:half + rem], s[half + rem:]

# needed for google vision to work
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

# Instantiates a google vision client
client = vision.ImageAnnotatorClient()

#grab screenshot of screen in certain position
img = PIL.ImageGrab.grab(bbox=(10,240,400,650))
imgByteArr = io.BytesIO()
img.save(imgByteArr, format='PNG')
imgByteArr = imgByteArr.getvalue()

# google vision gets text from image
image = types.Image(content=imgByteArr)
response = client.text_detection(image=image)
texts = response.text_annotations
text = texts[0]

# seperate question and answers
raw = text.description
question_index = raw.index('?')
q = ''.join(raw[0:question_index+1])
answers = raw.splitlines()[-3:]

# clean up questions as it is poorly formated with spaces
# removes stop words from question
# if question contains which, add the three answers to end of question
# if not in question remove it and when results come out pick questions with least hits
question = ''
tokens = [t for t in q.split()] 
clean_tokens = tokens[:] 
sr = stopwords.words('english') 
for token in tokens: 
    if token in stopwords.words('english'): 
        clean_tokens.remove(token) 

for q in clean_tokens:
    question += q + " "

#if "Which" or "What" in question:
#    question += " " +  answers[0] + " or " + answers[1] + " or " + answers[2]

question = question.replace("NOT", " ")

#google the question
url = 'https://www.google.com/search?q='
query = question.replace(" ","%20")
url = url+query
source = requests.get(url).content
soup = BeautifulSoup(source,"html.parser")
descs = soup.findAll('span',{'class':'st'})
desc, desc2 = split(descs)

#check for answers in google descriptions
vote = {el:0 for el in answers}
for d in desc:
    d = d.encode("utf-8")
    for answer in answers:
        if answer.encode("utf-8").lower() in d.lower():
            vote[answer]+=1


## Back up Plan if no results found
if sum(vote.values())== 0:
    for d in desc2:
        d = d.encode("utf-8")
        for answer in answers:
            if answer.encode("utf-8").lower() in d.lower():
                vote[answer]+=1


## prints Results
print question.encode("utf-8")
print (vote)



## Alternate Googling Method

# vote = {el:0 for el in answers}
# from googlesearch import search

# i = 0
# for url in search(question, stop=1):
#     if i > 2:
#         break
#     if "wiki" in url:
#         continue

#     i += 1
#     html = urllib.urlopen(url).read()
#     text = text_from_html(html)
#     for answer in answers:
#         if answer in text:
#             vote[answer]+=1

# print results
