#!/usr/bin/env python3

# Copyright (C) 2018 Gokberk Yaltirakli
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import requests
import shutil
import socketserver
import time
import glob
import random
import mp3
import tinytag
import img_to_bytes
from bs4 import BeautifulSoup as bs
import sqlite3
import urllib.parse

# music_files = list(glob.glob('music/*.mp3'))
# f = random.choice(music_files)
position = 0
duration = 30
albumimg = f'{os.path.curdir}/albumimg.jpg'

# music_files2 = []
# for root, dirs, files in os.walk("music2"):
#     for file in files:
#         if file.endswith(".mp3"):
#             music_files2.append(os.path.join(root, file))
# f2 = random.choice(music_files2)
# listloaded2 = [f2, ]


def get_img_url(artist, album) -> str:
    url = f'https://www.last.fm/ru/music/{artist.replace(" ", "+")}/{album.replace(" ", "+")}'.rstrip('+')
    print(url)

    resp = requests.get(url).text

    soup = bs(resp, 'html.parser')
    try:
        return soup.find('a', class_ = 'cover-art').find('img').get('src')
    except AttributeError:
        print('[x] Обложка не найдена')


def getTinyTags(path):

    tag = tinytag.TinyTag.get(path)


    return ('''Artist: {}<br>
    Album: {}<br>
    Track: {}<br>
    Genre: {}<br>
    Release Year: {}'''.format(tag.artist,tag.album,tag.title,tag.genre,tag.year))

    # print(
    # "Track Length: %s" % trackInfo.())


globaltag = ''
stream10list = ''

class RadioHandler(socketserver.StreamRequestHandler):
    def handle_mp3_stream(self, filtered):
        global duration
        global f
        global globaltag
        global albumimg
        for f in filtered:
            duration = f['duration']
            jpg = iter(glob.glob(f'{os.path.dirname(f["path"])}/*.jpg') or [])

            src = next(jpg, None)
            if not src:
                try:
                    response = requests.get(get_img_url(f['artist'], f['album']))
                    with open(f"{os.path.dirname(f['path'])}/albumimg.jpg", "wb") as pic:
                        if not response:
                            pic.write(open('icon.png', 'rb'))
                        else:
                            pic.write(response.content)
                        albumimg = f"{os.path.dirname(f['path'])}/albumimg.jpg"
                except:
                    albumimg = f"{os.path.curdir}/albumimg.jpg"
            else:
                # dst = os.path.join(os.curdir, 'albumimg.jpg')
                # shutil.copyfile(src, dst)
                albumimg = src
            globaltag = ('''
                            <li>Artist: {}</li>
                            <li>Album: {}</li>
                            <li>Track: {}</li>
                            <li>Genre: {}</li>
                            <li>Release Year: {}</li>'''.format(f['artist'], f['album'], f['title'],
                                                       f['genre'], f['year']))

            self.wfile.write(b'HTTP/1.1 200 OK\r\nContent-Type: audio/mpeg\r\n\r\n')

            try:
                print(f['path'])
                with open(f['path'], 'rb') as music_file:
                    seconds = 0
                    tstart = time.time()
                    for i, (head, fram) in enumerate(mp3.frames(music_file)):
                        self.wfile.write(fram)

                        # print(head)
                        seconds += mp3.time(head)
                        t = mp3.time(head) * 0.5
                        time.sleep(t)
                tend = time.time()
                time.sleep(seconds - (tend - tstart))
            except ConnectionAbortedError:
                print("Коннект аборт")
            except mp3.MP3Error:
                print('bad frame-header', f['path'])
                tend = time.time()
                try:
                    time.sleep(seconds - (tend - tstart))
                except:
                    pass


    def handle(self):
        global f
        global globaltag
        global stream10list
        global position
        global duration
        global albumimg

        content = f'''
        <!doctype html>
        <html>
        <head>   
        <link href="main.css" rel="stylesheet" type="text/css">
        <link rel="stylesheet" href="http://fonts.googleapis.com/css?family=Oswald:400,300" type="text/css">
        <meta charset=utf-8>
        <meta http-equiv="refresh" content="{duration}" >
        
        </head>
        <div id="wrapper">
        <header>
	        <a href="/"><img src="" alt=""></a>
	        <form name="search" action="#" method="get">
                <input type="text" name="q" placeholder="Search"><button type="submit">GO</button>
            </form>
        </header>
        <nav>
        	<ul class="top-menu">
                <li class="active">HOME</li>
                <li> <a href="/stream">STREAM</a></li>
	        </ul>
        </nav>
		<div id="heading"><h1>STREAMING MP3</h1></div>
		<aside>
            <nav>
                <ul class="aside-menu">
                    {globaltag}
                </ul>
            </nav>
            <h2>Now Playing</h2>
            <p><img src="/albumimg.jpg" alt="Обложка" width="230"></p>
        </aside>
        <section >
        <figure>
            <img src="/albumimg.jpg" width="320" alt="Обложка">
        </figure>
        <figure>
                <img src="" width="320" alt="Обложка">
        </figure>
        
    
        <blockquote>
            <p>
                {stream10list}
            </p>
            <cite><a href='/stream'>Stream</a></cite>
        </blockquote>
            </section>


                </div>
        <footer>
        <div id="footer">
            <div id="twitter">
                <div id="contacts">
                    <h3>Контакты</h3>
                    <time datetime=""2012-10-23""><a href="#">@2022</a></time>
                    <p>
                        https://github.com/kyavichus</br>
                        kyavichus@netsysadm.cf
                    </p>
                </div>
            </div> 
            <div id="sitemap">
            	<h3>SITEMAP</h3>
                <div>
                    <a href="/">Home</a>
                </div>
                <div>
                    <a href="/stream/">Stream</a>
                </div>
            </div>
            <div id="social">
            	<h3>SOCIAL NETWORKS</h3>
                <a href="http://twitter.com/" class="social-icon twitter"></a>
                <a href="http://facebook.com/" class="social-icon facebook"></a>
                <a href="http://plus.google.com/" class="social-icon google-plus"></a>
                <a href="http://vimeo.com/" class="social-icon-small vimeo"></a>
                <a href="http://youtube.com/" class="social-icon-small youtube"></a>
                <a href="http://flickr.com/" class="social-icon-small flickr"></a>
                <a href="http://instagram.com/" class="social-icon-small instagram"></a>
                <a href="/rss/" class="social-icon-small rss"></a>
            </div>
            <div id="footer-logo">
            <a href="/"><img src="" alt="Stream logo"></a>
	        <p>Copyright © 2022 netsysadm. <a href="https://github.com/kyavichus">Github</a></p>
            </div>
	    </div>
        </footer>
        </html>
        '''.encode('utf-8')


        station = self.rfile.readline().split(b' ')[1]
        if self.client_address[0] != '127.0.0.1':
            print('Connection from {}'.format(self.client_address[0]))
        if station not in (b'/favicon.ico', b'/albumimg.jpg', b'/main.css'):
            print('They want to play {}'.format(station))

        conn = sqlite3.connect('mp3base.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        if b'/111' in station:
            if b'genre=' in station:
                genre = station.decode().split('genre=')[1].replace('%20', ' ')
                select = f"SELECT artist,album,title,genre,year,duration, path " \
                         f"FROM muzlo WHERE genre like '%{genre}%' ORDER BY RANDOM();"
                cur.execute(select)
                filtered = cur.fetchmany(100)
                self.handle_mp3_stream(filtered)

            elif b'?' in station:
                query = station.split(b'?')[1].decode().replace('%20', ' ')
                query = urllib.parse.unquote(query)
                print(query)
                select = f"SELECT artist,album,title,genre,year,duration, path " \
                         f"FROM muzlo WHERE path LIKE '%{query}%' ORDER BY RANDOM();"
                cur.execute(select)
                filtered = cur.fetchmany(100)
                self.handle_mp3_stream(filtered)


            while True:
                cur.execute(f"SELECT artist,album,title,genre,year,duration, path "
                            f"FROM muzlo ORDER BY RANDOM() limit 100;")
                filtered = cur.fetchmany(100)
                self.handle_mp3_stream(filtered)


        elif station==b'/stream':

            while True:



                self.wfile.write(b'HTTP/1.1 200 OK\r\nContent-Type: audio/mpeg\r\n\r\n')
                cur.execute(f"SELECT artist,album,title,genre,year,duration, path "
                            f"FROM muzlo ORDER BY RANDOM() limit 10;")
                filtered = cur.fetchall()
                for i in [f"{i['artist']} - {i['title']}" for i in filtered]:
                    stream10list += i + '</br>'
                self.handle_mp3_stream(filtered)


        elif station == b'/favicon.ico':

            self.wfile.write(b'HTTP/1.1 200 OK\r\nContent-Type: image/x-icon\r\n\r\n')
            self.wfile.write(img_to_bytes.image_to_byte_array('icon.png'))

        elif station == b'/albumimg.jpg':
            self.wfile.write(b'HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n')
            self.wfile.write(img_to_bytes.image_to_byte_array(albumimg))

        elif station.endswith(b'.png') or station.endswith(b'.jpg') or station.endswith(b'.png'):
            self.wfile.write(b'HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n')
            self.wfile.write(img_to_bytes.image_to_byte_array(os.path.realpath(os.curdir+station.decode())))



        elif station.endswith(b'.css'):
            self.wfile.write(b'HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n')
            self.wfile.write(open('main.css', 'r').read().encode())

        else:
            self.wfile.write(b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
            self.wfile.write(content)





class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == '__main__':
    HOST, PORT = "0.0.0.0", 1234

    ThreadedTCPServer.allow_reuse_address = True
    ThreadedTCPServer.timeout=5
    server = ThreadedTCPServer((HOST, PORT), RadioHandler)


    server.serve_forever()
