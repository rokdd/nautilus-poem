#!/bin/bash
# To install the script use the following command:
# sudo 
# Terminal colors

red=`tput setaf 1`
green=`tput setaf 2`
yellow=`tput setaf 2`
blue=`tput setaf 4`
gray=`tput setaf 2`
reset=`tput sgr0`

curl='/usr/bin/curl'

# Prints a line with color using terminal codes
style_print() {
  echo -e "${!2}$1${reset}"
}

style_print "Start install.." 'gray'
#alternative way to download should not be nessary

$curl -H 'Cache-Control: no-cache' --silent https://raw.githubusercontent.com/rokdd/nautilus-poem/master/nautilus-poem.py > /usr/share/nautilus-python/extensions/nautilus-poem.py
style_print "Installed nautilus-poem" 'green'
mkdir -p ~/.config/nautilus-poem/
$curl -H 'Cache-Control: no-cache' --silent https://raw.githubusercontent.com/rokdd/nautilus-poem/master/items.yml > ~/.config/nautilus-poem/items.yml
style_print "Created config in ~/.config/nautilus-poem/
style_print "If cmd is not working, reload the nautilus with 'nautilus -q'. For help or getting started visit github.com/rokdd/nautilus-poem"
exec $SHELL