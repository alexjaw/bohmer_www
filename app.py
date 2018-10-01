# -*- coding: utf-8 -*-
# First argument is the full path to the www folder, if omitted, then
# default www-folder is ...temp/update/www

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.gen
import os
import sys
import base_handlers

HOME = os.getcwd()
WWWHOME = os.path.join(os.path.expanduser("~"), 'temp', 'update', 'www')  # on linux /home/<user>/temp/update/www

# ---------------------------------------------------------------- #
# --------------------------Config things--------------------------#
# todo: Add to CONFIG and update code
DEBUG = True
PORT = 8888
ADDRESS = "0.0.0.0"


################################ MAIN ################################

def main():
    handlers = []

    # Static handlers
    handlers.extend(base_handlers.static_handlers)

    # ws handlers
    handlers.extend(base_handlers.ws_handlers)

    settings = {"template_path": os.path.join(WWWHOME, 'templates'),
                "static_path": os.path.join(WWWHOME, 'static'),
                "debug": DEBUG,
                "address": ADDRESS,
                "port": PORT,
                }

    # todo: put this in a function (make_app()) so that its configurable!
    try:
        app = tornado.web.Application(handlers, **settings)
    except Exception as e:
        exit()

    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(PORT, address=ADDRESS)

    mainLoop = tornado.ioloop.IOLoop.instance()

    try:
        mainLoop.start()
    except KeyboardInterrupt as e:
        print('Server stopped. KeyboardInterrupt.')
    except Exception as e:
        print('Server stopped unexpectedly.')
    finally:
        pass


if __name__ == "__main__":
    if len(sys.argv) == 2:
        WWWHOME = sys.argv[1]
    print('-------------------- NEW SESSION --------------------')
    print('Serving pages from {} on port {}...'.format(WWWHOME, PORT))
    main()
