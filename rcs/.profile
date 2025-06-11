# ~/.profile: executed by Bourne-compatible login shells.

if [ "$BASH" ]; then
  if [ -f ~/.bashrc ]; then
    . ~/.bashrc
  fi
fi

/usr/local/bin/tty1_login
/usr/local/bin/hwdata
/usr/local/bin/netdata

mesg n
