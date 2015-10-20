#!/usr/bin/env python
#-*- coding: utf- -*-
import FPS
"""
Change baudrate from 9600 to 115200
"""
fps =  FPS.FPS_GT511C3(device_name='/dev/ttyAMA0', baud=9600, timeout=2, is_com=False)
fps.ChangeBaudRate(115200)
fps.Close()