System: raspbian os lite

Setup cage as systemd:
- copy /etc/systemd/system/cage@.service
- copy /etc/pam.d/cage
- copy /usr/local/bin/start_cage and chmod 755
- adduser cage
- systemctl enable cage@tty1.service
- systemctl set-default graphical.target