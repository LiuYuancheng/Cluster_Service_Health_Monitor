# Cluster Service Health Monitor

**Program Design Purpose** : we want to create a monitor system which can regular check the availability of each nodes (services) used in a cyber-range/cyber-exercise without do much change of the routing/config of whole network switches or install additional libs.  





| Firewall      |      |
| ------------- | ---- |
| Total service | 6    |

|      |      |      |      |
| ---- | ---- | ---- | ---- |
|      |      |      |      |



| Probed target service cluster | Node number | Service checked                                              |
| ----------------------------- | ----------- | ------------------------------------------------------------ |
| Firewall                      | 1           | icmp, ssh, http-alt, http-proxy, ident, blackice-icecap, http, https |
| Openstack                     | 4           | icmp, ssh, http-alt, upnp, mysql, https, vnc                 |
| Kypo-Crp                      | 3           | icmp, ssh, https, vnc, X11, X11:1-Win                        |
| CTF                           | 2           | icmp, ssh, http, vnc, X11, X11:1-Win                         |
| GPU                           | 3           | icmp, ssh, vnc, Nvidia-smi                                   |
| Support                       | 4           | NTP, ftp, file.                                              |

