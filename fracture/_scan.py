"""
This module holds the abstract class which defines the structure for a
scan plugin.
"""


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
class ScanProcess(object):
    """
    This type defines how data is found. This may be done by cycling folders
    and files or it could be scraping a REST API or pulling information from
    a third party source. 
    """
    scan_type = ''

    IS_VALID = 0
    NOT_VALID = 1
    UNKNOWN = 2

    # --------------------------------------------------------------------------
    @classmethod
    def can_represent(cls, location):
        """
        This is used to allow the plugin to determine if it thinks it is
        able to scrape the given data source identifier or not.

        :param location: Location Identifier. This could be a url, or a filepath
            or a uuid etc.
        :type location: string

        :return: bool
        """
        return False

    # --------------------------------------------------------------------------
    @classmethod
    def identifiers(cls, location, skip_pattern, recursive=True):
        """
        This will return a list of data identifiers found in the given data 
        locations.

        NOTE: This should always yield results!

        :param location: Location to scan
        :type location: str

        :param skip_pattern: This is a regular expression object which, if
            matched on a location should be skipped.
        :type skip_pattern: regex

        :param recursive: If True all locations below the given location
            will also be scanned, otherwise only the immediate location will
            be scanned
        :type recursive: True

        :return: generator
        """
        return list()

    # --------------------------------------------------------------------------
    @classmethod
    def above(cls, location):
        """
        Returns all the search locations above the current location. If there is
        no location above, or the concept of 'above' makes no sense for your
        scan plugin you may return an empty list.

        :return:
        """
        return list()

    # --------------------------------------------------------------------------
    @classmethod
    def below(cls, location):
        """
        This will return all the search locations immediately below the given
        location. If there is no location above, or the concept of 'above'
        makes no sense for your scan plugin you may return an empty list.

        :param location:
        :return:
        """
        return list()

    # --------------------------------------------------------------------------
    @classmethod
    def check(cls, identifier):
        """
        Given an identifier, this should check whether the identifier is
        still considered valid or not - or whether it cannot make that
        assumption. 

        This should return one of the three following:

            ScanProcess.IS_VALID
                If the identifier is still active and valid, this should
                be returned

            ScanProcess.NOT_VALID
                If the identifier should no longer be considered within
                fracture this should be returned

            ScanProcess.UNKNOWN
                If the identifier is not digestable by this process for
                any reason this should be returned.

        :return: int 
        """
        return cls.UNKNOWN
