import requests
import json
import folium


def makeMap(currentLat,
            currentLon,
            radius=2000,
            types=["chinese_restaurant"],
            maxResultCount=20):
    """makeMap

    Args:
        currentLat (float): latitude
        currentLon (float): longtitude
        radius (float, optional): search radius from 0.0 to 50000.0 . Defaults to 2000.
        types (list, optional): which types resturant to search. Defaults to ["chinese_restaurant"].
        maxResultCount (int, optional): Maxmum number of result will return. Defaults to 20.

    Returns:
        folium.Map: finally interactive map
    """

    searchNearBy = getSearchNearby(currentLat, currentLon, radius, types,
                                   maxResultCount)
    map = folium.Map(
        max_bounds=True,
        control_scale=True,
        location=[currentLat, currentLon],
        zoom_start=15,
        min_zoom=11,
        # boundaries
        min_lat=48,
        max_lat=60,
        max_lon=3,
        min_lon=-9,
        # control_scale=True,
        # attr="Mapbox attribution",
        # tiles='https://api.mapbox.com/v4/mapbox.streets/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiY2hhcmp0eCIsImEiOiJjbHRjeTluZTQwMHFtMmpxdW0yMHhiMmFvIn0.RjWj0q3i9XyxteWdhF3B9Q'
    )
    map = addDetails(searchNearBy, map)
    map = addRatingColor(map)

    return map


def getSearchNearby(currentLat, currentLon, radius, types, maxResultCount):
    """getSearchNearby

    Args:
        currentLat (float): latitude
        currentLon (float): longtitude
        radius (float): search radius
        types (list): types of restaurant
        maxResultCount (int): number of returns

    Returns:
        _type_: _description_
    """
    # which kind of data the API will return
    fieldMask = """places.name,places.types,places.displayName,places.location,places.internationalPhoneNumber,places.formattedAddress,places.rating,places.priceLevel,places.reviews,places.currentOpeningHours,places.primaryTypeDisplayName"""
    apiKey = ''
    # get the apiKey
    with open('key.txt', 'r') as keyFile:
        apiKey = keyFile.read()
    # request
    searchNearBy = requests.post(
        url="https://places.googleapis.com/v1/places:searchNearby",
        data=str({
            "includedTypes": types,
            "excludedPrimaryTypes": ["hotel"],
            "maxResultCount": maxResultCount,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": currentLat,
                        "longitude": currentLon
                    },
                    "radius": radius,
                }
            },
        }),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": apiKey,
            "X-Goog-FieldMask": fieldMask
            # "X-Goog-FieldMask":"*"
        },
    )
    # To facilitate debugging, write it to a file. Files can be read directly during debugging, saving API traffic fees
    with open("test3.json", "w") as outfile:
        outfile.write(json.dumps(searchNearBy.json()))
    return searchNearBy.json()


import branca


def addRatingColor(map):
    """_summary_

    Args:
        map (folium.Map): map

    Returns:
        folium.Map: map has legend
    """

    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="
        position: fixed;
        bottom: 15px;
        right: 5px;
        width: 200px;
        max-width:80%;
        height: 45px;
        z-index:9999;
        font-size:14px;
        background-color: #ffffff;
        ">
            <div>rating</div>
            <div style="width: 100%;">
                <div style="float:left;width:20%;height:10px;background-color:#ff4545"></div>
                <div style="float:left;width:20%;height:10px;background-color:#ffa534"></div>
                <div style="float:left;width:20%;height:10px;background-color:#ffe234"></div>
                <div style="float:left;width:20%;height:10px;background-color:#b7dd29"></div>
                <div style="float:left;width:20%;height:10px;background-color:#57e32c"></div>
            </div>
            <div>
                <div style="float: left;">bad</div>
                <div style="float: right;">good</div>
            </div>

        </div>
    {% endmacro %}
    """
    legend = branca.element.MacroElement()
    legend._template = branca.element.Template(legend_html)

    map.get_root().add_child(legend)
    return map


import folium
from folium import plugins
import math
from datetime import datetime


def addDetails(searchNearBy, map, location):
    """_summary_

    Args:
        searchNearBy (json): Google Maps platform response
        map (folium.Map): map
        location: location
    Returns:
        map: map
    """

    # get the today's weekday
    current_datetime = datetime.now()
    weekday = current_datetime.weekday()

    # add the
    nowAddressIcon = iconSet = plugins.BeautifyIcon(icon='user',
                                                    border_color='dodgerblue',
                                                    text_color='dodgerblue')
    folium.Marker(location, icon=nowAddressIcon).add_to(map)

    ratingColors = ['#ff4545', '#ffa534', '#ffe234', '#b7dd29', '#57e32c']

    typesToIcon = {
        'bakery': 'utensils',
        'bar': 'martini-glass-citrus',
        'barbecue_restaurant': 'utensils',
        'chinese_restaurant': 'bowl-rice',
        'coffee_shop': 'mug-saucer',
        'french_restaurant': 'utensils',
        'greek_restaurant': 'utensils',
        'hamburger_restaurant': 'burger',
        'ice_cream_shop': 'ice-cream',
        'indian_restaurant': 'utensils',
        'italian_restaurant': 'pizza-slice',
        'japanese_restaurant': 'fish',
        'pizza_restaurant': 'pizza-slice',
        'sandwich_shop': 'hotdog',
        'seafood_restaurant': 'fish',
        'steak_house': 'utensils',
        'sushi_restaurant': 'fish',
        'thai_restaurant': 'shrimp',
        'turkish_restaurant': 'shish-kebab',
        'restaurant': 'utensils'
    }
    allcategoryes = set()

    for i, point in enumerate(searchNearBy["places"]):

        icon = ''

        html = """
        <style>

            .details-line {
                border-top-style: solid;
                border-color: lightgray;
                display: flex;
                flex-direction: row;
                justify-content: start;
                align-items: baseline;
            }

            .title-line {
                background-color: dodgerblue;
            }

            .flex-container {
                display: flex;
                align-items: stretch;
                height: 30px;
            }

            .flex-container>i {
                display: flex;
                flex-direction: row;
                justify-content: center;
                align-items: center;
                border-top-style: solid;
                border-color: #eee;
                border-width: 1px;
            }

            .flex-container>div {
                border-top-style: solid;
                border-color: #eee;
                border-width: 1px;
                display: flex;
                flex-direction: row;
                justify-content: start;
                align-items: center;
            }
        </style>
        <div style="height: 400px;width: 300px;overflow-y: auto">
            <div class="title-line">
                <div style="margin-left: 15px;margin-top: 10px;">
                    <span style="color:white;width:80%;line-height:22px;">""" + point[
            'displayName']['text'] + """</span>

                </div>
                <div style="margin:8px 0 0 15px">
                    <span style="font-size: 12px;color:#fff">""" + str(
                point['rating']) + """</span>
                    <span style="font-size: 12px;color:#BCBCBC;">/5.0</span>
                </div>
                """ + ("""
                <div style="margin-left: 15px; color:#fff;font-size: 12px;">
                    <span>Price Level:</span>
                    <span>""" + point['priceLevel'].split('_')[-1] +
                       """</span>
                </div>""" if 'priceLevel' in point.keys() else
                       '') + ("""
                <div style="margin-left: 15px; color:#fff;font-size: 14px;">
                    <span>""" + point['primaryTypeDisplayName']['text'] +
                              """</span>
                </div>""" if 'primaryTypeDisplayName' in point.keys() else
                              '') + """
            </div>

            <div style="width:100%; border-bottom: 1px solid gray">

                <div class="flex-container">
                    <i class="fa-solid fa-phone" style="flex: 0 0 40px;"></i>
                    <div style="flex-grow:8">""" + point[
                                  'formattedAddress'] + """</div>
                </div>
                <div class="flex-container">
                    <i class="fa-solid fa-phone" style="flex: 0 0 40px;"></i>
                    <div style="flex-grow:8">""" + (
                                      point['internationalPhoneNumber']
                                      if 'internationalPhoneNumber'
                                      in point.keys() else '') + """</div>
                </div>
            </div>
            <div>
                <div style="border-bottom: 1px solid #eee;height:30px;line-height:30px">
                    <div style="width: 30%; float:left">Opening Hours</div>""" + (
                                          """<div style="width: 70%; float:left;color:red"></div>"""
                                          if point['currentOpeningHours']
                                          ['openNow'] else '') + """
                </div>
                <div style="width:100%; border-bottom: 1px solid gray;height:30px; line-height:30px">
                    """ + point['currentOpeningHours']['weekdayDescriptions'][
                                              weekday].replace(
                                                  "\u2009", " ").replace(
                                                      "\u2013", "–").replace(
                                                          "\u202f", " ") + """
                </div>
            </div>
            <div>
                <div style="border-bottom: 1px solid #eee;height:30px; line-height:30px;">
                    reviews
                </div>"""

        for j in range(len(point['reviews'])):

            html += """
                <div style="border-bottom: 1px solid #eee; width:270px">
                    <div style="height: 50px">
                        <div style=" margin: 10px 0 0 10px;float:left;height: 40px;">
                            <img width="40px" height="40px"
                                src=\"""" + point['reviews'][j][
                'authorAttribution']['photoUri'] + """\">
                        </div>
                        <div style="margin: 10px 0 0 10px; height:40px;width: 140px ;float:left">
                            <div style="height: 20px;">""" + point['reviews'][
                    j]['authorAttribution']['displayName'] + """</div>
                            <div style="height: 20px;">""" + str(
                        point['reviews'][j]['rating']) + """</div>
                        </div>
                        <div style="margin-top: 30px;width:70px; float:right"> """ + point[
                            'reviews'][j][
                                'relativePublishTimeDescription'] + """</div>

                    </div>
                    """ + '' if 'originalText' not in point['reviews'][j].keys(
                                ) else """
                    <div style=" width: 270px;word-break:break-word;margin:10px 10px 10px 10px ;clear:both">
                        """ + point['reviews'][j]['originalText']['text'] + """
                    </div>""" + """
                </div>
            """

        html += """</div> </div>"""

        for j in point['types']:
            if j in typesToIcon.keys():
                icon = typesToIcon[j]
                break

        category = point['types']
        category.remove('food')
        category.remove('point_of_interest')
        category.remove('establishment')
        allcategoryes = allcategoryes | set(category)

        iconSet = plugins.BeautifyIcon(
            icon=icon,
            text_color=ratingColors[math.ceil(float(point['rating'])) - 1],
            border_color=ratingColors[math.ceil(float(point['rating'])) - 1])

        folium.Marker([
            float(point["location"]["latitude"]),
            float(point["location"]["longitude"])
        ],
                      popup=html,
                      tooltip=point['displayName']['text'],
                      icon=iconSet,
                      tags=category).add_to(map)

    # allcategoryesList = list(allcategoryes)
    # plugins.TagFilterButton(allcategoryesList).add_to(map)

    return map


if __name__ == "__main__":
    makeMap(53.41058, -2.97794)
