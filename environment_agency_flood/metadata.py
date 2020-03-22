from utils import get_value
import assets
import json

class FloodHarvestorMeta(object):
    """A class to generate metadata for Environment Agency Flood observations"""

    def __init__(self, output_meta):
        """Initiate the properties"""

        self.output_meta = output_meta


    def build_site(self,station: json) -> assets.Site:
        """Generate a metadata file for a Site asset"""

        site = assets.Site(
            site_id=get_value(station, "items_stationReference"),
            longitude=get_value(station, "items_long"),
            latitude=get_value(station, "items_lat"),
            altitude=None,
            address=None,
            city=get_value(station, "items_town"),
            country="UK",
            postcode=None,
            first_date=get_value(station, "items_dateOpened"),
            operator=get_value(station, "meta_publisher"),
            desc_url=get_value(station, "meta_documentation")
        )

        return site

    def build_sensors(self, station):
        """Generate a metafile for a sensor"""

        sensors = []
        measures = get_value(station, "items_measures")
        measures = [measures] if type(measures) == dict else measures
        for i, measure in enumerate(measures):
            sensor = assets.Sensor(
                sensor_id=get_value(measure, "@id")[60:],
                provider=get_value(station, "meta_publisher"),
                serial_number=None,
                energy_supply=None,
                freq_maintenance=None,
                s_type=get_value(measure, "parameter"),
                family=get_value(measure, "parameterName"),
                data_acquisition_interval="daily",
                first_date=get_value(station, "items_dateOpened"),
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
            sensors.append(sensor)

        return sensors

    def generate_metadata(self, station):
        """Generate metadata for each site and sensor"""

        site = self.build_site(station)
        site.save()

        sensors = self.build_sensors(station)
        for sensor in sensors:
            sensor.save()

    def generate_metadata_csv(self, stations):
        """Generate a metadata CSV file for stations"""

        fields_stations = [
            "@id",
            "RLOIid",
            "catchmentName",
            "dateOpened",
            "datumOffset",
            "eaAreaName",
            "eaRegionName",
            "easting",
            "label",
            "lat",
            "long",
            "northing",
            "notation",
            "riverName",
            "stageScale_@id",
            "stageScale_datum",
            "stageScale_highestRecent_@id",
            "stageScale_highestRecent_dateTime",
            "stageScale_highestRecent_value",
            "stageScale_maxOnRecord_@id",
            "stageScale_maxOnRecord_dateTime",
            "stageScale_maxOnRecord_value",
            "stageScale_minOnRecord_@id",
            "stageScale_minOnRecord_dateTime",
            "stageScale_minOnRecord_value",
            "stageScale_scaleMax",
            "stageScale_typicalRangeHigh",
            "stageScale_typicalRangeLow",
            "stationReference",
            "status",
            "town",
            "type",
            "wiskiID"
        ]

        fields_measures = [
            "@id",
            "datumType",
            "label",
            "latestReading_@id",
            "latestReading_date",
            "latestReading_dateTime",
            "latestReading_value",
            "notation",
            "parameter",
            "parameterName",
            "period",
            "qualifier",
            "station",
            "stationReference",
            "type",
            "unit",
            "unitName",
            "valueType"
        ]

        # CSV station meta output to file
        site_file = "{}/stations.csv".format(self.output_meta)
        with open(site_file, 'w+') as file:
            file.write('|'.join(fields_stations) + '\n')
            for station in stations:
                station = get_value(station, "items")
                fields = [str(get_value(station, key)) for key in fields_stations]
                file.write('|'.join(fields) + '\n')

        # CSV measure meta output to file
        sensor_file = "{}/sensors.csv".format(self.output_meta)
        with open(sensor_file, 'w+') as file:
            file.write('|'.join(fields_measures) + '\n')
            for station in stations:
                measures = get_value(station, "items_measures")
                measures = [measures] if type(measures) == dict else measures
                for sensor in measures:
                    fields = [str(get_value(sensor, key)) for key in fields_measures]
                    file.write('|'.join(fields) + '\n')

