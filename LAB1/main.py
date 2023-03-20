'''

    Andres Emilio Quinto - 18288
    Universidad del Valle de Guatemala
    Diseño de Lenguajes de Programación
    Main.py
    implementacion de regez a postfix y luego a NFA


'''
# imports
import sys
sys.path.append(".")
from RegexToPostFix import RegexToPostfix
from functions import functions
from NFA import AFNT

# functions
def welcome():
    print("________________________________________BIENVENIDO_________________________________________")
    print("Implementación de los algoritmos básicos de autómatas finitos y expresiones regulares.")
    print()

def menu():
    #os.system('cls')
    print("Seleccione una opcion.")
    print("\t1. Metodo de Conversion por Thompson")
    print("\t2. Salir")

def userInteraction():
    expresion = input('Ingrese una expresion regular: ')
    expresion = expresion.replace(' ','')
    chain = ' '
    chain = chain.replace(' ','')

    obj = RegexToPostfix()
    postfix = obj.infix_to_postfix(expresion)

    return postfix, chain
# Executions
welcome()
functions = functions()
while True:

    menu()
    option = input('Ingrese una opcion: ')

    if(option == '1'):
        chain = ''

        postfixRegex,chain = userInteraction()
        if(postfixRegex == 'ERROR_POSTFIX_)'):
            print('\n ")" faltante en la expresion regular ingresada. Vuelva a intentar. \n')
        else:
            print(' - postfix     = '+ postfixRegex)
            tokens = functions.getRegExUniqueTokens(postfixRegex)
            postfixRegex = functions.stringToArray(postfixRegex)

            print(' - alfabeto (tokens): '+str(tokens))

            obj_afn = AFNT(tokens,chain)
            AFN = obj_afn.generateAFN(postfixRegex)

    elif(option == '3'):
        print('\nGracias por utilizar este programa! ')
        break
    else:
        input('No se ha elegido ninguna opcion valida en el menu. Intentalo otra vez! Presiona Enter!')