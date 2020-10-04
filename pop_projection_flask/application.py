# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 11:42:25 2019

@author: a.teffal
"""

from flask import Flask, request, redirect, url_for, render_template, session, send_from_directory, Blueprint, flash,g,request
from werkzeug.exceptions import abort
import pandas as pd
import random
import sys
from .auth import login_required
from.db import get_db

# import inspect
sys.path.insert(0, 'D:/Shared/Shared/a.teffal/OneDrive/OneDrive - Bank Al Maghrib/Application_Python/pop_projection')


from pop_projection import Effectifs as eff
from pop_projection import sample_laws as sl


from .helpers_functions import *


bp = Blueprint('application', __name__, static_folder='static', static_url_path='/static')



# app = Flask(__name__, static_url_path='',  static_folder='static')
# app.secret_key = get_secret_key()

@bp.route('/', methods=['GET', 'POST'])
def home():
    #    if 'login' in session:
    #        return render_template('index.html', user_login=session['login'])
    #    else:
    #        return redirect(url_for('page_de_login'))
    session['login'] = 'Guest'
    return bp.send_static_file('home.html')


@bp.route('/login', methods=['GET', 'POST'])
def page_de_login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        session['login'] = request.form['login']
        return redirect(url_for('acceuil'))


@bp.route('/parametres')
def parametres():
    session['login']='Guest'
    return render_template('parametres.html', user_login=session['login'])



@bp.route('/save_parameters', methods=['POST'])
def save_parameters():
    

    # one value parameters 
    session['login']='Guest'
    session['duree_sim'] = request.form['duree_sim']
    session['table_mortalite'] = request.form['table_mortalite']
    session['age_depart'] = request.form['age_depart']
        

    # laws parameters
    data, session['loi_ret'] = save_file(request.files['loi_ret'], PATH_UPLOADS + "parameters/")
    data, session['loi_dem'] = save_file(request.files['loi_dem'], PATH_UPLOADS + "parameters/")
    data, session['loi_mar'] = save_file(request.files['loi_mar'], PATH_UPLOADS + "parameters/")
    data, session['loi_remp'] = save_file(request.files['loi_remp'], PATH_UPLOADS + "parameters/")

    return redirect(url_for('application.display_parameters'))

@bp.route('/display_parameters', methods=['GET', 'POST'])
def display_parameters():
    session['login']='Guest'

    duree_sim_ = session['duree_sim'] if 'duree_sim' in session else 'Not defined'
    table_mortalite_ = session['table_mortalite'] if 'table_mortalite' in session else 'Not defined'
    age_depart_ = session['age_depart'] if 'age_depart' in session else 'Not defined'
    loi_ret_ = session['loi_ret'] if 'loi_ret' in session else 'Not defined'
    loi_dem_ = session['loi_dem'] if 'loi_dem' in session else 'Not defined'
    loi_mar_ = session['loi_mar'] if 'loi_mar' in session else 'Not defined'
    loi_remp_ = session['loi_remp'] if 'loi_remp' in session else 'Not defined'


    return render_template('afficher_parametres.html', duree_sim=duree_sim_, 
            table_mortalite=table_mortalite_, age_depart=age_depart_ ,loi_ret = loi_ret_, loi_dem = loi_dem_, 
            loi_mar = loi_mar_, loi_remp = loi_remp_,   user_login=session['login'])





@bp.route('/afficher_donnees', methods=['GET', 'POST'])
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


    if 'children' in session:
        path = PATH_UPLOADS + "data/"
        fic_name_children = session['children']
        data3 = pd.read_csv(path + fic_name_children, sep=";", decimal=",")
        cols_3 = list(data3.columns)
        values_3 = data3.values.tolist()
    else:
        cols_3 = []
        values_3 = []

    return render_template('afficher_donnees.html', cols=cols_, data=values_, cols2=cols_2, data2=values_2, 
                          cols3=cols_3, data3=values_3,user_login=session['login'])


@bp.route('/donnees', methods=['GET'])
def donnees():
    session['login']='Guest'
    return render_template('donnees.html', user_login=session['login'])


@bp.route('/calculer', methods=['GET', 'POST'])
def calculer():
    # Getting parameters
    # Mortality table
    if 'table_mortalite' in session:
        table_morta =session['table_mortalite']
    else:
        return 'Select a mortality table'


    # Years of projection
    if 'duree_sim' in session:
        MAX_ANNEES = int(session['duree_sim'])
    else:
        return 'Type the number of years of projection !'

    # Law of retirement
    if 'age_depart' in session:
        age_depart = int(session['age_depart'])

        # Construction law of retirement
        def law_ret(age):
            if age >= age_depart:
                return True
            else:
                return False
    else:
        if 'loi_ret' in session:
            fic_name = session['loi_ret']
            loi_ret = pd.read_csv(PATH_UPLOADS + 'parameters/' + fic_name, sep=";", decimal=",")
            law_ret = df_to_func(loi_ret)[0]
        else:
            return 'Saisissez un âge de retraite ou selectionner une loi de retraite !'

    
    # Law of resignation
    if 'loi_dem' in session :
        fic_name = session['loi_dem']
        if not fic_name == '':
            loi_dem = pd.read_csv(PATH_UPLOADS + 'parameters/' + fic_name, sep=";", decimal=",")
        else:
            loi_dem = None
    else:
        loi_dem = None


    
    # Law of marriage
    if 'loi_mar' in session :
        fic_name = session['loi_mar']
        if not fic_name=='':
            loi_mar = pd.read_csv(PATH_UPLOADS + 'parameters/' + fic_name, sep=";", decimal=",")
        else:
            loi_mar = None
    else:
        loi_mar = None


    # Law of replacement
    if 'loi_remp' in session :
        fic_name = session['loi_remp']
        if not fic_name=='':
            loi_remp = pd.read_csv(PATH_UPLOADS + 'parameters/' + fic_name, sep=";", decimal=",")
        else:
            loi_remp = None
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

    
    # projection of the population
    numbers_ = eff.projectNumbers(employees, spouses, children, table_morta, MAX_ANNEES,
                                  law_replacement_=fic_repl_to_law_repl(loi_remp),
                                  law_marriage_=df_to_func(loi_mar), law_resignation_=df_to_func(loi_dem),
                                  law_retirement_=law_ret)

    # get global numbers
    data = eff.globalNumbers(numbers_[0], numbers_[1], numbers_[2], MAX_ANNEES)

    # rename the columns
    data = data.rename(columns={'effectif_actifs':'active employees', 'effectif_retraites' : 'retired employees', 
                       'effectif_ayants_cause':'current widows',	'effectif_nouveaux_ayants_cause':'new widows', 
                       'effectif_conjoints_actifs':'spouses of active employees', 'effectif_conjoints_retraites':'spouses of retired employees',
                       'effectif_enfants_actifs':'children of active employees', 'effectif_enfants_retraites':'children of retired employees', 
                       'effectif_enfants_ayant_cause' : 'orphans'})


    # save the results
    data.to_csv(PATH_UPLOADS + 'results/results.csv',
                sep=';', index=False, decimal=',')

    return render_template('afficher_resultats.html', cols=list(data.columns), data=data.values.tolist(), user_login=session['login'])


@bp.route('/charger_donnees', methods=['POST'])
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


@bp.route('/exporter', methods=['GET'])
def exporter():
    return send_from_directory(PATH_UPLOADS + 'results/', 'results.csv')


@bp.errorhandler(400)
def erreur_400(error):
    return ("<h1>--------------------  Erreur 400 ---------------------------</h1>")


@bp.errorhandler(401)
def erreur_401(error):
    return ("<h1>Erreur 401</h1>")


@bp.errorhandler(404)
def erreur_404(error):

    return ("<h1>--------------------  Erreur 404 ---------------------------</h1>")




@bp.errorhandler(500)
def erreur_500(error):
    return ("<h1>--------------------  Erreur 500 ---------------------------</h1>")


if __name__ == '__main__':
    bp.run(debug=True)
