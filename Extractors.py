#!/usr/bin/python
#coding=utf-8
from rdflib import Graph, RDF, URIRef
from rdflib.namespace import XSD , FOAF, Namespace

def Sommets(texte) :
    """
    Fonction qui donne les sommets listés d'un fichier NRI
    Prend en paramètre la liste des lignes du fichier (créée avec readlines())
    Retourne un tableau des sommets
    """
    return texte[1].split("|")

def Attributs(texte) :
    """
    Fonction qui donne les attributs listés d'un fichier NRI
    Prend en paramètre la liste des lignes du fichier (créée avec readlines())
    Retourne un tableau des attributs
    """
    return texte[2].split("|")

def Itemsets(texte) :
    """
    Fonction qui donne l'itemsets d'un fichier NRI
    Prend en paramètre la liste des lignes du fichier (créée avec readlines())
    Retourne un tableau associatif/dictionnaire des sommet->attributs
    """
    itemsets = dict()
    #on commence a la 4eme ligne
    i = 3
    # le diese marque la fin de l'itemsets dans le fichier mais comme il y peut-être un espace on vérifie le premier carac de la ligne
    while texte[i][0] != "#" :
        tab1 = texte[i].split() #on sépare avec l'espace pour avoir d'un coté le numéros de sommet et de l'autre les numéros d'attributs
        nSommet = int(tab1[0])
        if len(tab1) > 1 : #attention aussi si on se retrouve avec un sommet sans attribut la vase tab[1] n'existe pas faudra la vérifier
            listAttributs = tab1[1].split(",") #attention listAttribut est un liste de numéros mais ce sont des String
        else :
            listAttributs = [] #un tableau vide
        itemsets[nSommet] = listAttributs
        i += 1
    return itemsets


def Graphe(texte) :
    """
    Fonction qui donne le graphe d'un fichier NRI
    Prend en paramètre la liste des lignes du fichier (créée avec readlines())
    Retourne un tableau associatif/dictionnaire des sommet->sommets liés
    Pas besoin de représenté les liaisons qui n'y sont pas donc c'est la même forme que l'itemsets
    """
    #pour connaitre la ligne du début : c'est après le #
    #ligne 1 est un commentaire
    #ligne 2 : liste des sommets
    #ligne 3 : liste des Attributs
    #ligne 4 : début de l'itemsets, liste des attributs de chaque sommets
    #ligne <nb de sommet + 3> : le #
    #ligne <nb de sommet + 4> : le début du graphe
    graph = dict()
    nbSommets = len(Sommets(texte))
    lgDebGraphe = nbSommets + 4
    #on peut aussi calculer le nb total de ligne : 2*nbSommets + 4
    #on parcours 2 fois tous les sommets (pour le graphe et l'itemsets) et on ajoute la ligne # et les 3 lignes du débuts
    nbTot = (2 * nbSommets) + 4
    i = lgDebGraphe
    while i < nbTot:
        tab1 = texte[i].split() #on sépare avec l'espace pour avoir d'un coté le numéro du sommet concerné et de l'autre les numéros des sommets liés
        nSommet = int(tab1[0])
        if len(tab1) > 1 : #attention aussi si on se retrouve avec un sommet sans lien la case tab[1] n'existe pas faudra la vérifier
            listliens = tab1[1].split(",") #attention listAttribut est un liste de numéros mais ce sont des String
        else :
            listliens = [] #un tableau vide
        graph[nSommet] = listliens
        i += 1
    return graph

def NRI(texte) :
    """
    Fonction qui créer un dictionnaire au format NRI à partir d'un fichier NRI
    Prend en paramètre la liste des lignes du fichier (créée avec readlines())
    Retourne un dictionnaire qui associe à chaque élément NRI ses données
    """
    nri = dict()
    sommets = Sommets(texte)
    attributs = Attributs(texte)
    itemsets = Itemsets(texte)
    graphe = Graphe(texte)
    nri["Graphe"] = graphe
    nri["Objets"] = sommets
    nri["Items"] = attributs
    nri["Itemsets"] = itemsets
    return nri

def AfficherNRI(dico):
    """
    """
    print(dico)


def getGrapheRDF(ttlFile) :
    """
    Crée et retourne un objet graphe de la librairi rdflib à partir d'un fichier turtle
    cet objet contient tout les triplets du fichier
    """
    graphe = Graph()
    graphe.parse(location=ttlFile, format="turtle")
    return graphe

def AfficherTriplets(graphe):
    """
    """
    for sujet, predicat, objet in graphe :
        print("\n")
        print(sujet)
        print(predicat)
        print(objet)
        print("\n---------------------")

ace = Namespace("http://www.semanticweb.org/acemap#")

def AjouterPrefixe(prefixe, chaine) :
    """
    Fonction qui ajouter un préfixe à une chaine de caractère et remplace les " " par des "_"
    retourne une chaine de caractères avec le préfixe placé devant
    exemple : AjouterPrefixe("AUTH", "Albert Einstein") retourne "AUTH_Albert_Einstein"
    """
    pref = prefixe + "_"
    new_chaine = pref + chaine.replace(" ", "_")
    return new_chaine

def ExtraireAuteurs(graphe) :
    """
    Extrait les identifiants des auteurs et leurs noms présents dans acemap
    prend en paramètre un objet graphe de la RDFlib
    retourne une dictionnaire qui associe authorID à son nom
    """

    IDToAuthors = dict()
    auteurs = graphe.subjects(RDF.type, ace.Author)
    for auteur in auteurs :
        noms = graphe.objects(auteur, ace.author_name)
        for nom in noms :
            IDToAuthors[auteur] = nom
    return IDToAuthors

def ExtraireConceptes(graphe, auteurs):
    """
    Extrait les domaines des auteurs
    prend en paramètre un objet graphe de rdflib et un liste d'id d'autheurs sous forme d'URI
    retourne un dictionnaire associant à un authorID tous les FieldID auxquelles il est rataché
    { authorID : [fieldID, fieldID, fieldID], authorID : [fieldID, ...] ... }
    """
    authIDToFieldID = dict()
    for auteur in auteurs :
        domaines = graphe.objects(auteur, ace.Field)
        authIDToFieldID[auteur] = []
        for domaine in domaines :
            authIDToFieldID[auteur].append(domaine)
    return authIDToFieldID

def ExtrairesDate(graphe, auteurs):
    """
    Extrait les dates de publication d'un auteur.
    prend en paramètre un graphe rdf et une liste d'authorID sous forme d'URI
    retourne un dictionnaire associant des authorID à des dates de publication 
    { authorID : [date, date, date], authorID : [date, ...] ... }
    """
    authIDToYears = dict()
    for auteur in auteurs :
        authIDToYears[auteur] = []
        #on va générer la liste de toutes les publication qui ont été ecrite par l'auteur en question
        publications = graphe.subjects(ace.paper_is_written_by, auteur)
        for publication in publications :
            dates = graphe.objects(publication, ace.paper_publish_date)
            for date in dates :
                authIDToYears[auteur].append(date)
    return authIDToYears

def ExtraireAuteursPubli(graphe) :
    """
    Extrait les auteurs pour toutes les publication
    prend en parametre un graphe rdf
    retourne un dictionnaire qui associe les paperID a tous ses authorID
    { paperID : [authorID, authoID, authorID], paperID : [authorID, ...] ... }
    """
    paperIDToAuthorID = dict()
    publications = graphe.subjects(RDF.type, ace.Paper)
    for publication in publications :
        auteurs = graphe.objects(publication, ace.paper_is_written_by)
        paperIDToAuthorID[publication] = []
        for auteur in auteurs :
            paperIDToAuthorID[publication].append(auteur)
    return paperIDToAuthorID

def YearFromDate(date) :
    """
    Extrait l'année d'un date qui est au format xsd.date (YYYY-MM-DD)
    Retourne la chaine de caractère correspondant à l'année de la date
    """
    return date[:4]
    


