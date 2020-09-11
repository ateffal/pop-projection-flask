# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 11:42:25 2019

@author: a.teffal
"""

from flask import Flask, request, redirect, url_for, render_template, session, send_from_directory
# from datetime import date
# from werkzeug import secure_filename
import pandas as pd
import random
import sys
# import inspect
# sys.path.insert(0, '../pop_projection')


from pop_projection import Effectifs as eff
from pop_projection import sample_laws as sl

# from flask_mysqldb import MySQL


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


app = Flask(__name__, static_url_path='',  static_folder='static')
app.secret_key = get_secret_key()

@app.route('/home', methods=['GET', 'POST'])
def home():
    #    if 'login' in session:
    #        return render_template('index.html', user_login=session['login'])
    #    else:
    #        return redirect(url_for('page_de_login'))
    session['login'] = 'Guest'
    return app.send_static_file('home.html')

@app.route('/', methods=['GET', 'POST'])
def acceuil():
    #    if 'login' in session:
    #        return render_template('index.html', user_login=session['login'])
    #    else:
    #        return redirect(url_for('page_de_login'))
    session['login'] = 'Guest'
    return app.send_static_file('home.html')


@app.route('/login', methods=['GET', 'POST'])
def page_de_login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        session['login'] = request.form['login']
        return redirect(url_for('acceuil'))


@app.route('/parametres')
def parametres():
    session['login']='Guest'
    return render_template('parametres.html', user_login=session['login'])


@app.route('/afficher_donnees', methods=['GET', 'POST'])
def afficher_donnees():

    if 'employees' in session:
        path = PATH_UPLOADS + "data/"
        fic_name_employees = session['employees']
        data = pd.read_csv(path + fic_name_employees, sep=";", decimal=",")
        cols_ = list(data.columns)
        values_ = data.values.tolist()
    else:
        cols_ = []
        values_ = []

    if 'spouses' in session:
        path = PATH_UPLOADS + "data/"
        fic_name_spouses = session['spouses']
        data2 = pd.read_csv(path + fic_name_spouses, sep=";", decimal=",")
        cols_2 = list(data2.columns)
        values_2 = data2.values.tolist()
    else:
        cols_2 = []
        values_2 = []

    return render_template('afficher_donnees.html', cols=cols_, data=values_, cols2=cols_2, data2=values_2, user_login=session['login'])


@app.route('/donnees', methods=['GET'])
def donnees():
    session['login'] = 'Guest'
    return render_template('donnees.html', user_login=session['login'])


@app.route('/calculer', methods=['GET', 'POST'])
def calculer():
    # Getting parameters
    # Mortality table
    table_morta = request.form['table_mortalite']

    # Years of projection
    MAX_ANNEES = int(request.form['duree_sim'])

    # Law of retirement
    if not request.form['age_depart'] == '':
        age_depart = int(request.form['age_depart'])
        # Construction law of retirement

        def law_ret(age):
            if age >= age_depart:
                return True
            else:
                return False
    else:
        if not request.files['loi_ret'].filename == '':
            loi_ret = save_file(
                request.files['loi_ret'], PATH_UPLOADS + 'parameters/')[0]
            law_ret = df_to_func(loi_ret)[0]
        else:
            return 'Saisissez un âge de retraite ou selectionner une loi de retraite !'

    # Law of marriage
    if not request.files['loi_mar'].filename == '':
        loi_mar = save_file(
            request.files['loi_mar'], PATH_UPLOADS + 'parameters/')[0]
    else:
        loi_mar = None

    # Law of resignation
    if not request.files['loi_dem'].filename == '':
        loi_dem = save_file(
            request.files['loi_dem'], PATH_UPLOADS + 'parameters/')[0]
    else:
        loi_dem = None

    # Loading employees data
    if 'employees' in session:
        path = PATH_UPLOADS + "data/"
        fic_name_employees = session['employees']
        employees = pd.read_csv(
            path + fic_name_employees, sep=";", decimal=",")
    else:
        return "Please upload employee !"

    # Loading spouses data
    if 'spouses' in session:
        path = PATH_UPLOADS + "data/"
        fic_name_spouses = session['spouses']
        spouses = pd.read_csv(path + fic_name_spouses, sep=";", decimal=",")
    else:
        return "Please upload spouses !"

    # Loading children data
    if 'children' in session:
        path = PATH_UPLOADS + "data/"
        fic_name_children = session['children']
        children = pd.read_csv(path + fic_name_children, sep=";", decimal=",")
    else:
        return "Please upload children !"

    print(loi_mar)
    print(loi_dem)

    numbers_ = eff.projectNumbers(employees, spouses, children, table_morta, MAX_ANNEES,
                                  law_replacement_=sl.law_replacement1,
                                  law_marriage_=df_to_func(loi_mar), law_resignation_=df_to_func(loi_dem),
                                  law_retirement_=law_ret)

    data = eff.globalNumbers(numbers_[0], numbers_[1], numbers_[2], MAX_ANNEES)

    # save the results
    data.to_csv(PATH_UPLOADS + 'results/results.csv',
                sep=';', index=False, decimal=',')

    return render_template('afficher_resultats.html', cols=list(data.columns), data=data.values.tolist(), user_login=session['login'])


@app.route('/charger_donnees', methods=['POST'])
def charger_donnees():
    # chargement employees
    fic_employees = request.files['employees']
    data, session['employees'] = save_file(fic_employees)

    # chargement spouses
    fic_spouses = request.files['spouses']
    data2, session['spouses'] = save_file(fic_spouses)

    # chargement children
    fic_children = request.files['children']
    data3, session['children'] = save_file(fic_children)

    return render_template('afficher_donnees.html', cols=list(data.columns), data=data.values.tolist(),
                           cols2=list(data2.columns), data2=data2.values.tolist(),
                           cols3=list(data3.columns), data3=data3.values.tolist(), user_login=session['login'])


@app.route('/exporter', methods=['GET'])
def exporter():
    return send_from_directory(PATH_UPLOADS + 'results/', 'results.csv')


@app.errorhandler(400)
def erreur_400(error):
    return ("<h1>Erreur 400</h1>")


@app.errorhandler(401)
def erreur_401(error):
    return ("<h1>Erreur 401</h1>")


@app.errorhandler(404)
def erreur_404(error):
    return ("<h1>Erreur 404</h1>")


@app.errorhandler(500)
def erreur_500(error):
    return ("<h1>Erreur 500</h1>")


if __name__ == '__main__':
    app.run(debug=True)
