# -*- coding: utf-8 -*-
"""
Copyright 2020-2022 Spiretech.co, Inc. All rights reserved.
Licenses: LICENSE.md
Description: AI Model processor component. This is a special component having an AI based predictions processor.

Reference: 


Utility class for loading daat from database and processing it as per requirment of AI model

Reference
- 

# Change History

"""
import os
import pandas as pd
import copy
import json
from utils.configloader import ConfigUtil
from utils.logging_init              import logging
from utils.file_loader import FileLoaderUtil
from utils.mssqlutil import MSSQLUtil
import db.constants as pr_constant
from processor.inference import Get_Predictions
from datetime import datetime


class InferenceLoaderutil:
    """
    Utility class for loading and processing data from database
    """
    __instance  = None

    @staticmethod
    def getInstance():
        if InferenceLoaderutil.__instance == None:
            InferenceLoaderutil()
        return InferenceLoaderutil.__instance
    
    def __init__(self):
        """
        Constructor for initializing the file loader isntance
        """
        if InferenceLoaderutil.__instance == None:
            InferenceLoaderutil.__instance = self
            self.__run()

    def __run(self):
        """
        Load configurations
        """
        instance = ConfigUtil.getInstance()
        self.__envConfiguration = instance.configJSON
        self.save_directory = os.path.join(self.__envConfiguration['dir.modelBaseLocation'], self.__envConfiguration['dir.modelName'])
        fileInstance = FileLoaderUtil.getInstance()
        self.meta_data = fileInstance.loadFile( self.save_directory, self.__envConfiguration['dir.meta_file'] )
        logging.info("preparing data for inference...")
        
    def read_input(self, input):
        
        """This method reads input coming as request from API, and normalizes the data."""
        logging.info("Input Data Received successfully...")
        try:
            df = pd.json_normalize(input) 
            unprocessed_df=copy.copy(df[~df.Spending.notnull()])
            unprocessed_df=unprocessed_df[['CustomerID','CategoryTypeCode','Week','AllocatedAmount']]
            unprocessed_df['CustomerID']=unprocessed_df['CustomerID'].astype(str)

            df['CustomerSeries'] = df['CustomerID'].astype(int).astype(str) + df['CategoryTypeCode'].astype(str).str.zfill(2)
            df.drop(['CustomerID','CategoryTypeCode'], axis = 1, inplace = True)

            logging.info("Input Data preprocessed successfully")
            return unprocessed_df,df
        
        except Exception as e:
            logging.error(e)

    def init_inference(self, input):
        try:
            logging.info("Inference Engine started")
            
            base_directory = self.__envConfiguration["dir.modelBaseLocation"]
            cat_df = self.meta_data['cat_df']
            cat_map = dict(zip(cat_df.CategoryTypeCode, cat_df.Code))
            for cats in input:
                cats['CategoryTypeCode'] = cat_map[cats['CategoryTypeCode']]


            unprocessed_df,df = self.read_input(input)

            obj = Get_Predictions(base_directory,df)
            obj.transform_dataset()
            results=obj.prepare_data()            
            merged_df=results.merge(unprocessed_df, on=['CustomerID','CategoryTypeCode','Week'])
            
            merged_df['Exceed Alert']=(merged_df['Spending']>merged_df['AllocatedAmount']).astype(int)
            merged_df[['CustomerID','CategoryTypeCode','Week','AllocatedAmount','Spending','Exceed Alert']]

            cat_map_db = dict(zip(cat_df.Code,cat_df.CategoryTypeCode))
            merged_df['CategoryTypeCode'] = merged_df['CategoryTypeCode'].map(cat_map_db)
            
            return merged_df
            
        except Exception as e:
            logging.error(e)

    def execute_predictions_api(self, input_received):
        try:
            logging.info("Inititating Inference Engine...")

            prepared_result = []
            prepared_input = []
            prepared_monthly_result = []
            for item in input_received.data:
                catData = [

                    {
                        "CustomerID": item.CustomerID,
                        "CategoryTypeCode": item.CategoryTypeCode,
                        "Week": item.Week[0],
                        "AllocatedAmount": item.AllocatedAmount[0],
                        "Spending": item.Spending[0]
                    },
                    {
                        "CustomerID": item.CustomerID,
                        "CategoryTypeCode": item.CategoryTypeCode,
                        "Week": item.Week[1],
                        "AllocatedAmount": item.AllocatedAmount[1],
                        "Spending": item.Spending[1]
                    },
                    {
                        "CustomerID": item.CustomerID,
                        "CategoryTypeCode": item.CategoryTypeCode,
                        "Week": item.Week[2],
                        "AllocatedAmount": item.AllocatedAmount[2],
                        "Spending": item.Spending[2]
                    },
                    {
                        "CustomerID": item.CustomerID,
                        "CategoryTypeCode": item.CategoryTypeCode,
                        "Week": item.Week[3],
                        "AllocatedAmount": item.AllocatedAmount[3],

                    },
                    {
                        "CustomerID": item.CustomerID,
                        "CategoryTypeCode": item.CategoryTypeCode,
                        "Week": item.Week[4],
                        "AllocatedAmount": item.AllocatedAmount[4],

                    },
                    {
                        "CustomerID": item.CustomerID,
                        "CategoryTypeCode": item.CategoryTypeCode,
                        "Week": item.Week[5],
                        "AllocatedAmount": item.AllocatedAmount[5],

                    }
                ]
                # raw_input = catData
                raw_input = copy.deepcopy(catData)  # Create a deep copy of the nested_list original_list.append(copied_nested_list)
                prepared_input.append(raw_input)
                inference_result = self.init_inference(catData)
                inference_result = json.loads(inference_result.to_json(orient='records'))
                prepared_result.append(inference_result)
                if prepared_result:
                    prepared_monthly_result.append(self.prepare_monthly_result(prepared_result, prepared_input))

            logging.info("Inference results prepared...")
            return prepared_monthly_result

        except Exception as e:
            logging.error(e)

    def calculate_spending_allocation(self,  inference_input, result_dict):
        for item in inference_input:
            print('\n calculating spend and allocation...')
            result_dict_prepared = {
                "CustomerID": '',
                "CategoryTypeCode": '',
                "Week": '',
                "AllocatedAmount": 0,
                "Spending": result_dict['Spending'],
                "Exceed Alert": 0,
                "Exceed Amount": 0,
            }
            for cat_item in item:
                prediction_week_ini = datetime.strptime(result_dict['Week'], '%Y-%m-%d')
                prediction_week = datetime.strptime(cat_item['Week'], '%Y-%m-%d')
                if prediction_week.month == prediction_week_ini.month and result_dict['CategoryTypeCode'] == cat_item['CategoryTypeCode']:
                    print('calculating same month and category spend and allocation')
                    result_dict_prepared['CustomerID'] = result_dict['CustomerID']
                    result_dict_prepared['CategoryTypeCode'] = result_dict['CategoryTypeCode']
                    result_dict_prepared['Week'] = result_dict['Week']
                    result_dict_prepared['AllocatedAmount'] += cat_item['AllocatedAmount']
                    if "Spending" in cat_item:
                        result_dict_prepared['Spending'] += cat_item['Spending']
                    result_dict_prepared['Exceed Alert'] = result_dict['Exceed Alert']
        print('======== Retrun from calculation is ===================')
        print(result_dict_prepared)
        print('\n')
        return result_dict_prepared


    def prepare_monthly_result(self, inference_result, inference_input):
        try:
            logging.info("Preparing Monthly Result Inference Engine...")
            print('\n InferenceInput is \n')
            print(inference_input)
            print('\n')
            print('\n InferenceResult is \n')
            print(inference_result)
            print('\n')
            infer_result = []
            for item in inference_result:
                result_dict = {
                        "CustomerID": '',
                        "CategoryTypeCode": '',
                        "Week": '',
                        "AllocatedAmount": 0,
                        "Spending": 0,
                        "Exceed Alert": 0,
                        "Exceed Amount": 0,
                    }
                for cat_item in item:
                    prediction_week_ini = datetime.strptime(item[0]['Week'], '%Y-%m-%d')
                    prediction_week = datetime.strptime(cat_item['Week'], '%Y-%m-%d')
                    if prediction_week.month == prediction_week_ini.month:
                        print(cat_item)
                        print('\n')
                        result_dict['CustomerID'] = cat_item['CustomerID']
                        result_dict['CategoryTypeCode'] = cat_item['CategoryTypeCode']
                        result_dict['Week'] = cat_item['Week']
                        # result_dict['AllocatedAmount'] += cat_item['AllocatedAmount']
                        result_dict['Spending'] += cat_item['Spending']
                        result_dict['Exceed Alert'] += cat_item['Exceed Alert']
                print('SUM...\n')
                print('########Result Cat Dict#############')
                print(result_dict)
                print('\n')
                result_dict = self.calculate_spending_allocation(inference_input, result_dict)
                print('##########Prepared Result from Past is#############:\n')
                print(result_dict)
                print('#############################\n')
                if result_dict['CustomerID'] != '':

                    if result_dict['Exceed Alert'] > 0:
                        result_dict['Exceed Alert'] = 1
                        result_dict['Exceed Amount'] = round(result_dict['Spending'] - result_dict['AllocatedAmount'], 2)
                    result_dict['AllocatedAmount'] = round(result_dict['AllocatedAmount'], 2)
                    result_dict['Spending'] = round(result_dict['Spending'], 2)
                    print(result_dict)
                    infer_result.append(result_dict)
                    print('\n')
            logging.info("Inference monthly results prepared...")
            print('-------------------------------\n')
            print(infer_result)

            return infer_result

        except Exception as e:
            logging.error(e)

    def execute_predictions(self, input_received):
        try:
            logging.info("Initiating Inference Engine...")

            prepared_result = []
            for item in input_received:
                catData = [
                    {
                        "CustomerID": item['CustomerID'],
                        "CategoryTypeCode": item['CategoryTypeCode'],
                        "Week": item['Week'][0],
                        "AllocatedAmount": item['AllocatedAmount'][0],
                        "Spending": item['Spending'][0]
                    },
                    {
                        "CustomerID": item['CustomerID'],
                        "CategoryTypeCode": item['CategoryTypeCode'],
                        "Week": item['Week'][1],
                        "AllocatedAmount": item['AllocatedAmount'][1],
                        "Spending": item['Spending'][1]
                    },
                    {
                        "CustomerID": item['CustomerID'],
                        "CategoryTypeCode": item['CategoryTypeCode'],
                        "Week": item['Week'][2],
                        "AllocatedAmount": item['AllocatedAmount'][2],
                        "Spending": item['Spending'][2]
                    },
                    {
                        "CustomerID": item['CustomerID'],
                        "CategoryTypeCode": item['CategoryTypeCode'],
                        "Week": item['Week'][3],
                        "AllocatedAmount": item['AllocatedAmount'][3],
                    },
                    {
                        "CustomerID": item['CustomerID'],
                        "CategoryTypeCode": item['CategoryTypeCode'],
                        "Week": item['Week'][4],
                        "AllocatedAmount": item['AllocatedAmount'][4],
                    },
                    {
                        "CustomerID": item['CustomerID'],
                        "CategoryTypeCode": item['CategoryTypeCode'],
                        "Week": item['Week'][5],
                        "AllocatedAmount": item['AllocatedAmount'][5],
                    }
                ]
                # print('\nInference Input In Loop: ', catData, '\n')
                inference_result = self.init_inference(catData)
                inference_result = json.loads(inference_result.to_json(orient='records'))
                # print('\n Inference Result: ', inference_result)
                # print('\n')
                prepared_result.append(inference_result)

            logging.info("Inference results prepared...")
            print(prepared_result)
            return prepared_result
        except Exception as e:
            logging.error(e)

    def save_predictions_db(self, input_results):
        try:
            logging.info("Initiating Inference Engine...")
            retrunResult = False
            if (input_results):
                sqlInstance = MSSQLUtil.getInstance()
                # sqlInstance.transactionQuery(self.__envConfiguration['db.tunrcatePredTableQry'])
                for item in input_results:
                    if item:
                        resultDf = pd.DataFrame(item, columns=['CustomerID', 'CategoryTypeCode', 'Week', 'Spending', 'AllocatedAmount', 'Exceed Alert'])
                        print(resultDf)
                        logging.info("Table truncated")
                        for index, row in resultDf.iterrows():
                            sqlParams = [row['CustomerID'], row['CategoryTypeCode'], row['Week'], row['Spending'], row['AllocatedAmount'], row['Exceed Alert']]
                            sqlInstance.transactionQuery(pr_constant.INSERT_AI_PREDICTIONS_SQL, sqlParams)
                            retrunResult = True
                        logging.info("Category wise inference result saved to DB...")
            return retrunResult
        except Exception as e:
            logging.error(e)