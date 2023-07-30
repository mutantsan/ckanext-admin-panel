[![Tests](https://github.com/mutantsan/ckanext-admin-panel/workflows/Tests/badge.svg?branch=main)](https://github.com/mutantsan/ckanext-admin-panel/actions)

# ckanext-admin-panel

Next generation admin interface for CKAN.

## Content

* [Requirements](#requirements)
* [Installation](#installation)
* [Config settings](#installation)
* [Developer installation](#developer-installation)
* [Tests](#tests)
* [Releasing a new version](#releasing-a-new-version)
* [License](#license)

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

3. Add `admin-panel` to the `ckan.plugins` setting in your CKAN
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


## Releasing a new version

If ckanext-admin-panel should be available on PyPI you can follow these steps to publish a new version:

1. Update the version number in the `setup.py` file. See [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) for how to choose version numbers.

1. Make sure you have the latest version of necessary packages:
   ```sh
   pip install --upgrade build twine
   ```


1. Tag the new release of the project on GitHub with the version number from
   the `setup.py` file. For example if the version number in `setup.py` is
   0.0.1 then do:
   ```sh
   git tag v0.0.1
   git push --tags
   ```

1. Update changelog:
   ```sh
   make changelog
   ```

1. Create a source and binary distributions of the new version:
   ```sh
   python -m build && twine check dist/*
   ```

   Fix any errors you get.

1. Upload the source distribution to PyPI:
   ```sh
   twine upload dist/*
   ```

1. Commit any outstanding changes:
   ```sh
   git commit -a
   git push
   ```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
