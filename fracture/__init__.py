"""
# Overview

Fracture is a lightweight and flexible data management system. It allows
you to interact with data through a trait compositing mechanism, whilst
also exposing the ability to quickly query and access information
about the data you're exploring.

# How it works

You start by creating a fracture.Project. The project file is where all
the metadata and look up tables are stored - allowing you to easily search
for data assets as well as find changes.

Fracture comes built-in with a file searching mechanism, but you can extend
this with your own search mechanisms too. For instance, if you have data
on an FTP, or within Source Control and you want to add that data to the
project without having to have it physically on disk you're able to do so
by implementing a fracture.ScanProcess plugin.

Finally, and probably the most important is the DataElement. This is a class
which you can use to express the functionality of data. Rather than having a
1:1 relationship between a DataElement class and a data type the DataElement
class supports class compositing. This allows for a piece of data to be
represented by more than one class simultaneously.

# Examples

This example uses the ```dino_example``` data which you can download from
https://github.com/mikemalinowski/fracture. 

To start with, we create a fracture project. To do this we must specify
two pieces of information, the first being where we want to save our 
project file and the second being the locations where we want fracture
to look for Scan and Data Plugins.

```python
import os
import fracture

project = fracture.create(
    project_path=os.path.join(current_path, '_dino.fracture'),
    plugin_locations=[os.path.join(current_path, 'plugins')]
)
```

This returns a fracture.Project instance which we can then start interacting
with, for instance we can define locations where the project should start
looking for data:

```python
# -- Tell the project where to look for data
project.add_scan_location('/usr/my_data'))
```

Finally, with the project made, and at least one search location added we
can initiate a search...

```python
# -- Now we initiate a scan. This will cycle over all the
# -- scan locations and scrape them for data
project.scan()
```

Scanning is the process of running over all the scan plugins - of which there
is always at least one (the file scraper), and populating the project with
information about each piece of data which is found. The process is pretty
quick and the amount of data stored is minimal - primarily just the identifier
such as the path along with any tags as defined by any DataElement composites
which can represent that data.

With the project populated we can now start querying the project for
data

```python
# -- Now we have scanned we can start to run queries over data
# -- very quickly. We can search by tags, or use the special
# -- * wildcard
for item in project.find('*'):

    # -- By default we get string identifiers back from a find, as
    # -- this is incredibly quick. However, we can ask for the data
    # -- composite representation of the item. A data composite is
    # -- a composition of all the data plugins which can represent
    # -- this identifier.
    item = project.get(item)

    # -- Print the identifier, and the item (which also shows the
    # -- class composition)
    print(item.identifier())
    print('\t%s' % item)

    # -- We can start interacting with this data, calling
    # -- functionality will return a dictionary of all the
    # -- functionality exposed by all the data plugins representing
    # -- this item
    for k, v in item.functionality().items():
        print('\t\t%s = %s' % (k, v))
```

The process of querying is very quick, even for reasonably large data sets. In
the example above we're then asking the project to 'get' the item. This process
take the identifier and binds all the relevent DataElements together which
can possibly represent the data.

Binding is particularly useful when there is no obvious hierarchy between
two elements. For instance, in the ```dino_example``` data set we have a
trait which is ```carnivore``` and a trait which is ```herbivore```. There
is no hierarchical relationship between the two, but an omnivore would need
both. By using class compositing we avoid complex multi-inheritence situations.

Using this same mechanism, if we know the locator of a piece of information,
such as a file path, we can get the composited class directly without having
to run a query, as shown here:

```python
# -- We do not have to utilise the find method to get access to data,
# -- and in fact we can get a Composite representation of data even
# -- if that data is not within our scan location.
data = project.get('/usr/my_data/my_file.txt')
```

For a full demo, download the ```dino_example``` and run main.py

# Data Composition

As mentioned in the examples, we use class composition to bind traits together
to represent data. This means we can have small, self contained traits which
do not need rigid hierarchical structures designed for them.

There are three main composited methods in the DataElement class, specifically:

* label : The first call that returns a positive result is taken
* mandatory_tags : All the lists are collated from all compositions and made unique
* functionality : All dictionaries are combined into a single dictionary
* icon : The first call that returns a positive result is taken

Given the ```dino_example``` files, the velociraptor.png file, when passed
to ```project.get('/usr/my_data/.../velociraptor.png')``` is expressed
as a class formed of the following traits: [Carnivore; File; Image;] where each
trait can expose its own information.

An implementation of a DataElement plugin looks like this:

```python
import re
import fracture

# -- All plugins must inherit from the fracture.DataElement class in order
# -- to be dynamically picked up.
class CarnivoreTrait(fracture.DataElement):

    # -- The data type is mandatory, and is your way of
    # -- denoting the name of this plugin
    data_type = 'carnivore'

    # -- These two lines are not at all required and are here
    # -- just to make performance better
    _split = re.compile('/|\.|,|-|:|_', re.I)
    _has_trait = re.compile('(carnivore|omnivore).*\.', re.I)

    # --------------------------------------------------------------------------
    # -- This method must be re-implemented, and its your oppotunity to
    # -- decide whether this plugin can viably represent the given data
    # -- identifier.
    # -- In this example we use a regex check, but it could be anything
    # -- you want. The key thing to remember is that this is called a lot,
    # -- so performance is worth keeping in mind.
    @classmethod
    def can_represent(cls, identifier):
        if CarnivoreTrait._has_trait.search(identifier):
            return True
        return False

    # --------------------------------------------------------------------------
    # -- This is your way of exposing functionality in a common and consistent
    # -- way. If you know the data types you can of course call things directly
    # -- but this is a good catch up consistent way of exposing functionality
    # -- and is typically harnessed by user interfaces.
    def functionality(self):
        return dict(
            feed_meat=self.feed_meat,
            ),
        )

    # --------------------------------------------------------------------------
    # -- This should return a 'nice name' for the identifier
    def label(self):
        return os.path.basename(self.identifier())

    # --------------------------------------------------------------------------
    # -- As fracture heavily utilises tags, this is your way of defining a
    # -- set of tags which are mandatory for anything with this trait
    def mandatory_tags(self):
        return ['carnivore', 'meat', 'hunter']

    # --------------------------------------------------------------------------
    # -- This is here just as a demonstration of a callable function which
    # -- which can be accessed on the trait
    def feed_meat(self):
        print('Would feed this creature some meat...')
```

By placing a trait plugin anywhere within the plugin locations you define
for your project will immediately make it accessible.


## ScanProcess

By default fracture comes with one built-in scan plugin which handles file
scanning, so that is a good example when wanting to write your own - if you 
have need to do so.

This plugin type defines how to find data. If your data is files on a disk
such as those in the example above then your scan plugin may do little more
than cycle directories and yield file paths.

Alternatively if you're caching data from a REST API you might be utilising
requests within the scan process and feeding back URL's.

# Origin

This library is a variation on the tools demonstrated during
GDC2018 (A Practical Approach to Developing Forward-Facing Rigs, Tools and
Pipelines), which can be explored in more detail here:
https://www.gdcvault.com/play/1025427/A-Practical-Approach-to-Developing

Slide 55 onward explores this concept. It is also explored in detail
on this webpage:
https://www.twisted.space/blog/insight-localised-asset-management

"""
from ._project import icon
from ._project import Project
from ._scan import ScanProcess
from ._element import DataElement

from ._access import create
from ._access import load
from .constants import log
