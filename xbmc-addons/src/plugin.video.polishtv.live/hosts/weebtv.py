# -*- coding: utf-8 -*-
import cookielib, os, string, cookielib, StringIO
import os, time, base64, logging, calendar
import urllib, urllib2, re, sys
import xbmcgui, xbmcplugin, xbmcaddon, xbmc

scriptID = 'plugin.video.polishtv.live'
scriptname = "Polish Live TV"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
#sys.path.append( os.path.join( os.getcwd(), "../" ) )

import pLog, settings

log = pLog.pLog()

mainUrl = 'http://weeb.tv'
#APP_HOSTS = { 1: '46.105.110.156',
#             2: '46.105.112.31' }
#APP_HOST = '46.105.112.31'


class WeebTV:
  def __init__(self):
    log.info('Loading WeebTV')
    self.settings = settings.TVSettings()
  

  def getChannels(self):
      outTab = []
      tabURL = []
      strTab = []
      urlChans = mainUrl + '/channels'
      openURL = urllib.urlopen(urlChans)
      readURL = openURL.read()
      openURL.close()
      match_opt1 = re.compile('<p style="color: green;font-weight:bold;">.+?<span style="color:#ccc;">(.+?)</span></p>').findall(readURL)
      match_opt2 = re.compile('<a href="(.+?)" title=".+?"><img src="(.+?)" alt="(.+?)" height="100" width="100" /></a>').findall(readURL)
      if len(match_opt2) > 0:
          for i in range(len(match_opt2)):
              quality = 'Brak'
              if len(match_opt1) > 0:
                  quality = match_opt1[i]
              link = match_opt2[i][0]
              image = match_opt2[i][1]
              title = match_opt2[i][2]
              #self.addLink('weebtv', title + ' --- [' + quality + ']', image, link)
          #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
          #xbmcplugin.endOfDirectory(int(sys.argv[1]))
              strTab.append(link)
              strTab.append(title)
              strTab.append(image)
              strTab.append(quality)
              outTab.append(strTab)
              strTab = []
      return outTab


  def getChannelNames(self):
    nameTab = []
    origTab = self.getChannels()
    for i in range(len(origTab)):
      value = origTab[i]
      name = value[1]
      nameTab.append(name)
    nameTab.sort()
    return nameTab


  def getChannelNamesAddLink(self):
      origTab = self.getChannels()
      origTab.sort(key=lambda x: x[1])
      for i in range(len(origTab)):
          value = origTab[i]
          url = value[0]
          name = value[1]
          iconimage = value[2]
          quality = value[3]
          self.addLink('weebtv', name + ' --- [' + quality + ']', iconimage, url)
      xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
    
  def getChannelURL(self, key):
      link = ''
      origTab = self.getChannels()
      for i in range(len(origTab)):
          value = origTab[i]
          name = value[1]
          if name == key:
              link = value[0]
              break
      return link
    

  def getChannelIcon(self, key):
    icon = ''
    origTab = self.getChannels()
    for i in range(len(origTab)):
      value = origTab[i]
      name = value[1]
      if key in name:
	icon = value[2]
	break
    return icon


  def videoLink(self, url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    match_src = re.compile('<param name="movie" value="(.+?)" />').findall(link)
    match_chn = re.compile('<param name="flashvars" value="(.+?)" />').findall(link)
    #log.info('src: ' + str(len(match_src)) + ', chn: ' + str(len(match_chn)))
    if len(match_src) == 1 and len(match_chn) == 1:
        channel = str(match_chn[0]).split('=')
        #rtmp = 'rtmp://' + APP_HOST + '/live/' + channel[1] + '/'
        rtmp = 'rtmp://' + self.settings.WeebIP + '/live/' + channel[1] + '/'
        rtmp += ' swfUrl='  + urllib.unquote_plus(str(match_src[0]))
        rtmp += ' pageUrl=' + url
        #rtmp += ' tcUrl=rtmp://' + APP_HOST + '/live/' + channel[1]
        rtmp += ' tcUrl=rtmp://' + self.settings.WeebIP + '/live/' + channel[1]
        rtmp += ' playpath=live'
        rtmp += ' swfVfy=true'
        rtmp += ' live=true'
        #log.info(rtmp)
        return rtmp
      
      
  def login(self, user, password):
    loginUrl = mainUrl + '/account/login/after&go=home'
    try:
      cookiejar = cookielib.LWPCookieJar()
      cookiejar = urllib2.HTTPCookieProcessor(cookiejar) 
      opener = urllib2.build_opener(cookiejar)
      urllib2.install_opener(opener)
      values = {'username': user, 'userpassword': password, 'go': 'home', 'v1': '', 'v2': ''}
      headers = { 'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3' }
      data = urllib.urlencode(values)
      req = urllib2.Request(loginUrl, data, headers)
      response = urllib2.urlopen(req)
      link = response.read()
      response.close()
      web = ''.join(link.splitlines()).replace('\t','').replace('\'','"')
      match=re.compile('Nazwa użytkownika lub hasło są nie poprawne.').findall(web)
      if(len(match) > 0):
	d = xbmcgui.Dialog()
        d.ok('BŁĄD logowania', 'Podana nazwa użytkownika,', 'lub hasło jest niepoprawne.', 'Wpisz poprawnie te dane.')
        return False
      else:
	return True
    except:
      d = xbmcgui.Dialog()
      d.ok('BŁĄD logowania.', 'Upłynął czas limitu rządania', 'Spróbuj ponownie za jakiś czas.')
      return False


  def addLink(self, service, name, iconimage, url):
    u=self.videoLink(url)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)


  def listsMenu(self, table, title):
    value = ''
    if len(table) > 0:
      d = xbmcgui.Dialog()
      choice = d.select(title, table)
      for i in range(len(table)):
        #log.info(table[i])
        if choice == i:
            value = table[i]
    return value


  def listsTable(self, table):
    nTab = []
    for num, val in table.items():
      nTab.append(val)
    return nTab
    

  def handleService(self):
    log.info('Wejście do TV komercyjnej')
    name = str(self.settings.paramName)
    chn = name.replace("+", " ")
    log.info('b: '+chn)
    if chn == 'None':
        try:
            if self.settings.WeebTVEnable == 'true':
                log.info('zalogowany')
                self.getChannelNamesAddLink()
                #self.getChannels()
            else:
                log.info('bez logowania')
                self.getChannelNamesAddLink()
                #self.getChannels()
        except:
            d = xbmcgui.Dialog()
            d.ok('Nie można pobrać kanałów.', 'Przyczyną może być tymczasowa awaria serwisu.', 'Spróbuj ponownie za jakiś czas')        
              
