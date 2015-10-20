#!/usr/bin/env python
#-*- coding: utf-8 -*-

#################################################################
#                           Fonctions                           #
#   Fonction de chargement de la config et de gestion des GPIO  #
#                                                               #
#    Auteur : Jucker Simon                                      #
#    Date : septembre 2015                                      #
#################################################################

import ConfigParser
import logging
import RPi.GPIO as g


#logger
logger = logging.getLogger("functions :")

#########################################
#        Chargement de la config        #
#########################################


def loadConfig():
    """
    Fonction de chargement des paramètres du fichier call.conf
    retourne un dictionaire; key = nom du paramètre; value = paramètre
    """
    try:
        configDict = {}
        config = ConfigParser.ConfigParser()
        config.read("call.conf")

        configDict["proxy"] = config.get('connexion', 'proxy')
        configDict["username"] = config.get('connexion', 'username')
        configDict["password"] = config.get('connexion', 'password')
        configDict["stun"] = config.get('connexion', 'serveur_STUN')

        configDict["uri_remote"] = config.get('remote', 'uri_destination')

        configDict["device_check"] = config.getboolean('devices', 'test_périphériques')
        configDict["camera"] = config.get('devices', 'camera')
        configDict["snd_capture"] = config.get('devices', 'micro')
        configDict["snd_playback"] = config.get('devices', 'playback')

        configDict["encryption"] = config.get('encryption', 'Chiffrement')
        configDict["encryption_mandatory"] = config.getboolean('encryption', 'Chiffrement_obligatoire')
        configDict["sip_tls"] = config.getboolean('encryption', 'Chiffrement_SIP_TLS')

        configDict["password_dtmf"] = str(config.get('passwords', 'password'))

        configDict["config_logs"] = config.getboolean('logs', 'Config_log')
        configDict["config_logs_path"] = config.get('logs', 'Chemin_fichier_config_log')

        #Mise en forme de la variable pour tls
        if configDict["sip_tls"]:
            configDict["sip_tls"] = "transport=tls"
        else:
            configDict["sip_tls"] = None

        #Mise en forme de la variable pour config log
        if configDict["config_logs"]:
            configDict["config_logs"] = configDict["config_logs_path"]
        else:
            configDict["config_logs"] = None

    except ConfigParser.NoSectionError:
        logger.error("Erreur de chargement du fichier de configuration")
        exit()

    except ConfigParser.ParsingError:
        logger.error("Erreur dans la structure du fichier de configuration")
        exit()

    except ValueError:
        logger.error("Erreur dans les valeurs du fichier de configuration, ou valeures manquantes")
        exit()

    else:
        logger.info("Configuration chargée avec succès")
        return configDict


def doorIsClose(ch):
    """
    Fonciton executées lors d'un changement d'état du contact de porte
    Met l'état de la LED porte a LOW
    """
    g.output(ch, g.LOW)
    logger.info("Porte fermée")


def doorIsOpen(ch):
    """
    Fonciton executées lors d'un changement d'état du contact de porte
    Met l'état de la LED porte a HIGH
    """
    g.output(ch, g.HIGH)
    logger.info("Porte ouverte")

