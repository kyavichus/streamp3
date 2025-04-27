# from mutagen.easyid3 import EasyID3
#
# audio = EasyID3("music/Korol_i_SHut_-_Ta_chto_smotrit_iz_pruda_48646404.mp3")
# print(audio.keys)
import os
import sqlite3
from tinytag import TinyTag
from tinytag.tinytag import TinyTagException

music_files2 = []
for root, dirs, files in os.walk("/srv/dev-disk-by-uuid-fa403ca7-7f99-4ba0-a7d7-9dda23076e1d/dl/complete"):
    for file in files:
        if file.endswith(".mp3"):
            music_files2.append(os.path.join(root, file))

conn = sqlite3.connect('torrentmp3base.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS muzlo(
   id INTEGER PRIMARY KEY autoincrement,
   path TEXT,
   artist TEXT,
   album TEXT,
   title TEXT,
   year INT,
   bitrate INT,
   duration TEXT,
   genre TEXT);
""")

conn.commit()

cur.execute("SELECT id FROM muzlo ORDER BY id DESC limit 1")
try:
    start_i = cur.fetchone()[0]
except:
    start_i = 1

for i, song in enumerate(music_files2, start_i+1):
    try:
        tags = TinyTag.get(song, encoding='cp1251')
        
        song_exec = (i, song, tags.artist, tags.album, tags.title, tags.year, tags.bitrate, tags.duration, tags.genre)
        if i%1000==0:
            print(i, song, tags.artist, tags.album, tags.title, tags.year, tags.bitrate, tags.duration, tags.genre)
        cur.execute("INSERT INTO muzlo VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", song_exec)
    
    except TinyTagException:
        print(song)

conn.commit()

