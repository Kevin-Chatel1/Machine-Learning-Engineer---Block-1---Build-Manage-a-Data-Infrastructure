# Importation des librairies
import os
import re
import requests
import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup

# Fonction pour extraire les coordonnées géographiques d'un hôtel à partir de son URL sur Booking.com
def get_lat_lon_from_booking(url):
    response = requests.get(url) # Effectue une requête HTTP pour obtenir le contenu de la page
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser') # Parse le contenu HTML de la réponse

    script_tags = soup.find_all('script') # Trouve tous les éléments <script> dans le document HTML
    for script in script_tags:
        if 'latitude' in script.text and 'longitude' in script.text: # Cherche les scripts contenant des données de latitude et longitude
            lat_lon_match = re.search(r'latitude":([0-9.-]+),"longitude":([0-9.-]+)', script.text) # Extrait les valeurs à l'aide d'une expression régulière
            if lat_lon_match:
                latitude = lat_lon_match.group(1)
                longitude = lat_lon_match.group(2)
                return latitude, longitude

    return None, None
# Définition d'un Spider Scrapy pour l'extraction des données des hôtels sur Booking.com
class BookingSpider(scrapy.Spider):
    name = 'booking'
    allowed_domains = ['booking.com']
    start_urls = [ # URLs pour les recherches initiales sur Booking.com
        'https://www.booking.com/searchresults.html?ss=Mont+Saint+Michel',
        'https://www.booking.com/searchresults.html?ss=St+Malo',
        'https://www.booking.com/searchresults.html?ss=Bayeux',
        'https://www.booking.com/searchresults.html?ss=Le+Havre',
        'https://www.booking.com/searchresults.html?ss=Rouen',
        'https://www.booking.com/searchresults.html?ss=Paris',
        'https://www.booking.com/searchresults.html?ss=Amiens',
        'https://www.booking.com/searchresults.html?ss=Lille',
        'https://www.booking.com/searchresults.html?ss=Strasbourg',
        'https://www.booking.com/searchresults.html?ss=Chateau+du+Haut+Koenigsbourg',
        'https://www.booking.com/searchresults.html?ss=Colmar',
        'https://www.booking.com/searchresults.html?ss=Eguisheim',
        'https://www.booking.com/searchresults.html?ss=Besancon',
        'https://www.booking.com/searchresults.html?ss=Dijon',
        'https://www.booking.com/searchresults.html?ss=Annecy',
        'https://www.booking.com/searchresults.html?ss=Grenoble',
        'https://www.booking.com/searchresults.html?ss=Lyon',
        'https://www.booking.com/searchresults.html?ss=Gorges+du+Verdon',
        'https://www.booking.com/searchresults.html?ss=Bormes+les+Mimosas',
        'https://www.booking.com/searchresults.html?ss=Cassis',
        'https://www.booking.com/searchresults.html?ss=Marseille',
        'https://www.booking.com/searchresults.html?ss=Aix+en+Provence',
        'https://www.booking.com/searchresults.html?ss=Avignon',
        'https://www.booking.com/searchresults.html?ss=Uzes',
        'https://www.booking.com/searchresults.html?ss=Nimes',
        'https://www.booking.com/searchresults.html?ss=Aigues+Mortes',
        'https://www.booking.com/searchresults.html?ss=Saintes+Maries+de+la+mer',
        'https://www.booking.com/searchresults.html?ss=Collioure',
        'https://www.booking.com/searchresults.html?ss=Carcassonne',
        'https://www.booking.com/searchresults.html?ss=Ariege',
        'https://www.booking.com/searchresults.html?ss=Toulouse',
        'https://www.booking.com/searchresults.html?ss=Montauban',
        'https://www.booking.com/searchresults.html?ss=Biarritz',
        'https://www.booking.com/searchresults.html?ss=Bayonne',
        'https://www.booking.com/searchresults.html?ss=La+Rochelle'
    ]
    # Configuration pour simuler un navigateur et gérer la fréquence des requêtes
    custom_settings = { 
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        'AUTOTHROTTLE_ENABLED': True,
        'HTTPCACHE_ENABLED': True
    }
    # Parse les données de chaque hôtel trouvées dans les résultats de recherche
    def parse(self, response):
        city_name = response.url.split('ss=')[-1].replace('+', ' ')

        for hotel in response.xpath("//div[@data-testid='property-card']"):
            hotel_name = hotel.xpath(".//div[@data-testid='title']/text()").get()
            hotel_url = hotel.xpath(".//a[@data-testid='title-link']/@href").get()
            hotel_score = hotel.xpath(".//div[@data-testid='review-score']//div[@class='a3b8729ab1 d86cee9b25']/text()").get()
            hotel_description = hotel.xpath(".//div[@class='abf093bdfe']/text()").get()

            full_hotel_url = response.urljoin(hotel_url) # Construit l'URL complète de la page de l'hôtel

            latitude, longitude = get_lat_lon_from_booking(full_hotel_url)  # Obtient les coordonnées géographiques de l'hôtel

            # Rend les données extraites disponibles pour le traitement ou la sauvegarde
            yield {
                'City': city_name,
                'Hotel Name': hotel_name,
                'Hotel URL': full_hotel_url,
                'Score': hotel_score,
                'Description': hotel_description,
                'Latitude': latitude,
                'Longitude': longitude,
            }
# Configuration et démarrage du processus de crawling
process = CrawlerProcess(settings={
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/97.0.4692.99 Safari/537.36',
    'FEEDS': {
        'hotels.json': {'format': 'json'},
    },
})

process.crawl(BookingSpider)
process.start()
