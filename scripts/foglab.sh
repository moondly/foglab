#!/bin/bash
LOCALACTIONSDIR=/opt/foglab/localActions
USER=root

help () {
  cat << EOF
Usage:
  -s [on|off]  Enable or disable the swap
  -i [on|off]  Enable or disable the eth1 interface
  -h  Help

EOF
}

# $1 => action name
# $2 => action tag 
action () {
  ansible-playbook ${LOCALACTIONSDIR}/$1.yml --tags $2
}

# $1 => type of validation
# $2 => data to validate
validate () {
  case "$1" in
    oo) if [ "$2" != "on" ] && [ "$2" != "off" ]; then
          echo "Invalid option '$2'. Should be [on|off]"
          exit 1
        fi
        ;;
  esac
}

while getopts "hs:i:" flag; do
  case "${flag}" in
    s) validate "oo" "${OPTARG}" && action "swap" "${OPTARG}";;
    i) validate "oo" "${OPTARG}" && action "eth1" "${OPTARG}";;
    h) help; exit 0;;
    \?) echo "Invalid Option: -${OPTARG}" 1>&2; exit 1;;
  esac
done

shift $((OPTIND - 1))

if [ $OPTIND -eq 1 ]; then echo "No options were passed. Try -h for help."; exit 1; fi


