The matrix server has to be scaled properly to take advantage of an SMP
system.  Ideally you need as many generic worker threads as there are CPUs.
This is achieved by systemd enabling and disabling the matrix-synapse-worker@N
services.

However, to plumb the added services in, each one needs a special config
file with a different listening port in the /etc/matrix-synapse/workers
directory (under generic_workerN.yaml)

Finally the newly started/stopped worker threads need adding/removing
from the nginx upstream generic-worker ip_hash entry.  The vehicle
that distributes work to the threads is that ip_hash. See

/etc/nginx/sites-enabled/scaled

To read more about all of this, refer to

https://blog.hansenpartnership.com/linux-plumbers-conference-matrix-and-bbb-integration/

Note: when inflating on Linode do not resize the disk.  We don't use
much disk space anyway and if you increase it, you'll have to
manually shrink it again before you can deflate the server
