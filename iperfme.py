import os
import socket
import subprocess
import sys

def askInput(question):
    try:
        return raw_input(question)
    except NameError:
        return input(question)

def getShellReturn(command):
    try:
        return subprocess.getoutput(command).strip()
    except:
        return subprocess.check_output(command, shell=True).strip()

def getIP(interface):
    return getShellReturn("ip addr show dev " + interface + " |grep 'inet ' |awk '{print $2}'")

def getMTU(interface):
    return getShellReturn("ip addr show dev " + interface + " |grep 'mtu ' |awk '{print $5}'")

def getHostsFromInterface(interface):
    """  Scans the local network from the specified interface and returns a list of discovered IP addresses. """
    myNetwork = getIP(interface)
    print ('Scanning network ' + myNetwork + '...'),
    sys.stdout.flush()
    nmap = getShellReturn("nmap -sn " + myNetwork + " |grep 'Nmap scan report for' |awk '{print $5}'")
    hosts = nmap.split('\n')
    print ('find ' + str(len(hosts)) + ' host(s)')
    return hosts

def getMyHostname():
    return getShellReturn("hostname")

def getYourHostname(socket):
    """ Requests the hostname from the remote machine """
    socket.send("hostname".encode())
    reponse = socket.recv(255)
    if reponse != "":
        return reponse

def PingMe(socket):
    """ Requests the remote machine to ping me. """
    socket.send(u"PingMe")
    reponse = socket.recv(255)
    if reponse != "":
        return reponse

def PingYou(host):
    """ Run ping over the remote host. """
    return getShellReturn("ping -c 10 " + host + " | tail -n 1")

def IPerfMe(socket, host):
    """ Initiates an iPerf server session and requests a performance test from the remote machine. """
    iperf = subprocess.Popen(["iperf -s"], stdout=subprocess.PIPE, shell=True)
    socket.send("IPerfMe")
    reponse = socket.recv(255)
    if reponse != "":
        subprocess.check_output("pkill iperf", shell=True)
        return reponse

def IPerfMeUDP(socket, host):
    """ Requests remote host to perform IPerf UDP """
    iperf = subprocess.Popen(["iperf -s -u"], stdout=subprocess.PIPE, shell=True)
    socket.send("IPerfMeUDP")
    reponse = socket.recv(255)
    if reponse != "":
        subprocess.check_output("pkill iperf", shell=True)
        return reponse

def IPerfYou(socket, host):
    """ Initiate IPERF TCP to the remote host """
    socket.send(u"IPerfYou")
    reponse = socket.recv(255)
    if reponse == 'IPerfYouReady':
        """" result = getShellReturn("iperf -c " + host + " | tail -n 1") """
        result = getShellReturn("iperf -c " + host + "")
        socket.send(u"IPerfYouEnd")
        return result

def IPerfYouUDP(socket, host):
    """ Initiate IPERF UDP to the remote host """
    socket.send(u"IPerfYouUDP")
    reponse = socket.recv(255)
    if reponse == 'IPerfYouUDPReady':
        """ result = getShellReturn("iperf -c " + host + " -u -b 800M -i 1 -t 10 | tail -n 1") """
        result = getShellReturn("iperf -c " + host + " -u -b 800M -i 1 -t 10 ")
        socket.send(u"IPerfYouUDPEnd")
        return result



def ServerListen(ipServer, portServer):
    global socket
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind((ipServer, portServer))
    while 1:
        socket.listen(5)
        client, ipClient = socket.accept()
        print (str(ipClient) + " connected")

        for i in range(0,50):
            response = client.recv(255)
            if response == 'hostname':
                reponse = getMyHostname()
                print ('Return my hostname (' + reponse + ') to {}'.format(ipClient))
                client.send(reponse)

            if response == 'PingMe':
                reponse = PingYou(ipClient[0])
                print ('Return my ping (' + reponse + ') to {}'.format(ipClient))
                client.send(reponse)

            if response == 'IPerfYou' or response == 'IPerfYouEnd':
                if response == 'IPerfYou':
                    print ('Start IPerf server for {}'.format(ipClient))
                    subprocess.Popen(["iperf -s"], stdout=subprocess.PIPE, shell=True)
                    client.send("IPerfYouReady")
                else:
                    print ('Stop IPerf server for {}'.format(ipClient))
                    getShellReturn("pkill iperf")

            if response == 'IPerfMe':
                print ('Start IPerf client to ' + str(ipClient))
                result = getShellReturn("iperf -c " + ipClient[0] + " | tail -n 1")
                client.send(result)

            if response == 'IPerfYouUDP' or response == 'IPerfYouUDPEnd':
                if response == 'IPerfYouUDP':
                    print ('Start IPerf UDP server for {}'.format(ipClient))
                    subprocess.Popen(["iperf -s -u"], stdout=subprocess.PIPE, shell=True)
                    client.send("IPerfYouUDPReady")
                else:
                    print ('Stop IPerf UDP server for {}'.format(ipClient))
                    getShellReturn("pkill iperf")

            if response == 'IPerfMeUDP':
                print ('Start IPerf UDP client to ' + str(ipClient))
                result = getShellReturn("iperf -c " + ipClient[0] + " -u -b 800M -i 1 -t 10 | tail -n 1")
                client.send(result)

    print ("Close")
    client.close()
    socket.close()

""" LAUNCHER """

def step0_checkPackets():
    try:
        tmp = subprocess.check_call("nmap -h > /dev/null 2>/dev/null", shell=True)
    except Exception:
        sys.exit('Need to install nmap: apt-get install nmap -y')

    try:
        tmp = subprocess.check_call("iperf > /dev/null 2>/dev/null", shell=True)
    except Exception:
        sys.exit('Need to install iperf: apt-get install iperf -y')


def step1_settings(interface, resetNetwork, mtu):
    print ("STEP1: Let's run settings!")
    currentHostname = getMyHostname()
    print ("  Current hostname is " + currentHostname)
    newHostname = askInput("  Change hostname [" + currentHostname + "]") or currentHostname
    getShellReturn("hostname " + newHostname)
    getShellReturn("echo " + newHostname + " > /etc/hostname")
    print ("  New hostname is now : " + newHostname)

    if resetNetwork == "y":
        getShellReturn("dhclient " + interface + " -r > /dev/null 2>&1")
        getShellReturn("ip link set " + interface + " down > /dev/null 2>&1 ")
        getShellReturn("ip link set " + interface + " mtu " + str(mtu) + " up > /dev/null 2>&1 ")
        getShellReturn("dhclient " + interface + " > /dev/null 2>&1")
        print ("  Interface " + interface + " is with mtu " + getMTU(interface) + " and ip " + getIP(interface))


def step2_tests(interface, port):
    print ("STEP2: Let's run tests!")
    hosts = getHostsFromInterface(interface)
    myHostname = getMyHostname()

    for host in hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((host, port))
            sock.settimeout(None)
        except socket.error:
            print ('  Error on connection to ' + host + ':' + str(port))
            continue

        hisHostname = getYourHostname(sock)
        print ("  Connection on " + host + ":" + str(port) + " : " + hisHostname + " is here!")

        # Ping you
        print ('    Ping  ' + myHostname + ' -> ' + hisHostname + ' : '),
        sys.stdout.flush()
        print (PingYou(host))

        # Ping me
        print ('    Ping  ' + myHostname + ' <- ' + hisHostname + ' : '),
        sys.stdout.flush()
        print (PingMe(sock))


        # IPerf you TCP
        print ('    IPerf TCP ' + myHostname + ' -> ' + hisHostname + ' : '),
        sys.stdout.flush()
        print (IPerfYou(sock, host))

        # IPerf me TCP
        print ('    IPerf TCP ' + myHostname + ' <- ' + hisHostname + ' : '),
        sys.stdout.flush()
        print (IPerfMe(sock, host))


        # IPerf you UDP
        print ('    IPerf UDP ' + myHostname + ' -> ' + hisHostname + ' : '),
        sys.stdout.flush()
        print (IPerfYouUDP(sock, host))

        # IPerf me UDP
        print ('    IPerf UDP ' + myHostname + ' <- ' + hisHostname + ' : '),
        sys.stdout.flush()
        print (IPerfMeUDP(sock, host))

        sock.close()


def step3_serverMode(port):
    print ("Let's run server mode!")
    ServerListen('0.0.0.0', port)



""" LAUNCHER """


serverPort = 15555
interface = ''
mtu = 9000

# Have to be run in root
if not os.geteuid() == 0:
    sys.exit('Script must be run as root')

# Check if nmap and iperf installed
step0_checkPackets()

askMode = askInput('Run a client or server mode? [c/s]: ')
if askMode == "c":
    # Ask an interface to the user
    interfaces = getShellReturn("ls /sys/class/net").replace("\n", "|")
    while interface not in interfaces or interface == '':
        interface = askInput("Choose an interface in [" + interfaces + "]: ")
    print ("  Interface " + interface + " is with mtu " + getMTU(interface) + " and ip " + getIP(interface))
    resetNetwork = askInput("Reset this interface (y or n)? [n]: ") or "n"

    step1_settings(interface, resetNetwork, mtu)
    step2_tests(interface, serverPort)

step3_serverMode(serverPort)
