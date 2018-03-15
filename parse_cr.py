'''
Parse tous les comptes-rendus et crée les matrices de vote

Auteur: Adrien Foucart
'''

import os
from CRParser import CRParser

PATH = './archives/' 	# Path des fichiers HTML de compte-rendu

def get_docs(leg):
	files_leg = [f for f in os.listdir(PATH) if f.find('%02d_'%leg) == 0]
	for f in files_leg:
		with open(os.path.join(PATH, f), 'r') as fp :
			html = fp.read()
			yield html
	return None

all_votes = []
for html in get_docs(54):
	parser = CRParser()
	parser.feed(html)
	all_votes.append(parser.votes)


# Récupère la liste des députés / sièges
import csv

deputes = {}
def clean_name(name):
	return name.encode("utf-8").decode('ascii', 'ignore')

with open('deputes_siege_parti.csv') as fp:
	reader = csv.reader(fp, delimiter=';')
	for row in reader:
		deputes[clean_name(row[1])] = {'parti': row[4], 'nom': row[2], 'prenom': row[3], 'id_siege': int(row[5])}

# Vérifie si il y a des "inconnus" (c'est-à-dire des nouveaux députés / députés qui ont changés de nom)
# Si c'est le cas, il faut mettre à jour le fichier deputes_siege_parti.csv
for session in all_votes:
	for vote in session:
		for qv in vote.keys():
			for dep in vote[qv]:
				if( clean_name(dep.upper()) not in deputes.keys() ):
					print("Nouveau député: ",dep)

# Nombre total de votes enregistrés
votes_tot = 0
for session in all_votes:
	votes_tot += len(session)

import numpy as np
N_SIEGES = 150
big_vote_matrix = np.zeros((N_SIEGES,votes_tot, 3))
v = 0
for session in all_votes:
	for vote in session:
		for qv in vote.keys():
			for dep in vote[qv]:
				D = deputes[clean_name(dep.upper())]
				big_vote_matrix[D['id_siege']-1, v, qv-2] = 1
		v += 1

compte_voix = big_vote_matrix.sum(axis=0)
votes_valides = compte_voix.sum(axis=1)>0
big_vote_matrix = big_vote_matrix[:,votes_valides,:]
votes_tot = big_vote_matrix.shape[1]

# Sauvegarder la matrice des votes
print("%d votes"%votes_tot)
np.save("big_vote_matrix.npy", big_vote_matrix)


# Créer la matrice de votes par partis
siege_to_parti = {}
for dep in deputes.keys():
	siege_to_parti[deputes[dep]['id_siege']] = deputes[dep]['parti']

# Sièges par parti
sieges = {}
for siege_id in siege_to_parti.keys():
    if( siege_to_parti[siege_id] not in sieges.keys() ):
        sieges[siege_to_parti[siege_id]] = [siege_id]
    else:
        sieges[siege_to_parti[siege_id]].append(siege_id)

id_partis = {}
i = 0
for parti in sieges.keys():
	id_partis[parti] = i
	i += 1

big_vote_matrix_partis = np.zeros((len(sieges), votes_tot, 3))
for v in range(votes_tot):
	for i in range(N_SIEGES):
		big_vote_matrix_partis[id_partis[siege_to_parti[i+1]], v, :] += big_vote_matrix[i, v, :]

# Sauvegarder la matrice des votes de partis
np.save("big_vote_matrix_partis.npy", big_vote_matrix_partis)
# Sauvegarder la référence ligne / parti
np.save("id_partis.npy", id_partis)