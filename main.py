# -*- coding: utf-8 -*-
"""
Copyright 2020-2022 Spiretech.co, Inc. All rights reserved.
Licenses: LICENSE.md
Description: Authorization API based component. This is a special component having a FastAPI based interface.
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
import time
from lib2to3.pytree import Base
from operator import lt
from fastapi import FastAPI, Path
import uvicorn
import os
from pydantic import BaseModel
from typing import List

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
        """ Start inferecne engine """  
        app_host = self.__envConfiguration['dir.appHost']
        env_port = int(self.__envConfiguration['dir.appPort'])
        context_root = self.__envConfiguration['dir.appContext']
        app = FastAPI()

        class PredictionsBase(BaseModel):

            CustomerID: int
            CategoryTypeCode: str
            Week: list 
            AllocatedAmount: List[int] = None
            Spending: List[float] = None 

        class PredictionList(BaseModel):
            data: List[PredictionsBase]
            
        @app.post(context_root+"/predictions")
        def get_predictions(data:PredictionList):
            # inferenceObj = InferenceLoaderutil()
            inference_monthly = ''
            inferenceObj = InferenceLoaderutil.getInstance()
            inferenceRes = inferenceObj.execute_predictions_api(data)
            # if inferenceRes:
            #     inference_monthly = inferenceObj.prepare_monthly_result(inferenceRes)
            return inferenceRes

        @app.get(context_root+"/healthcheck/")
        def healthcheck():
            return 'Health - OK'
        
        
        uvicorn.run(app, host=app_host, port=env_port)

        return True

if __name__ == "__main__":
    bootStart = BootStart()
    bootStart.run()
    
