#!/usr/bin/env python
#-*- coding: utf- -*-

###################################################################
#        Portier IP open source avec lecteur d'empreinte          #
#                                                                 #
#   Pré requis                                                    #
#   liblinphone 3.8.0 pour python                                 #
#     https://wiki.linphone.org/wiki/index.php/Raspberrypi:start  #
#    pyGT511C3; fichier FPS.py version modifiée par l'auteur      #
#     version originale : https:github.com/QuickGroup/pyGT511C3   #
#    Fichier ClientSIP                                            #
#    Fichier function.py                                          #
#    Fichier Input                                                #
#    Fichier Output                                               #
#    Fichier de configuration call.conf                           #
#                                                                 #
#    Le fichier call.conf contient les paramètres du client SIP   #
#        Utiliser le chiffrement TLS et SRTP pour chiffrer les    #
#        flux audio et vidéo                                      #
#                                                                 #
#    Fichier utilisable en mode debug, niveau par défaut:INFO     #
#                                                                 #
#    En cas d'échec au premier lancement du script, relancer      #
#                                                                 #
#    Auteur : Jucker Simon                                        #
#    Date : septembre 2015                                        #
###################################################################


import logging
import sys
import thread
import time
import RPi.GPIO as g
import linphone as lin
from pygame import mixer

import functions as f
import ClientSIP as sip
import Input as I
import Output as O
import FPS

#Logger, console et fichier log situé a la racine du dossier
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO}
#format logs dans le fichier
logging.basicConfig(filename = "./logs/mainlogs", format = '%(asctime)s %(name)-4s %(levelname)-4s %(message)s', level=logging.INFO)
logger = logging.getLogger()
console = logging.StreamHandler()
console.setLevel(logging.INFO)
#format logs dans la console
formatter = logging.Formatter('%(asctime)s %(name)-4s %(levelname)-4s %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

if len(sys.argv) > 1:
    level_name = sys.argv[1]
    level = LEVELS.get(level_name, logging.NOTSET)
    console.setLevel(level=level)
    logger.setLevel(level=level)

fps = None
core = None
LED_gache = None
LED_porte = None
attempt = 0

#Fonctions
def openDoor():
    """
    Fonction d'ouverture de la porte, referme automatiquement après 5 seconde
    """
    LED_gache.setHigh()
    time.sleep(5)#timer
    LED_gache.setLow()
    logger.info("Fermeture de la porte par le timer")


def ringbell(*args):
    """
    Fonction exectuée lors de la pression sur la sonnette
    Appel le client distant paramétré dans call.conf
    Appel les fonctions de récupération des codes DTMF et le traitement du password pramétré dans call.conf
    """
    global attempt
    attempt = 0
    #mixer.init()
    #door_bell = mixer.Sound('bell2.wave')
    #door_bell.play()
    logger.info("Sonnettre actionée")
    core.makeCall(config["uri_remote"])

    dtmfCollection()


def dtmfCollection():
    """
    Récupère les codes DTMF durant l'appel.
    Construit un string de 4 chiffre
    Appel la fonction de test de password
    """
    dtmf_string = ""
    dtmf_aborted = False

    while True:

        logger.debug("Liste dtmf: " + str(core.dtmf_list))
        time.sleep(1)

        if len(core.dtmf_list) >= 4:
            for element in core.dtmf_list:
                dtmf_string += element
            del core.dtmf_list[:]
            break

        if core.call.state == lin.CallState.End:
            dtmf_aborted = True
            del core.dtmf_list[:]
            break

    if not dtmf_aborted:
        passwordTest(dtmf_string)

def passwordTest(dtmf_string):
    """
    Test le mot de passe
    Si 3 échecs consécutif termine l'appel
    """

    global attempt

    password = config["password_dtmf"]

    if dtmf_string == password:
        logger.info("Ouverture de la porte par code DTMF")
        openDoor()

    elif not dtmf_string == password and attempt < 3:
        logger.info("Mauvais code DTMF")
        attempt +=1
        dtmfCollection()

    elif attempt >= 3:
        core.core.terminate_all_calls()
        logger.warning("3 essais échoués pour l'ouverture de la porte par code DTMF, appel terminé")


def enroll():
    """
    Fonction d'enregistrement d'un user pour le fps. Les users sont identifés par un int
    La recherche d'un id libre peut prendre du temps
    Il faut 3 prises pour faire l'enrollement
    Affiche la réussite ou l'échec de chaque prises
    Affiche la réussite ou l'échec de la procédure
    Ne retourne rien
    """
    #Recherche porchain Id de libre
    enrollid = fps.GetEnrollCount()#= nb total d'enregistrement
    okid=False
    #vérification de l'id (libre ou non)
    while not okid and enrollid < 200: #boucle de contrôle
        okid = not fps.CheckEnrolled(enrollid)
        if not okid:
            enrollid += 1
        if enrollid >= 200: # Si id = 200 (max mémoire) on retourne a 0 pour chercher des id qui aurait été effacées
            enrollid = 0

    #Start enroll process
    print "Appuyer votre doigt pour l'enregistrement %s" % str(enrollid)
    fps.SetLED(True)
    time.sleep(0.3)
    check = fps.EnrollStart(enrollid)

    while not fps.IsPressFinger():
        time.sleep(0.3)
    #1st take
    if fps.CaptureFinger(True):
        print 'Enlevez le doigt'
        logger.debug(fps.Enroll1())

        while fps.IsPressFinger():
            time.sleep(0.3)

        #2nd take
        print 'Appuyer votre doigt pour la 2ème prise'

        while not fps.IsPressFinger():
            time.sleep(0.3)

        if fps.CaptureFinger(True):
            print 'Enlevez le doigt'
            logger.debug(fps.Enroll2())

            while fps.IsPressFinger():
                time.sleep(0.3)

            #3rd take
            print 'Appuyer votre doigt pour la 3ème prise'

            while not fps.IsPressFinger():
                time.sleep(0.3)

            if fps.CaptureFinger(True):
                check = fps.Enroll3()
                fps.SetLED(False)
                logger.debug(check)

            #control
                if check == 'ACK':
                    logger.info("Enregistrement réussi pour l'ID: %s" % str(enrollid))
                else:
                    logger.error('Enregistrement échoué : %s' % str(check))
            else:
                logger.error("Echec 3ème prise")
        else:
            logger.error("Echec 2ème prise")
    else:
        logger.error("Echec 1ème prise")


def identification():
    """
    Fonction d'identification utilisée pour l'exploitation du portier
    A appeler dans un autre thread
    Log l'id de l'utilisateur
    Appel openDoor()
    """
    fps.SetLED(True)
    while True:
        if fps.IsPressFinger():
            logger.debug("doigt appuyé")
            if fps.CaptureFinger(False):
                logger.debug("Capture réussie")
                userid = fps.Identify1_N()
                logger.debug ("UserID: " + str(userid))
                if userid == 200:
                    logger.warning("Echec de l'authentification par le FPS")
                else:
                    logger.info("L'utilisateur " + str(userid) + " s'est authentifié")
                    logger.info("Ouverture de la porte")
                    openDoor()
            else:
                logger.error("Echec capture")


def initiateFps():
    """
    Création de l'objet fps
    """
    fps = FPS.FPS_GT511C3(device_name='/dev/ttyAMA0', baud=115200, timeout=2, is_com=False)
    fps.SetLED(False)
    fps.UseSerialDebug = False# Mettre à True pour afficher les bytes reçus et envoyés

    return fps


def menu():
    """
    Affichage du menu
    """
    try:
        print("\n            Menu du portier\n\
            ===================================\n\
            1 : Enregistrer une empreinte\n\
            2 : Supprimer une empreinte\n\
            3 : Mettre le portier en exploitation\n\
            4 : Informations\n\
            5 : Quitter")

        #Choix utilisateur
        choice_value = input("Choix: ")

        #Enregistrement
        if choice_value == 1:
            enroll()
            menu()

        #Suppression
        elif choice_value == 2:
            ID = input("User id a supprimer (-1 = tous): ")
            if ID == -1:
                check = fps.DeleteAll()
                if check:
                    logger.info ("DB effacée")
                else:
                    logger.info ("Erreur")
            else:
                check = fps.DeleteID(ID)
                if check:
                    logger.info ("User " + str(ID) + " supprimé")
                else:
                    logger.info ("Erreur")
            menu()

        #Exploitation
        elif choice_value == 3:
            logger.info ("Mode exploitation, ctrl+c pour quitter")
            fps.SetLED(True)
            thread.start_new_thread(identification(), ())
            menu()

        #Info
        elif choice_value == 4:
            print "Infos"
            menu()

        #Quitter
        elif choice_value == 5:
            g.cleanup()
            core.core.terminate_all_calls()
            core.quit=True
            fps.SetLED(False)
            time.sleep(1)
            fps.Close()
            quit()

        else:
            raise ValueError

    except ValueError or SyntaxError:
        logger.error ("Choix d'option de menu incorrect")
        menu()

#main
try:
    #Chargement configuration
    config = f.loadConfig()

    #Client SIP
    core = sip.SIPclient(config)
    thread.start_new_thread(core.iterate, ())
    if config["device_check"]:
        core.deviceCheck()

    #Commande porte
    g.setwarnings(False)
    LED_porte_channel = 13
    LED_porte_initial_state = "high"

    LED_gache_channel = 19
    LED_gache_initial_state = "low"

    ct_porte_channel = 5
    sonnette_channel = 6

    #Création output
    LED_porte = O.Output(LED_porte_channel, LED_porte_initial_state, "LED_porte")
    LED_gache = O.Output(LED_gache_channel, LED_gache_initial_state, "LED_gache")

    #Création input
    I.Input(ct_porte_channel, 10, "ct_porte", falling=f.doorIsClose, rising=f.doorIsOpen, output_channel=LED_porte_channel)
    I.Input(sonnette_channel, 2000, "sonnette", falling=ringbell)

    #Création FPS
    fps = initiateFps()

    #appel menu
    menu()

except KeyboardInterrupt:
    core.quit = True
    g.cleanup()
    core.core.terminate_all_calls()
    core.quit=True
    fps.SetLED(False)
    time.sleep(0.5)
    fps.Close()