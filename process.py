import json
from xml.dom import minidom
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


detail_titles = {
    "Calendar icon": "Registration",
    "Car icon": "Type",
    "Road icon": "Milage",
    "Gas station icon": "Fuel",
    "Transmission icon": "Transmission",
    "Vehicle power icon": "Power",
    "Drive type icon": "Drive",
    "Consumption icon": "Consumption"
}


def extract_info(html_text):
    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_text, 'html.parser')
    # Initialize XML root element
    root = ET.Element("VehicleListing")
    # Extract Vehicle Title
    title_tag = soup.find("h1", {"class": "chakra-text"})
    if title_tag:
        ET.SubElement(root, "Title").text = title_tag.text
    # Extract Price
    price_tag = soup.find("p", {"class": "chakra-text css-11u1yiy"})
    if price_tag:
        ET.SubElement(root, "Price").text = price_tag.text
    # Extract Offerer
    offerer_tag = soup.find("p", {"class": "chakra-text css-0"})
    if offerer_tag:
        ET.SubElement(root, "Offerer").text = offerer_tag.text
    # Extract Location
    location_tag = soup.find('a', {'href': '#seller-map'})
    if location_tag:
        ET.SubElement(root, "Location").text = location_tag.text
    # Extract Vehicle Details
    details_elem = ET.SubElement(root, "Details")
    for detail_div in soup.find_all('div', class_='chakra-stack'):
        detail_tag = detail_div.find('p')
        icon_tag = detail_div.find('svg')
        icon_title = icon_tag.find("title").text if icon_tag else None
        if not icon_title or not icon_title in detail_titles:
            continue
        detail_title = detail_titles[icon_title]
        if detail_tag:
            ET.SubElement(details_elem, detail_title).text = detail_tag.text
    # Create the 'Details' XML element
    optionals_elem = ET.SubElement(root, "Optionals")

    # Find the <script> element in the HTML
    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
    # parse the data as json, find optionals
    data = json.loads(script_tag.text)
    equipment_data = data['props']['pageProps']['equipment']
    for item in equipment_data['standard']:
        feature_elem = ET.SubElement(optionals_elem, "Option")
        feature_elem.text = item['name']

    for item in equipment_data['optional']:
        feature_elem = ET.SubElement(optionals_elem, "Option")
        feature_elem.text = item['name']
    return root


filename = "download/bmw-120-berlina-2017-occasione-10962334.html"


with open(filename, "r") as f:
    xml_output = extract_info(f.read())
    xml_str = ET.tostring(xml_output, encoding='utf-8').decode()
    xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="   ")
    print(xml_pretty)
