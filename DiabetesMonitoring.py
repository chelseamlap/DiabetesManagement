"""
A Python module to import diabetes management data from various sources for use to
integrate multiple views.

Supported files:
- Dexcom
- Omnipod log files (manually copied from Omnipod)

Future planned support:
- AppleHealth data


Chelsea Lapeikis
University of Utah
11-24-2017


"""
import os
import pandas as pd
import datetime
from datetime import time
import dateutil
import numpy as np
import holoviews as hv

hv.extension('bokeh')

__version__ = '0.1'


# Define person class
class Person(object):
    """
    A class for characteristics of a person.
    """

    def __init__(self, first_name=None, sex='F', dob=None):
        self.sex = sex
        self.first_name = first_name
        if dob is None:
            self.__dob = None
        elif isinstance(dob, str):
            try:
                self.__dob = dateutil.parser.parse(dob)
            except Exception as error:
                print(error)
                self.__dob = None
        elif isinstance(dob.datetime.date):
            self.__dob = dob
        else:
            raise TypeError("Invalid date of birth specification")

    @property
    def dob(self):
        return self.__dob

    @property
    def age(self):
        td = datetime.datetime.now() - self.__dob
        return {"years": td.days // 365, "months": td.days % 365 // 30}

    @property
    def sex(self):
        return self.__sex

    @sex.setter
    def sex(self, value):
        if not isinstance(value, str):
            raise TypeError("Sex must be a string")
        if not value.upper()[0] in "MF":
            raise ValueError("Sex must be Male or Female")
        self.__sex = value.upper()[0]

    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, value):
        if value is None:
            if self.sex == 'F':
                value = "Jane"
            else:
                value = "John"
        if not isinstance(value, str):
            raise TypeError("first name must be a string")
        self.__first_name = value

    def get_characteristics(self):
        """Get the individual characteristics in a string"""
        txt = """First Name=%s\n""" % self.first_name
        txt += """Sex=%s\n""" % self.sex
        txt += "Age=%d years, %d months\n" % (self.age["years"],
                                              self.age["months"])
        return txt


# Define Diabetic Person class
class Diabetic(Person):
    """
    A class for Diabetic people - inherits from the Person class
    """

    def __init__(self, first_name, sex, dob,
                 a1c_target=7.0, diagnosis_year='', diagnosis_type=1):
        Person.__init__(self, first_name, sex, dob)
        self.__a1c_target = a1c_target
        self.diagnosis_year = diagnosis_year
        self.diagnosis_type = diagnosis_type

    @property
    def a1c_target(self):
        return self.__a1c_target

    @a1c_target.setter
    def a1c_target(self, value):
        if not type(value) == float:
            raise TypeError("Target a1c value must be a number.")
        if type(value) == float:
            self.a1c_target = value

    @property
    def eag_target(self):
        """
        Returns the average blood glucose level for the target a1c.
        Source: http://care.diabetesjournals.org/content/diacare/early/2008/06/07/dc08-0545.full.pdf
        """
        eag = 28.7 * self.a1c_target - 46.7
        return eag


# -------------------------------------------------------------------
# -------------------------------------------------------------------


# Insulin on board (IOB) information is only contained within a comment string and must be extracted
regexMeal_IOB = r"""Meal IOB: (\d{0,2}\.\d{1,2})(?=;)"""
regexCorrection_IOB = r"""Correction IOB: (\d{0,2}\.\d{0,2})"""
varOverride = "Override"
omnipod_data_save = os.path.join('DiabetesManagement', 'Data', 'Omnipod', 'Generated')
dexcom_data_save = os.path.join('DiabetesManagement', 'Data', 'Dexcom', 'Generated')


class DiabetesData(object):
    """
    A class for diabetes data sources specific to this project.
    Data Sources:
        - Omnipod (11/2017)
        - Dexcom
    """

    def __init__(self, file_folder, file_name, data_source):
        self.file_folder = file_folder
        self.path = os.path.abspath(os.path.join("..", file_folder, file_name))
        self.directory = os.path.abspath(os.path.join("..", file_folder))
        self.file_format = os.path.splitext(self.path)[1]
        self.data_source = data_source

        if self.file_format not in ['.xlsx', '.xls', '.csv']:
            raise TypeError('File must be .xlsx, .xls, or .csv.')

        if self.data_source not in 'Dexcom,Omnipod':
            raise 'Accepts raw Omnipod log or Dexcom file (from Clarity).'

    @property
    def file_name(self):
        return self.file_name

    def read_data(self):
        """
        A function to read data into a dataframe from a variety of sources.

        :return: A diabetes dataframe.  This dataframe is also saved in the Generated subfolder
        of your data directory.
        """
        if self.file_format == ".xlsx" and self.data_source.upper() == "OMNIPOD":
            diabetes_dataframe = pd.read_excel(self.path, na_values='').fillna('0 NoDescription') \
                .drop_duplicates()
        elif self.file_format == ".csv" and self.data_source.upper() == "OMNIPOD":
            diabetes_dataframe = pd.read_csv(self.path, na_values='').fillna('0 NoDescription') \
                .drop_duplicates()

        # By definition, Dexcom data should not contain duplicates.
        elif self.file_format == ".xlsx" and self.data_source.upper() == "DEXCOM":
            diabetes_dataframe = pd.read_excel(self.path, header=0, skiprows=range(1, 15)) \
                .dropna(how="all", axis=1).drop_duplicates()
        elif self.file_format == ".csv" and self.data_source.upper() == "DEXCOM":
            diabetes_dataframe = pd.read_csv(self.path, header=0, skiprows=range(1, 15)). \
                dropna(how="all", axis=1).drop_duplicates()
        else:
            print("Function only accepts raw Omnipod (log) or Dexcom file (from Clarity).")

        # Generate a pickle file to save the data
        timestr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        diabetes_dataframe.to_csv(self.directory+'\\Generated\\'+self.data_source+'_Read_'+timestr+".csv",
                                  compression='gzip')

        return diabetes_dataframe

    def __str__(self):
        txt = "Datasource: %s\n" % self.data_source
        txt += "File is located at: %s\n" % self.path

        return txt


# ----------------------------------------------------
# ----------------------------------------------------


class Omnipod(DiabetesData):
    def __init__(self, file_folder, file_name, data_source="", diabetes_df=""):
        DiabetesData.__init__(self, file_folder, file_name, data_source)
        self.__diabetes_df = diabetes_df

    @property
    def diabetes_df(self):
        diabetes_df = DiabetesData.read_data(self)
        return diabetes_df


def omnipod_remove_summary(x):
    df_x = x[x.Type != 'Insulin Summary']
    df_x = df_x[df_x.Type != 'Notes']
    df_x = df_x[df_x.Type != 'Pump Alarm']
    df_x = df_x[df_x.Type != 'Glucose']
    return df_x


def omnipod_extract_dedup(df_i):
    """
    A function to return a cleaned up version of a dataframe.
    :param df_i:
    :return:
    """
    df = omnipod_remove_summary(df_i)

    # Change is_copy to False to eliminate warnings
    df.is_copy = False

    # Split units from values
    df['Value'], df['Units'] = df['Value'].str.split(' ', 1).str
    df[['Value']] = df[['Value']].apply(pd.to_numeric)
    df = df.fillna(float(0))

    # Create datetime field
    df['Date'] = df['Date'].apply(lambda x: x.date())
    df['Date Time'] = df[['Date', 'Time']].apply(lambda x: datetime.datetime.combine(*list(x)) \
                                                 , axis=1)

    # IOB values
    df['Meal IOB'] = df['Comment'].str.extract(regexMeal_IOB, expand=True)
    df['Meal IOB'] = df['Meal IOB'].apply(lambda x: float(x))
    df['Correction IOB'] = df['Comment'].str.extract(regexCorrection_IOB, expand=True)
    df['Correction IOB'] = df['Correction IOB'].apply(lambda x: float(x))

    # Add override flag
    df['Manual Override'] = pd.np.where(df.Comment.str.contains(varOverride), 1, 0)

    # remove redundancies to make data pivot table
    df.drop_duplicates()
    df['Bolus Clean'] = pd.np.where(
        df.Description.str.contains('Reverse Corrected.'),
        "Reverse Corrected",
        pd.np.where(df.Description.str.contains("Bolus-Meal"), "Meal Bolus",
                    pd.np.where(df.Description.str.contains("Correction"), "Correction Bolus",
                                pd.np.where(df.Description.str.contains("Extended"),
                                            "Extended Meal Bolus",
                                            pd.np.where(
                                                df.Description.str.contains("Basal suspended"),
                                                "Basal Suspended",
                                                pd.np.where(df.Description.str.contains(
                                                    "Temporary basal rate set"), "Temp Basal",
                                                    pd.np.where(df.Description.str.contains(
                                                        "Pod deactivated"),
                                                        "Pod Deactivated",
                                                        pd.np.where(
                                                            df.Description.str.contains("Basal resumed"),
                                                            "Basal Resumed",
                                                            df["Type"]))))))))

    return df


def omnipod_to_tabular(df_i):
    """
    A function to convert omnipod data in a dataframe to a usable (tabular) format for visualization
    :param df_i:
    :return: A cleaned up and tabularized Omnipod dataframe.  This data is also saved as a gzip to the Generated
    sub-folder in the Data section of your repository.  This will allow you to explore the data in excel as well.
    """
    df_o = omnipod_remove_summary(df_i)
    df_o = omnipod_extract_dedup(df_o)
    df_pivot = df_o.pivot(index='Date Time', columns='Bolus Clean', values='Value')
    df_pivot['Date Time'] = df_pivot.index  # Add Date Time index back into dataframe as a column

    new = pd.merge(df_pivot, df_o, how='inner', on='Date Time')

    # Removed glucose and pump alarm because they were causing duplicated.  12-14-17
    new = new[['Date Time',
               'Meal',  # carbohydrates
               'Meal Bolus', 'Bolus Insulin', 'Correction Bolus',
               'Extended Meal Bolus', 'Reverse Corrected',
               'Meal IOB', 'Correction IOB', 'Manual Override',
               'Basal Insulin', 'Basal Resumed', 'Basal Suspended', 'Temp Basal',
               'Pod Deactivated', 'Date', 'Time']]

    new = new.replace(np.NaN, 0.00).drop_duplicates()

    # create a csv with the newly cleaned dataframe
    timestr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    npath = os.path.abspath(os.path.join("..", omnipod_data_save, "Omnipod_Tabular" + timestr + ".csv"))
    new.to_csv(npath)  # , compression='gzip')

    return new


def average_bolus(df_i, list_cols=['Date', 'Meal Bolus', 'Correction Bolus', 'Bolus Insulin',
                                 'Extended Meal Bolus', 'Reverse Corrected', 'Total Bolus']):
    """
    A function that calculates the average daily bolus used.
    param: df_i - use the cleaned up insulin dataframe, the step after reading the data in
    """
    df = df_i[list_cols]
    df_x = df.replace(0, np.NaN)
    df_y = (df_x.mean(), df_x.count())
    return df_y


def daily_bolus(df_i):
    """
    A function to calculate the amount of bolus insulin used daily.
    param: df_i - use the cleaned up insulin dataframe, the step after reading the data in
    """

    table = pd.pivot_table(df_i, values='Total Bolus', index='Date', aggfunc=np.sum).reset_index()
    table['Date'] = table['Date'].astype('datetime64[ns]')
    return table


# ----------------------------------------------------
# ----------------------------------------------------


class Dexcom(DiabetesData):
    def __init__(self, file_folder, file_name, data_source="", diabetes_df=""):
        DiabetesData.__init__(self, file_folder, file_name, data_source)
        self.__diabetes_df = diabetes_df

    @property
    def diabetes_df(self):
        diabetes_df = DiabetesData.read_data(self)
        return diabetes_df


def dexcom_clean(dexcom_df):
    """
    A function to clean dexcom data to a better format for joining to Omnipod data.

    Input:
        - dexcom_df - a Dexcom dataframe generates from earlier functions

    Output:
        - A new dataframe cleaned up with better names and date formats to support joining
    """
    dexcom = dexcom_df
    dexcom = dexcom.rename(columns={'Timestamp (YYYY-MM-DDThh:mm:ss)': 'event_time'})
    dexcom['event_time'] = dexcom['event_time'].astype('datetime64[ns]')
    return dexcom


# ----------------------------------------------------
# ----------------------------------------------------


def bolus_efficacy(df_o, df_d, shift_minutes=120,
                   min_date=datetime.datetime(2000, 1, 1, 0, 0, 0),
                   max_date=None):
    """
    A function that will combine Insulin and Blood Glucose data, group the data by times of
    day, and show the resulting blood sugar values a variable time period after the bolus.
    Blood sugar and insulin measurements have a tolerance of 4.5 minutes as blood sugar is
    measured by the Dexcom every 5 minutes.

    Input:
    :param df_o: A dataframe generated from an early function containing insulin/bolus information
    :param df_d: A dataframe generated from the Dexcom data
    :param shift_minutes: shift_minutes = # of minutes (integer) to view blood sugar after bolus.
            shift_minutes default is 120 minutes, a standard value for understanding meal-bolus
    :param min_date: The minimum date for the window to explore
    :param max_date: The maximum date for the window to explore. Default is current date.

    :return:
        - A dataframe containing both Dexcom (blood sugar) and Omnipod (insulin) information.
    """

    if max_date is not None and not isinstance(max_date, datetime.datetime):
        raise TypeError('max_date must be datetime.')

    elif max_date is None:
        max_date = datetime.datetime.today()

    if min_date is not None and not isinstance(min_date, datetime.datetime):
        raise TypeError('min_date must be datetime.')

    bolus = df_o[['Date Time', 'Date', 'Time',
                  'Meal', 'Meal Bolus', 'Bolus Insulin', 'Correction Bolus', 'Extended Meal Bolus',
                  ]]
    hours = bolus['Date Time'].dt.hour.values
    times = np.array(['1. Morning', '2. Afternoon', '3. Evening', '4. Post Evening'])

    # In a future version, this should be variable.
    bolus = bolus.assign(BolusTimeOfDay=times[np.array([8, 12, 16]).searchsorted(hours)])
    bolus['BolusTimeOfDay'] = bolus['BolusTimeOfDay']

    # Join Omnipod and Dexcom data within the tolerance of 4.5 minutes
    omnipod_bolus = pd.merge_asof(bolus, df_d, left_on='Date Time', right_on='event_time',
                                  tolerance=pd.Timedelta("4.5 minutes"), direction="nearest") \
        .dropna(how="all", axis=1) \
        .rename(columns={'Time_x': 'Bolus Time'})

    # Simplify the dataframe after the merge
    omnipod_bolus = omnipod_bolus[['Date Time', 'Date', 'Time',
                                   'Meal', 'Meal Bolus', 'Bolus Insulin', 'Correction Bolus',
                                   'Extended Meal Bolus', 'Glucose Value (mg/dL)',
                                   'BolusTimeOfDay'
                                   ]]

    omnipod_bolus['TimeShift'] = omnipod_bolus['Date Time'] + datetime.timedelta(minutes=shift_minutes)
    omnipod_bolus = omnipod_bolus.rename(columns={'Time': 'Bolus Time', 'Glucose Value (mg/dL)': 'Glucose at Bolus'})

    omnipod_bolus = pd.merge_asof(omnipod_bolus, df_d, left_on='TimeShift', right_on='event_time',
                                  tolerance=pd.Timedelta("4.5 minutes"), direction="nearest").dropna(how="all", axis=1)

    omnipod_bolus = omnipod_bolus[['Date Time', 'Date', 'Bolus Time',
                                   'Meal', 'Meal Bolus', 'Bolus Insulin', 'Correction Bolus', 'Extended Meal Bolus',
                                   'Glucose at Bolus',
                                   'Glucose Value (mg/dL)',
                                   'BolusTimeOfDay'
                                   ]].rename(columns={'Glucose Value (mg/dL)': 'Glucose after time period',
                                                      'BolusTimeOfDay': 'Bolus Time of Day'})

    # extended meal bolus is excluded as it is a percentage of the actual bolus
    omnipod_bolus['Total Bolus'] = omnipod_bolus['Meal Bolus'] + \
                                   omnipod_bolus['Bolus Insulin'] + \
                                   omnipod_bolus['Correction Bolus']

    # Only include boluses where there is a glucose measurement at the bolus, and after the bolus
    # time shifted
    omnipod_bolus_only = omnipod_bolus[(omnipod_bolus['Total Bolus'] > 0.0) &
                                       (omnipod_bolus['Glucose at Bolus'] > 0.0) &
                                       (omnipod_bolus['Glucose after time period'] > 0.0)]

    # omnipod_meal = omnipod_bolus[(omnipod_bolus['Meal'] > 0.0)]

    omnipod_bolus_only = omnipod_bolus_only[(omnipod_bolus_only['Date Time'] >= min_date) &
                                            (omnipod_bolus_only['Date Time'] <= max_date)]

    return omnipod_bolus_only


def glucose_bolus_df(df_o, df_d,
                     min_date=datetime.datetime(2000, 1, 1, 0, 0, 0),
                     max_date=None):
    """
    A function to combine glucose values with bolus values for viewing on a time-series.  The
    default tolerance for a bolus-glucose relationship is 4.5 minutes

    :param df_o: A dataframe generated from an early function containing insulin/bolus information
    :param df_d: A dataframe generated from the Dexcom data
    :param min_date: The minimum date for the window to explore
    :param max_date: The maximum date for the window to explore. Default is current date.
    :return: A dataframe combining both sets of information.
    """

    if max_date is not None and not isinstance(max_date, datetime.datetime):
        raise TypeError('max_date must be datetime.')
    elif max_date is None:
        max_date = datetime.datetime.today()

    if min_date is not None and not isinstance(min_date, datetime.datetime):
        raise TypeError('min_date must be datetime.')

    # First, select only bolus data from this dataframe
    df_o['Total Bolus'] = df_o['Meal Bolus'] + df_o['Bolus Insulin'] + df_o['Correction Bolus']

    df_o = df_o[(df_o['Total Bolus'] > 0.0)]

    bolus = df_o[['Date Time', 'Date', 'Time', 'Total Bolus']]

    # Join Omnipod and Dexcom data within the tolerance of 4.5 minutes
    dexcom_bolus = pd.merge_asof(left=df_d, right=bolus, left_on='event_time', right_on='Date Time',
                                 tolerance=pd.Timedelta("4.5 minutes"), direction="nearest")

    # Return only the columns that are relevant
    dexcom_bolus['BolusFlg'] = np.where(dexcom_bolus['Total Bolus'] > 0.0,
                                        dexcom_bolus['Glucose Value (mg/dL)'],
                                        dexcom_bolus['Total Bolus'])
    dexcom_bolus = dexcom_bolus[['event_time', 'Glucose Value (mg/dL)', 'BolusFlg']]

    dexcom_chart = dexcom_bolus[(dexcom_bolus['event_time'] >= min_date) &
                                (dexcom_bolus['event_time'] <= max_date)]

    return dexcom_chart





