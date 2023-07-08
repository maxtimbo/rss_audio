import lxml
import requests
import wget

from bs4 import BeautifulSoup
import feedparser

from settings import get_fgLogger

logger = get_fgLogger()

def get_newest_entry(feed_url):
    logger.info(f'Traversing the RSS feed: {feed_url}')
    feed = feedparser.parse(feed_url)
    if feed.status != 200 and feed.status != 302:
        logging.critical(f'Feed URL: {feed_url}')
        logging.critical(f'Return status {feed.status}')

    newest_entry = feed.entries[0]

    logger.info(f'Newest entry: {newest_entry.link}')
    try:
        entry_page = requests.get(newest_entry.link)
    except Exception as exc:
        logger.critical(f'An error occurred while trying to access {newest_entry.link}')
        logger.critical(exc)
        raise

    soup = BeautifulSoup(entry_page.text, 'lxml')
    download_link = soup.find("a", {"title": "Download"})

    logger.info(f"Download link: {download_link['href']}")
    try:
        download_page = requests.get(download_link['href'])
        soup = BeautifulSoup(download_page.text, 'lxml')
        mp3_link = soup.find("div", class_="pod-content").find('a')
        logger.info(f"MP3 download link: {mp3_link['href']}")

        return mp3_link['href']
    except Exception as exc:
        logger.critical(f'An error occurred while trying to access {download_link["href"]}')
        logger.critical(exc)
        raise


def download_audio(mp3_link, download_dir):
    try:
        logger.info(f'Downloading {mp3_link} to {download_dir}')
        local_filename = wget.download(mp3_link, out=str(download_dir))
        logger.info(f'Download successful. Local filename: {local_filename}')
        return local_filename
    except Exception as exc:
        logger.critical(f'An error occurred while trying to download {mp3_link} to {download_dir}')
        logger.critical(exc)
        raise
