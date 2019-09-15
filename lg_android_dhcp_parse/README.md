# lg_android_dhcp_parse
Parse dhcp ack packets found in Android phones. LG phones will have many. Samsung has up to 10. Other phones usually just have the last one.

They are found at /data/misc/dhcp.

This examples has the dhcp ack files in the dhcpack folder, but you can change base_path in the code as you wish. The last-modified ate on the dhcp ack file determines the timestamp when it occurred, so if you use the function some other way, you may have to supply a timestamp.

Oh, yeah, this was written in Python2 because I wrote it a while ago, so...
