The Nmap config 

```
Peers:
    "public": "www.google.com.sg",
    "socFW": "172.18.178.10",
    "openstack_CT02": "10.0.6.4",
    "openstack_CP01": "10.0.6.11",
    "openstack_CP02": "10.0.6.12",
    "openstack_CP03": "10.0.6.13",
    "openstack_CP04": "10.0.6.20",
    "KypoLite_01": "10.0.6.21",
    "KypoLite_02": "10.0.6.22",
    "CISS_RED_01": "10.0.6.23",
    "CISS_RED_02": "10.0.6.24",
    "ncl_GPU07": "10.0.6.25",
    "ncl_GPU08": "10.0.6.26",
    "ncl_GPU09": "10.0.6.27"
```



```
ncl@controller1:~/programs/ncl_yc/NetworkConnDashboard/src$ nmap -F 172.18.178.10
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-15 05:24 UTC
Nmap scan report for 172.18.178.10
Host is up (0.00041s latency).
Not shown: 94 filtered ports
PORT     STATE  SERVICE
22/tcp   open   ssh
113/tcp  closed ident
443/tcp  open   https
8000/tcp open   http-alt
8080/tcp open   http-proxy
8081/tcp open   blackice-icecap
```



```
ncl@controller1:~/programs/ncl_yc/NetworkConnDashboard/src$ nmap -F 10.0.6.4
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-15 05:21 UTC
Nmap scan report for controller2 (10.0.6.4)
Host is up (0.00017s latency).
Not shown: 95 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
3306/tcp open  mysql
5000/tcp open  upnp
8000/tcp open  http-alt

Nmap done: 1 IP address (1 host up) scanned in 0.02 seconds
```



```
ncl@controller1:~/programs/ncl_yc/NetworkConnDashboard/src$ nmap -F 10.0.6.11
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-15 05:32 UTC
Nmap scan report for compute1 (10.0.6.11)
Host is up (0.00021s latency).
Not shown: 98 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
5900/tcp open  vnc
```



```
ncl@controller1:~/programs/ncl_yc/NetworkConnDashboard/src$ nmap -F 10.0.6.12
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-15 05:35 UTC
Nmap scan report for compute2 (10.0.6.12)
Host is up (0.00019s latency).
Not shown: 99 closed ports
PORT   STATE SERVICE
22/tcp open  ssh
```



```
ncl@controller1:~/programs/ncl_yc/NetworkConnDashboard/src$ nmap -F 10.0.6.13
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-15 05:37 UTC
Nmap scan report for 10.0.6.13
Host is up (0.0023s latency).
Not shown: 99 closed ports
PORT   STATE SERVICE
22/tcp open  ssh

Nmap done: 1 IP address (1 host up) scanned in 13.03 seconds
```



```
ncl@controller1:~/programs/ncl_yc/NetworkConnDashboard/src$ nmap -F 10.0.6.20
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-15 05:43 UTC
Nmap scan report for 10.0.6.20
Host is up (0.00015s latency).
Not shown: 96 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
5900/tcp open  vnc
6000/tcp open  X11
6001/tcp open  X11:1

Nmap done: 1 IP address (1 host up) scanned in 13.02 seconds
```



```
ncl@controller1:~/programs/ncl_yc/NetworkConnDashboard/src$ nmap -F 10.0.6.21
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-15 05:40 UTC
Nmap scan report for 10.0.6.21
Host is up (0.00015s latency).
Not shown: 96 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
5900/tcp open  vnc
6000/tcp open  X11
6001/tcp open  X11:1

Nmap done: 1 IP address (1 host up) scanned in 13.02 seconds
```



```
ncl@controller1:~/programs/ncl_yc/NetworkConnDashboard/src$ nmap -F 10.0.6.22
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-15 05:49 UTC
Nmap scan report for 10.0.6.22
Host is up (0.00012s latency).
Not shown: 98 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
5900/tcp open  vnc

Nmap done: 1 IP address (1 host up) scanned in 13.03 seconds
```



```
ncl@controller1:~/programs/ncl_yc/NetworkConnDashboard/src$ nmap -F 10.0.6.23
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-15 05:51 UTC
Nmap scan report for 10.0.6.23
Host is up (0.00014s latency).
Not shown: 96 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
5900/tcp open  vnc
6000/tcp open  X11
6001/tcp open  X11:1

Nmap done: 1 IP address (1 host up) scanned in 13.03 seconds
```



```
ncl@controller1:~/programs/ncl_yc/NetworkConnDashboard/src$ nmap -F 10.0.6.25
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-15 05:55 UTC
Nmap scan report for 10.0.6.25
Host is up (0.00015s latency).
Not shown: 98 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
5900/tcp open  vnc

Nmap done: 1 IP address (1 host up) scanned in 13.02 seconds
```

