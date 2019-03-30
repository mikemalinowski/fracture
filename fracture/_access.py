"""
These are the primary entry points which we expect users to
access and interact with fracture projects.
"""
from . import _project


# ------------------------------------------------------------------------------
def create(project_path, plugin_locations):
    """
    This will generate a new fracture project and return the project
    instance.

    :param project_path: Path to the location you want to save the project
        path.
    :type project_path: str

    :param plugin_locations: List of locations to search for plugins

    :return: fracture.Project instance
    """
    if not project_path.endswith('fracture'):
        project_path += '.fracture'

    project = load(project_path)
    project.create()

    for location in plugin_locations:
        project.add_plugin_location(location)

    return project


# ------------------------------------------------------------------------------
def load(project_path):
    """
    Loads the given project and returns a Project Instance
    
    :param project_path: Path to the location you want to save the project
        path.
    :type project_path: str

    :return: fracture.Project instance
    """
    return _project.Project(project_path)
