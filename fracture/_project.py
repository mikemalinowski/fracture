"""
The fracture.Project class is the central core to Fracture. It handles all the
database io and factories.
"""
import os
import re
import sys
import json
import sqlite3
import factories

from ._utils import Signal
from ._scan import ScanProcess
from ._element import DataElement

from . import constants


# ------------------------------------------------------------------------------
class Project(object):
    """
    The Project is the main backbone of fracture. This handles all the
    data accessing and getting. It also manages all the factories and
    general functionality.
    """

    # -- This is the location where we store all the
    # -- sqlite files
    _COMMAND_DIR = os.path.join(
        os.path.dirname(__file__),
        'sql',
    )

    _DEBUG = False

    # --------------------------------------------------------------------------
    def __init__(self, identifier):
        self.identifier = identifier

        # -- This signal is triggered on each scan identifier
        self.scanned = Signal()

        # -- This signal is emitted whenever a scan is completed
        self.scan_complete = Signal()

        # -- Read in all our command data. We do this once so we dont take
        # -- an IO hit each time we want to run an sql query
        self._commands = self._command_dict()

        # -- Only request plugin locations from the db if the
        # -- db actually exists
        plugin_locations = list()
        if os.path.exists(identifier):
            plugin_locations = self.plugin_locations()

        # -- Always add our built in plugins
        plugin_locations.append(constants.BUILT_IN_PLUGIN_DIR)

        # -- We do not hard code the concept of scan mechanisms or
        # -- data elements. Instead we utilise dynamic factories which
        # -- load plugins on the fly.
        self._scan_factory = factories.Factory(
            abstract=ScanProcess,
            paths=plugin_locations,
            plugin_identifier='scan_type',
        )

        self._data_factory = factories.Factory(
            abstract=DataElement,
            paths=plugin_locations,
            plugin_identifier='data_type',
        )

        # -- We will access data plugins a lot - and they need to be
        # -- in priority order, therefore we cache the plugin classes
        # -- in a prioritised list. We then re-cache this data whenever
        # -- plugin paths are changed.
        self._data_plugins = sorted(
            self._data_factory.plugins(),
            key=lambda x: x.priority,
            reverse=True,
        )

    # --------------------------------------------------------------------------
    def create(self):
        """
        This should be used to create the datasource (providing you decide
        to support such a feature).
        
        :return: None 
        """
        with ConnectionContext(self.identifier, commit=True) as ctxt:
            self._execute(
                ctxt,
                'create',
            )
            return True

    # --------------------------------------------------------------------------
    def find(self, tags, limit=None):
        """
        This should return a list of identifiers which match the given
        tags. 
        
        :param tags: List of tags to match against. 
        :type tags: list(str, str, )
        
        :param limit: Maximum number of hits to return
        :type limit: int
        
        :return: list(str, str, ...)
        """
        with ConnectionContext(self.identifier, get=True) as ctxt:
            # -- Define our replacements
            replacements = {
                '$(LIMIT)': limit or 9 ** 9,
            }

            if tags:
                if not isinstance(tags, (list, tuple)):
                    tags = [tags]

                # -- We need to build up strings for searching by
                # -- tags and locators
                compare_str = ''
                like_str = ''
                name_str = ''

                for tag in tags:
                    compare_str += "tag='%s' OR " % tag
                    like_str += "identifier LIKE '%" + tag + "%' AND "
                    name_str += "name LIKE '%" + tag + "%' AND "

                compare_str = compare_str[:-4]
                like_str = like_str[:-5]
                name_str = name_str[:-5]

                replacements.update(
                    {
                        '$(TAG_COMPARE)': compare_str,
                        '$(LIKE_COMPARE)': like_str,
                        '$(NAME_COMPARE)': name_str,
                        '$(COMPARE_COUNT)': str(len(tags)),
                    },
                )

                # -- Run the sql statement
                self._execute(
                    ctxt,
                    'find',
                    replacements=replacements,
                )

            else:
                self._execute(
                    ctxt,
                    'find_all',
                    replacements=replacements,
                )

        return [
            row[1]
            for row in ctxt.results
        ]

    # --------------------------------------------------------------------------
    def tag(self, identifier, tags):
        """
        This will assign the given tags to the element with the given 
        identifier.
        
        :param identifier: Data Element identifier
        :type identifier: str
        
        :param tags: A single tag, or list of tags to assign
        :type tags: string or list(str, str, ...)
        
        :return: None 
        """
        with ConnectionContext(self.identifier, commit=True) as ctxt:
            if not isinstance(tags, (list, tuple)):
                tags = [tags]

            for tag in tags:
                self._execute(
                    ctxt,
                    'tags_add',
                    replacements={
                        '$(IDENTIFIER)': identifier,
                        '$(TAG)': tag.lower(),
                    },
                )

    # --------------------------------------------------------------------------
    def untag(self, identifier, tags):
        """
        This will unassign the given tags from the element with the given 
        identifier.
        
        :param identifier: Data Element identifier
        :type identifier: str
        
        :param tags: A single tag, or list of tags to unassign
        :type tags: string or list(str, str, ...)
        
        :return: None 
        """
        with ConnectionContext(self.identifier, commit=True) as ctxt:
            if not isinstance(tags, (list, tuple)):
                tags = [tags]

            for tag in tags:
                self._execute(
                    ctxt,
                    'tags_rem',
                    replacements={
                        '$(IDENTIFIER)': identifier,
                        '$(TAG)': tag,
                    },
                )

    # --------------------------------------------------------------------------
    def tags(self, identifier):
        """
        This returns a list of all the tags which are assigned to the 
        given identifier.
        
        :param identifier: Data Element identifier
        :type identifier: str
        
        :return: list(str, str, ...)
        """
        with ConnectionContext(self.identifier, get=True) as ctxt:
            self._execute(
                ctxt,
                'tags_get',
                replacements={
                    '$(IDENTIFIER)': identifier,
                },
            )

        return [
            str(result[0])
            for result in ctxt.results
        ]

    # --------------------------------------------------------------------------
    def add(self, identifier):
        """
        Given an elements identifier, name, hash and data this will add or 
        update that elements information into the repository.
        
        :param identifier: Data Element identifier
        :type identifier: str
        
        :return: None 
        """
        with ConnectionContext(self.identifier, commit=True) as ctxt:
            self._execute(
                ctxt,
                'add',
                replacements={
                    '$(IDENTIFIER)': identifier,
                },
            )

    # --------------------------------------------------------------------------
    def remove(self, identifier=None):
        """
        This will remove the given identifier from the repository if it 
        exists.
        
        :param identifier: Data Element identifier
        :type identifier: str
        
        :return: None
        """
        with ConnectionContext(self.identifier, commit=True) as ctxt:
            self._execute(
                ctxt,
                'remove',
                replacements={
                    '$(IDENTIFIER)': identifier,
                },
            )

    # --------------------------------------------------------------------------
    def settings(self):
        """
        This will attempt to load the settings. In a situation where no
        settings are found an empty dictionary is returned.

        :return: dict
        """
        with ConnectionContext(self.identifier, get=True) as ctxt:
            self._execute(ctxt, 'settings_get')

        try:
            return json.loads(ctxt.results[0][0])
        except IndexError:
            return dict()

    # --------------------------------------------------------------------------
    def save_settings(self, settings):
        """
        Given a settings dictionary, this will be stored within the fracture
        database. The data being given must be json serialisable.

        :param settings: dict

        :return: None
        """

        with ConnectionContext(self.identifier, commit=True) as ctxt:
            self._execute(
                ctxt,
                'settings_set',
                replacements={'$(SETTINGS)': json.dumps(settings)},
            )
    
    # --------------------------------------------------------------------------
    def scan_locations(self):
        """
        This returns a list of scan locations stored within the repository.
        
        :return: list(str, str, ...) 
        """
        return self.settings().get('scan_locations', list())

    # --------------------------------------------------------------------------
    def add_scan_location(self, location):
        """
        This will store the given location in the repository. When a scan
        is initiated this location will then be picked up.
        
        :param location: Location to add to the repository
        :type location: str
        
        :return: 
        """
        # -- Get the current settings
        settings = self.settings()

        # -- Update the locations, ensuring the data always conforms
        key = 'scan_locations'
        settings[key] = settings.get(key, list()) + [self._conform(location)]

        # -- Save the settings back into the db
        self.save_settings(settings)

    # --------------------------------------------------------------------------
    def remove_scan_location(self, location):
        """
        This will remove the given location from the repositories list of 
        scan locations.
        
        :param location: Location to remove from the repository
        :type location: str
        
        :return: 
        """
        # -- Get the current settings
        settings = self.settings()

        # -- Update the locations, ensuring the data always conforms
        key = 'scan_locations'
        settings[key] = settings.get(key, list()).remove(location)

        # -- Save the settings back into the db
        self.save_settings(settings)

    # --------------------------------------------------------------------------
    def skip_regexes(self):
        """
        This returns a list of regular expression strings stored within 
        the repository.
        
        :return: list(str, str, ...) 
        """
        return self.settings().get('skip_regex', list())

    # --------------------------------------------------------------------------
    def add_skip_regex(self, pattern):
        """
        This will store the given regex pattern in the repository. When a scan
        is initiated this regex will then be picked up and omit and locations
        containing this pattern.
        
        :param pattern: String regex
        :type pattern: str
        
        :return: 
        """
        # -- Get the current settings
        settings = self.settings()

        # -- Update the locations, ensuring the data always conforms
        key = 'skip_regex'
        settings[key] = settings.get(key, list()) + [self._conform(pattern)]

        # -- Save the settings back into the db
        self.save_settings(settings)

    # --------------------------------------------------------------------------
    def remove_skip_regex(self, pattern):
        """
        This will remove the given regex string pattern from the repository.
        
        :param pattern: String regex
        :type pattern: str
        
        :return: 
        """
        # -- Get the current settings
        settings = self.settings()

        # -- Update the locations, ensuring the data always conforms
        key = 'skip_regex'
        settings[key] = settings.get(key, list()).remove(pattern)

        # -- Save the settings back into the db
        self.save_settings(settings)

    # --------------------------------------------------------------------------
    def plugin_locations(self):
        """
        This will return all the places this project is currently
        loading plugins from.

        :return: list(str, str, ...)
        """
        return self.settings().get('plugin_locations', list())

    # --------------------------------------------------------------------------
    def add_plugin_location(self, location):
        """
        Adds the given location to the list of locations being searched
        for when looking for plugins. This data is persistent between
        sessions and will invoke a reload of plugins.

        :param location: Location to add

        :return: None
        """
        # -- Get the current settings
        settings = self.settings()

        # -- Update the locations, ensuring the data always conforms
        key = 'plugin_locations'
        settings[key] = settings.get(key, list()) + [self._conform(location)]

        # -- Save the settings back into the db
        self.save_settings(settings)

        # -- Now update teh factories
        self._scan_factory.add_path(location)
        self._data_factory.add_path(location)

        # -- Re-cache the sorted data plugins
        self._data_plugins = sorted(
            self._data_factory.plugins(),
            key=lambda x: x.priority,
            reverse=True,
        )

    # --------------------------------------------------------------------------
    def remove_plugin_location(self, location):
        """
        This will remove a plugin from the plugin location list and
        trigger a rescan for plugins.

        :param location: Location to remove
        :return:
        """
        # -- Get the current settings
        settings = self.settings()

        # -- Update the locations, ensuring the data always conforms
        key = 'plugin_locations'
        settings[key] = settings.get(key, list()).remove(location)

        # -- Save the settings back into the db
        self.save_settings(settings)

        # -- Update the factories
        self._scan_factory.remove_path(location)
        self._data_factory.remove_path(location)

        # -- Re-cache the sorted data plugins
        self._data_plugins = sorted(
            self._data_factory.plugins(),
            key=lambda x: x.priority,
            reverse=True,
        )

    # --------------------------------------------------------------------------
    def scan(self, locations=None, recursive=True, full=True):
        """
        This will cycle over all the search locations stored in the
        fracture project and attempt to populate the db with that data
        if the data has been changed or is new.

        :return: None 
        """
        # -- Log the start
        constants.log.info('Starting Scan : %s' % locations)

        # -- Get a list of locations to skip, if we have any then
        # -- we compile them into a single regex
        skip_regex = None
        patterns = self.skip_regexes()

        if patterns:
            skip_regex = re.compile(
                '(' + ')|('.join(patterns) + ')',
            )

        # -- Take the given scan locations if the user passes them
        # -- otherwise we take all the scan locations stored within
        # -- the project
        locations = locations or self.scan_locations()
        if not isinstance(locations, (list, tuple)):
            locations = [locations]

        # -- We return a list of all the added identifiers, so
        # -- keep track of that here
        scanned_identifiers = list()

        with ConnectionContext(self.identifier, commit=True) as ctxt:
            # -- Get a list of locations to scan
            for location in locations:

                # -- Cycle over all our scan plugins
                for scan_plugin in self._scan_factory.plugins():

                    # -- Skip any plugins incapable of scanning
                    # -- this location
                    if not scan_plugin.can_represent(location):
                        continue

                    # -- We now need to cycle over all the identifiers given
                    # -- to us via the scan plugin. Note that the scan plugin
                    # -- always yields
                    for identifier in scan_plugin.identifiers(location, skip_regex, recursive=recursive):

                        self._execute(
                            ctxt,
                            'add',
                            replacements={
                                '$(IDENTIFIER)': identifier,
                            },
                        )

                        # -- Emit the scan signal
                        self.scanned.emit(identifier)

                        # -- Store the fact that we have matched this item
                        scanned_identifiers.append(identifier)

        # -- A full scan involves data extraction such as tags,
        # -- which we only want to do if we're performing a full scan
        if full:

            # -- As a performance optimisation we first add all the
            # -- dates to the db, so get a list of all the tags
            all_tags = list()
            mapped_tags = dict()

            for scanned_identifier in scanned_identifiers:
                element = self.get(scanned_identifier)

                if not element:
                    continue

                # -- Get the tags for this element
                expected_tags = element.mandatory_tags()

                # -- Add them to our tracking variables
                all_tags.extend(expected_tags)
                mapped_tags[scanned_identifier] = expected_tags

            # -- Now we add all those tags into the db under a single
            # -- connection
            with ConnectionContext(self.identifier, commit=True) as ctxt:
                for tag in set(all_tags):
                    self._execute(
                        ctxt,
                        'tag_insert',
                        replacements={
                            '$(TAG)': tag,
                        },
                    )

            # -- With the tags all added, we now create the links between
            # -- the tags and the identifiers.
            with ConnectionContext(self.identifier, commit=True) as ctxt:
                for scanned_identifier in mapped_tags:
                    for tag in mapped_tags[scanned_identifier]:
                        try:
                            self._execute(
                                ctxt,
                                'tag_connect',
                                replacements={
                                    '$(IDENTIFIER)': scanned_identifier,
                                    '$(TAG)': tag,
                                },
                            )
                        except sqlite3.IntegrityError:
                            pass

            # -- If the project allows for data cleanup, lets perform
            # -- that now
            for identifier in self.find(None):
                for scan_plugin in self._scan_factory.plugins():
                    if scan_plugin.check(identifier) == scan_plugin.NOT_VALID:
                        self.remove(identifier)
                        break

        # -- Emit the fact that the scan is now complete
        self.scan_complete.emit()

        # -- Log the completion
        constants.log.info('Scan Complete : %s' % locations)

        return scanned_identifiers

    # --------------------------------------------------------------------------
    def explore(self, location):
        """
        This will return the above and below for the given location

        :param location:
        :return:
        """
        # -- Cycle over all our scan plugins
        for plugin in self._scan_factory.plugins():
            if plugin.can_represent(location):
                return plugin.above(location), plugin.below(location)

        return list(), list()

    # --------------------------------------------------------------------------
    def get(self, identifier):
        """
        This will create a composite binding of a DataElement plugin, bringing
        together all the plugins which can viably represent the data.

        :param identifier: Data Identifier to be passed to the DataElement
            plugins.
        :type identifier: str

        :return: DataElement composite 
        """
        template = None

        # -- Cycle all the data plugins and composite them together
        # -- if they can represent the given data
        for data_plugin in self._data_plugins:
            if data_plugin.can_represent(identifier):

                template = template or DataElement(
                    identifier,
                    self,
                )

                # -- Bind this plugin to the template
                template.bind(data_plugin(identifier, self))

        # -- If in debug mode, log the result
        constants.log.debug('Compounded %s to %s' % (identifier, template))

        return template

    # --------------------------------------------------------------------------
    def _execute(self, ctxt, command, replacements=None):
        """
        Private method which all sql queries should be routed through. This
        ensures a consistent result and suite of reporting.

        :param ctxt: ConnectionContext (all _execute calls should be done
            within a ConnectionContext to aid performance).

        :param command: The sql command name to run

        :param replacements: Any search and replace strings to process
            on the sql command
        :return:
        """
        # -- Get the statement
        statements = self._commands[command]

        # -- We must execute our sql in individual statements
        for single_statement in statements:

            # -- Create the replacements
            if replacements:
                for k, v in replacements.items():
                    single_statement = single_statement.replace(k, str(v))

            # -- Check if we need to print
            constants.log.debug('\n' + ('-' * 100))
            constants.log.debug(single_statement)

            try:
                ctxt.cursor.execute(single_statement)

            except sqlite3.Error:
                constants.log.debug(sys.exc_info())
                constants.log.debug('Unable to execute : %s' % single_statement)
                return list()

    # --------------------------------------------------------------------------
    def _command_dict(self):
        """
        This generates a dictionary whereby the key is the sql command name
        and the value is the sql data.

        :return: dict
        """
        command_dict = dict()

        for command in os.listdir(self._COMMAND_DIR):
            with open(os.path.join(self._COMMAND_DIR, command)) as f:
                command_dict[command[:-4]] = [
                    statement.strip()
                    for statement in f.read().split(';')
                    if statement.strip()
                ]
        return command_dict

    # --------------------------------------------------------------------------
    @classmethod
    def _conform(cls, item):
        """
        Takes in a path and ensures its correctly conformed for use
        within fracture.

        :param item: str

        :return: str
        """
        return item.replace('\\', '/')


# ------------------------------------------------------------------------------
class ConnectionContext(object):
    """
    This is a contextual class which handles the connection and cursor
    mechanisms. Its intended to be an optimisation to allow for multiple
    calls to occur without connection overheads.
    """
    # --------------------------------------------------------------------------
    def __init__(self, identifier, commit=False, get=False):
        self.identifier = identifier
        self.connection = None
        self.cursor = None
        self.results = []

        self.commit = commit
        self.get = get

    # --------------------------------------------------------------------------
    def __enter__(self):

        self.connection = sqlite3.connect(self.identifier)
        self.cursor = self.connection.cursor()
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, exc_type, exc_val, exc_tb):

        # -- If we need to get, call a fetch
        if self.get:
            self.results = self.cursor.fetchall()

        if self.commit:
            self.connection.commit()

        self.connection.close()


# ------------------------------------------------------------------------------
def icon(icon_name='fracture'):
    """
    Returns the fracture icon

    :param icon_name: Name of the icon you want to request
    :return:
    """
    return os.path.join(
        os.path.dirname(__file__),
        '_res',
        '%s.png' % icon_name,
    )
