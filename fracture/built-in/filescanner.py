"""
By default we ship with a file scanner, as this is - in most cases - the type
of data most users will be using
"""
import os
import fracture


# ------------------------------------------------------------------------------
class ScanProcess(fracture.ScanProcess):
    scan_type = 'file_scanner'

    # --------------------------------------------------------------------------
    @classmethod
    def can_represent(cls, location):
        """
        Determines whether this data plugin can represent the given identifier

        :param location: Data Identifier. This could be a url, or a filepath
            or a uuid etc.
        :type location: string

        :return: bool
        """
        if os.path.exists(location):
            return True
        return False

    # --------------------------------------------------------------------------
    @classmethod
    def identifiers(cls, location, skip_pattern, recursive=True):

        if recursive:
            for root, _, filenames in os.walk(location):
                for filename in filenames:
                    result = os.path.join(root, filename).replace('\\', '/')

                    if not skip_pattern or not skip_pattern.search(result):
                        yield result

        else:
            for filename in os.listdir(location):
                result = os.path.join(location, filename).replace('\\', '/')

                if not skip_pattern or not skip_pattern.search(result):
                    yield result
                    

    # --------------------------------------------------------------------------
    @classmethod
    def above(cls, location):
        location = location.replace('\\', '/')
        parts = location.split('/')

        folders = list()

        for i in range(len(parts)):
            folder_path = '/'.join(parts[:-i])

            if folder_path and not folder_path.endswith(':'):
                folders.append(folder_path)

        return folders

    # --------------------------------------------------------------------------
    @classmethod
    def below(cls, location):
        folders = list()
        for folder in os.listdir(location):
            folder_path = os.path.join(location, folder).replace('\\', '/')

            if os.path.isdir(folder_path):
                folders.append(folder_path)

        return folders

    # --------------------------------------------------------------------------
    @classmethod
    def check(cls, identifier):
        """
        Checks the list of given identifiers and return any which should
        be cleaned/removed.

        :param identifier: 
        :return: 
        """
        if len(identifier) < 2:
            return cls.UNKNOWN

        if identifier[1] != ':':
            return cls.UNKNOWN

        if identifier[2] != '\\' and identifier[2] != '/':
            return cls.UNKNOWN

        if not os.path.exists(identifier):
            return cls.NOT_VALID

        return cls.IS_VALID

