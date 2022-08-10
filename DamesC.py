from tkinter import *
import numpy as np
import random as random
import tkinter.font as font
 

class Pion:
    
    def __init__(self, canevas, x, y,couleur = "white"):
        self._couleur = couleur
        self._canevas = canevas
        self._item = canevas.create_oval(x-2*self._canevas.rayonp_x,y-2*self._canevas.rayonp_y,x+2*self._canevas.rayonp_x,y+2*self._canevas.rayonp_y,fill =self._couleur)
        self.x = x
        self.y = y
        self.casex,self.casey = self._canevas._canv2plat(x,y)
    
    def __str__(self):
        c = "blanc" if self._couleur == "white" else "noir"
        return(f"Pion {c} ({self.casex},{self.casey})")
    
    def __repr__(self):
        c = "b" if self._couleur =="white" else "n"
        return(f"P{c}{self.casex}{self.casey}")
    
    def redraw(self):
        self._canevas.delete(self._item)
        self._item = self._canevas.create_oval(self.x-2*self._canevas.rayonp_x,self.y-2*self._canevas.rayonp_y,self.x+2*self._canevas.rayonp_x,self.y+2*self._canevas.rayonp_y,fill =self._couleur)
        
    def deplacement(self, dx, dy):
        self._canevas.move(self._item, dx, dy)
        self.x += dx
        self.y += dy

        
    def est_en_case(self,i,j):
        return((i == self.casex) and (j == self.casey))
    
    def get_couleur(self):
        return(self._couleur)
    

    
    def deplacer(self,x,y):
        ncasex,ncasey = self._canevas._canv2plat(x,y)
        xf,yf = self._canevas._plat2canv(ncasex,ncasey)
        self.deplacement(xf-self.x,yf-self.y)
        self.x = xf
        self.y = yf
        self.casex = ncasex
        self.casey = ncasey



class ZonePlateau(Canvas):
    
    def __init__(self, parent, largeur, hauteur):
        #initialisation du canevas
        Canvas.__init__(self, parent, width=largeur, height=hauteur,highlightthickness=0)
        self.largeur = largeur
        self.hauteur = hauteur
        self.cote_x = largeur/13
        self.cote_y = hauteur/13
        self.rayon_x = self.cote_x/8
        self.rayon_y = self.cote_y/8
        self.rayonp_x = self.cote_x/6
        self.rayonp_y = self.cote_y/6

        
        #dessin du plateau
        for i in range(8):
            for j in range(8):
                posx,posy = self._plat2canv(i,j)
                self.create_oval(posx-self.rayon_x,posy -self.rayon_y,posx+self.rayon_x,posy+self.rayon_y,fill ="grey")

        #ajout des pièces
        self.pb =[] #pions blancs
        self.pn =[] #pions noirs
        for i in range(4):
            for j in range(4):
                if i+j <= 3:
                    x,y = self._plat2canv(i,j)
                    self.pb.append(Pion(self,x,y,"white"))
                    x,y = self._plat2canv(7-i,7-j)
                    self.pn.append(Pion(self,x,y,"black"))
        

        self.ia = IA(self,'black')

        
        #working data pour tester les coups du joueur
        self.__piece_courante = ""
        self.joueurajouer = False
        self.pospioninit = (-1,-1)
        self.coup_precedent = ""
        self.coup_courant = []
        
        
     
    def reset_working_data(self):
        self.__piece_courante = ""
        self.joueurajouer = False
        self.pospioninit = (-1,-1)
        self.coup_precedent = ""
        self.coup_courant = []
                        
    def  _plat2canv(self,i,j): 
        posx =  (i*self.cote_x - j*self.cote_y)/2 + self.largeur/2
        posy = (-i*self.cote_x - j*self.cote_y)*np.sqrt(3)/2 + self.hauteur-self.cote_y/2
        return(posx,posy)
    
    def _canv2plat(self,x,y):
        X = x-self.largeur/2
        Y = y +self.cote_y/2 - self.hauteur
        i = round((X-Y/np.sqrt(3))/self.cote_x)
        j = round((-X-Y/np.sqrt(3))/self.cote_y)
        return(i,j)
    
    def jouerIA(self):
        if self.joueurajouer:
            print("J:",self.coup_courant)
            temp = self.ia.joueralphabeta(depth = 3)
            print("IA:",temp[1])
            self.appliquer_coup(temp[0],temp[1])
            self.reset_working_data()
    
    def bouton1_appuye(self,event):
        eventi,eventj = self._canv2plat(event.x,event.y)
        for p in self.pb:
            if p.est_en_case(eventi,eventj):
                if not self.joueurajouer:
                    self.__piece_courante = p
                    break
        if self.__piece_courante != "":
            self.__piece_courante.redraw()
            if self.pospioninit == (-1,-1):
                self.pospioninit = self.__piece_courante.casex,self.__piece_courante.casey
                self.coup_courant = [(eventi,eventj)]
 

    def bouton1_deplace(self,event):
        if self.__piece_courante != "":
            dx = event.x - self.__piece_courante.x
            dy = event.y - self.__piece_courante.y
            self.__piece_courante.deplacement(dx,dy)

            

    
    def bouton1_relache(self,event):
        if self.__piece_courante != "" :
            ncasex,ncasey = self._canv2plat(event.x,event.y)
            etude_coup = self.coup_legal(self.__piece_courante.casex,self.__piece_courante.casey,ncasex,ncasey)
            print(etude_coup)
            if ncasex == self.pospioninit[0] and ncasey == self.pospioninit[1]:
                self.__piece_courante.deplacer(event.x,event.y) 
                self.reset_working_data()
            elif etude_coup != 'ilegal' and (self.coup_precedent =="" or (self.coup_precedent == "saut" and etude_coup == "saut")):#coup legal
                self.__piece_courante.deplacer(event.x,event.y)
                self.coup_precedent = etude_coup
                self.joueurajouer = True
                self.coup_courant.append((ncasex,ncasey))
    
            else:
                xf,yf = self._plat2canv(self.__piece_courante.casex,self.__piece_courante.casey)
                self.__piece_courante.deplacement(xf-self.__piece_courante.x,yf-self.__piece_courante.y)
            
            
        
    
    def piece_dans_case(self,i,j):
        for p in self.pb:
            if p.est_en_case(i,j) :
                return(True)
        for p in self.pn:
            if p.est_en_case(i,j) :
                return(True)
        return(False)
    
    
    def appliquer_coup(self,p,l):
        if p.casex == l[0][0] and p.casey == l[0][1]:
            for i in range(1,len(l)):
                a,b =l[i-1]
                c,d = l[i]
                
                test = self.coup_legal(a,b,c,d)
                if test != "ilegal":
                    x,y = self._plat2canv(c,d)
                    _ = p.deplacer(x,y)
                    p.redraw()
                    if test == "non saut":
                        break
                else:
                    break
                

    
    def coup_legal(self,a,b,c,d):
        if (0<= a <= 7) and (0<= b <= 7) and (0<= c <= 7) and (0<= d <= 7):
            if ((c-a)*(d-b) == 0) or ((d-b)/(c-a)==-1):
                rep = (abs(a-c+b-d) <= 1) and (abs(a-c) +abs(b-d) <= 2)
                if not rep:
                    for p in self.pn:
                        if p.casex == c and p.casey ==d:
                            return('ilegal')
                        elif p.casex != a or p.casey != b :
                            if p.casex == (a+c)/2 and p.casey == (b+d)/2:
                                print(p)
                                rep = True
                            elif (p.casex- a)*(d-b) == (p.casey-b)*(c-a) and (p.casex -a)*(c-a) + (p.casey-b)*(d-b) >= 0 and (p.casex -c)*(a-c) + (p.casey-d)*(b-d) >= 0:
                                return('ilegal')
    
                    for p in self.pb:
                        if p.casex == c and p.casey ==d:
                            return('ilegal')
                        elif p.casex != a or p.casey !=b :
                            if p.casex == (a+c)/2 and p.casey == (b+d)/2:
                                print(p)
                                rep = True
                            elif (p.casex- a)*(d-b) == (p.casey-b)*(c-a) and (p.casex -a)*(c-a) + (p.casey-b)*(d-b) >= 0 and (p.casex -c)*(a-c) + (p.casey-d)*(b-d) >= 0:
                                return('ilegal')
                if rep:
                    if (abs(a-c+b-d) <= 1) and abs(a-c) +abs(b-d) <= 2:
                        return("non saut")
                    else:
                        return("saut")
                else:   
                    return('ilegal')
            else:
                return('ilegal')
        else:
            return('ilegal')

class IA():
    def __init__(self,canevas,couleur):
        self.couleur = couleur
        self._canevas = canevas
        self.pions = canevas.pn if couleur == "black" else canevas.pb
        self.pospions = np.empty((8,8),dtype = bool)
        self.maj_pospions()
        self.directions_possibles = [(1,0),(0,1),(-1,0),(0,-1),(1,-1),(-1,1)]
    
    
    def maj_pospions(self):
        self.pospions.fill(False)
        for p in self._canevas.pb:
            self.pospions[p.casex,p.casey] = True
        for p in self._canevas.pn:
            self.pospions[p.casex,p.casey] = True
    
    def coups_possibles(self,p):
        rep = []
        self.pospions[p.casex,p.casey] = False
        nb_non_sauts = 0
        for a,b in self.directions_possibles:
            if (0 <= p.casex +a <= 7) and (0<= p.casey +b <= 7) and (not self.pospions[p.casex +a,p.casey+b]):
                rep.append((p,[(p.casex,p.casey),(p.casex+a,p.casey +b)]))
                nb_non_sauts +=1
        
        #gestion des sauts
        vus = [(p.casex,p.casey)]
        a_voir = [[(p.casex,p.casey)]]
        while len(a_voir) != 0:
            l =  a_voir.pop(0)
            pp =  l[-1]
            for (a,b) in self.directions_possibles:
                ii = pp[0] + a
                jj = pp[1] + b
                saut = False
                while (0 <= ii <= 7) and (0<= jj <= 7):#on se déplace dans la direction donnée par a,b et on cherche le premier pion
                    if  self.pospions[ii,jj]:
                        saut = True
                        break
                    ii += a
                    jj += b
                if saut:
                    arrivex = 2*ii - pp[0]
                    arrivey = 2*jj - pp[1]
                    if (0<= arrivex <= 7) and (0<= arrivey <= 7) and (not self.pospions[arrivex,arrivey]) and (not (arrivex,arrivey) in vus):
                        saut_legal = True
                        ii += a
                        jj += b
                        while ii != arrivex and jj != arrivey:
                            if self.pospions[ii,jj]:
                                saut_legal = False
                                break
                            ii += a
                            jj += b
                        if saut_legal:
                            ll = l.copy()
                            ll.append((arrivex,arrivey))
                            a_voir.append(ll)
                            vus.append((arrivex,arrivey))
                            rep.append((p,ll))
                    

        _ = vus.pop(0)
        self.pospions[p.casex,p.casey] = True
        return(rep)
    
    
    def coups_possibles2(self,p,pospions):
        rep = []
        pospions[p[0],p[1]] = False
        nb_non_sauts = 0
        for a,b in self.directions_possibles:
            if (0 <= p[0] +a <= 7) and (0<= p[1] +b <= 7) and (not pospions[p[0] +a,p[1]+b]):
                rep.append([(p[0],p[1]),(p[0]+a,p[1] +b)])
                nb_non_sauts +=1
        
        #gestion des sauts
        vus = [(p[0],p[1])]
        a_voir = [[(p[0],p[1])]]
        while len(a_voir) != 0:
            l =  a_voir.pop(0)
            pp =  l[-1]
            for (a,b) in self.directions_possibles:
                ii = pp[0] + a
                jj = pp[1] +b
                saut = False
                while (0 <= ii <= 7) and (0<= jj <= 7):#on se déplace dans la direction donnée par a,b et on cherche le premier pion
                    if pospions[ii,jj]:
                        saut = True
                        break
                    ii += a
                    jj += b
                if saut:
                    arrivex = 2*ii - pp[0]
                    arrivey = 2*jj - pp[1]
                    if (0<= arrivex <= 7) and (0<= arrivey <= 7) and (not pospions[arrivex,arrivey]) and (not (arrivex,arrivey) in vus):
                        saut_legal = True
                        ii += a
                        jj += b
                        while ii != arrivex and jj != arrivey:
                            if pospions[ii,jj]:
                                saut_legal = False
                                break
                            ii += a
                            jj += b
                        if saut_legal:
                            ll = l.copy()
                            ll.append((arrivex,arrivey))
                            a_voir.append(ll)
                            vus.append((arrivex,arrivey))
                            rep.append((ll))
                    

        _ = vus.pop(0)
        pospions[p[0],p[1]] = True
        return(rep)
    
    def coups_possibles3(self,p,pospions):
        rep = []
        pospions[p[0],p[1]] = False
        
        #gestion des sauts
        vus = np.empty((8,8),dtype = 'bool')
        vus.fill(False)
        vus[p[0],p[1]] = True
        a_voir = [(p[0],p[1])]
        while len(a_voir) != 0:
            pp =  a_voir.pop(0)
            for (a,b) in self.directions_possibles:
                ii = pp[0] + a
                jj = pp[1] + b 
                saut = False
                while (0 <= ii <= 7) and (0<= jj <= 7):#on se déplace dans la direction donnée par a,b et on cherche le premier pion
                    if pospions[ii,jj]:
                        saut = True
                        break
                    ii += a
                    jj += b
                if saut:
                    arrivex = 2*ii - pp[0]
                    arrivey = 2*jj - pp[1]
                    if (0<= arrivex <= 7) and (0<= arrivey <= 7) and (not pospions[arrivex,arrivey]) and (not vus[arrivex,arrivey]):
                        saut_legal = True
                        ii += a
                        jj += b
                        while ii != arrivex and jj != arrivey:
                            if pospions[ii,jj]:
                                saut_legal = False
                                break
                            ii += a
                            jj += b
                        if saut_legal:
                            a_voir.append((arrivex,arrivey))
                            vus[arrivex,arrivey] = True
                            rep.append(((p[0],p[1]),(arrivex,arrivey)))
        
        pospions[p[0],p[1]] = True
        for a,b in self.directions_possibles:
            arrivex = p[0] + a
            arrivey =  p[1] + b
            if (0 <= arrivex <= 7) and (0<= arrivey <= 7) and (not pospions[arrivex,arrivey]) and (not vus[arrivex,arrivey]):
                rep.append(((p[0],p[1]),(arrivex,arrivey)))
        return(rep)
    
    def pbpn2pospion(self,pb,pn):
        pospion = np.empty((8,8), dtype = 'bool')
        pospion.fill(False)
        for a,b in pb:
            pospion[a,b] = True
        for a,b in pn:
            pospion[a,b] = True
        return(pospion)
        
    def jouerRnd(self):
        temp = []
        self.maj_pospions()
        for p in self.pions:
            temp += self.coups_possibles(p)
        ind = random.randint(0,len(temp)-1)
        return(temp[ind])
    
    def changer(self,ll,x,y):
        for i,l in enumerate(ll):
            if l ==x:
                ll[i]= y
                break
        
    
    def jouerprofondeur1(self):
        pb = []
        for p in self._canevas.pb:
            pb.append((p.casex,p.casey))
        pn = []
        for p in self._canevas.pn:
            pn.append((p.casex,p.casey))
            

        temp = []
        self.maj_pospions()
        for p in self.pions:
            temp += self.coups_possibles(p)
        
        score = 1300
        coupf  = temp[0]
        for t in temp:
            piece,coup = t
            if self.couleur =="black":
                self.changer(pn,coup[0],coup[-1])
            else:
                self.changer(pb,coup[0],coup[-1])
            score_eval = self.evaluer(pb,pn)
            if score_eval <= score:
                score = score_eval
                coupf = t
                
            if self.couleur =="black":
                self.changer(pn,coup[-1],coup[0])
            else:
                self.changer(pb,coup[-1],coup[0])
        return(coupf)
            
        
    def joueralphabeta(self,depth):
        pb = []
        for p in self._canevas.pb:
            pb.append((p.casex,p.casey))
        pn = []
        for p in self._canevas.pn:
            pn.append((p.casex,p.casey))
        
        pospion = self.pbpn2pospion(pb, pn)
        
        coups_possibles = []
        for p in pn:#on joue les noirs
            coups_possibles += self.coups_possibles2(p,pospion)
        alpha = -1e10
        beta = 1e10
        v = beta
        coup_a_jouer = coups_possibles[0]
        for iii,coup in enumerate(coups_possibles):
            self.changer(pn,coup[0],coup[-1])
            ab = self.alphabeta(depth-1,pb,pn,alpha,beta,"max")
            self.changer(pn,coup[-1],coup[0])
            if ab <= v:
                v = ab
                coup_a_jouer = coup
            if v <= alpha:
                coup_a_jouer = coup
                break
            beta = min(beta,v)
        for p in self.pions:
            if (p.casex,p.casey) == coup_a_jouer[0]:
                return(p,coup_a_jouer)
            
        
    
    def alphabeta(self,depth,pb,pn,alpha,beta,t):
        if self.evaluerpb(pb) ==20:
            return(1e10)
        if self.evaluerpn(pn) == 20:
            return(-1e10)
        if depth ==0:
            return(self.evaluer(pb,pn))
        if  t == "min":
            v = 1e10
            # récupération des coups possibles
            pospion = self.pbpn2pospion(pb, pn)
            fils = []
            for p in pn:#les noirs jouent
                fils += self.coups_possibles3(p,pospion)
                
            for fil in fils:
                self.changer(pn,fil[0],fil[-1])
                v = min(v,self.alphabeta(depth-1,pb,pn,alpha,beta,"max"))
                self.changer(pn,fil[-1],fil[0])
                
                if alpha >= v:
                    return(v)
                beta = min(beta,v)
        else:
            v = -9999999999999
            #récupération des fils
            pospion = self.pbpn2pospion(pb, pn)
            fils = []
            for p in pb:#leses blancs jouent
                fils += self.coups_possibles3(p,pospion)
            for fil in fils:
                self.changer(pb,fil[0],fil[-1])
                v = max(v,self.alphabeta(depth-1,pb,pn,alpha,beta,"min"))
                self.changer(pb,fil[-1],fil[0])
                if v >= beta:
                    return(v)
                alpha = max(alpha,v)
                
        return(v)
            
    
    def evaluer(self,pb,pn):
        return(6*self.evaluerpn(pn) -self.evaluerpb(pb))
                
    
    def evaluerpn(self,pn):
        rep = 0
        for p in pn:
            rep += p[0] + p[1]
        return(rep)
    
    def evaluerpb(self,pb):
        rep = 0
        for p in pb:
            rep +=14- p[0] - p[1]
        return(rep)
                
                


class Plateau(Tk):

    def __init__(self):

        
        
        Tk.__init__(self)
        
        # L'initialisation de l'arbre de scène se fait ici
        self.title('Fenetre principale')
        self.geometry('1200x850+300+0' )
        self.configure(bg = "grey")

        #initialisation de l'échiquier
        self.__zonePlateau = ZonePlateau(self,800,800)
        self.__zonePlateau.configure(bg='darkolivegreen')
        self.__zonePlateau.pack(padx = 50,side = LEFT)
        
        
        self.boutonIA= Button(self,text = "Jouer IA")
        self.boutonIA.pack(side=LEFT, padx  = 10)
        bfont = font.Font(family='Helvetica', size=40)
        self.boutonIA.config(command = self.__zonePlateau.jouerIA, bg = 'lightgrey', font = bfont)
        
        #Config des événements
        self.__zonePlateau.bind("<ButtonRelease-1>", self.__zonePlateau.bouton1_relache)
        self.__zonePlateau.bind("<Button-1>", self.__zonePlateau.bouton1_appuye)
        self.__zonePlateau.bind("<B1-Motion>", self.__zonePlateau.bouton1_deplace)
            
        
if __name__ == "__main__":
    

    fen = Plateau()
    fen.mainloop()
