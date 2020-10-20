import random
import pandas as pd
import os


# PATH_UPLOADS = '/home/ateffal/mysite/uploads/'
# PATH_UPLOADS = '/app/'

PATH_UPLOADS = os.getcwd() + '/'

# Helper functions
def save_file(fic, path=None):
    """Saves file to path

    Parameters
    ----------
    fic : File object
        The file location of the spreadsheet
    path : string, optional
        path to which the file will be saved

    Returns
    -------
    tuple
        dataframe, file name
    """

    fic_name = fic.filename

    if fic_name == '':
        return None, ''

    if path == None:
        path = PATH_UPLOADS + "data/"

    print('path = ' , path)

    fic.save(path + fic_name)
    data = pd.read_csv(path + fic_name, sep=";", decimal=",")
    return data, fic_name

def get_secret_key():
    """Rturn a 14 lenght random string

    """
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    letters = [alphabet[i] for i in range(52)]
    sk = ""
    for i in range(14):
        temp = random.choice(range(52))
        sk = sk + letters[temp]
        sk = sk + str(random.choice(range(100)))
    return sk


def fic_to_func(path_fic, not_found_return_value = 0):
    """Transforms a csv file to a function.
       This function returns the value of the last column
       of the file when passed the values of first columns
       as parameters. If such combinaison does not exist,
       the function returns 0

    Parameters
    ----------
    path_fic : string
               full path of the file.

    not_found_return_value : numeric

    Returns
    -------
    tuple
        function, names of parameters (list)

    """
    df = pd.read_csv(path_fic, sep=";", decimal=",")
    cols = list(df.columns)[:-1]
    val = list(df.columns)[-1]

    def func(**params):
        assert len(cols) == len(
            params), 'number of parameters must much cols of file'
        assert list(
            params.keys()) == cols, 'parameters does not much colonnes of file'
        df_temp = df.copy()
        i = 0
        for param, value in params.items():
            df_temp = df_temp[df_temp[cols[i]] == value]
            i = i+1
        if len(list(df_temp[val])) == 1:
            return list(df_temp[val])[0]
        else:
            return not_found_return_value

    return func, tuple(cols)


def df_to_func(df, not_found_return_value = 0):
    """Transforms a dataframe to a function.
       This function returns the value of the last column
       of the dataframe when passed the values of first columns
       as parameters. If such combinaison does not exist,
       the function returns 0

    Parameters
    ----------
    df : dataframe

    not_found_return_value : numeric

    Returns
    -------
    tuple
        function, names of parameters (list)

    """

    if not isinstance(df, pd.DataFrame):
        return None
    cols = list(df.columns)[:-1]
    val = list(df.columns)[-1]

    def func(*params):
        assert len(cols) == len(
            params), 'number of parameters must much cols of file'
        # assert list(params.keys()) == cols, 'parameters does not much colonnes of file'
        df_temp = df
        i = 0
        for value in params:
            df_temp = df_temp[df_temp[cols[i]] == value]
            i = i+1
        if len(list(df_temp[val])) == 1:
            return list(df_temp[val])[0]
        else:
            return 0

    return (func, cols)


def fic_repl_to_law_repl(df):

    if df is None:
        return None

    # get df columns
    df_cols = list(df.columns)

    if 'group_out' in df_cols and 'year_' in df_cols:
        return create_law_repl_gy(df)

    if 'group_out' in df_cols:
        return create_law_repl_g(df)

    if 'year_' in df_cols:
        return create_law_repl_y(df)


# Create replacement law function if group_out and year_ are present in df
def create_law_repl_gy(df):

    def law(departures_, year_):
        new_employees = []
        j = 0
        key = ''
        data_=[]
        for g in departures_:
            # get lines from df with group_out = g and year_=year_
            df_g = df[(df['group_out']==g) & (df['year_']==year_)]
            df_g = df_g.reset_index(drop=True)
            n = len(df_g)
            for i in range(n) :
                key = 'id_' + str(j) + '_year_' + str(df_g.loc[i,'year_'])
                data_= list(df_g.loc[i,:])[4:]

                temp = {'key': key, 'number': departures_[g]*df_g.loc[i,'replacement_rate'],'data':data_}
                new_employees.append(temp)
                j = j + 1
        return new_employees

    return law



# Create replacement law function if only group_out is present in df
def create_law_repl_g(df):

    def law(departures_, year_):
        new_employees = []
        j = 0
        key = ''
        data_=[]
        for g in departures_:
            # get lines from df with group_out = g
            df_g = df[(df['group_out']==g)]
            df_g = df_g.reset_index(drop=True)
            n = len(df_g)
            for i in range(n) :
                key = 'id_' + str(j) + '_year_' + str(year_)
                data_= list(df_g.loc[i,:])[3:]
                temp = {'key': key, 'number': departures_[g]*df_g.loc[i,'replacement_rate'],'data':data_}
                new_employees.append(temp)
                j = j + 1
        return new_employees

    return law


# Create replacement law function if only year_ is present in df
def create_law_repl_y(df):

    def law(departures_, year_):
        new_employees = []
        j = 0
        key = ''
        data_=[]
        for g in departures_:
            # get lines from df with year_ = year_
            df_g = df[(df['year_']==year_)]
            df_g = df_g.reset_index(drop=True)
            n = len(df_g)
            for i in range(n) :
                key = 'id_' + str(j) + '_year_' + str(year_)
                data_= list(df_g.loc[i,:])[3:]
                temp = {'key': key, 'number': departures_[g]*df_g.loc[i,'replacement_rate'],'data':data_}
                new_employees.append(temp)
                j = j + 1
        return new_employees

    return law