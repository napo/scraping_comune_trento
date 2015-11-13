# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Created on Fri Nov 13 15:28:08 2015

@author: napo
"""

from builtins import str as futureenc
import sys  
import os
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import requests
from lxml import html

class scrapeBioStradario():
    deathsymbol="†"
    bornsymbol = "*"
    cookies = None
    people = []

    def scrape(self):
        #step 1: home page
        url="https://webapps.comune.trento.it/stradario-rete/ArkAccesso.do"
        r = requests.get(url) #,cookies=cookies)
        self.cookies = r.cookies
        tree = html.fromstring(r.content)
        hidRifMenu=tree.xpath('//form[@id="menuContextForm"]//input')[0].value
        arkButtons=tree.xpath('//form[@id="menuContextForm"]//button')[0].attrib['onclick'].split(",'")[1].replace("')","")
        
        #step 2: va sullo stradario
        url="https://webapps.comune.trento.it/stradario-rete/menuContext.do"
        params = {"hidRifMenu":hidRifMenu,"arkButtons":arkButtons} 
        r = requests.post(url,data=params,cookies=self.cookies)
        if (len(r.cookies) != 0):
          self.cookies = r.cookies
        tree = html.fromstring(r.content)
        arkRifMan = tree.xpath("//form[@id='vieForm']//input")[0].value
        arkButtons=tree.xpath('//form[@id="vieForm"]//button')[0].attrib['onclick'].split(";")[0].split(",'")[1].replace("')","")
        
        people = []
        arkbuttonsbio = []
        url = "https://webapps.comune.trento.it/stradario-rete/vie.do"
        params={"arkRifMan":arkRifMan,"wkdesc":"","wkdcir":"","wkloca":"","arkButtons":arkButtons}
        r = requests.post(url,data=params,cookies=self.cookies)
        tree = html.fromstring(r.content)
        arkRifMan = tree.xpath("//form[@id='vieForm']//input")[0].value
        items = tree.xpath('//span[@class="pagerTestata"]')[0].text.split(" vie")[0].split("Trovate ")[1]
        anchors = tree.xpath("//a")
        for a in anchors:
            if a.attrib.has_key('onmouseover'):
                if a.attrib['onmouseover'] == "self.status='Biografia'; return true":
                    arkbuttonsbio.append(a.attrib['href'].replace("javascript:arkImpBut('vieForm',0,0,0,1,","").replace("')","").replace("'",""))
                    
        for arkbutton in arkbuttonsbio:
            story = self.getstory(self.cookies,arkRifMan,arkbutton)
            arkRifMan = story["arkRifMan"]
            arkButtons = story["arkButtons"]
            arkRifMan = self.resetbio(story["arkRifMan"],story["arkButtons"])
            url = "https://webapps.comune.trento.it/stradario-rete/vie.do"
            params={"arkRifMan":arkRifMan,"wkdesc":"","wkdcir":"","wkloca":"","arkButtons":arkButtons}
            people.append(story)
        
        for i in range(10, int(items), 10):
            arkbuttonsbio = []
            url = "https://webapps.comune.trento.it/stradario-rete/vie.do"
            params={"arkRifMan":arkRifMan,"wkdesc":"","wkdcir":"","wkloca":"","pager": "offset," + str(i), "arkButtons":""}
            r  = requests.post(url,data=params,cookies=self.cookies)
            tree = html.fromstring(r.content)
            arkRifMan = tree.xpath("//form[@id='vieForm']//input")[0].value
            anchors = tree.xpath("//a")
            for a in anchors:
                if a.attrib.has_key('onmouseover'):
                    if a.attrib['onmouseover'] == "self.status='Biografia'; return true":
                        arkbuttonsbio.append(a.attrib['href'].replace("javascript:arkImpBut('vieForm',0,0,0,1,","").replace("')","").replace("'",""))
        
            for arkbutton in arkbuttonsbio:
                story = self.getstory(self.cookies,arkRifMan,arkbutton)
                arkRifMan = story["arkRifMan"]
                arkButtons = story["arkButtons"]
                arkRifMan = self.resetbio(story["arkRifMan"],story["arkButtons"])
                url = "https://webapps.comune.trento.it/stradario-rete/vie.do"
                params={"arkRifMan":arkRifMan,"wkdesc":"","wkdcir":"","wkloca":"","arkButtons":arkButtons}
                self.people.append(story)
    
        return self.people
        
  
    def __init__(self):
        reload(sys)  
        sys.setdefaultencoding('utf8')

    def trentinoimg2text(self,imgsrc):
        answer=1
        if imgsrc == 'images/arkImg/rad_off.gif':
            answer=0
        return answer
    
    def getbiodata(self,borndata,what):
        data = {}
        date = ""
        place = ""
        row = 0
        fr = 0

        for b in borndata:
            b = futureenc(b)
            if b.find(what) > -1:
                for counter in range(len(b),0,-1):
                    d = b[counter-1:counter]
                    if  d== " ":
                        fr = row
                        break
                    else:
                        date += d
            row += 1
                    
        date = date[::-1]
        if date != "":
            if (date[0].isdigit()):
                place = borndata[fr].replace(date,"").replace(what+" ","").replace(",","")
                
            else:
                date = ""
        data["date"]=date
        data["place"]=place
        return data
    
    def findbiojob(self,borndata):
        job = ""
        if (len(borndata) > 0):
            for b in borndata:
                if b.find(self.deathsymbol) > -1:
                        borndata.remove(b)
                for b in borndata:
                    if b.find(self.bornsymbol) > -1:
                        borndata.remove(b)  
        if (len(borndata) > 0):
            job = borndata[0]
        return borndata[0]


    def resetbio(self,arkRifMan,arkButtons):
        url = "https://webapps.comune.trento.it/stradario-rete/biografia.do"
        params={"arkRifMan":arkRifMan,"bianag":"","bibiog":"","arkButtons":arkButtons}
        r = requests.post(url,data=params,cookies=self.cookies)
        tree = html.fromstring(r.content)
        arkRifMan = tree.xpath("//form[@id='vieForm']//input")[0].value
        return arkRifMan

   
    def getstory(self,cookies,arkRifMan,arkButtons):
        story = {}
        url = "https://webapps.comune.trento.it/stradario-rete/vie.do"
        params={"arkRifMan":arkRifMan,"wkdesc":"","wkdcir":"","wkloca":"","arkButtons":arkButtons}
        r = requests.post(url,data=params,cookies=self.cookies)
        if (len(r.cookies) != 0):
            self.cookies = r.cookies
        tree = html.fromstring(r.content)
        arkRifMan = tree.xpath("//form[@id='biografiaForm']//input")[0].value
        arkButtons = tree.xpath("//form[@id='biografiaForm']//button")[0].attrib['onclick'].split(";")[0].split(",'")[1].replace("')","")
        who = tree.xpath("//span[@class='textboxVis']")
        story["street"] = who[0].text
        names = who[1].text.split(",")
        if len(names) > 1:
            story["name"] = names[1]
            story["lastname"] = names[0]
        else:
            story["name"] = names[0]
            story["lastname"] = ""           
        biodata = tree.xpath("//textarea[@name='bianag']")[0].text.split("\r\n") #.split("\r\n")[1]
        data = self.getbiodata(biodata,self.deathsymbol)
        story["death_place"]=data["place"] 
        story["death_date"]=data["date"] 
        data = self.getbiodata(biodata,self.bornsymbol)
        story["born_place"]=data["place"] 
        story["born_date"]=data["date"] 
        story["job"] = self.findbiojob(biodata)            
        story["bio"] = tree.xpath("//textarea[@name='bibiog']")[0].text
        infotrentino = tree.xpath("//tr/td/img")
        story["bornintrentino"] =self. trentinoimg2text(infotrentino[0].attrib['src'])
        story["livedintrentino"] = self.trentinoimg2text(infotrentino[1].attrib['src'])
        story["arkRifMan"] = arkRifMan
        story["cookies"] = self.cookies
        story["arkButtons"] = arkButtons
        return story
        


class TopoDB():
    Base = declarative_base()
    class Person(Base):
        __tablename__ = 'person'
        __table_args__ = {'sqlite_autoincrement': True}
        id = Column(Integer, primary_key=True)
        name = Column(Text)
        bio = Column(Text)
        name = Column(Text)
        lastname = Column(Text)
        born_date = Column(Text)
        born_place= Column(Text)
        death_date = Column(Text)
        death_place = Column(Text)
        livedintrentino = Column(Text)
        bornintrentino = Column(Text)
        job = Column(Text)
        street = Column(Text)
        
    def __init__(self):   
        reload(sys)  
        sys.setdefaultencoding('utf8')
    
    def writedb(self,people,outdb):
        if (os.path.isfile(outdb)):
            os.remove(outdb)
            
        engine = create_engine('sqlite:///' + outdb)
        self.Base.metadata.create_all(engine)
        self.Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        
        for p in people:
            keys = ("bio","name","lastname","born_date","born_place","death_date","death_place","livedintrentino","bornintrentino","job","street")
            data = {}    
            for k in keys:
                data[k] = ""
                try:
                    data[k] = futureenc(p[k])
                except KeyError:
                    data[k] = ""
                
            bio = data["bio"]
            name = data["name"]
            lastname = data["lastname"]
            born_date = data["born_date"]
            born_place= data["born_place"]
            death_date = data["death_date"]
            death_place = data["death_place"]
            livedintrentino = data["livedintrentino"]
            bornintrentino = data["bornintrentino"]
            job = data["job"]
            street = data["street"]
        
               
            new_person = self.Person(bio=bio,name=name,lastname=lastname, \
                                born_date=born_date,born_place=born_place, \
                                death_date=death_date,death_place=death_place, \
                                livedintrentino=livedintrentino, \
                                bornintrentino=bornintrentino,\
                                job=job,street=street)
                                
            session.add(new_person)
            session.commit()