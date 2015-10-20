#!/usr/bin/env python
#-*- coding: utf-8 -*-

#################################################################
#                      classeClientSIP                          #
#             Définition d'une classe de client SIP             #
#  Création du core, enregistrement, appel et récupération DTMF #
#                                                               #
#    Auteur : Jucker Simon                                      #
#    Date : septembre 2015                                      #
#################################################################


import linphone as lin
import time
import logging


#logger
logger = logging.getLogger("ClientSIP :")

class SIPclient:

    registering_progress = True
    registering_ok = True

    def __init__(self, configuration):
        """
        Constructeur. Création de l'objet en fonction des paramètres du fichier call.conf'
        """
        self.quit = False
        self.dtmf_list = []
        self.callbacks = {'call_state_changed': self.callStateChanged,
                     'registration_state_changed': self.registrationStateChanged,
                      'dtmf_received': self.dtmfReceived,
        }

        #création du core et paramètrage
        self.core = lin.Core.new(self.callbacks, configuration["config_logs"], None)

        self.core.echo_cancellation_enabled = False
        self.core.video_capture_enabled = True
        self.core.video_display_enabled = False
        self.core.max_calls = 1

        self.core.video_device = configuration["camera"]
        self.core.capture_device = configuration["snd_capture"]
        self.core.playback_device = configuration["snd_playback"]

        self.core.firewall_policy = lin.FirewallPolicy.PolicyUseStun
        self.core.stun_server = configuration["stun"]

        if configuration["encryption"] == "ZRTP":
            self.core.media_encryption = lin.MediaEncryption.ZRTP
        elif configuration["encryption"] == "SRTP":
            self.core.media_encryption = lin.MediaEncryption.SRTP
        elif configuration["encryption_mandatory"]:
            self.core.media_encryption_mandatory = True

        #codecs audio, activation du payload seuleument si le codec correspond
        for codec in self.core.audio_codecs:
            if codec.mime_type == "PCMA" or codec.mime_type == "PCMU":
                self.core.enable_payload_type(codec, True)
            else:
                self.core.enable_payload_type(codec, False)

        #codecs video
        for codec in self.core.video_codecs:
            if codec.mime_type == "VP8":
                self.core.enable_payload_type(codec, True)
            else:
                self.core.enable_payload_type(codec, False)

        self.registration(configuration)

    #Configuration du compte SIP
    def registration(self, configuration):
        """
        Création et ajout des paramètres nécéssaires a l'enregistrement au core
        Appelé automatiquement dans le constructeur
        """
        proxy_cfg = self.core.create_proxy_config()
        proxy_cfg.identity = 'sip:{username}@{proxy}'.format(username = configuration["username"], proxy = configuration["proxy"])
        proxy_cfg.server_addr = 'sip:{proxy};{tls}'.format(proxy = configuration["proxy"], tls = configuration["sip_tls"])
        proxy_cfg.register_enabled = True
        self.core.add_proxy_config(proxy_cfg)
        auth_info = self.core.create_auth_info(configuration["username"], None, configuration["password"], None, None, configuration["proxy"])
        self.core.add_auth_info(auth_info)

    def makeCall(self, uri):
        """
        Création d'un appel (objet call) uri est l'adresse à atteindre
        """
        self.call = self.core.invite(uri)

    def deviceCheck(self):
        """
        Fonction de test des capacité des device pour l'audio et la vidéo
        Affiche la liste des devices
        Affiche True si le device peut être utilisé
        """
        sound_device_list = self.core.sound_devices
        video_device_list = self.core.video_devices
        print ("Peripherique audio :", sound_device_list)

        for i, devid in enumerate(sound_device_list):
            print(devid, "Peut capturer", self.core.sound_device_can_capture(devid))
            print(devid, "Peut jouer", self.core.sound_device_can_playback(devid))

        print ("Peripherique video :", video_device_list)

    def callStateChanged(self, core, call, state, message):
        """
        Fonction appelée lors d'un changement d'état de l'appel
        Les états peuvent être récupérés avec Instance of ClentSIP.call.state
        """

        if call.state == lin.CallState.OutgoingInit:
            logger.debug("Appel en cours")

        elif call.state == lin.CallState.OutgoingRinging:
            logger.debug("Sonne")

        elif call.state == lin.CallState.Connected:
            logger.debug("Connecté")

        elif call.state == lin.CallState.StreamsRunning:
            logger.info("Appel établi")

        elif call.state == lin.CallState.End:
            logger.info("Appel terminé")
            call_log = call.call_log
            logger.info("Duree de l'appel: " + str(call_log.duration))
            self.core.terminate_all_calls()

    def registrationStateChanged(self, core, proxy_cfg, state, message):
        """
        Fonction appelée lors d'un changement d'état de l'enregistrement
        Les états peuvent être récupérés avec Instance of ClentSIP.proxy_cfg.state
        """

        if proxy_cfg.state == lin.RegistrationState.Progress:
            logger.debug("Enregistrement proxy SIP en cours")

        elif proxy_cfg.state == lin.RegistrationState.Ok:
            logger.info("Enregistrement proxy SIP réussi")

        elif proxy_cfg.state == lin.RegistrationState.Failed:
            logger.error("Enregistrement proxy SIP échoué")

    def dtmfReceived(self, core, call, digits):
        """
        Fonction appelé lors de la récéption d'un code DTMF selon la RFC 2833
        Les valeurs peuvent être récupérée avec Instance of ClientDIP.dtmf_list
        """
        digit = chr(digits)
        logger.debug("DTMF:" + digit)
        self.dtmf_list.append(digit)

    def iterate(self):
        """
        Fonction de gestion des tâches de fond et d'actualisation des états
        A lancer après le constructeur dans un autre thread et avant la fonction makeCall()
        """
        while not self.quit:
            self.core.iterate()
            time.sleep(0.5)


