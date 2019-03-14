# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AlicraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    id_producto = scrapy.Field()
    nombre_producto = scrapy.Field()
    nombre_tienda = scrapy.Field()
    precio_original = scrapy.Field()
    precio_descuento = scrapy.Field()
    unidades = scrapy.Field()
    puntuacion = scrapy.Field()
    votos = scrapy.Field()
    vendidos = scrapy.Field()
    disponibilidad = scrapy.Field()
    numero_imagenes = scrapy.Field()
