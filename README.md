# Features
you can create new menus for rightclick in Nautilus with one extension and multiple commands in one yaml file:

- you can configure the labels, icons, tips of items and subitems
- set your command with template which will be executed when the user clicks
- set your conditions when the item or tree is executed based on the selection of user and os

# How to use

## Basic Configuration

Before you start make sure to install `nautilus-python` with `sudo apt-get install python-nautilus``


Create your yaml file for the items in `HOME_DIR + "/.config/nautilus-poem/items.yml"`

```
- label: Best right click ever
  tip: Click me now
  subitems:
     - label: 2nd level right
- label: Flatten folder
  conditions:
     - "directory_count > 0"
  click: /do-something.sh {POEM_FILES}
```

## Execute your item

- you can use the environment vars to template your command
- the name of the vars are documentated currently in code
- you can also use the Environment vars of system
- access the vars like python format https://docs.python.org/3/library/string.html#format-string-syntax : `{POEM_FILES}` `{POEM_FILES[0]}`

```
- label: Flatten folder
  click: /do-something.sh {POEM_FILES}
```


## Set conditions for the item (or tree)

- if no condition is added, it is always displayed
- else add your conditions by the vars of the code coming from the selection and the os

```
- label: Flatten folder
  - "directory_count > 0"
  click: /do-something.sh {POEM_FILES}
```


## Debug or Developing

- create your yaml config for the settings:`HOME_DIR + "/.config/nautilus-poem/config.yml"` and put `DEBUG: True`
- give permission for logging: `sudo chmod -R 0773 /var/log/nautilus/nautilus-poem.log`
- to restart nautilus use: `NAUTILUS_PYTHON_DEBUG=misc nautilus -q`

# Future ideas

- implement background items
- connect to python click / pyproject.toml
- try the icons
- test the extension
- implement other events then click?