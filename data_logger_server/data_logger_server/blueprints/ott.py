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
import datetime
import pathlib

import atomicwrites
import flask

import settings

app = flask.current_app
blueprint = flask.Blueprint('ott', __name__)


def get_dir(root_dir: pathlib.Path, time: datetime.datetime) -> pathlib.Path:
    """
    Build the target directory and ensure it exists
    """

    root_dir = pathlib.Path(root_dir)

    # Subdirectories for each day
    path = root_dir.joinpath(*time.date().isoformat().split('-'))

    # Create target directory
    path.mkdir(parents=True, exist_ok=True)

    return path


def get_filename(station_id, time: datetime.datetime) -> str:
    """
    Build file name
    """

    # Build filename-safe timestamp
    safe_timestamp = time.isoformat().replace(':', '+')

    return f"{station_id}_{safe_timestamp}"


def get_path(root_dir: pathlib.Path, station_id: str,
             time: datetime.datetime) -> pathlib.Path:
    """
    Build target file path and create subdirectories
    """

    # Get target directory
    target_dir = get_dir(root_dir=root_dir, time=time)

    filename = get_filename(station_id=station_id, time=time)

    return target_dir.joinpath(filename)


def serialise(data: str, path: pathlib.Path) -> None:
    """
    Save the input data as a file

    :param data: Binary data to save
    :param path: Target file path
    """

    # Save to disk (open for exclusive creation, failing if the file already
    # exists). Use atomic writes to avoid partially-written files if a sync
    # starts mid-write. The data will be written to a named temporary file
    # until all data is written.
    with atomicwrites.atomic_write(
            path=str(path), overwrite=False, suffix=settings.TEMP_SUFFIX,
            dir=settings.TEMP_DIR) as file:
        file.write(data)


def build_response_body(station_id: str, resp_time: datetime.datetime) -> str:
    """
    Build a response message (OTT_Response.xsd)
    """

    # Insert parameters into string template
    return app.config['RESPONSE_TEMPLATE'].format(
        station_id=station_id,
        resp_time=resp_time.isoformat()
    )


def decode_request_data() -> str:
    """
    Decode string data from incoming request
    """
    return flask.request.get_data(as_text=True)


def ott_response(root_dir: pathlib.Path):
    """
    Generic OTT netDL response

    :param root_dir: The root directory for this function type or interface
                     e.g. senddata, sendalarm, etc.
    """

    # Get data logger identifier
    station_id = flask.request.args['stationid']

    data = decode_request_data()

    # Generate timestamp
    now = datetime.datetime.utcnow()

    # Build target file name
    path = get_path(root_dir=root_dir, station_id=station_id, time=now)

    # Save data to disk
    serialise(data, path=path)

    body = build_response_body(station_id=station_id, resp_time=now)

    return flask.Response(body, mimetype='application/xml')


@blueprint.route('/ott/', methods=['POST'])
def ott():
    """
    Route request to the appropriate function
    """

    # Map action to handler
    # Each handler has a different function and serialisation directory
    handlers = dict(
        senddata=ott_senddata,
        sendalarm=ott_sendalarm,
    )

    handler = handlers[flask.request.args['action']]

    return handler()


def ott_senddata():
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


def ott_sendalarm():
    """
    Receive OTT netDL alarm signals (action=sendalarm or OTT_Alarm.xsd)

    See manual Sec 6.2

    :return: XML response (OTT_Response.xsd)
    """

    # Raise the alarm
    app.logger.error(decode_request_data())

    return ott_response(root_dir=settings.ALARM_DIR)


@blueprint.route('/ping')
def ping():
    """
    Test endpoint
    """
    return 'pong\n'
