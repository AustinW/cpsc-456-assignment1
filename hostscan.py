#######################################################
# This file illustrates how to scan network for other
# host systems.
#######################################################

# Import the necessary files
import nmap

#######################################################
# Returns the list of systems on the same network
# @return - a list of IP addresses on the same network
#######################################################
def getHostsOnTheSameNetwork():
	
	# TODO: Add code for scanning
	# for hosts on the same network
	# and return the list of discovered
	# IP addresses.
	# Create an instance of the port scanner class
	portScanner = nmap.PortScanner()

	# Scan the network for systems whose
	# port 22 is open (that is, there is possibly
	# SSH running there). 
	portScanner.scan('192.168.1.0/24', arguments='-p 22 --open')

	# Scan the network for hoss
	hostInfo = portScanner.all_hosts()

	# Hosts that are alive
	runningHosts = []

	for host in hostInfo:
		if portScanner[host].state() == "up":
			runningHosts.append(host)

	return runningHosts