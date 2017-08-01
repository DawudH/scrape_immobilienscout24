# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exporters import JsonItemExporter
from scrapy import log
import sqlite3
from pathlib import Path

class ScrapeImmobilienscout24Pipeline(object):
    def process_item(self, item, spider):
        return item


class ImmobilienscoutPipeline(object):
    def __init__(self):
        self.file = open("results.json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class SQLite3Pipeline(object):
    def __init__(self):
        self.connection = sqlite3.connect(str(Path('results', 'db.sqlite3')))
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS
                                   properties (
                                       id INTEGER PRIMARY KEY NOT NULL, 
                                       title TEXT, 
                                       bare_price REAL, 
                                       additional_costs REAL, 
                                       total_price REAL, 
                                       build_year INTEGER, 
                                       zipcode INTEGER, 
                                       address TEXT, 
                                       city TEXT, 
                                       neighborhood TEXT, 
                                       building_type TEXT, 
                                       property_id INTEGER NOT NULL, 
                                       living_area REAL, 
                                       lot_size REAL, 
                                       rooms REAL, 
                                       pets TEXT, 
                                       url TEXT NOT NULL, 
                                       img_url TEXT ,
                                       sent_in_email INTEGER NOT NULL,
                                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
                                   );
                            """
                            )

    # Take the item and put it in database - do not allow duplicates
    def process_item(self, item, spider):
        self.cursor.execute("""SELECT * FROM properties 
                                    WHERE 
                                        property_id=? 
                            """, (item['property_id'],))
        result = self.cursor.fetchone()
        if result:
            log.msg("Item already in database: %s" % item, level=log.INFO)
        else:
            keys = []
            values = []
            for key, value in item.items():
                keys.append(key)
                values.append(value)

            query = "INSERT INTO properties ( " + \
                    ",".join(keys + ['sent_in_email']) + \
                    ") VALUES ( " + ",".join([' ?']*(len(values)+1)) + \
                    " );"
            self.cursor.execute(query, values + [0])
            self.connection.commit()

            log.msg("Item stored : " % item, level=log.DEBUG)
        return item

    def __del__(self):
        self.connection.close()

    def handle_error(self, e):
        log.err(e)

