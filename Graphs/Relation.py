'''

    Andres Quinto - 18288
    Este archivo contiene la definición de la clase "Relation", que representa una relación entre dos nodos en un grafo. 
'''

class Relation:
    '''
    Clase que representa una relacion entre 2 nodos

    Atributos:
     - origin = the origin node 
     - token = the token 
     - destiny = the destiny node 
    ''' 
    def __init__(self,origin,token,destiny):
        self.origin = origin
        self.token = token
        self.destiny = destiny

    #gets
    def getOrigin(self):
        return self.origin

    def getToken(self):
        return self.token

    def getDestiny(self):
        return self.destiny

    #others
    def updateRelation(self,dictionary):
        '''
        Funcion que actualiza el estado viejo de la relacion en base a los 
        valores diccionario de entrada.
        '''
        self.origin = dictionary[self.origin]
        self.destiny = dictionary[self.destiny]
        return 0