'''
Classe pour parser les comptes-rendus de lachambre.be

Auteur: Adrien Foucart
'''

from html import parser

INACTIVE = 0
NOMINATIF = 1
NOMS_OUI = 2
NOMS_NON = 3
NOMS_ABS = 4

class CRParser(parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.cleaned_text = ''
        self.state = INACTIVE
        self.votes = []
        self.n_vote = 0
    
    def handle_data(self, data):
        data = data.replace('\n', '')
        data = data.replace(' ', '')
        data = data.replace('\xa0', '')
        if( self.state == INACTIVE ):
            if( data.upper().find('VANDENAAMSTEMMINGEN') >= 0 ): 
                self.state = NOMINATIF
        elif( self.state in [NOMINATIF, NOMS_OUI, NOMS_NON, NOMS_ABS] ):
            if( data.upper().find('NAAMSTEMMING') >= 0 ): self.votes.append({})
            elif( data.upper() == "OUI"): self.state = NOMS_OUI
            elif( data.upper() == "NON"): self.state = NOMS_NON
            elif( data.upper() == "ABSTENTIONS"): self.state = NOMS_ABS
            elif( self.state != NOMINATIF and data.upper() not in ['', 'JA', 'NEE', 'OUI', 'NON', 'ABSTENTIONS', 'ONTHOUDINGEN'] and len(data) != 3 and data != '013(geannuleerd–annulé)'):
                if( data.find(',') >= 0 ): 
                    self.votes[len(self.votes)-1][self.state] = data.split(',')
                else:
                    self.votes[len(self.votes)-1][self.state] = [data]
                self.state = NOMINATIF