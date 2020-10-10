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
# sys.path.insert(0, 'D:/Shared/Shared/a.teffal/OneDrive/OneDrive - Bank Al Maghrib/Application_Python/pop_projection')


from pop_projection import Effectifs as eff
from pop_projection import sample_laws as sl


from .helpers_functions import *

from .db import get_db


bp = Blueprint('application', __name__, static_folder='static', static_url_path='/static')



# app = Flask(__name__, static_url_path='',  static_folder='static')
# app.secret_key = get_secret_key()

@bp.route('/', methods=['GET', 'POST'])
def home():
    return bp.send_static_file('home.html')


@bp.route('/login', methods=['GET', 'POST'])
# def page_de_login():
#     if request.method == 'GET':
#         return render_template('login.html')

#     if request.method == 'POST':
#         session['login'] = request.form['login']
#         return redirect(url_for('acceuil'))


@bp.route('/parametres')
def parametres():
    # session['login']='Guest'
    return render_template('parametres.html')



@bp.route('/save_parameters', methods=['POST'])
def save_parameters():


    # one value parameters
    session['duree_sim'] = request.form['duree_sim']
    session['table_mortalite'] = request.form['table_mortalite']
    session['age_depart'] = request.form['age_depart']


    # laws parameters
    data, session['loi_ret'] = save_file(request.files['loi_ret'], session['sim_folder'] + "/parameters/")
    data, session['loi_dem'] = save_file(request.files['loi_dem'], session['sim_folder'] + "/parameters/")
    data, session['loi_mar'] = save_file(request.files['loi_mar'], session['sim_folder'] + "/parameters/")
    data, session['loi_remp'] = save_file(request.files['loi_remp'], session['sim_folder'] + "/parameters/")

    return redirect(url_for('application.display_parameters'))

@bp.route('/display_parameters', methods=['GET', 'POST'])
def display_parameters():
    duree_sim_ = session['duree_sim'] if 'duree_sim' in session else 'Not defined'
    table_mortalite_ = session['table_mortalite'] if 'table_mortalite' in session else 'Not defined'
    age_depart_ = session['age_depart'] if 'age_depart' in session else 'Not defined'
    loi_ret_ = session['loi_ret'] if 'loi_ret' in session else 'Not defined'
    loi_dem_ = session['loi_dem'] if 'loi_dem' in session else 'Not defined'
    loi_mar_ = session['loi_mar'] if 'loi_mar' in session else 'Not defined'
    loi_remp_ = session['loi_remp'] if 'loi_remp' in session else 'Not defined'


    return render_template('afficher_parametres.html', duree_sim=duree_sim_,
            table_mortalite=table_mortalite_, age_depart=age_depart_ ,loi_ret = loi_ret_, loi_dem = loi_dem_,
            loi_mar = loi_mar_, loi_remp = loi_remp_)





@bp.route('/afficher_donnees', methods=['GET', 'POST'])
def afficher_donnees():

    if 'employees' in session:
        path = session['sim_folder'] + "/data/"
        fic_name_employees = session['employees']
        data = pd.read_csv(path + fic_name_employees, sep=";", decimal=",")
        cols_ = list(data.columns)
        values_ = data.values.tolist()
    else:
        cols_ = []
        values_ = []

    if 'spouses' in session:
        path = session['sim_folder'] + "/data/"
        fic_name_spouses = session['spouses']
        data2 = pd.read_csv(path + fic_name_spouses, sep=";", decimal=",")
        cols_2 = list(data2.columns)
        values_2 = data2.values.tolist()
    else:
        cols_2 = []
        values_2 = []


    if 'children' in session:
        path = session['sim_folder'] + "/data/"
        fic_name_children = session['children']
        data3 = pd.read_csv(path + fic_name_children, sep=";", decimal=",")
        cols_3 = list(data3.columns)
        values_3 = data3.values.tolist()
    else:
        cols_3 = []
        values_3 = []

    return render_template('afficher_donnees.html', cols=cols_, data=values_, cols2=cols_2, data2=values_2,
                          cols3=cols_3, data3=values_3)


@bp.route('/donnees/<int:sim_id>', methods=['GET'])
def donnees(sim_id):
    session['sim_id'] = sim_id
    db = get_db()
    user_id = session['user_id']
    sim = db.execute('SELECT * FROM simulations WHERE user_id = ? and id = ?', (user_id, sim_id)).fetchone()
    session['active_sim'] = sim[1]
    session['sim_folder'] = sim[3]
    return render_template('donnees.html')


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
            loi_ret = pd.read_csv(session['sim_folder'] + 'parameters/' + fic_name, sep=";", decimal=",")
            law_ret = df_to_func(loi_ret)[0]
        else:
            return 'Saisissez un âge de retraite ou selectionner une loi de retraite !'


    # Law of resignation
    if 'loi_dem' in session :
        fic_name = session['loi_dem']
        if not fic_name == '':
            loi_dem = pd.read_csv(session['sim_folder'] + 'parameters/' + fic_name, sep=";", decimal=",")
        else:
            loi_dem = None
    else:
        loi_dem = None



    # Law of marriage
    if 'loi_mar' in session :
        fic_name = session['loi_mar']
        if not fic_name=='':
            loi_mar = pd.read_csv(session['sim_folder'] + 'parameters/' + fic_name, sep=";", decimal=",")
        else:
            loi_mar = None
    else:
        loi_mar = None


    # Law of replacement
    if 'loi_remp' in session :
        fic_name = session['loi_remp']
        if not fic_name=='':
            loi_remp = pd.read_csv(session['sim_folder'] + 'parameters/' + fic_name, sep=";", decimal=",")
        else:
            loi_remp = None
    else:
        loi_remp = None

    # Loading employees data
    if 'employees' in session:
        path = session['sim_folder'] + "/data/"
        fic_name_employees = session['employees']
        employees = pd.read_csv(
            path + fic_name_employees, sep=";", decimal=",")
    else:
        return "Please upload employee !"

    # Loading spouses data
    if 'spouses' in session:
        path = session['sim_folder'] + "/data/"
        fic_name_spouses = session['spouses']
        spouses = pd.read_csv(path + fic_name_spouses, sep=";", decimal=",")
    else:
        return "Please upload spouses !"

    # Loading children data
    if 'children' in session:
        path = session['sim_folder'] + "/data/"
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
    data.to_csv(session['sim_folder'] + 'results/results.csv',
                sep=';', index=False, decimal=',')

    return render_template('afficher_resultats.html', cols=list(data.columns), data=data.values.tolist())


@bp.route('/charger_donnees', methods=['POST'])
def charger_donnees():
    # chargement employees
    fic_employees = request.files['employees']
    data, session['employees'] = save_file(fic_employees,session['sim_folder']+'/data/')

    # chargement spouses
    fic_spouses = request.files['spouses']
    data2, session['spouses'] = save_file(fic_spouses, session['sim_folder'] + '/data/')

    # chargement children
    fic_children = request.files['children']
    data3, session['children'] = save_file(fic_children, session['sim_folder'] + '/data/')

    return render_template('afficher_donnees.html', cols=list(data.columns), data=data.values.tolist(),
                           cols2=list(data2.columns), data2=data2.values.tolist(),
                           cols3=list(data3.columns), data3=data3.values.tolist())


@bp.route('/exporter', methods=['GET'])
def exporter():
    return send_from_directory(session['sim_folder'] + 'results/', 'results.csv')


@bp.route('/create_sim', methods=['GET', 'POST'])
def create_sim():
    if request.method == 'GET':
        return render_template('create_simulation.html')
    if request.method == 'POST':
        sim_name = request.form['sim_name']
        sim_description = request.form['sim_description']
        user_id = session['user_id']
        # create simulation's folder in simulations folder
        db_path = PATH_UPLOADS + 'simulations' + '/SIM_' + sim_name
        if not os.path.exists(db_path):
            os.makedirs(db_path)
            db = get_db()
            db.execute('INSERT INTO simulations (sim_name, sim_description, db_path, user_id) VALUES (?, ?, ?, ?)', (sim_name, sim_description, db_path, user_id))
            db.commit()

            db_path = db_path + '/data'
            if not os.path.exists(db_path):
                os.makedirs(db_path)



            return redirect(url_for('application.simulations'))
        else:
            return 'Error in creating simulation : ' + sim_name



@bp.route('/simulations', methods=['GET'])
def simulations():
    if request.method == 'GET':
        db = get_db()
        user_id = session['user_id']
        sims = db.execute('SELECT * FROM simulations WHERE user_id = ?', (user_id,)).fetchall()
        sims = list(sims)
        return render_template('simulations.html', simulations=sims)


@bp.route('/delete_sim/<int:sim_id>', methods=['GET'])
def delete_sim(sim_id):
    if request.method == 'GET':
        db = get_db()
        user_id = session['user_id']
        db.execute('DELETE FROM simulations WHERE user_id = ? and id = ?', (user_id, sim_id, ))
        db.commit()
        return redirect(url_for('application.simulations'))




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
