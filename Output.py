#!/usr/bin/env python
#-*- coding: utf-8 -*-

#################################################################
#                       classes Output                          #
#         Création d'objet de type output pour les GPIO         #
#                                                               #
#    Auteur : Jucker Simon                                      #
#    Date : septembre 2015                                      #
#################################################################

import RPi.GPIO as g
import logging

#logger
logger = logging.getLogger("Output :")
    #g.setwarning(False)


class Output:
    g.setmode(g.BCM)

    def __init__(self, channel, initial_state, name):
        """
        Constructeur. Le nom sert pour l'identificatio dans les logs'
        """
        self.channel = channel
        self.initial_state = initial_state
        self.name = name

        #Séléction du plan de numérotation des pins
        g.setmode(g.BCM)
        if initial_state == "low":
            g.setup(self.channel, g.OUT, initial=g.LOW)

        elif initial_state == "high":
            g.setup(self.channel, g.OUT, initial=g.HIGH)

        logger.debug(self.name + ": Output créé")

    def setHigh(self):
        """
        Mise de la sortie à l'état haut
        """
        g.output(self.channel, g.HIGH)
        logger.debug(self.name + ": High")

    def setLow(self):
        """
        Mise de la sortie à l'état bas
        """
        g.output(self.channel, g.LOW)
        logger.debug(self.name + ": Low")

    def getState(self):
        """
        Retourne l'état actuel de la sortie
        True = haut
        False = bas
        """
        if g.input(self.channel):
            return True
        else:
            return False