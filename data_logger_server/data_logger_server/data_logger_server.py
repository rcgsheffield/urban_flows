"""
Data Logger Web Server

A simple web application to receive data from an OTT Data app.logger.
The script will accept different actions (determined by the action URL query
parameter.)

Accepted actions:
    * senddata
    * sendalarm

The function ott() is called when a POST request is
sent to the URI /ott/. This routes the action to the appropriate handler.
This then calls the function serialise() which writes
the body of the message to disk. The response is an XML snippet.

Use atomic file writing to ensure that no partially-written files are
synced downstream by the data pipeline.

Authentication is handled separately by the web server (e.g. Apache or NGINX).
"""

import os
import logging.config
import datetime

import atomicwrites
import flask

import settings
import app_factory

logging.config.dictConfig(settings.LOGGING_CONFIG)

app = app_factory.create_app()


def get_dir(root_dir: str, now: datetime.datetime) -> str:
    """Build the target directory and ensure it exists"""

    path_parts = [
        root_dir,
        # Subdirectories for each day
        *now.date().isoformat().split('-')
    ]

    path = os.path.join(*path_parts)

    # Create target directory
    os.makedirs(path, exist_ok=True)

    return path


def get_filename(station_id, now: datetime.datetime) -> str:
    """Build file name"""

    # Build filename-safe timestamp
    safe_timestamp = now.isoformat().replace(':', '+')

    return "{}_{}".format(station_id, safe_timestamp)


def get_path(root_dir: str, station_id: str, now: datetime.datetime) -> str:
    """Build target file path and create subdirectories"""

    # Get target directory
    path = get_dir(root_dir=root_dir, now=now)

    filename = get_filename(station_id=station_id, now=now)

    return os.path.join(path, filename)


def serialise(data: str, root_dir: str, station_id: str,
              now: datetime.datetime) -> str:
    """
    Save the input data as a file with a timestamp filename

    :param data: Binary data to save
    :param root_dir: Base filesystem location to store data
    :param station_id: Data logger device identifier
    :param now: Current timestamp
    :return: Path to written file
    """

    path = get_path(root_dir=root_dir, station_id=station_id, now=now)

    # Save to disk (open for exclusive creation, failing if the file already
    # exists). Use atomic writes to avoid partially-written files if a sync
    # starts mid-write. The data will be written to a named temporary file
    # until all data is written.
    with atomicwrites.atomic_write(path, overwrite=False,
                                   suffix=settings.TEMP_SUFFIX,
                                   dir=settings.TEMP_DIR) as file:
        app.logger.debug("Temp: %s", file.name)
        file.write(data)

    app.logger.info(f'Wrote "{path}"')

    return path


def build_response_body(station_id: str, now: datetime.datetime) -> str:
    """Build a response message (OTT_Response.xsd)"""

    # Insert parameters into string template
    return app.config['RESPONSE_TEMPLATE'].format(
        station_id=station_id,
        resp_time=now.isoformat()
    )


def decode_request_data():
    """Decode string data from incoming request"""
    return flask.request.get_data(as_text=True)


def get_station_id():
    """Get data logger identifier"""
    return flask.request.args['stationid']


def ott_response(root_dir: str):
    """Generic OTT netDL response"""

    station_id = get_station_id()

    data = decode_request_data()

    # Generate timestamp
    now = datetime.datetime.utcnow()

    serialise(data, root_dir=root_dir, station_id=station_id, now=now)

    body = build_response_body(station_id=station_id, now=now)

    response = flask.Response(body, mimetype=settings.RESPONSE_MIME_TYPE)

    return response


@app.route('/ott/', methods=['POST'])
def ott():
    """Route request to the appropriate function"""

    # Map action to handler
    handlers = dict(
        senddata=ott_data,
        sendalarm=ott_alarm,
    )

    handler = handlers[flask.request.args['action']]

    return handler()


def ott_data():
    """
    OTT data app.logger server (action=senddata or OTT_Data.xsd)

    The client will send a self-timed data transmission (see Description of XML
    Data Exchange, section 6.1). The HTTP POST will be sent in XML format
    (using OTT_Data.xsd shown in Sec 9.4).

    In response to the HTTP POST request containing the data, the server
    returns an acknowledge message as defined by the XML schema file
    OTT_Response.xsd (see section 3)

    :return: XML data received success response (OTT_Response.xsd)
            (see Sec. 4.2 and 9.3)
    """

    return ott_response(root_dir=settings.DATA_DIR)


def ott_alarm():
    """
    Receive OTT netDL alarm signals (action=sendalarm or OTT_Alarm.xsd)

    See manual Sec 6.2

    :return: XML response (OTT_Response.xsd)
    """

    # Raise the alarm
    body = decode_request_data()
    app.logger.error(body)

    return ott_response(root_dir=settings.ALARM_DIR)


def main():
    app.run()


if __name__ == '__main__':
    main()
