#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
base_handlers.py

Here we have common handlers and at the end three lists
that collect all the handlers (static, ws, and api).
Products are supposed to extend theses base handlers and
are supposed to be in handlers.py
The final list of handlers is created by websocketserver.py
'''
import json
import requests
import tornado.websocket
import logging.config
logger = logging.getLogger(__name__)

# Can be changed from handlers.py
USE_PWD_FOR_SETUP = True  # Controls if setup is allowed without password

class BaseHandler(tornado.web.RequestHandler):
    pwd = '2001'

    def get_current_user(self):
        cookie = None
        if not USE_PWD_FOR_SETUP:
            # We do not use pwd in Legacy products, so cookie is auto set to pwd
            # And we do not want to handle cookies, see issue
            cookie = self.pwd
        else:
            cookie = self.get_cookie("user")
        logger.debug('user cookie: %s', cookie) 
        return cookie

    def get_current_theme(self):
        theme = self.get_cookie("theme")
        logger.debug('current theme: {}'.format(theme))
        if not self.get_cookie("theme"):
            theme = 'c'
            self.set_cookie("theme", theme)
        return theme

    def verify_user(self):
        '''Use on pages that require pwd'''
        is_verified = True
        if self.get_current_user() != self.pwd:  # not self.current_user or self.get_current_user() != self.pwd
            is_verified = False
        logger.debug('verified user: %s', is_verified)
        return is_verified

# send index.html if browser connects to port 8080
class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html', page_id='remote', theme=self.get_current_theme())

class InputHandler(BaseHandler):
    def get(self):
        self.render('input.html', page_id='input', theme=self.get_current_theme())

class SettingsHandler(BaseHandler):
    def get(self):
        self.render('settings.html', page_id='settings', theme=self.get_current_theme())

class MasterConfigHandler(BaseHandler):
    '''
    This controller handles master slave configuration.
    We can have one master and several slave units. User scenario:

    *** Installation of a system with one master and several slaves ***
    - Start to add ip-addresses and check that all slaves respond, i.e. conn check
    - When all connections are ok, addresses are stored in app db

    ***  Checking slave configuration and status ***
    - If app db contains any slaves, then their addresses are displayed in the input
     fields

    ***  Updating a configuration with new slave(s) ***
    - Update the input fields with new addresses and submit
    - If connections ok, then db is updated with the content in the input fields
    '''
    def prepare(self):
        self.master = self.settings.get('masteramp')

    def get(self):
        if self.verify_user():
            #todo: update input fields with urls in app db (if any)
            #This could be done by sending in a slave_urls list to the html-page
            self.render('master_config.html',
                        page_id='master_config',
                        slave_urls=self.master.get_slave_urls(),
                        theme=self.get_current_theme())
        else:
            self.redirect('/login.html')

    def post(self, *args, **kwargs):
        # form data comes in as a dicts, see request.arguments and request.body_arguments
        slave_urls = []
        for slave_url in self.request.body_arguments.get('slave_urls'):
            if slave_url == '':
                continue
            slave_urls.append(slave_url)

        '''
        Check connection to slaves:
        - If any request to slave fails the conn_status = conn_fail
        - This will prevent writing to app db
        '''
        connection_results = []
        conn_ok = 'Connection ok'
        conn_fail = 'Connection error'
        conn_status = conn_ok
        for slave_url in slave_urls:
            if slave_url == '':
                continue
            try:
                r = requests.get('http://' + slave_url, timeout=5)
                conn_status = conn_ok
            except Exception as e:
                logger.error('Error. Could not connect to {}'.format(slave_url))
                conn_status = conn_fail
            connection_results.append({'url': slave_url, 'status': conn_status})

        # Save slave urls if all slaves have connection ok
        if conn_status == conn_ok:
            try:
                self.master.set_slave_urls_in_db(slave_urls)
            except Exception as e:
                logger.error('Error. Could not set slave urls in db')

        self.write(json.dumps(connection_results))

class ModeHandler(BaseHandler):
    def get(self):
        self.render('mode.html', page_id='mode', theme=self.get_current_theme())

class HomeTheatreHandler(BaseHandler):
    def get(self):
        self.render('home_theatre.html', page_id='home_theatre', theme=self.get_current_theme())

class PresetsHandler(BaseHandler):
    def prepare(self):
        self.api = self.settings.get('api')

    def get(self):
        self.render('presets.html', api=self.api, page_id='presets', theme=self.get_current_theme())

class FiltersHandler(BaseHandler):
    def get(self):
        self.render('filters.html', page_id='filters', theme=self.get_current_theme())

class UserTargetsInfoHandler(BaseHandler):
    def get(self):
        self.render('user_targets_info.html', page_id='user_targets_info', theme=self.get_current_theme())

class UserTargetsSaveHandler(BaseHandler):
    def get(self):
        self.render('user_targets_save.html', page_id='user_targets_save', theme=self.get_current_theme())

class RoomCorrectionHandler(BaseHandler):
    def get(self):
        self.render('room_correction.html', page_id='roomCorrection', theme=self.get_current_theme())

class FrontPanelHandler(BaseHandler):
    def get(self):
        self.render('front_panel.html', page_id='front_panel', theme=self.get_current_theme())

class SystemUpdateHandler(BaseHandler):
    def get(self):
        self.render('system_update.html', page_id='system_update', theme=self.get_current_theme())

class SetupPrologHandler(BaseHandler):
    def get(self):
        self.render('setup_prolog.html', page_id='setupProlog', theme=self.get_current_theme())

class SetupHandler(BaseHandler):
    def get(self):
        if self.verify_user():
            self.render('setup.html', page_id='setup', theme=self.get_current_theme())
        else:
            self.redirect('/login.html')

class StartupVolumeHandler(BaseHandler):
    def get(self):
        self.render('startup_volume.html', page_id='startupVolume', theme=self.get_current_theme())

class TestlevelHandler(BaseHandler):
    def get(self):
        if self.verify_user():
            self.render('test_level.html', page_id='test_level', theme=self.get_current_theme())
        else:
            self.redirect('/login.html')

class RoomCorrectionSetupHandler(BaseHandler):
    def get(self):
        if self.verify_user():
            self.render('room_correction_setup.html', page_id='roomCorrection_setup', theme=self.get_current_theme())
        else:
            self.redirect('/login.html')

class RoomCorrectionMenuHandler(BaseHandler):
    def get(self):
        logger.debug('indata to Handler: %s', repr(self.request.path))
        if self.verify_user():
            self.render('room_correction_menu.html', page_id='roomCorrectionMenu', theme=self.get_current_theme())
        else:
            self.redirect('/login.html')

class RoomCorrectionResultsHandler(BaseHandler):
    def get(self):
        if self.verify_user():
            self.render('room_correction_results.html', page_id='room_correction_results', theme=self.get_current_theme())
        else:
            self.redirect('/login.html')

class HelpMeasureUploadHandler(BaseHandler):
    def get(self):
        if self.verify_user():
            resource = self.request.path
            if 'left' in resource:
                self.render('help_measure_left_channel.html',
                            page_id='help_measure_left',
                            theme=self.get_current_theme())
            elif 'right' in resource:
                self.render('help_measure_right_channel.html',
                            page_id='help_measure_right_popup',
                            theme=self.get_current_theme())
            elif 'upload' in resource:
                self.render('help_upload.html',
                            page_id='help_upload',
                            theme=self.get_current_theme())
        else:
            self.redirect('/login.html')

class ChannelLevelManualHandler(BaseHandler):
    def get(self):
        if self.verify_user():
            self.render('channel_level_manual.html', page_id='channel_level_manual', theme=self.get_current_theme())
        else:
            self.redirect('/login.html')

class LoginHandler(BaseHandler):
    def get(self):
        if self.verify_user():
            self.redirect('/setup.html')
        else:
            self.render('login.html', page_id='login', theme=self.get_current_theme())

    def post(self):
        self.set_cookie("user", self.get_argument("password"))
        self.redirect('/setup.html')

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect('/')

class ThemeHandler(BaseHandler):
    def get(self):
        self.render('theme.html', page_id='theme', theme=self.get_current_theme())

    def post(self):
        self.set_cookie("theme", self.get_argument("theme"))
        self.redirect('/theme.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):  # enable cross origin calls
        return True

    def open(self):  # new connection
        logger.info('New connection')
        # print 'new connection'
        self.settings.get('clients').append(self)
        self.write_message("connected")

    def on_message(self, message):  # new message incoming
        # print 'msg2bap:', message
        logger.debug('ws2bap: %s', repr(message))
        self.settings.get('taskQ').put(message)

    def on_close(self):  # Disconnected
        # print 'connection closed'
        logger.info('Connection closed')
        self.settings.get('clients').remove(self)


#todo: handlers must be manually modified with respect to sycon config,
# see for example handlers for presets/
static_handlers = [(r"/", IndexHandler),
                (r"/index.*", IndexHandler),
                (r"/input.*", InputHandler),
                (r'/settings.*', SettingsHandler),
                (r"/master_config.*", MasterConfigHandler),
                (r'/mode.*', ModeHandler),
                (r'/home_theatre.*', HomeTheatreHandler),
                (r'/filters.*', FiltersHandler),
                (r'/presets.*', PresetsHandler),
                (r'/user_targets_info.*', UserTargetsInfoHandler),
                (r'/user_targets_save.*', UserTargetsSaveHandler),
                (r'/room_correction_setup.*', RoomCorrectionSetupHandler),
                (r'/room_correction_menu.*', RoomCorrectionMenuHandler),
                (r'/room_correction_results.*', RoomCorrectionResultsHandler),
                (r'/help.*', HelpMeasureUploadHandler),
                (r'/room_correction.*', RoomCorrectionHandler),
                (r'/front_panel.*', FrontPanelHandler),
                (r'/system_update.*', SystemUpdateHandler),
                (r'/setup_prolog.*', SetupPrologHandler),
                (r'/setup.*', SetupHandler),
                (r'/startup_volume.*', StartupVolumeHandler),
                (r'/test_level.*', TestlevelHandler),
                (r'/channel_level_manual.*', ChannelLevelManualHandler),
                (r"/login.*", LoginHandler),
                (r"/logout.*", LogoutHandler),
                (r"/theme.*", ThemeHandler),
                   ]

ws_handlers = [(r"/ws", WebSocketHandler),]

def get_api_handlers(api):
    return [(r"/api/v1/", api.TopHandler,),
                (r"/api/v1/status", api.TopStatusHandler),
                (r"/api/v1/brightness(.*)", api.ResourceHandler,),
                (r"/api/v1/home_theater(.*)", api.ResourceHandler,),
                (r"/api/v1/mute(.*)", api.ResourceHandler),
                (r"/api/v1/power(.*)", api.ResourceHandler,),
                (r"/api/v1/volume(.*)", api.ResourceHandler,),
                (r"/api/v1/contours/", api.CollectionHandler),
                (r"/api/v1/inputs/", api.CollectionHandler),
                (r"/api/v1/modes/", api.CollectionHandler),
                (r"/api/v1/presets/", api.CollectionHandler),
                (r"/api/v1/contours/status", api.CollectionStatusHandler),
                (r"/api/v1/inputs/status", api.CollectionStatusHandler),
                (r"/api/v1/modes/status", api.CollectionStatusHandler),
                (r"/api/v1/presets/status", api.CollectionStatusHandler),
                (r"/api/v1/contours/c_1(.*)", api.ResourceHandler),
                (r"/api/v1/contours/c_2(.*)", api.ResourceHandler),
                (r"/api/v1/contours/c_3(.*)", api.ResourceHandler),
                (r"/api/v1/contours/c_4(.*)", api.ResourceHandler),
                (r"/api/v1/contours/c_5(.*)", api.ResourceHandler),
                (r"/api/v1/contours/c_6(.*)", api.ResourceHandler),
                (r"/api/v1/inputs/rca_1(.*)", api.ResourceHandler),
                (r"/api/v1/inputs/rca_2(.*)", api.ResourceHandler),
                (r"/api/v1/inputs/spdif(.*)", api.ResourceHandler),
                (r"/api/v1/inputs/toslink(.*)", api.ResourceHandler),
                (r"/api/v1/inputs/xlr_1(.*)", api.ResourceHandler),
                (r"/api/v1/inputs/xlr_2(.*)", api.ResourceHandler),
                (r"/api/v1/inputs/usb(.*)", api.ResourceHandler),
                (r"/api/v1/modes/mono(.*)", api.ResourceHandler),
                (r"/api/v1/modes/stereo(.*)", api.ResourceHandler),
            ]


if __name__ == '__main__':
    pass

