#!/bin/bash -eu

# Download and install BBB with LPC customizations on a clean Ubuntu 20.04
# Linode

if [ $# -lt 1 ]; then
    echo "USAGE: $0 <hostname>"
    exit 1
fi;

host=$1
release=${2:-"v2.7.1-lpc2023"}

# Debian package of bbb-html5 with matrix chat
deb="bbb-html5_lpc.deb"
deb_url="https://github.com/LinuxPlumbersConf/bigbluebutton/releases/download/$release/$deb"

# LPC configuration tweaks, visual assets and riot-embedded
#
# /etc/bigbluebutton/bbb-html5.yml
# /usr/share/meteor/bundle/programs/web.browser/app/resources/images/virtual-backgrounds/
# /var/www/bigbluebutton-default/assets/riot-embedded/
# /var/www/bigbluebutton-default/assets/favicon.ico
# /var/www/bigbluebutton-default/assets/default.pdf
lpc_files="lpc.tar.gz"
lpc_files_url="https://github.com/LinuxPlumbersConf/bigbluebutton/releases/download/$release/$lpc_files"

bbb_install_url="https://raw.githubusercontent.com/bigbluebutton/bbb-install/v2.7.x-release/bbb-install.sh"

hostnamectl set-hostname $host

apt-get -y install wget

mkdir -p $HOME/bbb-deploy
cd $HOME/bbb-deploy

for url in $deb_url $lpc_files_url $bbb_install_url; do
    wget $url
done

bash bbb-install.sh -w -v focal-270 -s $host.lpc.events -e mike.rapoport@gmail.com
sleep 20

#creates a copy of the meteor configuration files (with the keys, urls, ...)
cp /usr/share/meteor/bundle/programs/server/assets/app/config/settings.yml $host.default.settings.yml

bbb-conf --stop

# installs bbb-html5 with matrix
apt-get -y install $HOME/bbb-deploy/$deb
tar -C / -xzf $HOME/bbb-deploy/$lpc_files

# runs bbb-install.sh to fixup configuration files
bash bbb-install.sh -w -v focal-270 -s $host.lpc.events -e mike.rapoport@gmail.com

# Runs status check just because the arrows are funny
bbb-conf --status

# Prints the secret on the screen for everyone in the room to see
bbb-conf --secret
