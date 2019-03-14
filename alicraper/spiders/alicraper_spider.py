import scrapy
import re
import xml.etree.ElementTree as ET
from alicraper.items import AlicraperItem

class AlicraperSpider(scrapy.Spider):
    name = "alicraper"
    handle_httpstatus_list = [404]
    
    def start_requests(self):
        lista_requests = []
        
        # Getting arguments from command line        
        borrar = getattr(self, 'borrar', None)
        if (borrar is not None) and (borrar == '1'):
                f = open('tracker.csv', 'w')
                f.close()
        debug = getattr(self, 'debug', None)

        # Starting normal or debug mode
        if debug is not None and debug != '1':
            tree = ET.parse('ps_product.xml')
            root = tree.getroot()
            
            for linea in root.iter('column'):
                url = linea.text
                self.crear_requests(url, lista_requests)
        else:
            with open("lista_temp.txt") as f: 
                for url in f:
                    self.crear_requests(url, lista_requests)

        return lista_requests            

    # First HTTP request without numero_imagenes
    def parse(self, response):
        item = AlicraperItem()

        codigo = response.meta["codigo"]
        item['id_producto'] = codigo
        item['precio_original'] = ""
        item['precio_descuento'] = ""
        item['unidades'] = ""
        item['puntuacion'] = ""
        item['votos'] = ""
        item['vendidos'] = ""
        item['disponibilidad'] = "404"
        item['numero_imagenes'] = 0

        if response.status == 404:
            yield item

        else:
            item['nombre_producto'] = response.xpath(
                "//h1[contains(@class, 'product-name')]//text()").extract()

            item['nombre_tienda'] = response.xpath(
                "//*[@class='shop-name']//a/text()").extract()

            item['precio_original'] = self.unir(response.xpath(
                "//span[contains(@id, 'j-sku-price')]//text()").extract())

            item['precio_descuento'] = self.unir(response.xpath(
                "//span[contains(@id, 'j-sku-discount-price')]//text()").extract())
            if len(item['precio_descuento']) < 1:
                item['precio_descuento'] = "SIN DESCUENTO"

            item['unidades'] = response.xpath(
                "//script[contains(@type, 'text/javascript')]/text()").re_first(r'totalAvailQuantity=(\d+);')
            
            item['puntuacion'] = self.convertirDecimal(response.xpath(
                "//span[contains(@itemprop, 'ratingValue')]//text()").extract())

            item['votos'] = response.xpath(
                "//span[contains(@itemprop, 'reviewCount')]//text()").extract()

            vendidos = response.xpath(
                "//span[contains(@id, 'j-order-num')]//text()").extract()
            if len(vendidos) > 0:
                item['vendidos'] = re.sub(r"\D", '', vendidos[0])
            else:
                item['vendidos'] = vendidos

            item['disponibilidad'] = "SI" if (response.xpath(
                "//script[contains(@type, 'text/javascript')]/text()").re_first(r'offline=(.+?);') == "false")  else "NO"

            link_iframe = response.xpath('//iframe/@thesrc').extract()
            
            # If an iframe link is found, parse it, else, set numero_imagenes to 0
            if len(link_iframe) > 0:
                link = link_iframe[0]
                yield scrapy.Request(url='https://'+ link[2:], callback=self.parse_imagen, meta={'item': item})
            else:
                item['numero_imagenes'] = 0
                yield item

    # Iframe HTTP request parsing to get numero_imagenes
    def parse_imagen(self, response):
        item = response.meta['item']
        numero = response.xpath('//input[@id="cb-withPictures-filter"]/following-sibling::em/text()').extract()
        item['numero_imagenes'] = numero
        return item

    # For each Product ID create a scrapy request and add it to a list
    def crear_requests(self, url, lista_requests):
        id_numero = url.strip()
        url_completa = f"https://es.aliexpress.com/item/-/{id_numero}.html"
        request = scrapy.Request(url=url_completa, callback=self.parse, meta={'codigo': id_numero})
        lista_requests.append(request)

    def unir(self, texto):
        result = ''
        for element in texto:
            result += str(element)
        return result

    def convertirDecimal(self, texto):
        result = ''
        for element in texto:
            result += str(element).replace('.',',')
        return result
