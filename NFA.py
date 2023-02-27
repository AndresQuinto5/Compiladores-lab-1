'''

    Andres Quinto - 18288
    REGEX TO POSTFIX
    Clase que realiza modificaciones a una expresion infix y luego la convierte a formato postfix
    lABORATORIO 1
    La clase AFNT representa un Automata Finito No Determinista (AFN) y tiene como objetivo convertir una expresión regular en un AFN mediante el uso del algoritmo de Thompson.

'''
# imports
import time
import collections
import sys
sys.path.append(".")
from functions import *
from Graphs.NodeT import *
from Graphs.Relation import Relation
from graphviz import Digraph

class AFNT:
    '''
    Clase que comvierte una expresion regular en un automata finito no determinista.
    tokens: una lista de símbolos que representan el alfabeto del lenguaje.
    chain: una cadena que representa la expresión regular a convertir en un AFN.
    AFNArray: una lista vacía que se utilizará para almacenar los AFN construidos durante el proceso de conversión.
    AFNResult: un diccionario que se utilizará para almacenar el resultado final del proceso de conversión.
    '''
    def __init__(self, tokens, chain):
        self.AFNArray = []
        self.AFNResult = {}
        self.chain = chain
        self.alphabet = tokens

    def postFixParser(self, expresion):
        '''
        Este método es el encargado de convertir una expresión regular en formato infix a postfix y construir el AFN 
        correspondiente utilizando el algoritmo de Thompson. Para ello, se recorre la cadena expresion y se interpretan cada uno de los tokens y operandos.
        '''
        for i in expresion:
            # si el iterador es un token
            if(i in "".join(self.alphabet)):
                self.token_afn(i)
            # si el iterador apunta a un operador
            elif(i in ".|*"):
                if(i == "."):
                    self.concat_afn()
                elif(i == "|"):
                    self.or_afn()
                elif(i == "*"):
                    self.kleene_afn()

        endAFN = self.AFNArray.pop()
        self.simAFN(endAFN)
        self.drawGraph(endAFN)

        return endAFN


    def drawGraph(self, AFN, filename='this is a NFA - thompson'):
        '''
            Este método se encarga de dibujar una representación gráfica del AFN utilizando la biblioteca Graphviz. Para ello, recibe como parámetros:

            AFN: el grafo que representa el AFN construido por el algoritmo de Thompson.
            filename: el nombre que se le dará al archivo de imagen que se generará.
        '''
        print('Dibujando representacion del AFN... \n')
        resultAFN = AFN
        file_name = 'dibujitosAFN/'+filename
        dot = Digraph(comment=filename, format='png')
        dot.attr(rankdir='LR', size='8,8')
        dot.attr('node', style='filled',color='lightblue')

        acceptingState = getAcceptingStates(resultAFN)
        dot.attr('node', shape='doublecircle')
        dot.node(str(acceptingState[0]))

        dot.attr('node', shape='circle')
        initState = getInitialStates(resultAFN)

        afnRelations = getAFNRelations(resultAFN)

        for rels in afnRelations:
            if(len(rels) > 0):
                if(len(rels) > 1):
                    for rel in rels:
                        dot.edge(str(rel.getOrigin()), str(rel.getDestiny()), label=str(rel.getToken()))
                else:
                    rel = rels.pop()
                    dot.edge(str(rel.getOrigin()), str(rel.getDestiny()), label=str(rel.getToken()))

        dot.attr(label=r'\n'+filename, fontsize='20')
        dot.render(filename=file_name, view=True)
      
    def token_afn(self,token):
        '''
        Funcion para generar el par de nodos correspondientes.
        Ej. (Ni) --token--> (Nf)

        Parametros:
        - token - token cualquiera del alfabeto en cuestion que servira como transicion entre ambos nodos
        - return - un grafo pequeño compuesto por dos nodos
        '''
        #se crea un grafo local
        localGraph = {}
        counter = 0
        #Nodo inicial y final
        node1 = NodeT(isInitial=True)
        node2 = NodeT(isAccepting=True)
        # Relacion: origen ---a---> Destino
        relation = Relation(counter,token,counter+1)
        node1.addRelation(relation)
        #Se agregan los nodos al grafo local
        localGraph[counter] = node1
        localGraph[counter+1] = node2
        #colocamos este grafo local en el AFN global
        self.AFNArray.append(localGraph)

    def concat_afn(self):
        '''
        Funcion para concatenar 2 grafos cualesquiera. 
            Ej. (Gi) --a--> (Nu) --b--> (Gf)
        - El nodo final de Gi se convierte en el nodo inicial de Gf.

        Esta funcion no recibe parametros ya que concatenara dos grafos o 
        AFNs que se encuentren en el array global de afns (AFNArray).
        '''
        # se crea un grafo local
        localGraph = {}
        #Este contador actualiza los estados de los nodos
        counter = -1
        #obtenemos los grafos a concatenar
        graph2 = self.AFNArray.pop()
        graph1 = self.AFNArray.pop()
        #Se actualizan los estados de cada nodo del grafo1
        afnCounter1, newAFN1 = updateNodesId(counter,graph1)
        #se obtiene el id del nodo de aceptacion del nuevo grafo o afn
        id_fnode_graph1, newAFN1 = getAcceptingNodeId(newAFN1)
        #se obtiene el id final del nodo del grafo 1 y se actualiza      
        #actualizamos los estados del afn2
        afnCounter2, newAFN2 = updateNodesId(afnCounter1-1,graph2)
        id_inode_graph2, newAFN2 = getInitialNodeId(newAFN2)

        counter = afnCounter2

        localGraph.update(newAFN1)
        localGraph.update(newAFN2)
        #colocamos el resultado de la concatenacion en el array de afns
        self.AFNArray.append(localGraph)

        return 0


    def or_afn(self):
        '''
        Funcion para operar | entre dos grafos cualesquiera. 

        Esta funcion no recibe parametros ya que operara Or entre dos grafos o 
        AFNs que se encuentren en el array global de afns (AFNArray).
        '''
        #El grafo que contendra el resultado
        orGraph = {}
        #Este contador actualiza los estados de los nodos
        counter = 0
        
        # Se crea el nodo inicial del grafo OR
        i_node = NodeT(isInitial=True)
        #obtenemos los grafos a concatenar
        graph2 = self.AFNArray.pop()
        graph1 = self.AFNArray.pop()

        #colocameos el nodo incial al principio del grafo de resultado or
        orGraph[counter] = i_node

        #Construccion y actualizacion de estados

        #Actualizamos estados del grafo 1
        afnCounter1, newAFN1 = updateNodesId(counter,graph1)
        #obtenemos nodos inicial y final del grafo 1
        id_inode_graph1, newAFN1 = getInitialNodeId(newAFN1)
        id_fnode_graph1, newAFN1 = getAcceptingNodeId(newAFN1)

        #Actualizamos estados del grafo 2
        afnCounter2, newAFN2 = updateNodesId(afnCounter1,graph2)
        #obtenemos nodos inicial y final del grafo 2
        id_inode_graph2, newAFN2 = getInitialNodeId(newAFN2)
        id_fnode_graph2, newAFN2 = getAcceptingNodeId(newAFN2)

        #Ingresamos los grafos actualizados al grafo que contendra el resultado de la operacion OR
        orGraph.update(newAFN1)
        orGraph.update(newAFN2)

        #se crea el nodo final del grafo OR
        f_node = NodeT(isAccepting=True)

        # relacion del nodo inicial de OR hacia el nodo inicial del grafo 1 a travez de epsilon
        i_node_rel_to_AFN1 = Relation(counter,'ε',id_inode_graph1)
        # relacion del nodo inicial de OR hacia el nodo inicial del grafo 2 a travez de epsilon
        i_node_rel_to_AFN2 = Relation(counter,'ε',id_inode_graph2)

        #se agregan las relaciones al nodo inicial del grafo OR
        orGraph[counter].addRelation(i_node_rel_to_AFN1)
        orGraph[counter].addRelation(i_node_rel_to_AFN2)
        counter = afnCounter2+1

        # relacion del nodo inicial de OR hacia el nodo inicial del grafo 1
        AFN1_to_f_node_OR = Relation(id_fnode_graph1,'ε',counter)
        # relacion del nodo inicial de OR hacia el nodo inicial del grafo 2
        AFN2_to_f_node_OR = Relation(id_fnode_graph2,'ε',counter)

        #relacionamos el ultimo nodo del grafo 1 al ultimo nodo del grafo OR con epsilon
        orGraph[afnCounter1].addRelation(AFN1_to_f_node_OR)
        #relacionamos el ultimo nodo del grafo 2 al ultimo nodo del grafo OR con epsilon
        orGraph[afnCounter2].addRelation(AFN2_to_f_node_OR)

        #agregamos el nodo final
        orGraph[counter] = f_node

        #colocamos el grafo OR de resultado en el array de afns global
        self.AFNArray.append(orGraph)

        return 0


    def kleene_afn(self):
        '''
        Funcion para operar * entre dos grafos cualesquiera. 

        Esta funcion no recibe parametros ya que operara kleene entre dos grafos o 
        AFNs que se encuentren en el array global de afns (AFNArray).
        '''
        #se crea el grafo que contendra la operacion kleene sobre el grafo en cuestion
        kleeneGraph = {}
        # contador para actualizacion de estados de los nodos
        counter = 0

        #creamos el nodo inicial del grafo kleene
        i_node = NodeT(isInitial=True)
        #grafo tomado del stack de afns global
        graph1 = self.AFNArray.pop()
        #agregamos nodo inicial
        kleeneGraph[counter] = i_node
        initCounterKleene = counter

        # se actualizan los id de cada nodo
        afnCounter1, newAFN1 = updateNodesId(counter,graph1)

        # obtenemos el estado de los nodos inicial y final del grafo 1
        id_inode_graph1, newAFN1 = getInitialNodeId(newAFN1)
        id_fnode_graph1, newAFN1 = getAcceptingNodeId(newAFN1)
        #agregamos este grafo al grafo kleene
        kleeneGraph.update(newAFN1)

        #creamos el nodo final del grafo kleene
        f_node = NodeT(isAccepting=True)
        counter = afnCounter1+1

        kleeneGraph[counter] = f_node

        #se procede a crear las 4 relaciones a travez de epsilon en un grafo kleene
        #relacion entre el nodo inicial y el nodo final de kleene a travez de epsilon
        rel_i_to_f = Relation(initCounterKleene,'ε',counter)
        kleeneGraph[initCounterKleene].addRelation(rel_i_to_f)
        #relacion entre el nodo inicial de kleene y el grafo 1
        rel_i_to_igraph1 = Relation(initCounterKleene,'ε',id_inode_graph1)
        kleeneGraph[initCounterKleene].addRelation(rel_i_to_igraph1)
        #relacion entre el nodo final del grafo 1 y el nodo final de kleene
        rel_fgraph1_to_f = Relation(id_fnode_graph1,'ε',counter)
        kleeneGraph[id_fnode_graph1].addRelation(rel_fgraph1_to_f)
        #relacion entre el nodo final del grafo 1 y el nodo final de kleene
        rel_fgraph1_to_igraph1 = Relation(id_fnode_graph1,'ε',id_inode_graph1)
        kleeneGraph[afnCounter1].addRelation(rel_fgraph1_to_igraph1)

        #actualizamos el array de afns con el grafo kleene recien construido
        self.AFNArray.append(kleeneGraph)

        return 0


    def simAFN(self,AFN):
        '''
        Funcion que simula un AFN recorriendo la cadena a evaluar ingresada.
        '''
        print('\nSimulando AFN con cadena de prueba... ')
        
        start_time = time.perf_counter()
        s0 = getInitialStates(AFN)
        F = getAcceptingStates(AFN)

        S = self.e_clossure(AFN,[0])
        for token in self.chain:
            move = self.move(AFN,S,token)
            S = self.e_clossure(AFN,move)


                

    def move(self, AFN, statesSet, transition):
        '''
        Funcion mover() que retorna los estados (del conjunto de estados proporcionado), que pasan
        por la transicion especificada. Ej. move(A,a) --> (a|b)*abb

        Params:
        - AFN: diccionario que representacion del AFN en question
        - statesSet: Un conjunto de estados de un AFN Ej. A = [0,1,2,4,7]
        - transition: transicion por la que pueden pasar algunos de los estados en A.
        - return - [3,8] 
        '''
        resultSet = []
        for state in statesSet:
            for node in AFN.values():
                rels = node.getRelations()
                if(len(rels) > 0):
                    for rel in rels:
                        # Si el estado es igual al origen del nodo(relacion) en cuestion y el token es igual que la 
                        # transicion se agregara el destino a resultSet 
                        if(state == rel.getOrigin() and rel.getToken() == transition):
                            # Eliminacion de duplicados
                            resultSet = list(dict.fromkeys(resultSet))
                            # Los estados se ordenan de forma ascendente
                            resultSet.sort()
                            # Este sera el estado al que podemos llegar a travez de la 
                            # transicion especificada.
                            resultSet.append(rel.getDestiny())

        # Eliminacion de duplicados
        resultSet = list(dict.fromkeys(resultSet))
        resultSet.sort()
        return resultSet

    def e_clossure(self,AFN,move):
        '''
        Funcion de cerradura epsilon que retorna todos los estados a los que se 
        puede llegar en el AFN a travez de epsilon o un token cualquiera. 
        Ej. ε_closure(AFN,[3,8]) --> (a|b)*abb

        Params:
        - AFN: diccionario con el AFN en question
        - move: Resultado proporcionado por la funcion mover()
        - return - Dtran(A,a) = ε_closure(move(A,a)) = [1,2,3,4,6,7,8]
        '''
        resultStateSet = []
        resultStateSet += move
        for state in move:
            for node in AFN.values():
                rels = node.getRelations()
                if(len(rels) > 1):
                    for rel in rels:
                        if(state == rel.getOrigin() and rel.getToken() == 'ε'):
                            # Eliminacion de duplicados
                            resultStateSet = list(dict.fromkeys(resultStateSet))
                            # Ordenamiento en orden ascendente
                            resultStateSet.sort()
                            resultStateSet += self.e_clossure(AFN,[rel.getDestiny()])
                elif(len(rels) != 0):
                    if(state == rels[0].getOrigin() and rels[0].getToken() == 'ε'):
                        resultStateSet = list(dict.fromkeys(resultStateSet))
                        resultStateSet.sort()
                        resultStateSet += self.e_clossure(AFN,[rels[0].getDestiny()])

        # Eliminacion de duplicados
        resultStateSet = list(dict.fromkeys(resultStateSet))
        # Ordenamiento en orden ascendentes
        resultStateSet.sort()
        return resultStateSet


    def generateAFN(self,postFixRegex):
        resultAFN = self.postFixParser(postFixRegex)

        return resultAFN
