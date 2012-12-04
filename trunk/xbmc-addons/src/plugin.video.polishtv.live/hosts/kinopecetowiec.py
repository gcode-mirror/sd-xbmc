# -*- coding: utf-8 -*-
import cookielib, os, string, StringIO
import os, time, base64, logging, calendar
import urllib, urllib2, re, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin

scriptID = 'plugin.video.polishtv.live'
scriptname = "Polish Live TV"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import pLog, settings, Parser, urlparser, pCommon

log = pLog.pLog()

HOST = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.18) Gecko/20110621 Mandriva Linux/1.9.2.18-0.1mdv2010.2 (2010.2) Firefox/3.6.18'
SERVICE = 'kinopecetowiec'
MAINURL = 'http://www.kino.pecetowiec.pl'
LOGOURL = 'http://pecetowiec.pl/images/blackevo4-space/logo.png'
IMGURL = MAINURL + '/chimg/'

NEW_LINK = MAINURL + '/videos/basic/mr/'
POP_LINK = MAINURL + '/videos/basic/mv/'
COM_LINK = MAINURL + '/videos/basic/md/'
FAV_LINK = MAINURL + '/videos/basic/tf/'
SCR_LINK = MAINURL + '/videos/basic/tr/'
PRC_LINK = MAINURL + '/videos/basic/rf/'
RDM_LINK = MAINURL + '/videos/basic/rd/'

SERVICE_MENU_TABLE = {1: "Kategorie Filmowe",
		      2: "Najnowsze",
		      3: "Najczesciej Ogladane",
		      4: "Najczesciej Komentowane",
		      5: "Ulubione",
		      6: "Najwyzej Ocenione",
		      7: "Wyroznione",
		      8: "Losowe",
		      
		      10: "Szukaj",
		      11: "Historia Wyszukiwania"
		      }

class KinoPecetowiec:
    def __init__(self):
        log.info('Loading ' + SERVICE)
        self.settings = settings.TVSettings()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()
        self.cm = pCommon.common()
	self.history = pCommon.history()


    def setTable(self):
	return SERVICE_MENU_TABLE


    def listsMainMenu(self, table):
        for num, val in table.items():
            self.addDir(SERVICE, 'main-menu', val, '', '', '', LOGOURL, True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getCategoryTab(self,url):   
        strTab = []
        valTab = []
        data = self.cm.requestData(url)
        match = re.compile('<div class=".+?"><a href="http://www.kino.pecetowiec.pl/categories/(.+?)/.+?" title="(.+?)"><span').findall(data)
        if len(match) > 0:
	    for i in range(len(match)):
		value = match[i]
		strTab.append(value[0])
		strTab.append(value[1])	
		valTab.append(strTab)
		strTab = []
	    valTab.sort(key = lambda x: x[1])
        return valTab


    def listsCategoriesMenu(self,url):
        table = self.getCategoryTab(url)
        for i in range(len(table)):
	    value = table[i]
	    img = IMGURL + value[0] + '.jpg'
	    title = value[1]
	    if title > 0:
		self.addDir(SERVICE, 'category', value[0], title, '', '', img, True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getFilmTab(self, url, category):
        strTab = []
        valTab = []
        data = self.cm.requestData(url)
	#Kategorie
	if category == self.setTable()[1]:
	    match = re.compile('<div class="channel-details-thumb-box-texts"> <a href="http://www.kino.pecetowiec.pl/video/(.+?)/(.+?)">(.+?)</a><br/>').findall(data)
	else:
	#Najnowsze, Najczescie Ogladane
	    match = re.compile('<div class="video-title"><a href="http://www.kino.pecetowiec.pl/video/(.+?)/(.+?)" title="(.+?)">').findall(data)
        if len(match) > 0:
	    for i in range(len(match)):
		value = match[i]
		strTab.append(MAINURL + '/thumb/1_' + value[0] +'.jpg')
		strTab.append(MAINURL + '/video/' + value[0] + '/' + value[1])
		strTab.append(value[2])	
		valTab.append(strTab)
		strTab = []
	#pagination
	match = re.compile('<a href="(.+?)">&raquo;</a>').findall(data)
	if len(match) > 0:
            strTab.append('')
            strTab.append('')
            strTab.append('Następna strona')	
            valTab.append(strTab) 	    
        return valTab

   
    def getFilmTable(self, url, category, page):
        table = self.getFilmTab(url, category)
        for i in range(len(table)):
	    value = table[i]
	    if value[2] != 'Następna strona':
		self.addDir(SERVICE, 'playSelectedMovie', '', value[2], '', value[1], value[0], True, False)
	    else:
		page = str(int(page) + 1)
		self.addDir(SERVICE, 'category', category, value[2], '', page, '', True, False) 
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def setLinkTable(self, host, url):
        strTab = []
	strTab.append(host)
	strTab.append(url)
	return strTab

	
    def getItemTitles(self, table):
        out = []
        for i in range(len(table)):
            value = table[i]
            out.append(value[0])
        return out 

    def listsHistory(self, table):
	print str(table)
	for i in range(len(table)):
	    print str(table[i])
	    if table[i] <> '':
		self.addDir(SERVICE, table[i], 'history', table[i], 'None', LOGOURL, 'None', True, False)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchTable(self, table):
        #table = self.searchTab()
        for i in range(len(table)):
	    value = table[i]
	    self.addDir(SERVICE, 'playSelectedMovie', 'history', value[2], '', value[1], value[0], True, False)   
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def searchInputText(self):
        text = None
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
	    text = k.getText()
	    self.history.addHistoryItem(SERVICE, text)
        return text


    def searchTab(self, text):
        strTab = []
        valTab = []
        values = {'search_id': text}
        headers = { 'User-Agent' : HOST }
        data = urllib.urlencode(values)
        req = urllib2.Request(MAINURL + '/search/', data, headers)
        response = urllib2.urlopen(req)
        link = response.read()
        match = re.compile('<img src="(.+?)" width="126"  height="160" id="rotate').findall(link)
        if len(match) > 0:
          img = match
        else:
          img = []
        match = re.compile('<div class="video-title"><a href="(.+?)" title="(.+?)">').findall(link)
        if len(match) > 0:
          for i in range(len(match)):
            value = match[i]
            strTab.append(img[i])
            strTab.append(value[0])
            strTab.append(value[1])	
            valTab.append(strTab)
            strTab = []
        return valTab


    def getHostTable(self,url):
	valTab = []
        link = self.cm.requestData(url)
	match = re.compile('<div id="videoplayer">(.+?)</div>', re.DOTALL).findall(link)
	if len(match) > 0:
	    match2 = re.compile('http://(.+?)["\\r]').findall(match[0])
	    if len(match2) > 0:
		for i in range(len(match2)):
		    match2[i] = 'http://' + match2[i]
		    valTab.append(self.setLinkTable(self.up.getHostName(match2[i]), match2[i]))
	    valTab.sort(key = lambda x: x[0])
	
	d = xbmcgui.Dialog()
        item = d.select("Wybór filmu", self.getItemTitles(valTab))
        if item != '':
	    videoID = str(valTab[item][1])
	    log.info('mID: ' + videoID)
            return videoID


    def addDir(self, service, name, category, title, plot, page, iconimage, folder = True, isPlayable = True):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&page=" + urllib.quote_plus(page)
        if name == 'main-menu':
            title = category
        if iconimage == '':
            iconimage = "DefaultVideo.png"
        liz=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if isPlayable:
            liz.setProperty("IsPlayable", "true")
        liz.setInfo( type="Video", infoLabels={ "Title": title, "Plot": plot } )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)
    
      
    def LOAD_AND_PLAY_VIDEO(self, videoUrl):
        ok=True
        if videoUrl == '':
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu.', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
            return False
        try:
            xbmcPlayer = xbmc.Player()
            xbmcPlayer.play(videoUrl)
        except:
            d = xbmcgui.Dialog()
            d.ok('Błąd przy przetwarzaniu, lub wyczerpany limit czasowy oglądania.', 'Zarejestruj się i opłać abonament.', 'Aby oglądać za darmo spróbuj ponownie za jakiś czas')        
        return ok


    def handleService(self):
        params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        title = self.parser.getParam(params, "title")
        category = self.parser.getParam(params, "category")
        page = self.parser.getParam(params, "page")
        icon = self.parser.getParam(params, "icon")

	log.info ('name: ' + str(name))
	log.info ('title: ' + str(title))
	log.info ('category: ' + str(category))
	log.info ('page: ' + str(page))

	if page=='': page = 1
	
	#main menu	
        if name == None:
            self.listsMainMenu(SERVICE_MENU_TABLE)	
	#kategorie filmowe    
	elif category == self.setTable()[1]:
	    self.listsCategoriesMenu(MAINURL + '/categories')	    
	#najnowsze
	elif category == self.setTable()[2]:
	    self.getFilmTable(NEW_LINK + str(page), category, page)	
	#najczesciej ogladane
	elif category == self.setTable()[3]:
	    self.getFilmTable(POP_LINK + str(page), category, page)	
	#najczesciej komentowane
	elif category == self.setTable()[4]:
	    self.getFilmTable(COM_LINK + str(page), category, page)		
	#ulubione
	elif category == self.setTable()[5]:
	    self.getFilmTable(FAV_LINK + str(page), category, page)		
	#najwyzej ocenione
	elif category == self.setTable()[6]:
	    self.getFilmTable(SCR_LINK + str(page), category, page)	
	#wyroznione
	elif category == self.setTable()[7]:
	    self.getFilmTable(PRC_LINK + str(page), category, page)	
	#losowe
	elif category == self.setTable()[8]:
	    self.getFilmTable(RDM_LINK + str(page), category, page)

	#szukaj
	elif category == self.setTable()[10]:
	    text = self.searchInputText()
	    self.getSearchTable(self.searchTab(text))
	#Historia Wyszukiwania
	elif category == self.setTable()[11]:
	    t = self.history.loadHistoryFile(SERVICE)
	    print str(t)
	    self.listsHistory(t)
	if category == 'history' and name != 'playSelectedMovie':
	    self.getSearchTable(self.searchTab(name))	
	
	#lista tytulow w kategorii    
	elif name == 'category':
	    url = MAINURL + '/categories/' + category + '/' + str(page) + '/'
	    self.getFilmTable(url, category, page)	    
	    	    
        if name == 'playSelectedMovie':
            url = self.getHostTable(page)
            linkVideo = self.up.getVideoLink(url)
            if linkVideo != False:
                self.LOAD_AND_PLAY_VIDEO(linkVideo)
            else:
                d = xbmcgui.Dialog()
                d.ok('Brak linku', SERVICE + ' - przepraszamy, chwilowa awaria.', 'Zapraszamy w innym terminie.')
