from flask import Flask, render_template, request, make_response
import pandas as pd
import folium
import re
from folium import plugins

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    fuel_types = ['Бензин', 'Дизел', 'Електричество', 'Метан', 'Пропан Бутан']
    available_fuels = [['Бензин A95', 'Бензин A100', 'Бензин A95+', 'Бензин A98'],
                       ['Дизел', 'Дизел премиум'],
                       ['Електричество'],
                       ['Метан'],
                       ['Пропан Бутан']
                       ]

    fuel_reference = dict(zip(fuel_types, available_fuels))
    selected_fuel = "Please select a fuel:"
    datasource_df = pd.read_csv("GasStationData.csv")

    def regex_nav_links():
        lat_long_regex = re.compile(r'[-]?[\d]+[.][\d]*')
        lat_long_list = []
        for link in datasource_df["Navigation links"]:
            lat_and_long = lat_long_regex.findall(link)
            lat_long_list.append(lat_and_long)
        return lat_long_list

    if request.method == 'POST':
        selected_fuel = request.form["fuel_types"]

        # temporary dataframe building
        temp_df = pd.DataFrame()
        for key, value in fuel_reference.items():
            if selected_fuel == key:
                temp_df = temp_df.append(datasource_df.loc[datasource_df[value[0]] != "None"], ignore_index=True)

        # map rendering
        coordinates_list = regex_nav_links()
        starting_coordinates = (42.6954333, 23.338155)
        folium_map = folium.Map(location=starting_coordinates, zoom_start=12, height="75%", width="60%", top="10%",
                                left="20%")

        for idx, item in enumerate(coordinates_list):
            if selected_fuel == "Бензин":
                popup_html = f"""
                    <h3 style="font-size:16px; text-align:center">{datasource_df["Gas Station"][idx]}<p>
                    <p>{datasource_df["Address"][idx]}<p>
                    <ol style="list-style-type:none; text-align:left; font-size:13px;">
                        <li>{temp_df["Бензин A100"].name}: {temp_df["Бензин A100"][idx]}</li>
                        <li>{temp_df["Бензин A95"].name}: {temp_df["Бензин A95"][idx]}</li>
                        <li>{temp_df["Бензин A95+"].name}: {temp_df["Бензин A95+"][idx]}</li>
                        <li>{temp_df["Бензин A98"].name}: {temp_df["Бензин A98"][idx]}</li>
                    </ol>
                    <form target="_blank" action="{datasource_df["Navigation links"][idx]}">
                        <input type="submit" value="Навигация" />
                    </form>

        """

                popup = folium.Popup(popup_html, min_width=300, max_width=1200)

                folium.Marker(location=item,
                              popup=popup,
                              icon=folium.Icon(color='#28568f', icon='gas-pump', prefix='fa')).add_to(folium_map)

            elif selected_fuel == "Дизел":
                popup_html = f"""
                                    <h3 style="font-size:16px; text-align:center">{datasource_df["Gas Station"][idx]}<p>
                                    <p>{datasource_df["Address"][idx]}<p>
                                    <ol style="list-style-type:none; text-align:left; font-size:13px;">
                                         <li>{temp_df["Дизел"].name}: {temp_df["Дизел"][idx]}</li>
                                        <li>{temp_df["Дизел премиум"].name}: {temp_df["Дизел премиум"][idx]}</li>
                                    </ol>
                                    <form target="_blank" action="{datasource_df["Navigation links"][idx]}">
                                        <input type="submit" value="Навигация" />
                                    </form>

                        """

                popup = folium.Popup(popup_html, min_width=300, max_width=1200)

                folium.Marker(location=item,
                              popup=popup,
                              icon=folium.Icon(color='#451f6e', icon='gas-pump', prefix='fa')).add_to(folium_map)
            elif selected_fuel == "Електричество":
                popup_html = f"""
                                    <h3 style="font-size:16px; text-align:center">{datasource_df["Gas Station"][idx]}<p>
                                    <p>{datasource_df["Address"][idx]}<p>
                                    <ol style="list-style-type:none; text-align:left; font-size:13px;">
                                        <li>{temp_df["Електричество"].name}: {temp_df["Електричество"][idx]}</li>
                                    </ol>
                                    <form target="_blank" action="{datasource_df["Navigation links"][idx]}">
                                        <input type="submit" value="Навигация" />
                                    </form>

                        """

                popup = folium.Popup(popup_html, min_width=300, max_width=1200)

                folium.Marker(location=item,
                              popup=popup,
                              icon=folium.Icon(color='#4efc03', icon='gas-pump', prefix='fa')).add_to(folium_map)
            elif selected_fuel == "Метан":
                popup_html = f"""
                                    <h3 style="font-size:16px; text-align:center">{datasource_df["Gas Station"][idx]}<p>
                                    <p>{datasource_df["Address"][idx]}<p>
                                    <ol style="list-style-type:none; text-align:left; font-size:13px;">
                                        <li>{temp_df["Метан"].name}: {temp_df["Метан"][idx]}</li>
                                    </ol>
                                    <form target="_blank" action="{datasource_df["Navigation links"][idx]}">
                                        <input type="submit" value="Навигация" />
                                    </form>

                        """

                popup = folium.Popup(popup_html, min_width=300, max_width=1200)

                folium.Marker(location=item,
                              popup=popup,
                              icon=folium.Icon(color='#1f4a0c', icon='gas-pump', prefix='fa')).add_to(folium_map)
            elif selected_fuel == "Пропан Бутан":
                popup_html = f"""
                                    <h3 style="font-size:16px; text-align:center">{datasource_df["Gas Station"][idx]}<p>
                                    <p>{datasource_df["Address"][idx]}<p>
                                    <ol style="list-style-type:none; text-align:left; font-size:13px;">
                                        <li>{temp_df["Пропан Бутан"].name}: {temp_df["Пропан Бутан"][idx]}</li>
                                    </ol>
                                    <form target="_blank" action="{datasource_df["Navigation links"][idx]}">
                                        <input type="submit" value="Навигация" />
                                    </form>

                        """

                popup = folium.Popup(popup_html, min_width=300, max_width=1200)

                folium.Marker(location=item,
                              popup=popup,
                              icon=folium.Icon(color='#690d25', icon='gas-pump', prefix='fa')).add_to(folium_map)

        folium_map.save('templates/map.html')

        response = make_response(render_template("index.html", fuel_types=fuel_types, default=selected_fuel))

        response.set_cookie("fuel", value=request.form["fuel_types"])
        return response

    if request.cookies.get("fuel"):
        selected_fuel = request.cookies.get("fuel")

        # map rendering
        coordinates_list = regex_nav_links()
        starting_coordinates = (42.6954333, 23.338155)
        folium_map = folium.Map(location=starting_coordinates, zoom_start=12, height="75%", width="60%", top="10%",
                                left="20%")
        filtered_df = datasource_df.replace("None", "Не е налично")
        for idx, item in enumerate(coordinates_list):
            popup_html = f"""
            <h3 style="font-size:16px; text-align:center">{datasource_df["Gas Station"][idx]}<p>
            <p>{datasource_df["Address"][idx]}<p>
            <ol style="list-style-type:none; text-align:left; font-size:13px;">
                <li>{filtered_df["Бензин A100"].name}: {filtered_df["Бензин A100"][idx]}</li>
                <li>{filtered_df["Бензин A95"].name}: {filtered_df["Бензин A95"][idx]}</li>
                <li>{filtered_df["Бензин A95+"].name}: {filtered_df["Бензин A95+"][idx]}</li>
                <li>{filtered_df["Бензин A98"].name}: {filtered_df["Бензин A98"][idx]}</li>
                <li>{filtered_df["Дизел"].name}: {filtered_df["Дизел"][idx]}</li>
                <li>{filtered_df["Дизел премиум"].name}: {datasource_df["Дизел премиум"][idx]}</li>
                <li>{filtered_df["Електричество"].name}: {filtered_df["Електричество"][idx]}</li>
                <li>{filtered_df["Метан"].name}: {filtered_df["Метан"][idx]}</li>
                <li>{filtered_df["Пропан Бутан"].name}: {filtered_df["Пропан Бутан"][idx]}</li>
            </ol>
            <form target="_blank" action="{datasource_df["Navigation links"][idx]}">
                <input type="submit" value="Навигация" />
            </form>
            
"""
            popup = folium.Popup(popup_html, min_width=300, max_width=1200)

            folium.Marker(location=item,
                          popup=popup,
                          icon=folium.Icon(color='blue', icon='gas-pump', prefix='fa')).add_to(folium_map)
        folium_map.save('templates/map.html')

        return render_template("index.html", fuel_types=fuel_types, default=selected_fuel)


if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
