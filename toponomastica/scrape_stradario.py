# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 09:59:34 2015

@author: Maurizio Napolitano
"""
from __future__ import unicode_literals
from webappscomunetrento import TopoDB, scrapeBioStradario

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')
deathsymbol="†"
bornsymbol = "*"
outdb = 'streetpeopletrento.sqlite'
scrape = scrapeBioStradario()
people = scrape.scrape()  
tb = TopoDB()
tb.writedb(people,outdb)