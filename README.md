# iperfme

<h4 align="center">A simple way to perform network checks on hosts within your network</h4>

<p align="center">
<a href="https://github.com/vttrj/iperfme/issues"><img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat"></a>
<a href="https://jvetter.net"><img src="https://img.shields.io/badge/🌐_-jvetter.net-blue" alt="jvetter.net"></a>
</a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation-instructions">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#-notes">Notes</a>
</p>


---

`iperfme` is a tool to automate network performance checks across hosts within your subnet. It automatically scans the network to identify potential candidates for testing, then conducts a series of test on each. Then it ouputs the result.

Tests are bidirectional. One speaker (client) run the test to a listener (server), and it also requests the listener to reciprocate. This two-way testing gives a better result by measuring performance in both directions. It’s especially useful for spotting network paths that work well one way but may be slower or less reliable on the return.


# Features

 - Latency checks
 - TCP/UDP network bandwidth testing
 - Packet loss detection

# Installation Instructions


Install the prerequisite : 

```sh
sudo apt install iperf nmap iproute -y
```

# Usage

☝️ Requires root privileges to run.

## Server mode
On all hosts that will wait to be checked.

```console
root@hostY:~# python2 iperfme.py 
Run a client or server mode? [c/s]: s
Let's run server mode!

```

## Client mode

On the host that initiates the checks.

```console
root@hostX:~# python2 iperfme.py 
Run a client or server mode? [c/s]: c
Choose an interface in [eth0|lo]: eth0
  Interface eth0 is with mtu 1500 and ip 10.10.0.10/24
Reset this interface (y or n)? [n]:
STEP1: Let's run settings!
  Current hostname is hostX
  Do you want to change hostname [hostX]
  New hostname is now : hostX
STEP2: Let's run tests!
Scanning network 10.10.0.10/24... find 3 host(s)
  Error on connection to 10.10.0.1:15555
  Connection on 10.10.0.11:15555 : hostY is here!
    Ping  hostX -> hostY :  rtt min/avg/max/mdev = 0.261/0.413/0.482/0.067 ms
    Ping  hostX <- hostY :  rtt min/avg/max/mdev = 0.423/0.457/0.514/0.032 ms
    IPerf TCP hostX -> hostY :  ------------------------------------------------------------
Client connecting to 10.10.0.11, TCP port 5001
TCP window size: 85.0 KByte (default)
------------------------------------------------------------
[  5] local 10.10.0.10 port 55432 connected with 10.10.0.11 port 5001
[ ID] Interval       Transfer     Bandwidth
[  5]  0.0-10.0 sec  1.26 GBytes  1.08 Gbits/sec
    IPerf TCP hostX <- hostY :  [  4]  0.0-10.0 sec  1.24 GBytes  1.07 Gbits/sec
    IPerf UDP hostX -> hostY :  ------------------------------------------------------------
Client connecting to 10.10.0.11, UDP port 5001
Sending 1470 byte datagrams
UDP buffer size:  208 KByte (default)
------------------------------------------------------------
[  5] local 10.10.0.10 port 37870 connected with 10.10.0.11 port 5001
[ ID] Interval       Transfer     Bandwidth
[  5]  0.0- 1.0 sec  97.2 MBytes   815 Mbits/sec
[  5]  1.0- 2.0 sec  97.1 MBytes   814 Mbits/sec
[  5]  2.0- 3.0 sec  97.2 MBytes   815 Mbits/sec
[  5]  3.0- 4.0 sec  97.1 MBytes   815 Mbits/sec
[  5]  4.0- 5.0 sec  97.2 MBytes   815 Mbits/sec
[  5]  5.0- 6.0 sec  97.2 MBytes   815 Mbits/sec
[  5]  6.0- 7.0 sec  97.1 MBytes   814 Mbits/sec
[  5]  7.0- 8.0 sec  97.1 MBytes   815 Mbits/sec
[  5]  8.0- 9.0 sec  97.2 MBytes   815 Mbits/sec
[  5]  9.0-10.0 sec  97.1 MBytes   815 Mbits/sec
[  5]  0.0-10.0 sec   971 MBytes   815 Mbits/sec
[  5] Sent 692897 datagrams
[  5] Server Report:
[  5]  0.0-10.0 sec   971 MBytes   815 Mbits/sec   0.011 ms   56/692896 (0.0081%)
[  5]  0.0-10.0 sec  1 datagrams received out-of-order
    IPerf UDP hostX <- hostY : Waiting for server threads to complete. Interrupt again to force quit.
 [  4]  0.0-10.0 sec  22 datagrams received out-of-order
  Error on connection to 10.10.0.10:15555
Let's run server mode!

```



# 📋 Notes

- Only compatible python2
- After completing a check in client mode, the client switches to server mode and waits to be tested by another client
