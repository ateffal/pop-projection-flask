import random
import pandas as pd


# PATH_UPLOADS = '/home/ateffal/mysite/uploads/'
PATH_UPLOADS = './uploads/'

# Helper functions
def save_file(fic, path=None):
    fic_name = fic.filename
    if path == None:
        path = PATH_UPLOADS + "data/"

    fic.save(path + fic_name)
    data = pd.read_csv(path + fic_name, sep=";", decimal=",")
    return data, fic_name

def get_secret_key():
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    letters = [alphabet[i] for i in range(52)]
    sk = ""
    for i in range(14):
        temp = random.choice(range(52))
        sk = sk + letters[temp]
        sk = sk + str(random.choice(range(100)))
    return sk


def fic_to_func(path_fic):
    df = pd.read_csv(path_fic, sep=";", decimal=",")
    cols = list(df.columns)[:-1]
    val = list(df.columns)[-1]

    def func(**params):
        assert len(cols) == len(
            params), 'number of parameters must much cols of file'
        assert list(
            params.keys()) == cols, 'parameters does not much colonnes of file'
        df_temp = df
        i = 0
        for param, value in params.items():
            df_temp = df_temp[df_temp[cols[i]] == value]
            i = i+1
        if len(list(df_temp[val])) == 1:
            return list(df_temp[val])[0]
        else:
            return 0

    return func, tuple(cols)


def df_to_func(df):
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

    # get df columns
    df_cols = list(df.columns)

    # law of replacement
    def law(departures_, year_):
        new_employees = []
        j = 0
        key = ''
        data_=[]
        for g in departures_:
            # get lines from df with group_out = g
            if 'year_' in df_cols:
                df_g = df[(df['group_out']==g) & (df['year_']==year_)]
                n = len(df_g)
                for i in range(n) :
                    key = 'id_' + str(j) + '_year_' + str(df_g.loc[i,'year_'])
                    data_= list(df_g.loc[i,:])[4:]

                    temp = {'key': key, 'number': departures_[g]*df_g.loc[i,'replacement_rate'],'data':data_}
                    new_employees.append(temp)
                    j = j + 1

            else:
                df_g = df[(df['group_out']==g)]
                n = len(df_g)
                for i in range(n) :
                    key = 'id_' + str(j) + '_year_' + str(year_)
                    data_= list(df_g.loc[i,:])[3:]

                    temp = {'key': key, 'number': departures_[g]*df_g.loc[i,'replacement_rate'],'data':data_}
                    new_employees.append(temp)
                    j = j + 1

        return new_employees

    return law