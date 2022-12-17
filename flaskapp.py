import pandas as pd
import folium
import re

from flask import Flask, render_template, request, make_response


FUEL_TYPES = ('Бензин', 'Дизел', 'Електричество', 'Метан', 'Пропан Бутан')
AVAILABLE_FUELS = (['Бензин A95', 'Бензин A100', 'Бензин A95+', 'Бензин A98'],
                   ['Дизел', 'Дизел премиум'],
                   ['Електричество'],
                   ['Метан'],
                   ['Пропан Бутан']
                   )
FUEL_REFERENCE = dict(zip(FUEL_TYPES, AVAILABLE_FUELS))


app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    """
    Function that displays the index ("/") page of the flask app
    :return:
    rendered_template: response
    renders the html on the webpage
    """
    selected_fuel = "Please select a fuel:"
    datasource_df = pd.read_csv("GasStationData.csv")
    pump_color = 'blue'

    if request.method == "GET":

        fuel_selected = request.cookies.get("fuel")
        if fuel_selected:
            selected_fuel = fuel_selected

        # map rendering
        render_map(datasource_df, pump_color, AVAILABLE_FUELS)

        return render_template("index.html", fuel_types=FUEL_TYPES, default=selected_fuel)

    if request.method == 'POST':
        rendered_template = index_post_request(datasource_df)
        return rendered_template


def render_map(datasource_df, pump_color, selected_fuels):
    """
    Function that renders the map for the webpage based on the passed arguments
    :param datasource_df: pandas dataframe
    a dataframe created from the GasStationData.csv
    :param pump_color:list
    A list of available colors used for the marker color
    :param selected_fuels:string
    The fuel that corresponds to the option selected from the dropdown menu
    :return:
    Saves the generated map with all of its parameters in the map.html file
    """
    coordinates_list = regex_nav_links(datasource_df)
    starting_coordinates = (42.6954333, 23.338155)
    filtered_df = datasource_df.replace("None", "Не е налично")
    folium_map = folium.Map(location=starting_coordinates, zoom_start=12, height="75%", width="60%", top="5%",
                            left="20%")
    for idx, item in enumerate(coordinates_list):
        popup_html = generate_popup_html(filtered_df, idx, selected_fuels)
        popup = folium.Popup(popup_html, min_width=300, max_width=1200)
        folium.Marker(location=item,
                      popup=popup,
                      icon=folium.Icon(color=pump_color, icon='gas-pump', prefix='fa')).add_to(folium_map)
    folium_map.save('templates/map.html')


def index_post_request(dataframe):
    """
    Function that outlines the operations carried out by the post request:
        -Creating a filtered dataframe with the records, based on the user's fuel
        selection
        -Sets a cookie for each dropdown menu option
        -Returns a rendering of the map based on the user selection
    :param dataframe: pandas dataframe
    :return:
    """
    fuel_colors = ['cadetblue', 'orange', 'green', 'darkred', 'purple']
    selected_fuel = request.form["fuel_types"]
    selected_fuels = [FUEL_REFERENCE[selected_fuel]]
    fuel_color_index = FUEL_TYPES.index(selected_fuel)
    pump_color = fuel_colors[fuel_color_index]
    # temporary dataframe building
    temp_df = pd.DataFrame()
    for key, value in FUEL_REFERENCE.items():
        if selected_fuel == key:
            temp_df = temp_df.append(dataframe.loc[dataframe[value[0]] != "None"], ignore_index=True)

    # map rendering
    render_map(temp_df, pump_color, selected_fuels)

    response = make_response(render_template("index.html", fuel_types=FUEL_TYPES, default=selected_fuel))
    response.set_cookie("fuel", value=request.form["fuel_types"])
    return response


def generate_popup_html(dataframe, station_index, fuels=AVAILABLE_FUELS):
    """
    Method that generates the html markup for each gas station infobox
    :param dataframe: pandas dataframe
    a dataframe containing all the records used in generating the html
    :param station_index: int
    the index at which the record exists in the dataframe
    :param fuels: list
    A list of all available fuel types
    :return:
    final_string: str
    The parsable html generated for each infobox
    """
    final_string = f"""
                <h3 style="font-size:16px; text-align:center">{dataframe["Gas Station"][station_index]}<p>
                <p>{dataframe["Address"][station_index]}<p>
                <ol style="list-style-type:none; text-align:left; font-size:13px;">
                """
    for fuel_type in fuels:
        for fuel_name in fuel_type:
            final_string += f"""<li>{dataframe[fuel_name].name}: {dataframe[fuel_name][station_index]}</li>"""

    final_string += f"""
                </ol>
                <form target="_blank" action="{dataframe["Navigation links"][station_index]}">
                <input type="submit" value="Навигация" />
                </form>
                """
    return final_string


def regex_nav_links(dataframe):
    """
    A function that takes the coordinates (longitude and latitude)
    from the Navigation links
    :param dataframe: pandas dataframe
    A dataframe from which the links are pulled
    :return:
    latitudes_longitudes: list
    a list of lists that contains the latitude and longitude for each gas station
    """
    lat_long_regex = re.compile(r'[-]?[\d]+[.][\d]*')
    latitudes_longitudes = []
    for link in dataframe["Navigation links"]:
        lat_and_long = lat_long_regex.findall(link)
        latitudes_longitudes.append(lat_and_long)
    return latitudes_longitudes


if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
