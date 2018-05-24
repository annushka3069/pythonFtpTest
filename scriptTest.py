#####################################################################
#						Script Python permettant de chercher		#
#						     des fichiers un serveur FTP			#																							
#####################################################################
import os
import sys
import smtplib
import subprocess
from ftplib import FTP
from datetime import *

#On verifie si une date est donnee en argument
if(len(sys.argv) > 1):
	dateSaisie = sys.argv[1]
else:
	dateSaisie = ""

#Fonction permettant de verifier la validite d'une date selon nos criteres(AnneeMoisJour)
def valider(dateEntree):
	try:
		if dateEntree != datetime.strptime(dateEntree, "%Y%m%d").strftime('%Y%m%d'):
			raise ValueError
		return True
	except ValueError:
		return False
		
		
#Fonction permettant de transferer un fichier distant en local, 
#prend en argument le nom du fichier distant et celui qu'on veut donner a sa copie en local.	
def transfererFichier(fichierLocal, fichierDistant):
	try :
		f = open(fichierLocal, 'wb')
		ftp.retrbinary('RETR ' + fichierDistant, f.write)
		f.close()
	except ftplib.error_perm:
		pass
		
#Si la date est valide on l'utilise pour chercher le fichier de log, 
#sinon on utilise la date de la veille.
if(valider(dateSaisie)):
	dateFichier = dateSaisie
else:
	hier = date.today() - timedelta(1)
	dateFichier = hier.strftime('%Y%m%d')
	
#On utilise ssh pour chercher le fichier de log sur la machine distante, 
#ftp n'offre pas de commande permettant de le faire.
fichierLog = 'containAllFiles-'+dateFichier+'.log'
Commande = "find -name "+fichierLog
ssh = subprocess.Popen(["ssh", "192.168.83.154", Commande], shell = False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
result = ssh.stdout.readlines()

#Si le resultat est vide on a pas trouvé de fichier de log pour cette date; 
#sinon on commence à lire le fichier et telecharger les fichiers écrits dans le log.
if result == []:
	error = ssh.stderr.readlines()
	print(sys.stderr, "ERROR: %s" % error)
else:
	print(result)
	#On se connecte via ftp a la machine distante et on telecharge le fichier de log en premier
	ftp = FTP("192.168.83.154")
	ftp.login('anna', 'ubuntu')
	transfererFichier(fichierLog, result)
	ftp.quit()
	#Par la suite on cree une expression reguliere pour differencier les sous-répertoires des fichiers, 
	#On aurait pu utiliser os.path mais vu qu'on travaille sur une machine distante, il aurait fallu utiliser plusieurs sessions SSH(pas optimal)
	regex = re.compile(r"*\.*")
	fichiers = [] #stocke les fichiers
	sousRep = []  #stocke les sous repertoires
	logFile = open(fichierLog, 'r')
	for line in file : 
		if regex.match(line):
			fichiers.append(line)
		else: 
			sousRep.append(line)
	logFile.close()
	
#On commence ensuite a telecharger les fichiers un a un	
	
if (len(fichiers) !=0):
	i=0
	ftp = FTP("192.168.83.154")
	ftp.login('anna', 'ubuntu')
	for fichier in fichiers:
		transfererFichier("fichier"+i, fichier)
		i = i+1
	ftp.quit()
	
#On fait de meme dans les sous repertoires	
if(len(sousRep) !=0):
	j=0
	ftp= FTP("192.168.83.154")
	ftp.login('anna', 'ubuntu')
	for rep in sousRep:
		ftp.cwd(rep)
		for fich in ftp.nlst():
			transfererFichier("fich"+j, fich)
			j=j+1
	ftp.quit()
			
	
################################################### Envoi d'Email avec statut de l'envoi ##################################################


sender = 'anna@domain.com'
receivers = ['jennye@planaxis.com']

message = """From: From Anna <anna@domain.com>
To: To Jennye <jennye@planaxis.com>
Subject: Python script test

This is a python script test .
"""

try:
   smtpObj = smtplib.SMTP('localhost')
   smtpObj.sendmail(sender, receivers, message)         
   print "Email envoyé avec succès"
except SMTPException:
   print "Erreur: impossible d'envoyer l'email"