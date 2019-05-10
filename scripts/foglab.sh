#!/bin/bash
LOCALACTIONSDIR=/opt/foglab/localActions
USER=root

export ANSIBLE_LOCALHOST_WARNING=false

help () {
  cat << EOF
Usage:
  -s [on|off]  Enable or disable the swap
  -i [on|off]  Enable or disable the eth1 interface
  -b "base ip" The base ip segment to use. Ex: 192.168.55
  -h  Help

EOF
}

# $1 => action name
# $2 => action tag 
# $3 => action variables
action () {
  echo "$1 $2 $3"
  ansible-playbook "${LOCALACTIONSDIR}/$1.yml" --tags "$2" --extra-vars "$3"
}

# $1 => type of validation
# $2 => data to validate
validate () {
  case "$1" in
    oo) 
      if [ "$2" != "on" ] && [ "$2" != "off" ]; then
        echo "Invalid option '$2'. Should be [on|off]"
        exit 1
      fi
    ;;
    baseip)
      echo "hi"
      if ! [[ $2 =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        echo "Invalid base ip '$2'. Ex: 192.168.55"
        exit 1
      fi
    ;;
  esac
}

while getopts "hs:i:b:" flag; do
  case "${flag}" in
    s) validate "oo" "${OPTARG}" && action "swap" "${OPTARG}";;
    i) validate "oo" "${OPTARG}" && action "eth1" "${OPTARG}";;
    b) validate "baseip" "${OPTARG}" && action "lxdip" "all" "base_segment=${OPTARG}";;
    h) help; exit 0;;
    \?) echo "Invalid Option: -${OPTARG}" 1>&2; exit 1;;
  esac
done

shift $((OPTIND - 1))

if [ $OPTIND -eq 1 ]; then echo "No options were passed. Try -h for help."; exit 1; fi



