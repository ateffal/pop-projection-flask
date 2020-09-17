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
sys.path.insert(0, 'D:/Shared/Shared/a.teffal/OneDrive/OneDrive - Bank Al Maghrib/Application_Python/pop_projection')


from pop_projection import Effectifs as eff
from pop_projection import sample_laws as sl


from helpers_functions import *






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



@app.route('/save_parameters', methods=['POST'])
def save_parameters():
    session['login']='Guest'
    session['duree_sim'] = request.form['duree_sim']
    session['table_mortalite'] = request.form['table_mortalite']
    session['age_depart'] = request.form['age_depart']

    return redirect(url_for('display_parameters'))

@app.route('/display_parameters', methods=['GET', 'POST'])
def display_parameters():
    session['login']='Guest'

    if 'duree_sim' in session:
        duree_sim_ = session['duree_sim']
    else:
        duree_sim_ = 'Not defined'

    if 'table_mortalite' in session:
            table_mortalite_ = session['table_mortalite']
    else:
        table_mortalite_ = 'Not defined'

    if 'age_depart' in session:
            age_depart_ = session['age_depart']
    else:
        age_depart_ = 'Not defined'


    return render_template('afficher_parametres.html', duree_sim=duree_sim_, 
            table_mortalite=table_mortalite_, age_depart=age_depart_ ,user_login=session['login'])





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
    session['login']='Guest'
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

    # Law of replacement
    if not request.files['loi_remp'].filename == '':
        loi_remp = save_file(
            request.files['loi_remp'], PATH_UPLOADS + 'parameters/')[0]
    else:
        loi_remp = None

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

    

    numbers_ = eff.projectNumbers(employees, spouses, children, table_morta, MAX_ANNEES,
                                  law_replacement_=fic_repl_to_law_repl(loi_remp),
                                  law_marriage_=df_to_func(loi_mar), law_resignation_=df_to_func(loi_dem),
                                  law_retirement_=law_ret)

    data = eff.globalNumbers(numbers_[0], numbers_[1], numbers_[2], MAX_ANNEES)

    # save the results
    data.to_csv(PATH_UPLOADS + 'results/results.csv',
                sep=';', index=False, decimal=',')

    return render_template('afficher_resultats.html', cols=list(data.columns), data=data.values.tolist(), user_login=session['login'])


@app.route('/charger_donnees', methods=['POST'])
def charger_donnees():
    session['login'] = 'Guest'
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
