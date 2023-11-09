# -*- coding: utf-8 -*-
"""
Copyright 2020-2022 Spiretech.co, Inc. All rights reserved.
Licenses: LICENSE.md
Description: Utility file for managing configurations
Reference: https://spiretech.atlassian.net/wiki/spaces/PA/pages/592183297/HE-FUC-015+Authorization

# Reference:
- https://developers.google.com/protocol-buffers/docs/proto3
-


# Change History
[23042022/MFB/SIN-416] - Authentication and Authorization
"""

from environs               import Env
from marshmallow.validate import OneOf, Email, Length, Range, Equal
from utils.logging_init          import logging

class ConfigUtil:

    __instance      = None
    configJSON     = {
        ## Load all configurations here
        "db.host"                   : "", # PRED_MONEY_DB_SERVER
        "db.port"                   : "", # PRED_MONEY_DB_PORT
        "db.name"                   : "", # PRED_MONEY_DB_NAME
        "db.user"                   : "", # PRED_MONEY_DB_USERNAME
        "db.password"               : "", # PRED_MONEY_DB_PASSWORD
        "db.aiDbName"               : "", # PRED_MONEY_AI_DB_NAME
        "db.stmttimeout"            : "", # PRED_MONEY_DB_STMT_TIMEOUT
        "dir.modelBaseLocation"     : "", # PRED_MONEY_MODEL_BASE_DIRECTORY
        "dir.modelName"             : "", # PRED_MONEY_MODEL_NAME
        "dir.modelObj"              : "", # PRED_MONEY_DEPLOYED_MODEL_OBJECT
        "dir.meta_file"             : "", # PRED_MONEY_MODEL_META_FILE
        "dir.appHost"               : "", # PRED_MONEY_APP_HOST
        "dir.appContext"            : "", # PRED_MONEY_APP_CTXROOT
        "dir.appPort"               : "", # PRED_MONEY_APP_PORT
        "db.queryCatTypes"          : "", # PRED_MONEY_QUERY_CATTYPES
        "db.queryBudgetTrans"       : "", # PRED_MONEY_QUERY_BUDGETTRANS
        "db.queryBudget"            : "", # PRED_MONEY_QUERY_BUDGET
        "db.tunrcateBudgtTableQry"  : "", # PRED_MONEY_TRUNC_TABLE_QUERY
        "db.tunrcatePredTableQry"   : "", # PRED_MONEY_TRUNC_PRED_TABLE_QUERY
        "db.budgetTable"            : "", # PRED_MONEY_TABLE_NAME
        "db.predictionsTable"       : "", # PRED_MONEY_PREDICTIONS_TABLE_NAME
        "dir.monthsBack"            : "", # PRED_MONEY_MONTHS_BACK
        "dir.leastMonths"           : "", # PRED_MONEY_LEAST_MONTHS
        "dir.totalMonths"           : "", # PRED_MONEY_TOTAL_MONTHS
    }
        
    @staticmethod
    def getInstance():
        """ Static access method for gettign the class isntance """
        if ConfigUtil.__instance == None:
            ConfigUtil()
        return ConfigUtil.__instance        

    def __init__(self):
        if ConfigUtil.__instance == None:
            ConfigUtil.__instance = self            
            self.__loadEnvironmentVariables()            

    def __loadEnvironmentVariables(self):
        """ Loads environment variables in configJSON dictionary """
        logging.info("Loading environment variables...")
        env = Env()
        env.read_env()
        # Database Related Variablees
        self.configJSON['db.host']                  = env.str('PRED_MONEY_DB_SERVER',                 validate=[Length(min=1,max=128, error='Invalid host name. Should not be > 128 chars')])
        self.configJSON['db.port']                  = env.str('PRED_MONEY_DB_PORT',                   validate=[Length(min=4,max=5,   error ='Invalid database port. Should not be > 5 chars')])
        self.configJSON['db.name']                  = env.str('PRED_MONEY_DB_NAME',                   validate=[Length(min=1,max=128, error ='Invalid database name. Should not be > 128 chars')])
        self.configJSON['db.user']                  = env.str('PRED_MONEY_DB_USERNAME',               validate=[Length(min=1,max=128, error ='Invalid database username, Should not be > 128 chars')])
        self.configJSON['db.password']              = env.str('PRED_MONEY_DB_PASSWORD',               validate=[Length(min=1,max=128, error ='Invalid database password. Should not be > 128 chars')])
        self.configJSON['db.aiDbName']              = env.str('PRED_MONEY_AI_DB_NAME',                validate=[Length(min=1,max=128, error ='Invalid AI database name. Should not be > 128 chars')])
        self.configJSON['db.stmttimeout']           = env.str('PRED_MONEY_DB_STMT_TIMEOUT', validate=[ Length(min=1, max=5, error='Invalid statement timeout. Should not be > 5 chars')])
        self.configJSON['dir.modelBaseLocation']    = env.str('PRED_MONEY_MODEL_BASE_DIRECTORY',validate=[Equal("../data", error ='Invalid model directory name')])
        self.configJSON['dir.modelName']            = env.str('PRED_MONEY_MODEL_NAME',validate=[Equal("LSTM", error ='Invalid model name')])
        self.configJSON['dir.modelObj']             = env.str('PRED_MONEY_DEPLOYED_MODEL_OBJECT',validate=[Equal("deployed_model_new.h5", error ='Invalid deployed model object name')])
        self.configJSON['dir.meta_file']            = env.str('PRED_MONEY_MODEL_META_FILE',validate=[Equal('meta_data_new', error ='Invalid AI model meta file name')])
        self.configJSON['dir.appHost']              = env.str('PRED_MONEY_APP_HOST',validate=[Length(min=7,max=50,   error ='Invalid App host')])
        self.configJSON['dir.appContext']           = env.str('PRED_MONEY_APP_CTXROOT',validate=[Length(min=2,max=20,   error ='Invalid App context root')])
        self.configJSON['dir.appPort']              = env.str('PRED_MONEY_APP_PORT',validate=[Length(min=2,max=4,   error ='Invalid App Port')])
        self.configJSON['db.queryCatTypes']         = env.str('PRED_MONEY_QUERY_CATTYPES',validate=[Length(min=1,   error ='Invalid category type query. Should not be < 0 chars')])
        self.configJSON['db.queryBudgetTrans']      = env.str('PRED_MONEY_QUERY_BUDGETTRANS',validate=[Length(min=1,   error ='Invalid budget transactions query. Should not be < 0 chars')])
        self.configJSON['db.queryBudget']           = env.str('PRED_MONEY_QUERY_BUDGET',validate=[Length(min=1,   error ='Invalid budget query. Should not be < 0 chars')])
        self.configJSON['db.tunrcateBudgtTableQry'] = env.str('PRED_MONEY_TRUNC_TABLE_QUERY',validate=[Length(min=1,   error ='Invalid weekly budget query. Should not be < 0 chars')])
        self.configJSON['db.tunrcatePredTableQry']  = env.str('PRED_MONEY_TRUNC_PRED_TABLE_QUERY',validate=[Length(min=1,   error ='Invalid predictions truncate query. Should not be < 0 chars')])
        self.configJSON['db.budgetTable']           = env.str('PRED_MONEY_TABLE_NAME',validate=[Length(min=1,   error ='Invalid weekly budget table. Should not be < 0 chars')])
        self.configJSON['db.predictionsTable']      = env.str('PRED_MONEY_PREDICTIONS_TABLE_NAME',validate=[Length(min=1,   error ='Invalid predictions budget table. Should not be < 0 chars')])
        self.configJSON['dir.monthsBack']           = env.str('PRED_MONEY_MONTHS_BACK',               validate=[Length(min=1,max=2,   error ='Invalid months back. Should not be > 2 chars')])
        self.configJSON['dir.leastMonths']          = env.str('PRED_MONEY_LEAST_MONTHS',              validate=[Length(min=1,max=2,   error ='Invalid least motnhs. Should not be > 2 chars')])
        self.configJSON['dir.totalMonths']          = env.str('PRED_MONEY_TOTAL_MONTHS',              validate=[Length(min=1,max=2,   error ='Invalid total months. Should not be > 2 chars')])

        # Write project specific configuration items below:
        # END        
                     