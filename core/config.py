import ConfigParser
import random
import shutil
import os
import json
import core

import logging
logging = logging.getLogger(__name__)

class Config():

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.optionxform = str

        self.file = core.CONF_FILE
        self.base_file = 'core/base_config.cfg'

    def new_config(self):
        ''' Copies base_file to config directory.
        Automatically assigns random values to searchtimehr, searchtimemin, and apikey.
        '''

        try:
            shutil.copy2(self.base_file, self.file)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            print 'Could not move base_config.'
            raise

        self.config.readfp(open(self.file))

        self.config.set('Search', 'searchtimehr', str(random.randint(0, 23)).zfill(2) )
        self.config.set('Search', 'searchtimemin', str(random.randint(0, 59)).zfill(2) )

        apikey = "%06x" % random.randint(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        self.config.set('Server', 'apikey', apikey )

        with open(self.file, 'w') as conf_file:
            self.config.write(conf_file)
        return 'Config Saved'

    def write_dict(self, data):
        ''' Writes a dict to the config file.
        :param data: dict of Section with nested dict of keys and values
            {'Section': {'key': 'val', 'key2': 'val2'}, 'Section2': {'key': 'val'}}
        '''
        self.config.read(self.file)

        for cat in data:
            self.config.remove_section(cat)
            self.config.add_section(cat)
            for k, v in data[cat].items():
                self.config.set(cat, k, v)

        with open(self.file, 'w') as cfgfile:
            self.config.write(cfgfile)

        # After writing, copy it back to core.CONFIG
        self.stash()

    def merge_new_options(self):
        ''' Opens base_config and config,
            then saves them merged with config taking priority.
        '''

        self.config.read([self.base_file, self.file])
        with open(self.file, 'w') as cfgfile:
            self.config.write(cfgfile)

    def stash(self):
        ''' Stores entire config as dict to core.CONFIG
        Splits comma-separated strings into lists for Indexers, Quality
        Removes '__name__' keys generated by sqlalchemy
        '''

        d = json.loads(json.dumps(self.config._sections))

        # remove all '__name__' keys
        for i in d:
            if '__name__' in d[i]:
                del d[i]['__name__']

        # split Indexers values into lists
        for k, v in d['Indexers'].iteritems():
            d['Indexers'][k] = v.split(',')

        # split Quality values into lists
        for k, v in d['Quality'].iteritems():
            d['Quality'][k] = v.split(',')

        core.CONFIG = d

