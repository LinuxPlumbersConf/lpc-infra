# BBB

BBB deploymnet on a linode server is automated with
[scripts/bbb-deploy.sh](https://github.com/LinuxPlumbersConf/lpc-infra/blob/main/scripts/bbb-deploy.sh).
It relies on a custom bbb-html5.deb package containig JavaScript with
modications for matrix support and lpc.tar.gz archive containing LPC backround,
BBB configuration and EmbeddedRiot files.

BBB deployment uses bbb-install.sh linked from [BigBlueButton installation
docs](https://docs.bigbluebutton.org/2.7/administration/install/). The script
downloads latest .deb packages. This means that the custom bbb-html5.deb with
matrix support should be build from the latest BBB sources.

## bbb-html5.deb
* rebase Matirx chat intergration on latest BBB, required for compatability
  with BBB version installed by bbb-install.sh
* build bbb-html5.deb; in bigbluebutton source directory run:
```
./build/setup.sh bbb-html5
```
* create a release at https://github.com/LinuxPlumbersConf/bigbluebutton
* upload bbb-html5_<version>.deb to that release

## lpc.tar.gz
* download lpc.tar.gz from last year's release
* add virtual background for the current year
* update favicon.ico
* update the default presentation
* repack the archive and upload it to the release created for the current year

## Servers
* spawn several BBB serves in linode
* update DNS records for the new servers
* update rDNS on linode
* deploy BBB with bbb-deploy.sh
* note secret with
```
bbb-conf --secret
```

# Matrix
* create rooms for new MCs and tracks

# Indico
* Link matrix rooms to sessions
  - Matrix room id: internal room ID, e.g. `![:alnum:]{18}:lpc.events`
  - Matrix URL: room URL, e.g. https://matrix.to/#/#refereed-track:lpc.events

# ldap
```
while (new people register):
	export registration list to CSV
	run csv2ldap.py
	update admin/moderator permissions if required
```

# lpcfe
* Update sponsors on meet.lpc.events
  - https://github.com/LinuxPlumbersConf/lpcfe/blob/master/page.ptl
* Update `servers` with hostnames and secrets of the new servers
* Update `sessions` with generate-sessions.py
* Update `rooms` to match between physcal rooms to BBB servers
* Update `tracks` to match between tracks and matrix rooms
