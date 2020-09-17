from helpers_functions import *
import pandas as pd

path = 'D:/Shared/Shared/a.teffal/OneDrive/OneDrive - Bank Al Maghrib/Application_Python/pop-projection-flask/input_files/'


file = pd.read_csv(path+'law_replacement-2.csv', sep=';', decimal=',')


law_repl_1 = fic_repl_to_law_repl(file)

