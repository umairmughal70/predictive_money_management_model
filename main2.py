# -*- coding: utf-8 -*-
"""
Copyright 2020-2022 Spiretech.co, Inc. All rights reserved.
Licenses: LICENSE.md
Description: Authorization API based component. This is a special component having a Scheduler based interface.
Reference: https://spiretech.atlassian.net/wiki/spaces/PA/pages/592183297/HE-FUC-015+Authorization

# Installation Guide

# Reference:
- https://developers.google.com/protocol-buffers/docs/proto3
- 

# Change History
"""
__author__  = "Adeel Yaqoob <adeel@spiretech.co>"
__version__ = "0.12"
__license__ = "Proprietary"

from utils.logging_init     import logging
from processor.inference_loader import InferenceLoaderutil
from utils.configloader import ConfigUtil
from processor.weekly_data_processor import DataLoaderUtil
import pandas as pd

class BootStart:

    __envConfiguration = None # Environment configuration object laoded from ConfigUtil

    """
    This is the main class for the authorization processor.
    """
    def __init__(self):
        """
        This is the constructor for the class.
        """                
        self.displayBanner()
        instance = ConfigUtil.getInstance()
        self.__envConfiguration = instance.configJSON
        self.displayBanner('ALL')

    def displayBanner(self,det=''):
        """ Display State of ENV variables"""        
        if det == 'ALL':              
            logging.info('')
        else:
            logging.info('*************************************')
            logging.info('┌─┐┌─┐┬┬─┐┌─┐┌┬┐┌─┐┌─┐┬ ┬ ┌─┐┌─┐')
            logging.info('└─┐├─┘│├┬┘├┤  │ ├┤ │  ├─┤ │  │ │')
            logging.info('└─┘┴  ┴┴└─└─┘ ┴ └─┘└─┘┴ ┴o└─┘└─┘')
            logging.info('*************************************')  

    def run(self):
        """ Start inference engine """
        dataLoader = DataLoaderUtil.getInstance()
        inputData = dataLoader.initGenerateData()
        retrunRes = False
        # print(inputData)
        # print(type(inputData))
        # if(inputData):
        #     for item in inputData['data']:
        #         print('\n######## ITEM: ', item, ' #############\n')
        #         inferenceObj = InferenceLoaderutil.getInstance()
        #         infrenceResult =  inferenceObj.execute_predictions(item)
        #         # print(infrenceResult)
        #         print('###############################################################')
        #         if(infrenceResult):
        #             saveResults = inferenceObj.save_predictions_db(infrenceResult)
        #             retrunRes = True
        #     return retrunRes
if __name__ == "__main__":
    bootStart = BootStart()
    bootStart.run()
    
