import json

import ufmetadata.assets as assets


class DEFRASOSHarvestorMeta(object):
    """A class to generate metadata for DEFRA SOS observations"""

    def __init__(self, output_meta):
        """Initiate the properties"""

        self.output_meta = output_meta

    def build_site(self, station: json) -> assets.Site:
        """Generate a metadata file for a Site asset"""

        site = assets.Site(
            site_id=station["properties"]["id"],
            longitude=station["geometry"]["coordinates"][0],
            latitude=station["geometry"]["coordinates"][1],
            altitude=station["geometry"]["coordinates"][2],
            address=station["properties"]["label"],
            city=None,
            country="UK",
            postcode=None,
            first_date=None,
            operator="DEFRA",
            desc_url=None
        )

        return site

    def build_sensor(self, timeseries) -> assets.Sensor:
        """Generate a metadata for a sensor"""

        sensor = assets.Sensor(
            sensor_id=timeseries["id"],
            provider="DEFRA",
            serial_number=None,
            energy_supply=None,
            freq_maintenance=None,
            s_type=None,
            family=None,
            data_acquisition_interval="daily",
            first_date=None,
            datoz18_handle=None,
            detectors=[],
            desc_url=None,
            iot_import_ip=None,
            iot_import_port=None,
            iot_import_token=None,
            iot_import_username=None,
            iot_import_password=None,
            iot_export_ip=None,
            iot_export_port=None,
            iot_export_token=None,
            iot_export_username=None,
            iot_export_password=None
        )

        return sensor

    def generate_metadata(self, station):
        """Generate metadata for each site and sensor"""

        site = self.build_site(station)
        site.save()

        sensor = self.build_sensor(station)
        sensor.save()

        return site, sensor

    def generate_row_station(self, station):
        row = list()
        row.append(str(station["geometry"]["coordinates"]))
        row.append(str(station["geometry"]["type"]))
        row.append(str(station["properties"]["id"]))
        row.append(str(station["properties"]["label"]))
        row.append(str(station["type"]))
        return row

    def generate_row_timeseries(self, timeseries):
        row = list()
        row.append(str(timeseries["firstValue"]["timestamp"]))
        row.append(str(timeseries["firstValue"]["value"]))
        row.append(str(timeseries["id"]))
        row.append(str(timeseries["label"]))
        row.append(str(timeseries["lastValue"]["timestamp"]))
        row.append(str(timeseries["lastValue"]["value"]))
        row.append(str(timeseries["parameters"]["category"]["id"]))
        row.append(str(timeseries["parameters"]["category"]["label"]))
        row.append(str(timeseries["parameters"]["feature"]["id"]))
        row.append(str(timeseries["parameters"]["feature"]["label"]))
        row.append(str(timeseries["parameters"]["offering"]["id"]))
        row.append(str(timeseries["parameters"]["offering"]["label"]))
        row.append(str(timeseries["parameters"]["phenomenon"]["id"]))
        row.append(str(timeseries["parameters"]["phenomenon"]["label"]))
        row.append(str(timeseries["parameters"]["procedure"]["id"]))
        row.append(str(timeseries["parameters"]["procedure"]["label"]))
        row.append(str(timeseries["parameters"]["service"]["id"]))
        row.append(str(timeseries["parameters"]["service"]["label"]))
        row.append(str(timeseries["referenceValues"]))
        row.append(str(timeseries["station"]))
        row.append(str(timeseries["station"]["geometry"]["coordinates"]))
        row.append(str(timeseries["station"]["geometry"]["type"]))
        row.append(str(timeseries["station"]["properties"]["id"]))
        row.append(str(timeseries["station"]["properties"]["label"]))
        row.append(str(timeseries["station"]["type"]))
        row.append(str(timeseries["uom"]))
        return row

    def generate_metadata_csv_stations(self, stations):
        """Generate a metadata CSV file for stations"""

        fields_station = [
            "coordinates",
            "type",
            "id",
            "label",
            "type"
        ]

        # CSV station meta output to file
        site_file = "{}/stations.csv".format(self.output_meta)
        with open(site_file, 'w+') as file:
            file.write('|'.join(fields_station) + '\n')
            for station in stations:
                fields = self.generate_row_station(station)
                file.write('|'.join(fields) + '\n')

    def generate_metadata_csv_timeseries(self, stations):
        """Generate a metadata CSV file for timeseries"""

        timeseries_list = []
        for station in stations:
            timeseries_id = list(station["properties"]["timeseries"].keys())[0]
            endpoint_ts = "timeseries/{}".format(timeseries_id)
            timeseries = self.session.call_iter(self.base_url, endpoint_ts)
            timeseries_list.append(timeseries)

        fields_timeseries = [
            "timestamp",
            "value",
            "id",
            "label",
            "timestamp",
            "value",
            "category_id",
            "category_label",
            "feature_id",
            "feature_label",
            "offering_id",
            "offering_label",
            "phenomenon_id",
            "phenomenon_label",
            "procedure_id",
            "procedure_label",
            "service_id",
            "service_label",
            "referenceValues",
            "station",
            "geometry_coordinates",
            "geometry_type",
            "properties_id",
            "properties_label",
            "type"
            "uom"
        ]

        # CSV timeseries meta output to file
        sensor_file = "{}/sensors.csv".format(self.output_meta)
        with open(sensor_file, 'w+') as file:
            file.write('|'.join(fields_timeseries) + '\n')
            for ts in timeseries_list:
                fields = self.generate_row_timeseries(ts)
                file.write('|'.join(fields) + '\n')

    def generate_metadata_csv(self, stations):
        """Generate metadata CSV fileы for stations and timeseries"""

        self.generate_metadata_csv_stations(stations)
        self.generate_metadata_csv_timeseries(stations)
