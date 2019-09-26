# kismet_baseline
This takes a kismet db and a time interval in seconds, and returns a list of all macs (devices)
that are present in every interval of the speficied size.

Use 1: static monitoring and you want to filter out all devices that are there all the time (APs, TV sets, etc.)
Use 2: mobile monitoring and you want to filter out your devices, i.e., were with you all the time
Use 3: identify devices that are always present for further shenanigans

I typically use something around 300 seconds for the interval, but... if it's a longer capture
you can go with something quite larger. Play around with it.
