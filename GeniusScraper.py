import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import numpy as np

# Class to scrape the lyrics and other details of the songs from the Genius website
class GeniusScraper:
    # Constructor
    def __init__(self):
        pass
    
    def __create_soup(self, url):
        '''Create a BeautifulSoup object for the given URL and return it.'''
        response = requests.get(url)
        return BeautifulSoup(response.text, 'lxml')
    
    def __scrape_lyrics(self, soup):
        '''Scrape the song from the Genius website and return the lyrics as a string.'''
        #### Lyrics Generation ####
        lyricsblocks = soup.select('body>div#application>main>div:nth-of-type(2)>div#annotation-portal-target>div#lyrics-root-pin-spacer>div#lyrics-root>div[data-lyrics-container="true"]')
        song_lyrics_full = ""
        for block in lyricsblocks:
            selector1 = block.select('a')
            for article in selector1:
                selector2= article.select('span')
                for span in selector2:
                    lyric = span.get_text(separator='\n')
                    song_lyrics_full= song_lyrics_full+"\n"+lyric
        return song_lyrics_full
    

    def __scrape_release_date(self, soup):
        '''Scrape the release date of the song from the Genius website and return the date as a datetime object.'''
        metadataselector = soup.select('body> div#application> main >div.PageGriddesktop-a6v82w-0.SongPageGriddesktop-sc-1px5b71-0.jecoie.SongHeaderdesktop__Container-sc-1effuo1-0> div.SongHeaderdesktop__Right-sc-1effuo1-2.lfjman>div.SongHeaderdesktop__Information-sc-1effuo1-4.ieJVb > div.SongHeaderdesktop__Bottom-sc-1effuo1-3.hEtDoX div.MetadataStats__Container-sc-1t7d8ac-0 > span:nth-child(1) > span')
        try :
            date= metadataselector[0].get_text()
            date_object = datetime.strptime(date, "%b. %d, %Y")
        except:
            date_object = np.nan
        return date_object


    def __scrape_lyrics_views(self, soup):
        '''Scrape the views of the song from the Genius website and return the views as an integer.'''
        views_selector = soup.select('body> div#application> main >div.PageGriddesktop-a6v82w-0.SongPageGriddesktop-sc-1px5b71-0.jecoie.SongHeaderdesktop__Container-sc-1effuo1-0> div.SongHeaderdesktop__Right-sc-1effuo1-2.lfjman>div.SongHeaderdesktop__Information-sc-1effuo1-4.ieJVb > div.SongHeaderdesktop__Bottom-sc-1effuo1-3.hEtDoX div.MetadataStats__Container-sc-1t7d8ac-0 > span:nth-child(3) > span')
        try:
            views = views_selector[0].get_text().split()[0]
            views = self.__parse_string(views)
        except:
            views = np.nan
        return views
    
    def __scrape_artist(self, soup):
        '''Scrape the artist of the song from the Genius website and return the artist as a string.'''
        artist_selector = soup.select('body>div#application > main > div.PageGriddesktop-a6v82w-0.SongPageGriddesktop-sc-1px5b71-0.jecoie.SongHeaderdesktop__Container-sc-1effuo1-0 > div.SongHeaderdesktop__Right-sc-1effuo1-2.lfjman > div.SongHeaderdesktop__Information-sc-1effuo1-4.ieJVb > div.SongHeaderdesktop__SongDetails-sc-1effuo1-5.dhqXbj > div.HeaderArtistAndTracklistdesktop__Container-sc-4vdeb8-0.hjExsS > span > span > a')
        try:
            artist = artist_selector[0].get_text()
        except:
            artist = np.nan
        return artist
    
    def __scrape_tags(self, soup):
        '''Scrape the tags of the song from the Genius website and return the tags as a string.'''
        selector= soup.select("body>div#application > main > div:nth-child(3) > div.PageGriddesktop-a6v82w-0.SongPageGriddesktop-sc-1px5b71-0.jecoie.About__Grid-ut4i9m-0 > div.About__Container-ut4i9m-1.eSiFpi > div.ExpandableContent__Container-sc-1165iv-0.ikywhQ> div.ExpandableContent__Content-sc-1165iv-4 > div > div.SongTags__Container-xixwg3-1.bZsZHM > a")
        tags = ""
        for i in range(3):
            try:
                tags = tags + selector[i].text + ","
            except:
                continue
        tags = tags.strip(",")
        return tags

    def full_scrape_song(self, url):
        '''Scrape full song details from the Genius website and return the attributes.'''
        soup = self.__create_soup(url)
        #### Lyrics Generation ####
        lyrics = self.__scrape_lyrics(soup)

        ###### Release Date Generation ######
        date =  self.__scrape_release_date(soup)

        ###### LyricsViews Generation #######
        views = self.__scrape_lyrics_views(soup)

        ###### Artist Generation #######
        artist = self.__scrape_artist(soup)

        ###### Tags Generation #######
        tags = self.__scrape_tags(soup)

        return lyrics , date, views, artist ,tags
        

    def __parse_string(self,string):
        multiplier = 1
        if string[-1].lower() == 'k':
            multiplier = 1000
        elif string[-1].lower() == 'm':
            multiplier = 1000000
        elif string[-1].lower() == 'b':
            multiplier = 1000000000
        if multiplier != 1:
            return int(float(string[:-1]) * multiplier)
        return int(float(string))


    def scrape_albums(self, albums):
        '''Scrape the albums from the Genius website and return the albums details as a DataFrame.'''
        lyrics_links = []
        songs = []
        album_names=[]
        songlyrics=[]
        dates =[]
        lyric_views=[]
        artists=[]
        tags_list= []
        for album in albums:
            response = requests.get(album)
            soup = BeautifulSoup(response.text, 'lxml')
            tracks= soup.select('body > routable-page >ng-non-bindable > div.column_layout.u-top_margin>div.column_layout-column_span.column_layout-column_span--primary >div.chart_row.chart_row--light_border.chart_row--full_bleed_left.chart_row--align_baseline.chart_row--no_hover>div.chart_row-content')
            album_name = soup.select("body > routable-page>ng-non-bindable > div.header_with_cover_art>div>div>div.header_with_cover_art-primary_info_container>div>h1")
            album_name = album_name[0].text.strip()
            for track in tracks:
                lyricslink=track.a["href"]
                song_name = track.h3.text.strip().split('\n')[0]
                lyrics_links.append(lyricslink)
                songs.append(song_name)
                album_names.append(album_name)
        
        for song in lyrics_links:

            lyrics, date, views,artist,tags = self.full_scrape_song(song)
            songlyrics.append(lyrics)
            dates.append(date)
            lyric_views.append(views)
            artists.append(artist)
            tags_list.append(tags)

        mydict = {"Song_name" : songs , "Lyrics_link" : lyrics_links,"Album" : album_names,"Lyrics" : songlyrics , "Release Date" : dates, "Lyrics Views" : lyric_views,"Tags" : tags_list, "Artist" : artists}
        df = pd.DataFrame(mydict).set_index("Song_name")
        return df



