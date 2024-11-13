# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals
import difflib
import os
import re
import string
from bs4 import BeautifulSoup
from .SubscenebestUtilities import geturl, get_language_info
from six.moves import html_parser
from six.moves.urllib.request import FancyURLopener
from six.moves.urllib.parse import quote_plus, urlencode
from ..utilities import log
import urllib3
import requests, re
import requests , json, re,random,string,time,warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from six.moves import html_parser
warnings.simplefilter('ignore',InsecureRequestWarning)


HDR= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
      'Upgrade-Insecure-Requests': '1',
      'Content-Type': 'application/x-www-form-urlencoded',
      'Referer': 'https://subscene.best',
      'Connection': 'keep-alive',
      'Accept-Encoding':'gzip, deflate'}
      
s = requests.Session()      
main_url = "https://subscene.best"
debug_pretext = ""
ses = requests.Session()
# Seasons as strings for searching  </div>
# Seasons as strings for searching
seasons = ["Specials", "First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Ninth", "Tenth"]
seasons = seasons + ["Eleventh", "Twelfth", "Thirteenth", "Fourteenth", "Fifteenth", "Sixteenth", "Seventeenth",
                     "Eighteenth", "Nineteenth", "Twentieth"]
seasons = seasons + ["Twenty-first", "Twenty-second", "Twenty-third", "Twenty-fourth", "Twenty-fifth", "Twenty-sixth",
                     "Twenty-seventh", "Twenty-eighth", "Twenty-ninth"]

movie_season_pattern = ("<a href=\"(?P<link>/subscene/[^\"]*)\">(?P<title>[^<]+)\((?P<year>\d{4})\)</a>\s+"
                        "<div class=\"subtle count\">\s*(?P<numsubtitles>\d+\s+subtitles)</div>\s+")

# Don't remove it we need it here
subscenebest_languages = {
    'Chinese BG code': 'Chinese',
    'Brazillian Portuguese': 'Portuguese (Brazil)',
    'Serbian': 'SerbianLatin',
    'Ukranian': 'Ukrainian',
    'Farsi/Persian': 'Persian'
}

def geturl(url):
    log(__name__, " Getting url: %s" % (url))
    try:
        response = urllib.request.urlopen(url)
        content = response.read()
        print(content)
    except:
        log(__name__, " Failed to get url:%s" % (url))
        content = None
    return(content)
    
def getSearchTitle(title, year=None): ## new Add
    url = 'https://subscene.best/search?query=%s' % quote_plus(title)
    #data = geturl(url)
    data = requests.get(url,headers=HDR,verify=False,allow_redirects=True).content
    data = data.decode('utf-8')
    div1 = data.split('<footer>')
    div1.pop(1)
    div1 = str(div1)
    div2 = div1.split('class="search-result"')
    div2.pop(0)
    middle_part = str(div2)
    blocks = middle_part.split('class="title"')
    blocks.pop(0)
    list1 = []
    for block in blocks:
        regx = '''<a href="(.*?)">(.*?)</a>'''
        try:
            matches = re.findall(regx, block)
            name = matches[0][1]
            href = matches[0][0]
            print(("hrefxxx", href))
            print(("yearxx", year))
            href = 'https://subscene.best' + href
            if year and year == '':
              if "/subscene/" in href:
                  return href
            if not year:
              if "/subscene/" in href:
                  return href
            if year and str(year) in name:
                if "/subscene/" in href:
                   print(("href", href))
                   return href
                   

        except:
            break                             
    return 'https://subscene.best/search?query=' + quote_plus(title)

def find_movie(content, title, year):
    url_found = None
    h = html_parser.HTMLParser()
    for matches in re.finditer(movie_season_pattern, content, re.IGNORECASE | re.DOTALL):
        print((tuple(matches.groups())))
        found_title = matches.group('title')
        found_title = html.unescape(found_title) 
        print(("found_title", found_title))  
        log(__name__, "Found movie on search page: %s (%s)" % (found_title, matches.group('year')))
        if found_title.lower().find(title.lower()) > -1:
            if matches.group('year') == year:
                log(__name__, "Matching movie found on search page: %s (%s)" % (found_title, matches.group('year')))
                url_found = matches.group('link')
                print(url_found)
                break
    return url_found


def find_tv_show_season(content, tvshow, season):
    url_found = None
    possible_matches = []
    all_tvshows = []

    season_pattern = "<a href=\"(?P<link>/subscene/[^\"]*)\">(?P<title>[^<]+)</a>\s*"
    for matches in re.finditer(season_pattern, content, re.IGNORECASE | re.DOTALL):
        found_title = matches.group('title')
        #found_title = html.unescape(found_title)
        print(("found_title2", found_title)) 
        log(__name__, "Found tv show season on search page: %s" % found_title)
        url_found = matches.group('link')
                                                                   
    return url_found                                                                     

def getallsubs(content, allowed_languages, filename="", search_string=""):
    soup = BeautifulSoup(content.text, 'html.parser')
    block = soup.find('tbody')
    movies = block.find_all("tr")
    i = 0
    subtitles = []
    for movie in movies:
        #numfiles = 1
        #numfiles = movie.find('td', class_="a3").get_text(strip=True)
        movielink = movie.find('td', class_="a1").a.get("href")
        languagefound = movie.find('td', class_="a1").a.div.span.get_text(strip=True)
        language_info = get_language_info(languagefound)
        print(('language_info', language_info))
        if language_info and language_info['name'] in allowed_languages:
            link = main_url + movielink
            print(('link', link))
            filename = movie.find('td', class_="a1").a.div.find('span', class_="new").get_text(strip=True)
            subtitle_name = str(filename)
            print(('subtitle_name', subtitle_name))
            print(filename)
            rating = '0'
            sync = False
            if filename != "" and filename.lower() == subtitle_name.lower():
                sync = True
            if search_string != "":
                if subtitle_name.lower().find(search_string.lower()) > -1:
                    subtitles.append({'filename': subtitle_name, 'sync': sync, 'link': link,
                                     'language_name': language_info['name'], 'lang': language_info})
                    i = i + 1
                #elif numfiles > 2:
                    #subtitle_name = subtitle_name + ' ' + ("%d files" % int(matches.group('numfiles')))
                    #subtitles.append({'rating': rating, 'filename': subtitle_name, 'sync': sync, 'link': link, 'language_name': language_info['name'], 'lang': language_info, 'comment': comment})
                #i = i + 1
            else:
                subtitles.append({'filename': subtitle_name, 'sync': sync, 'link': link, 'language_name': language_info['name'], 'lang': language_info})
                i = i + 1

    subtitles.sort(key=lambda x: [not x['sync']])
    return subtitles


def prepare_search_string(s):
    s = s.strip()
    s = re.sub(r'\(\d\d\d\d\)$', '', s)  # remove year from title
    
    s = quote_plus(s)
    return s

def search_movie(title, year, languages, filename):
    try:
        title = title.strip()
        search_string = prepare_search_string(title)
        print(("getSearchTitle", getSearchTitle))
        url = getSearchTitle(title, year)#.replace("%2B"," ")
        print(("true url", url))
        content = requests.get(url,headers=HDR,verify=False,allow_redirects=True)
        #print("true url", url)
        #content = geturl(url)
        print(("title", title))
        #print("content", content)
        if content != '':
            _list = getallsubs(content, languages, filename)
            print(("_list", _list))
            return _list
        else:
            return []
    except Exception as error:
        print(("error", error))


def search_tvshow(tvshow, season, episode, languages, filename):
    tvshow = tvshow.strip()
    #print(("tvshow", tvshow))
    search_string = prepare_search_string(tvshow)
    #print(("search_string", search_string))
    search_string = search_string.replace("+"," ")
    print(("search_string", search_string))
    search_string += " - " + seasons[int(season)] + " Season"
    print(("search_string", search_string))

    log(__name__, "Search tvshow = %s" % search_string)
    url = main_url + "/search?query=" + quote_plus(search_string)
    print(("url", url))
    content = requests.get(url,headers=HDR,verify=False,allow_redirects=True).text
    print("content", content)
    if content is not None:
        log(__name__, "Multiple tv show seasons found, searching for the right one ...")
        tv_show_seasonurl = find_tv_show_season(content, tvshow, seasons[int(season)])
        if tv_show_seasonurl is not None:
            log(__name__, "Tv show season found in list, getting subs ...")
            url = main_url + tv_show_seasonurl
            print(("season_url", url))
            content = requests.get(url,headers=HDR,verify=False,allow_redirects=True)
            if content is not None:
                search_string = "s%#02de%#02d" % (int(season), int(episode))
                print(("search_string", search_string))
                return getallsubs(content, languages, filename)


def search_manual(searchstr, languages, filename):
    search_string = prepare_search_string(searchstr)
    url = main_url + "/subtitles/release?q=" + search_string + '&r=true'
    content, response_url = requests.get(url,headers=HDR,verify=False,allow_redirects=True).text

    if content is not None:
        return getallsubs(content, languages, filename)


def search_subtitles(file_original_path, title, tvshow, year, season, episode, set_temp, rar, lang1, lang2, lang3, stack):  # standard input
    log(__name__, "%s Search_subtitles = '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'" %
         (debug_pretext, file_original_path, title, tvshow, year, season, episode, set_temp, rar, lang1, lang2, lang3, stack))
    if lang1 == 'Farsi':
        lang1 = 'Persian'
    if lang2 == 'Farsi':
        lang2 = 'Persian'
    if lang3 == 'Farsi':
        lang3 = 'Persian'
    if tvshow:
        sublist = search_tvshow(tvshow, season, episode, [lang1, lang2, lang3], file_original_path)
    elif title:
        sublist = search_movie(title, year, [lang1, lang2, lang3], file_original_path)
    else:
        try:
          sublist = search_manual(title, [lang1, lang2, lang3], file_original_path)
        except:
            print("error")
    return sublist, "", ""


def download_subtitles (subtitles_list, pos, zip_subs, tmp_sub_dir, sub_folder, session_id):  # standard input
    url = subtitles_list[pos][ "link" ]
    language = subtitles_list[pos][ "language_name" ]
    content = requests.get(url,headers=HDR,verify=False,allow_redirects=True).text
    #content = requests.get(url,headers=HDR,verify=False,allow_redirects=True)
    downloadlink_pattern = '<!--<span><a class="button"\s+href="(.+)">'
    match = re.compile(downloadlink_pattern).findall(content)
    #downloadlink = main_url + download_block
    #print(("downloadlink", url))
    #content = geturl(url)
    #downloadlink_pattern = "<a class=\"button\"  href=\"(?P<match>/download/\d+)"
    #match = re.compile(downloadlink_pattern).findall(content)
    if match:
        downloadlink = match[0]
        print(("downloadlink", downloadlink))
        local_tmp_file = re.split("/file/", downloadlink)[1]
        print(("local_tmp_file", local_tmp_file))
        log(__name__ , "%s Downloadlink: %s " % (debug_pretext, downloadlink))
        viewstate = 0
        previouspage = 0
        subtitleid = 0
        typeid = "zip"
        filmid = 0
        postparams = { '__EVENTTARGET': 's$lc$bcr$downloadLink', '__EVENTARGUMENT': '' , '__VIEWSTATE': viewstate, '__PREVIOUSPAGE': previouspage, 'subtitleId': subtitleid, 'typeId': typeid, 'filmId': filmid}
        #postparams = urllib3.request.urlencode({ '__EVENTTARGET': 's$lc$bcr$downloadLink', '__EVENTARGUMENT': '' , '__VIEWSTATE': viewstate, '__PREVIOUSPAGE': previouspage, 'subtitleId': subtitleid, 'typeId': typeid, 'filmId': filmid})
        #class MyOpener(urllib.FancyURLopener):
            #version = 'User-Agent=Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/115.0'
        #my_urlopener = MyOpener()
        #my_urlopener.addheader('Referer', url)
        log(__name__ , "%s Fetching subtitles using url '%s' with referer header '%s' and post parameters '%s'" % (debug_pretext, downloadlink, url, postparams))
        #response = my_urlopener.open(downloadlink, postparams)
        response = requests.get(downloadlink,data=postparams,headers=HDR,verify=False,allow_redirects=True) 
        local_tmp_file = zip_subs
        try:
            log(__name__ , "%s Saving subtitles to '%s'" % (debug_pretext, local_tmp_file))
            if not os.path.exists(tmp_sub_dir):
                os.makedirs(tmp_sub_dir)
            local_file_handle = open(local_tmp_file, 'wb')
            local_file_handle.write(response.content)
            local_file_handle.close()
            # Check archive type (rar/zip/else) through the file header (rar=Rar!, zip=PK) urllib3.request.urlencode
            myfile = open(local_tmp_file, "rb")
            myfile.seek(0)
            if (myfile.read(1).decode('utf-8') == 'R'):
                typeid = "rar"
                packed = True
                log(__name__ , "Discovered RAR Archive")
            else:
                myfile.seek(0)
                if (myfile.read(1).decode('utf-8') == 'P'):
                    typeid = "zip"
                    packed = True
                    log(__name__ , "Discovered ZIP Archive")
                else:
                    typeid = "srt"
                    packed = False
                    subs_file = local_tmp_file
                    log(__name__ , "Discovered a non-archive file")
            myfile.close()
            log(__name__ , "%s Saving to %s" % (debug_pretext, local_tmp_file))
        except:
            log(__name__ , "%s Failed to save subtitle to %s" % (debug_pretext, local_tmp_file))
        if packed:
            subs_file = typeid
        log(__name__ , "%s Subtitles saved to '%s'" % (debug_pretext, local_tmp_file))
        return packed, language, subs_file  # standard output
