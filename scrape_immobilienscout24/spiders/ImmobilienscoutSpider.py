# -*- coding: utf-8 -*-
import scrapy
import sqlite3
import re
from pathlib import Path

from scrapy import signals
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.selector import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrape_immobilienscout24.items import ImmobilienscoutItem

from mailer.send_mail import send_email


class ImmobilienSpider(scrapy.Spider):
    name = 'ImmobilienSpider'

    start_urls = [
        'https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Umkreissuche/D_fcsseldorf/-/-220434/2375031/-/-/10/2,00-/50,00-/EURO-750,00-1200,00/-/-/-/-/-/-/true?enteredFrom=result_list',
        'https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Umkreissuche/Essen/-/-209694/2384810/-/-/10/2,00-/50,00-/EURO-750,00-1200,00/-/-/-/-/-/-/true?enteredFrom=result_list',
        'https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Umkreissuche/D_fcsseldorf/-/-220388/2381490/-/-/5/2,00-/50,00-/EURO-750,00-1200,00/-/-/-/-/-/-/true?enteredFrom=result_list',
        'https://www.immobilienscout24.de/Suche/S-T/Haus-Miete/Umkreissuche/D_fcsseldorf/-/-220434/2375031/-/-/10/2,00-/60,00-/EURO-750,00-1200,00?enteredFrom=result_list',
        'https://www.immobilienscout24.de/Suche/S-T/Haus-Miete/Umkreissuche/Essen/-/-209694/2384810/-/-/10/2,00-/70,00-/EURO-750,00-1200,00?enteredFrom=result_list',
        'https://www.immobilienscout24.de/Suche/S-T/Haus-Miete/Umkreissuche/D_fcsseldorf/-/-220388/2381490/-/-/5/2,00-/60,00-/EURO-750,00-1200,00?enteredFrom=result_list']

    allowed_domains = ['www.immobilienscout24.de']

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def start_requests(self):

        # Loop over all the start urls.
        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse_response, meta={'cookiejar': i})

    def is_property_page(self, response):
        """" This function will check if the current page is a property page """

        if Selector(response=response).xpath(
                '//div[@class="is24-ex-details"]//div[contains(@class,"criteriagroup")]//dl[dt[contains(text(),"Kaltmiete")]]//dd/text()').extract():
            # There is a field in the table called Kaltmiete!
            return True

        # apperently not a property page
        return False

    def extract_table_parameter(self, response, name, is_number=False, is_float=False):
        """ This function extracts parameters from the tables on a immobilienscout24.de property page.
        The name is the value in the first column of the table, and the value in the second column will be extracted and returned (as a list)
        """

        # Extract the value from the second column where the first column has value 'name'
        parameter = self.extract_text_xpath(response,
                                            '//div[@class="is24-ex-details"]//div[contains(@class,"criteriagroup")]//dl[dt[contains(text(),"' + name + '")]]//dd/text()')

        if not parameter:
            return None

        if is_number:
            # Only keep the number until the first letter (case-insensitive)
            parameter = re.sub('([^0-9\.])([a-zA-Z]+.*)', '', parameter)  # Remove the m2 or m3 from the string
            parameter = re.sub('\.', '', parameter)  # Remove the possible thousand seperator point
            parameter = re.sub(r'[^\x00-\x7F]', '', parameter)  # remove unicode characters
            # It could be that instead of a number a dash is given or nothing at all... handle this.
            if parameter == '-' or parameter.strip() == '':
                # There was no value given..
                parameter = None
            else:
                # Convert from string to int
                if is_float:
                    parameter = float(parameter.replace(',', '.'))
                else:
                    parameter = int(parameter)

        return parameter

    def extract_text_xpath(self, response, xpath):

        text = Selector(response=response).xpath(xpath).extract()
        # Return None if xpath does not resolve to anything
        if not text:
            return None

        # Only take the first value non empty value
        for value in text:
            if value and value.strip() is not '':
                break
        text = value

        # Strip all the leading and trailing whitespace (including \n\r\t)
        text = text.strip()

        return text

    def parse_response(self, response):

        # First check if it is a property page
        if self.is_property_page(response):
            # Now it should be a page containing a property!

            pets = self.extract_table_parameter(response, 'Haustiere', False)
            # Filter out the properties that do not allow pets
            if pets == 'Nein':
                # Skip this property!
                return

            total_price = self.extract_table_parameter(response, 'Gesamtmiete', True, is_float=True)
            # Filter on total price
            if total_price > 1300:
                # Skip this property!
                return
            property_id = int(self.extract_text_xpath(response,
                                                      '//div[@id="is24-content"]//div//div[@class="grid"]//ul//li//span[contains(text(),"Scout-ID")]/text()').split(
                ':')[1].strip())
            # Extract the data
            bare_price = self.extract_table_parameter(response, 'Kaltmiete', True, is_float=True)
            additional_costs = self.extract_table_parameter(response, 'Nebenkosten', True, is_float=True)
            build_year = self.extract_table_parameter(response, 'Baujahr', True)
            zip_and_city = self.extract_text_xpath(response,
                                                   '//h4//div[@class="address-block"]//div//span[@class="zip-region-and-country"]/text()').replace(
                ';', ',')
            zipcode = zip_and_city[:5].strip()
            address = self.extract_text_xpath(response,
                                              '//h4//div[@class="address-block"]//div[span[@class="zip-region-and-country"]]/text()').split(
                ',')[0].strip()
            city_and_neighborhood = zip_and_city[5:].split(',')
            city = city_and_neighborhood[0].strip()
            neighborhood = city_and_neighborhood[1].strip() if len(city_and_neighborhood) > 1 else None
            building_type = self.extract_table_parameter(response, 'Wohnungstyp', False)
            if building_type is None:
                building_type = self.extract_table_parameter(response, 'Haustyp', False)
            living_area = self.extract_table_parameter(response, 'Wohnfläche ca.', True, is_float=True)
            lot_size = self.extract_table_parameter(response, 'Grundstücksfläche ca.', True, is_float=True)
            if lot_size is None:
                lot_size = self.extract_table_parameter(response, 'Nutzfläche ca.', True, is_float=True)
            rooms = self.extract_table_parameter(response, 'Zimmer', True, is_float=True)
            img_url = self.extract_text_xpath(response,
                                              '//div[@id="gallery-container"]/div[@id="is24-slider-gallery"]/div[@class="sp-slides"]/div/img/@src')
            title = self.extract_text_xpath(response, '//meta[@property="og:title"]/@content')

            # Create an item
            item = ItemLoader(item=ImmobilienscoutItem(), response=response)
            item.default_output_processor = TakeFirst()

            # Add all the values to the list
            item.add_value('property_id', property_id)
            item.add_value('bare_price', bare_price)
            item.add_value('additional_costs', additional_costs)
            item.add_value('total_price', total_price)
            item.add_value('build_year', build_year)
            item.add_value('zipcode', zipcode)
            item.add_value('address', address)
            item.add_value('city', city)
            item.add_value('neighborhood', neighborhood if neighborhood else "")
            item.add_value('building_type', building_type if building_type else "")
            item.add_value('living_area', living_area)
            item.add_value('lot_size', lot_size)
            item.add_value('rooms', rooms)
            item.add_value('pets', pets)
            item.add_value('url', response.url)
            item.add_value('img_url', img_url)
            item.add_value('title', title)

            yield item.load_item()

        else:
            # Not a property page, only extract links from non property pages

            # Check if we are on a page with a property-list div
            restrict_xpaths = ['//a[@data-is24-qa="paging_bottom_next"]',
                               '//a[@class="result-list-entry__brand-title-container"]']

            # Give a list of regular expressions to ignore in links to be extracted
            deny = []

            # Extract the links on the page
            links = LxmlLinkExtractor(deny=deny, allow_domains=self.allowed_domains, unique=True,
                                      restrict_xpaths=restrict_xpaths).extract_links(response)

            # Process each link
            for link in links:
                # add it to the response or so?? dont know why but every example has it..
                url = response.urljoin(link.url)

                # And call this function again for each link found!
                yield scrapy.Request(url=url, callback=self.parse_response)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ImmobilienSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        # Here do the stuff when done!

        # Check if there are new appartments
        # If so, make a nice email and send it
        spider.logger.info('Done scraping!')
        spider.logger.info('Check if there are new apartments')

        connection = sqlite3.connect(str(Path('results', 'db.sqlite3')))
        cursor = connection.cursor()

        cursor.execute("""SELECT title, total_price, living_area, city, neighborhood, url, img_url, property_id, building_type, lot_size FROM properties 
                                                    WHERE 
                                                        sent_in_email=0
                                                    ORDER BY date(timestamp) DESC;
                               """)
        results = cursor.fetchall()

        cursor.execute("""SELECT title, total_price, living_area, city, neighborhood, url, img_url, property_id, building_type, lot_size FROM properties 
                                                    WHERE 
                                                        sent_in_email=1
                                                    AND 
                                                        date(timestamp) > date('now', '-7 days')
                                                    ORDER BY date(timestamp) DESC;
                               """)
        results_last_7_days = cursor.fetchall()

        if not results:
            spider.logger.info('No new apartments to send')
            return

        # There are new apartments, send the email
        send_email("Immobilienscout24 apartment update.", results, results_last_7_days)

        # Update the sent_in_email fields
        property_ids = [str(result[7]) for result in results]
        cursor.execute("""  UPDATE properties
                                SET sent_in_email = 1
                                WHERE 
                                    property_id in (
                        """ + ",".join(property_ids) + ");")
        connection.commit()
        connection.close()
