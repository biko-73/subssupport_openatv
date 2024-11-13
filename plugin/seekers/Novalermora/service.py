# -*- coding: UTF-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals

import sys
import difflib
import requests
import json
import re
import random
import string
import time
import warnings
import os
import os.path
import calendar
from ..utilities import languageTranslate, log, getFileSize
from ..seeker import SubtitlesDownloadError, SubtitlesErrors





headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/115.0'}
       

main_url = "http://subs.ath.cx"
debug_pretext = "subs.ath.cx"

def get_rating(downloads):
Refactor this function to reduce its Cognitive Complexity from 18 to the 15 allowed.

    rating = int(downloads)
    
if (rating < 50):
        rating = 1
    
elif (rating >= 50 
and rating < 100):
        rating = 2
    
elif (rating >= 100 
and rating < 150):
        rating = 3
    
elif (rating >= 150 
and rating < 200):
        rating = 4
    
elif (rating >= 200 
and rating < 250):
        rating = 5
    
elif (rating >= 250 
and rating < 300):
        rating = 6
    
elif (rating >= 300 
and rating < 350):
        rating = 7
    
elif (rating >= 350 
and rating < 400):
        rating = 8
    
elif (rating >= 400 
and rating < 450):
        rating = 9
    
elif (rating >= 450):
        rating = 10
    return rating

def search_subtitles(file_original_path, title, tvshow, year, season, episode, set_temp, rar, lang1, lang2, lang3, stack): #standard input
    subtitles_list = []
    msg = ""
    title = str(title).replace(':', '').replace(',', '').replace("'", "").replace("&", "and").replace("!", "").replace("?", "").replace("- ", "").replace(" III", " 3").replace(" II", " 2").title()
    if len(tvshow) == 0 and year: # Movie
        searchstring = "%s (%s)" % (title, year)
    elif len(tvshow) > 0 and title == tvshow: # Movie not in Library
        searchstring = "%s (%#02d%#02d)" % (tvshow, int(season), int(episode))
    elif len(tvshow) > 0: # TVShow
        searchstring = "%s S%#02dE%#02d" % (tvshow, int(season), int(episode))
    else:
        searchstring = title
    log(__name__, "%s Search string = %s" % (debug_pretext, searchstring))
    get_subtitles_list(title, searchstring, "ar", "Arabic", subtitles_list)
    return subtitles_list, "", msg #standard output


def download_subtitles(subtitles_list, pos, zip_subs, tmp_sub_dir, sub_folder, session_id): #standard input
    language = subtitles_list[pos]["language_name"]
    id = subtitles_list[pos]["id"]
    downloadlink = 'http://subs.ath.cx/subtitles/%s' % (id)
    if downloadlink:
        log(__name__ , "%s Downloadlink: %s " % (debug_pretext, downloadlink))
        viewstate = 0
        previouspage = 0
        subtitleid = 0
        typeid = "zip"
        filmid = 0
        postparams = { '__EVENTTARGET': 's$lc$bcr$downloadLink', '__EVENTARGUMENT': '' , '__VIEWSTATE': viewstate, '__PREVIOUSPAGE': previouspage, 'subtitleId': subtitleid, 'typeId': typeid, 'filmId': filmid}
        log(__name__ , "%s Fetching subtitles using url with referer header '%s' and post parameters '%s'" % (debug_pretext, downloadlink, postparams))
        response = requests.get(downloadlink,data=postparams,verify=False,allow_redirects=True) 
        #response = urllib2.request.urlopen(req)
        local_tmp_file = zip_subs
        try:
            log(__name__ , "%s Saving subtitles to '%s'" % (debug_pretext, local_tmp_file))
            if not os.path.exists(tmp_sub_dir):
                os.makedirs(tmp_sub_dir)
            local_file_handle = open(local_tmp_file, 'wb')
            local_file_handle.write(response.content)
            local_file_handle.close()
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

def get_subtitles_list(title, searchstring, languageshort, languagelong, subtitles_list):
    url = '%s/subtitles' % (main_url) 
    title = title.strip()
    d = title.replace('+', '.')
    try:
        log(__name__, "%s Getting url: %s" % (debug_pretext, url))
        content = requests.get(url,verify=False,allow_redirects=True).text
    except:
        pass
        log(__name__, "%s Failed to get url:%s" % (debug_pretext, url))
        return
    try:
        log( __name__ ,"%s Getting '%s' subs ..." % (debug_pretext, languageshort))
        subtitles = re.compile(r'(<td><a href.+?">'+d+'.+?</a></td>)', re.IGNORECASE).findall(content)                     
    except:
        log( __name__ ,"%s Failed to get subtitles" % (debug_pretext))
        return
    for subtitle in subtitles:
        try:
            filename = re.compile('<td><a href=".+?">(.+?)</a></td>').findall(subtitle)[0]
            filename = filename.strip().replace('.srt', '')
            id = re.compile('href="(.+?)"').findall(subtitle)[0]
            if not (filename == 'Εργαστήρι Υποτίτλων' or filename == 'subs4series'):
                log( __name__ ,"%s Subtitles found: %s (id = %s)" % (debug_pretext, filename, id))
                subtitles_list.append({'no_files': 1, 'filename': filename, 'sync': True, 'id' : id, 'language_flag': 'flags/' + languageshort + '.gif', 'language_name': languagelong})
        except:
            pass
    return
