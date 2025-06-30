# ~/.bashrc: executed by bash(1) for non-login shells.

#export PS1='\h:\w\$ '
export PS1='\[\033[01;31m\]\u\[\033[01;33m\]@\[\033[01;32m\]\h \[\033[01;33m\]\w \[\033[01;35m\]\$ \[\033[00m\]'
umask 022

export LS_OPTIONS='--color=auto -h'
eval "`dircolors`"

alias ls='ls $LS_OPTIONS'
alias ll='ls $LS_OPTIONS -l'
alias l='ls $LS_OPTIONS -lA'
alias ..='cd ..'
alias ...='cd ../..'
source /root/.oldroot/nfs/bash_aliases
source /root/.oldroot/nfs/functions.sh
