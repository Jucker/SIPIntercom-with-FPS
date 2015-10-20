#!/usr/bin/env python
#-*- coding: utf-8 -*-

##################################################################
#                       classes Input                            #
#              Création d'objet input avec les GPIO              #
#           Les input sont de type threaded callback,            #
# détéction à l'enfoncement (falling) et au relachement (rising) #
#                                                                #
#    Auteur : Jucker Simon                                       #
#    Date : septembre 2015                                       #
##################################################################


import RPi.GPIO as g
import logging

#logger
logger = logging.getLogger("Input :")


class Input:

    #Séléction du plan de numérotation des pins
    g.setmode(g.BCM)

    def __init__(self, channel, bouncetime, name, **kwargs):
        """
        Constructeur. Le nom sert a l'identification dans les logs.
        Liste des kwargs:
            falling:         fonction appelée à l'enfoncement du boutton
            rising:          fonction appelée au relâchement du boutton
            output_channel:  agrument de la fonction (ex: channel de sortie a modifier)
        """
        self.channel = channel
        self.bouncetime = bouncetime
        self.name = name
        self.kwargs = kwargs

        g.setup(self.channel, g.IN, pull_up_down=g.PUD_DOWN)
        logger.debug(self.name + ": Input créé")

        g.add_event_detect(self.channel, g.BOTH, bouncetime=bouncetime, callback=self.callback)
        logger.debug(self.name + ": Event créé")

    def callback(self, channel):
        """
        Mise en place des kwargs
        """
        if g.input(self.channel):
            if "falling" in self.kwargs:
                fn = self.kwargs["falling"]
                if "output_channel" in self.kwargs:
                    arg = self.kwargs["output_channel"]
                    fn(arg)
                else:
                    fn()
                logger.debug(self.name + ": Falling")
        else:
            if "rising" in self.kwargs:
                fn = self.kwargs["rising"]
                if "output_channel" in self.kwargs:
                    arg = self.kwargs["output_channel"]
                    fn(arg)
                else:
                    fn()
                logger.debug(self.name + ": Rising")