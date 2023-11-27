[![Tests](https://github.com/mutantsan/ckanext-admin-panel/workflows/Tests/badge.svg?branch=main)](https://github.com/mutantsan/ckanext-admin-panel/actions)

# ckanext-admin-panel

Next generation admin interface for CKAN.

## Content

* [Todo](#todo)
* [Requirements](#requirements)
* [Installation](#installation)
* [Config settings](#installation)
* [Developer installation](#developer-installation)
* [Tests](#tests)
* [License](#license)

## TODO
This extension is under development, so there are many things to do:

- CKAN forms:
 - What do we want to do, if we are editing an entity from admin panel? Use default form or replace it with an admin version?
- Users:
 - Add `User edit` page
- Recent log messages:
 - We have  some types, that we don't want to include in list. E.g xloader resources. Research what is better to do with them.
 - Rework the pagination approach, because the current naive one will work very slow on big amount of data
- Rewrite `user_list` action. Currently it's just a copy of contrib one with one small change. Maybe it's a good idea to write
  our own versatile version.
- Think about configuration section pages. Do we need a separate page for a section?
- Work on `Extensions` page. What do we want: replace `status_show`. This page should be more informative. Show here what
  extensions we are using with the respective versions. For now we don't have a standartized mechanism to retrieve versions
  from extensions, think about it.
- Work on `Available updates?` page. Show user if he could upgrade an extension or CKAN to a new version.
- Work on `Appearance` page. TODO
- Work on `Help` page. TODO

## Requirements

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | no          |
| 2.10         | yes         |
| 2.11         | yes         |



## Installation

To install ckanext-admin-panel:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com/mutantsan/ckanext-admin-panel.git
    cd ckanext-admin-panel
    pip install -e .
	pip install -r requirements.txt

3. Add `admin_panel admin_panel_cron` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Config settings

None at present

## Developer installation

To install ckanext-admin-panel for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/mutantsan/ckanext-admin-panel.git
    cd ckanext-admin-panel
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini


## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
