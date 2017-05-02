import json
import os
import ts3
import logging
from config.ts_config import *
import argparse
import cherrypy

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)
_server_name = "'%s:%s'" % (ts_host, ts_port)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity", dest="v")
    args = parser.parse_args()
    if args.v:
        _logger.setLevel(logging.DEBUG)
        print("Verbose logging enabled.")
        _logger.debug("Verbose logging enabled.")
    connect_ts_server()

def connect_ts_server():
    with ts3.query.TS3Connection() as tsconn:
        try:
            tsconn.open(ts_host)
            _logger.info("Connected to server: " + str(ts_host))
            tsconn.login(client_login_name=ts_user, client_login_password=ts_password)
            _logger.info("Logged into server " + str(ts_host))
        except ConnectionRefusedError as e:
            _logger.debug(e)
            _logger.info("Could not connect to host " + _server_name)
        except TimeoutError as e:
            _logger.debug(e)
            _logger.info("Connection to server " + _server_name + " timed out")
        finally:
            if tsconn.is_connected():
                tsconn.close()
                _logger.info("Closed connection to " + _server_name)
            else:
                _logger.debug("Not disconnected as was never connected.")

class TSStatus(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_host_list(self):
        return {"hosts": json.loads(json.dumps(host_list))}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def check_status(self):
        pass

if __name__ == "__main__":
    cherrypy.quickstart(TSStatus(), "/",
                        {"/": {
                            "tools.staticdir.root": os.path.abspath(os.path.join(__file__, "..", "static")),
                            "tools.staticdir.on": True,
                            "tools.staticdir.dir": "",
                            "tools.staticdir.index": "index.html"
                        }})
