"""
This module contains the DataElement class. This is the class which
all data elements inherit from and their compositions are utilised to
represent data.
"""
import xcomposite


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
class DataElement(xcomposite.Composition):
    """
    A DataElement is a block of functionality and an interface to a
    piece of data. A piece of data can be represented by multiple
    DataElements in a composite form.
    """

    # -- This allows you to define a unique identifier for the type
    # -- of plugin this is. When querying a return from fracture this will
    # -- form part of the composition string.
    data_type = ''

    # -- This is useful if you plan to re-implement a plugin with the same
    # -- data_type as another plugin. In this way only the highest version
    # -- will be used.
    version = 1

    # -- Priority to determines the order of class composition. A higher
    # -- values means that the class will be composited first. This can
    # -- have an effect on methods decorated with xcomposite.First etc.
    priority = 1

    # --------------------------------------------------------------------------
    def __init__(self, identifier, db):
        super(DataElement, self).__init__()

        self.db = db
        self._identifier = identifier

    # --------------------------------------------------------------------------
    def __repr__(self):
        base_repr = super(DataElement, self).__repr__()
        return base_repr.replace(
            'DataElement',
            'DataElement: %s' % (
                self._identifier,
            )
        )

    # --------------------------------------------------------------------------
    # -- The following 8 methods below should be re-implemented by your
    # -- plugin. You can however omit the decoration of these functions

    # --------------------------------------------------------------------------
    @classmethod
    def can_represent(cls, identifier):
        """
        Determines whether this data plugin can represent the given identifier

        :param identifier: Data Identifier. This could be a url, or a filepath
            or a uuid etc.
        :type identifier: string

        :return: bool
        """
        return False

    # --------------------------------------------------------------------------
    @xcomposite.first_true
    def icon(self):
        """
        This will return the icon for the DataElement. If multiple DataElements
        are bound to represent a piece of information then the first to return
        a non-false result will be taken.

        :return: string 
        """
        return None

    # --------------------------------------------------------------------------
    @xcomposite.first_true
    def label(self):
        """
        Returns the label or name for the DataElement. This is typically 
        considered a 'pretty' name, or short name and does not need to be
        unique.

        If multiple DataElements are bound to represent a piece of information
        then the first to return a non-false result will be taken.

        :return: string 
        """
        return None

    # --------------------------------------------------------------------------
    @xcomposite.extend_unique
    def mandatory_tags(self):
        """
        Returns any tags that should always be assigned to this data element.
        In a situation where multiple DataElements are bound then the combined
        results of all the mandatory tags are used.

        :return: list(str, str, ...)
        """
        return None

    # --------------------------------------------------------------------------
    @xcomposite.update_dictionary
    def functionality(self):
        """
        This exposes per-data functionality in the form of a dicitionary where
        the key is the string accessor, and the value is the callable.

        In a situation where multiple DataElements are bound then a single
        dictionary with all the entries combined is returned.

        :return: dict(label: callable,)
        """
        return xcomposite.Ignore

    # --------------------------------------------------------------------------
    # -- NO METHODS BELOW NEED TO BE RE-IMPLEMENTED

    # --------------------------------------------------------------------------
    def identifier(self):
        """
        This returns the identifier of this data element.

        :return: string 
        """
        return self._identifier

    # --------------------------------------------------------------------------
    def tags(self):
        """
        Returns a list of all the tags assigned to this DataElement

        :return: None 
        """
        return self.db.tags(self._identifier)

    # --------------------------------------------------------------------------
    def tag(self, tags):
        """
        Assigns the given tags to this data element

        :param tags: This can be a single string tag, or a list of tags

        :return: None 
        """
        return self.db.tag(self._identifier, tags)

    # --------------------------------------------------------------------------
    def untag(self, tags):
        """
        Un-assigns the given tags from this data element

        :param tags: This can be a single string tag, or a list of tags

        :return: None 
        """
        return self.db.untag(self._identifier, tags)
