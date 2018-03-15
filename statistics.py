'''
Calcule les statistiques diverses & peut-être intéressantes...

Author: Adrien Foucart
'''

import numpy as np

# Chargement des matrices
big_vote_matrix = np.load("big_vote_matrix.npy")
big_vote_matrix_partis = np.load("big_vote_matrix_partis.npy")
id_partis = np.load("id_partis.npy").item()

# Récupération des députés et correspondances sièges / parti
import csv
deputes = {}
def clean_name(name):
	return name.encode("utf-8").decode('ascii', 'ignore')
with open('deputes_siege_parti.csv') as fp:
	reader = csv.reader(fp, delimiter=';')
	for row in reader:
		deputes[clean_name(row[1])] = {'parti': row[4], 'nom': row[2], 'prenom': row[3], 'id_siege': int(row[5])}
siege_to_parti = {}
for dep in deputes.keys():
	siege_to_parti[deputes[dep]['id_siege']] = deputes[dep]['parti']

#---- CALCUL DES DISSIDENTS PAR PARTIS ----#
print("#---- CALCUL DES DISSIDENTS PAR PARTIS ----#")
vote_du_parti = big_vote_matrix_partis.argmax(axis=2)
suiveurs = big_vote_matrix_partis.max(axis=2)
votants = big_vote_matrix_partis.sum(axis=2)
dissidents = votants - suiveurs

# Pour chaque parti: nombre de votes unanimes, nombre de votes avec "dissidents"
print("PARTI\tUnanimes Split\t%")
for parti in id_partis.keys():
	votes_unanimes = (dissidents[id_partis[parti]]==0).sum()
	votes_split = (dissidents[id_partis[parti]]!=0).sum()

	print("%s\t%d\t%d\t%.2f%%"%(parti[:7], votes_unanimes, votes_split,(100*votes_split/votes_unanimes)))
print("---------------")



#---- CALCUL DES DISSIDENCES PAR DEPUTE ----#
print("#---- CALCUL DES DISSIDENCES PAR DEPUTE ----#")
vote_du_depute = big_vote_matrix.argmax(axis=2)
print("ID\tPARTI\tParticipé Dissident")
for i in range(150):
	votes_total = big_vote_matrix.shape[1]
	votes_participes = (big_vote_matrix[i].sum(axis=1)>0)
	votes_dissidents = (vote_du_depute[i,votes_participes]!=vote_du_parti[id_partis[siege_to_parti[i+1]], votes_participes]).sum()
	print("%d\t%s\t%d\t%d"%(i+1, siege_to_parti[i+1][:7],votes_participes.sum(), votes_dissidents))
print("---------------")



#---- CALCUL DES TAUX D'ACCORD INTER-PARTIS ----#
print("#---- CALCUL DES TAUX D'ACCORD INTER-PARTIS ----#")
id_to_parti = {}
for parti in id_partis.keys():
	id_to_parti[id_partis[parti]] = parti

vote_partis = big_vote_matrix_partis.argmax(axis=2)
partis_line = "\t"
for p in id_to_parti.keys():
	partis_line += "%s\t"%(id_to_parti[p][:7])
print(partis_line)
for i in range(13):
	line = "%s\t"%(id_to_parti[i])
	for j in range(13):
		line += "%d\t"%((vote_partis[i]==vote_partis[j]).sum())
	print(line)
print("---------------")


#---- CALCUL DES TYPES DE VOTES ----#
print("#---- CALCUL DES TYPES DE VOTES ----#")
vote_du_parti = big_vote_matrix_partis.argmax(axis=2)
majorite = ['MR', 'CD&V', 'N-VA', 'Open Vld']
opp_gdpartis = ['Ecolo-Groen', 'PS', 'sp.a', 'cdH', 'DéFI']
partis_majorite = [id_partis[key] for key in id_partis.keys() if key in majorite]
partis_opposition = [id_partis[key] for key in id_partis.keys() if key not in majorite]
partis_opposition_gd = [id_partis[key] for key in id_partis.keys() if key in opp_gdpartis]
partis_opposition_sansvw = [id_partis[key] for key in id_partis.keys() if (key not in majorite and key != 'Vuye&Wouters')]

votes_majorite = np.zeros((len(partis_majorite), votes_total))
for i,p in enumerate(partis_majorite):
	votes_majorite[i,:] = vote_du_parti[p,:]

votes_opp = np.zeros((len(partis_opposition), votes_total))
for i,p in enumerate(partis_opposition):
	votes_opp[i,:] = vote_du_parti[p,:]
votes_opp2 = np.zeros((len(partis_opposition_sansvw), votes_total))
for i,p in enumerate(partis_opposition_sansvw):
	votes_opp2[i,:] = vote_du_parti[p,:]
votes_opp3 = np.zeros((len(partis_opposition_gd), votes_total))
for i,p in enumerate(partis_opposition_gd):
	votes_opp3[i,:] = vote_du_parti[p,:]

maj_unan = votes_majorite.min(axis=0)==votes_majorite.max(axis=0)
opp_unan = votes_opp.min(axis=0)==votes_opp.max(axis=0)
opp2_unan = votes_opp2.min(axis=0)==votes_opp2.max(axis=0)
opp3_unan = votes_opp3.min(axis=0)==votes_opp3.max(axis=0)
all_unan = vote_du_parti.min(axis=0)==vote_du_parti.max(axis=0)
votes_unan = all_unan.sum()
votes_maj_vs_opp = (maj_unan[all_unan==False]*opp_unan[all_unan==False]).sum()
votes_maj_vs_opp2 = (maj_unan[all_unan==False]*opp2_unan[all_unan==False]).sum()
votes_maj_vs_opp3 = (maj_unan[all_unan==False]*opp3_unan[all_unan==False]).sum()
print("Votes unanimes: %d (%.4f)"%(votes_unan, votes_unan/votes_total))
print("Votes majorite contre opposition: %d (%.4f)"%(votes_maj_vs_opp, votes_maj_vs_opp/votes_total))
print("Votes majorite contre opposition (en ignorant V&W): %d (%.4f)"%(votes_maj_vs_opp2, votes_maj_vs_opp2/votes_total))
print("Votes majorite contre Ecolo-PS-sp.a-cdH: %d (%.4f)"%(votes_maj_vs_opp3, votes_maj_vs_opp3/votes_total))

print("--- en ignorant les abstentions ---")
maj_unan = (((votes_majorite==0)+(votes_majorite==2)).sum(axis=0)==len(partis_majorite))+(((votes_majorite==1)+(votes_majorite==2)).sum(axis=0)==len(partis_majorite))
opp_unan = (((votes_opp==0)+(votes_opp==2)).sum(axis=0)==len(partis_opposition))+(((votes_opp==1)+(votes_opp==2)).sum(axis=0)==len(partis_opposition))
opp2_unan = (((votes_opp2==0)+(votes_opp2==2)).sum(axis=0)==len(partis_opposition_sansvw))+(((votes_opp2==1)+(votes_opp2==2)).sum(axis=0)==len(partis_opposition_sansvw))
opp3_unan = (((votes_opp3==0)+(votes_opp3==2)).sum(axis=0)==len(partis_opposition_gd))+(((votes_opp3==1)+(votes_opp3==2)).sum(axis=0)==len(partis_opposition_gd))
all_unan = (((vote_du_parti==0)+(vote_du_parti==2)).sum(axis=0)==len(id_partis))+(((vote_du_parti==1)+(vote_du_parti==2)).sum(axis=0)==len(id_partis))
votes_unan = all_unan.sum()
votes_maj_vs_opp = (maj_unan[all_unan==False]*opp_unan[all_unan==False]).sum()
votes_maj_vs_opp2 = (maj_unan[all_unan==False]*opp2_unan[all_unan==False]).sum()
votes_maj_vs_opp3 = (maj_unan[all_unan==False]*opp3_unan[all_unan==False]).sum()
print("Votes unanimes: %d (%.4f)"%(votes_unan, votes_unan/votes_total))
print("Votes majorite contre opposition: %d (%.4f)"%(votes_maj_vs_opp, votes_maj_vs_opp/votes_total))
print("Votes majorite contre opposition (en ignorant V&W): %d (%.4f)"%(votes_maj_vs_opp2, votes_maj_vs_opp2/votes_total))
print("Votes majorite contre Ecolo-PS-sp.a-cdH: %d (%.4f)"%(votes_maj_vs_opp3, votes_maj_vs_opp3/votes_total))

print("--- en ignorant les petits partis ---")
partis_gd = partis_majorite+partis_opposition_gd
votes_gd = np.zeros((len(partis_gd), votes_total))
for i,p in enumerate(partis_gd):
	votes_gd[i,:] = vote_du_parti[p,:]

maj_unan = votes_majorite.min(axis=0)==votes_majorite.max(axis=0)
opp3_unan = votes_opp3.min(axis=0)==votes_opp3.max(axis=0)
all_unan = votes_gd.min(axis=0)==votes_gd.max(axis=0)
votes_unan = all_unan.sum()
votes_maj_vs_opp3 = (maj_unan[all_unan==False]*opp3_unan[all_unan==False]).sum()
print("Votes unanimes: %d (%.4f)"%(votes_unan, votes_unan/votes_total))
print("Votes majorite contre opposition: %d (%.4f)"%(votes_maj_vs_opp3, votes_maj_vs_opp3/votes_total))

print("--- en ignorant les petits partis et les abstentions ---")
partis_gd = partis_majorite+partis_opposition_gd
votes_gd = np.zeros((len(partis_gd), votes_total))
for i,p in enumerate(partis_gd):
	votes_gd[i,:] = vote_du_parti[p,:]

maj_unan = (((votes_majorite==0)+(votes_majorite==2)).sum(axis=0)==len(partis_majorite))+(((votes_majorite==1)+(votes_majorite==2)).sum(axis=0)==len(partis_majorite))
opp3_unan = (((votes_opp3==0)+(votes_opp3==2)).sum(axis=0)==len(partis_opposition_gd))+(((votes_opp3==1)+(votes_opp3==2)).sum(axis=0)==len(partis_opposition_gd))
all_unan = (((votes_gd==0)+(votes_gd==2)).sum(axis=0)==len(partis_gd))+(((votes_gd==1)+(votes_gd==2)).sum(axis=0)==len(partis_gd))
votes_unan = all_unan.sum()
votes_maj_vs_opp3 = (maj_unan[all_unan==False]*opp3_unan[all_unan==False]).sum()
print("Votes unanimes: %d (%.4f)"%(votes_unan, votes_unan/votes_total))
print("Votes majorite contre opposition: %d (%.4f)"%(votes_maj_vs_opp3, votes_maj_vs_opp3/votes_total))

#big_vote_matrix_maj = big_vote_matrix_partis[partis_majorite[0]]+big_vote_matrix_partis[partis_majorite[1]]+big_vote_matrix_partis[partis_majorite[2]]+big_vote_matrix_partis[partis_majorite[3]]
