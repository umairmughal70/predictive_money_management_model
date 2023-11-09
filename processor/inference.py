
import pandas as pd
import os
from os.path import join, dirname
import numpy as np
import pickle
from tensorflow.keras.models import load_model
from datetime import timedelta
from utils.logging_init import logging
from utils.configloader import ConfigUtil
from utils.file_loader import FileLoaderUtil
import copy

import warnings
warnings.filterwarnings("ignore")

class Get_Predictions():
    def __init__(self, base_directory,input):

        try:
            logging.info("Constructor Called")

            instance = ConfigUtil.getInstance()
            self.__envConfiguration = instance.configJSON

            self.save_directory = os.path.join(self.__envConfiguration['dir.modelBaseLocation'], self.__envConfiguration['dir.modelName'])
            fileInstance = FileLoaderUtil.getInstance()
            self.meta_data = fileInstance.loadFile( self.save_directory, self.__envConfiguration['dir.meta_file'] )

            self.features = self.meta_data['features']
            self.all_columns = self.meta_data['all_columns']
            self.object_cols = self.meta_data['object_cols']
            self.numeric_cols = self.meta_data['numeric_cols']
            self.timestamp_cols = self.meta_data['timestamp_cols']
            self.timesteps = self.meta_data['timesteps']
            self.forecast_horizon = self.meta_data['forecast_horizon']
            self.n_features = self.meta_data['n_features']
            self.feature_scaler = self.meta_data['feature_scaler']
            self.numeric_col_means = self.meta_data['numeric_col_means']
            self.group_specific_numeric_col_means = self.meta_data['group_specific_numeric_col_means']
            self.target_column = self.meta_data['target_column']
            self.look_back = self.meta_data['timesteps']
            self.dimension_cols = self.meta_data['dimension_cols']
            self.date_column = self.meta_data['date_column']
            self.all_groups = []
            self.frequency = self.meta_data['frequency']
            logging.info("lookback = {0}, timesteps = {1}".format(self.look_back , self.meta_data['timesteps']))
            self.model = load_model(os.path.join(os.path.dirname(__file__),self.save_directory, self.__envConfiguration["dir.modelObj"]))
            self.frequencies = {'Monday': 'W-MON', 'Tuesday': 'W-TUE', 'Wednesday': 'W-WED', 'Thursday': 'W-THU',
                                'Friday': 'W-FRI', 'Saturday': 'W-SAT', 'Sunday': 'W-SUN'} 
            
            self.x_test = input
            self.x_test = self.x_test[self.all_columns]
            self.x_test[self.date_column] = pd.to_datetime(self.x_test[self.date_column])

            self.add_records = 0

            if self.object_cols:
                self.oe = self.meta_data['categorical_encoder']
                self.x_test[self.object_cols] = self.oe.transform(self.x_test[self.object_cols])
            
            
        except Exception as e:
            logging.error(e)

    def get_test_data(self, x_test):
        """This method generates test data in the format which LSTM Model takes as input."""

        try:
            in_start = 0
            features, target = list(), list()
            x_test = x_test.values
            for _ in range(len(x_test)):
                # define the end of the input sequence
                in_end = in_start + self.meta_data['timesteps']
                out_end = in_end + self.forecast_horizon
                # ensure we have enough data for this instance
                if out_end <= len(x_test):
                    x_input = x_test[in_start:in_end, :]  # Leaving date column
                    features.append(x_input)
                    target.append(
                        x_test[in_end:out_end, len(self.all_columns) - 1])  # Just target column which is at the last
                # move along one time step
                in_start += self.forecast_horizon
                
            x_test = np.array(features)
            y_test = np.array(target)

            logging.info("Model ready input data generated")
            return x_test, y_test

        except Exception as e:
            logging.error(e)

    def normalize_data(self):
        """This method normalizes the test dataset before feeding to the model as our model was trained on the normalized data."""
        try:
            logging.info("Normalizing Data")
            if len(self.features) > 1:
                test_data_shape = self.x_test.shape
                self.x_test = self.x_test.reshape((test_data_shape[0] * test_data_shape[1], test_data_shape[2]))
                feature_scaler = self.meta_data['feature_scaler']
                self.x_test[:, 1:len(self.all_columns) - 1] = feature_scaler.transform(
                    self.x_test[:, 1:len(self.all_columns) - 1])

                self.feature_scaler = feature_scaler
                self.x_test = self.x_test.reshape(test_data_shape)

                logging.info("Data Normalized")

        except Exception as e:
            logging.error(e)

    def transform_dataset(self):
        """This method transforms the test dataset into the format which is ready to feed the trained model to get predictions."""
        try:

            logging.info("Data Transformation started")
            grouped_data = self.x_test.groupby(self.dimension_cols)
            group_no = 1

            for group_name, df_grouped in grouped_data:

                if group_no == 1:

                    logging.info('Total data of {} is : {}'.format(group_name,len(df_grouped)))
                    self.x_test, self.y_test = self.get_test_data(df_grouped)
                    self.all_groups.append(group_name)
                else:

                    logging.info('Total data of {} is : {}'.format(group_name,len(df_grouped)))
                    x_test, y_test = self.get_test_data(df_grouped)
                    

                    self.x_test = np.concatenate((self.x_test, x_test))
                    self.y_test = np.concatenate((self.y_test, y_test))
                    self.all_groups.append(group_name)

                group_no += 1

            self.normalize_data()
            logging.info("Data Transformed")
        except Exception as e:
            logging.error(e)

    def prepare_data(self):
        """This method prepares data using test and predicted data of each customer to get any budget exceedings. """
        
        try:
            all_predictions = []
            predictions = self.model.predict(self.x_test[:, :, 1:len(self.all_columns)].astype(np.float64),verbose=1)
        
            for index, data_chunk in enumerate(self.x_test):
                df_input = pd.DataFrame(data=data_chunk, columns=self.all_columns)
                df_input[self.features[1:]] = self.feature_scaler.inverse_transform(df_input[self.features[1:]])
                cols = [self.date_column] + self.dimension_cols + [self.target_column]
                df_input = df_input[cols]

                df_output = pd.DataFrame()
                if self.frequency == 'D':
                    s_date = df_input[self.date_column].iloc[-1]
                    df_output[self.date_column] = pd.date_range(s_date + timedelta(days=1),
                                                            periods=self.forecast_horizon,
                                                            freq=self.frequency)

                elif self.frequency == 'W' or self.frequency == 'w':
                    if df_input[self.date_column].iloc[-1].day in [1,8,15]:
                        s_date = df_input[self.date_column].iloc[-1] + timedelta(days=7)
                    else:
                        s_date = df_input[self.date_column].iloc[-1] + timedelta(days=32)
                        s_date  = s_date.replace(day=1)
                    dow = s_date.strftime('%A')[:]

                    df_output[self.date_column] = pd.date_range(s_date,
                                                            periods=self.forecast_horizon,
                                                            freq=self.frequencies[dow])
                    if df_output[self.date_column].iloc[-1].day == 29 :
                        df_output[self.date_column].iloc[-1] = df_output[self.date_column].iloc[-1] + timedelta(days=32)
                        df_output[self.date_column].iloc[-1] = df_output[self.date_column].iloc[-1].replace(day = 1)

                else:
                    s_date = df_input[self.date_column].iloc[-1]
                    df_output[self.date_column] = pd.date_range(s_date,
                                                            periods=self.forecast_horizon,
                                                            freq=self.frequency)

            
                df_output[self.dimension_cols] = df_input[self.dimension_cols]
                df_output[self.dimension_cols] = df_output[self.dimension_cols].ffill()
                
                df_output['Spending'] = predictions[index]

                df_input_output = pd.concat([df_input, df_output], ignore_index=True)
                
                df_input_output = pd.concat([df_output], ignore_index=True)


                all_predictions.append(df_input_output)



            df_final = pd.concat(all_predictions, ignore_index=True)

            df_final['Spending'][df_final['Spending']<1]=0

            #Removing the unnecessary predictions

            df_final["CustomerSeries"] = df_final["CustomerSeries"].astype(int)
            df_final["CustomerID"] = df_final['CustomerSeries'].astype(str).str[:-2]  
            
            df_final["CategoryTypeCode"] = df_final['CustomerSeries'].astype(str).str[-2:]  
            df_final.drop(['CustomerSeries'], axis = 1, inplace = True)
            df_final = df_final[['CustomerID', 'CategoryTypeCode', 'Week', 'Spending']]

            df_final['Week']=df_final['Week'].astype(str)

            return df_final
            
        
        except Exception as e:
            logging.error(e)
