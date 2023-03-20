'''

    Andres Quinto - 18288
    REGEX TO POSTFIX
    Clase que realiza modificaciones a una expresion infix y luego la convierte a formato postfix
    lABORATORIO 1
    Aqui almaceno mis utils para el proyecto y construccion de los automatas

    
'''

class functions:

    def getRegExUniqueTokens(self,postfix_regex,words=False):
        '''
        El primer método, "getRegExUniqueTokens", toma una expresión regular en formato postfix y devuelve una lista de tokens únicos o el lenguaje de la expresión regular. 
        '''
        ops = '*|.#'
        tokens = []
        for i in range(len(postfix_regex)):
            token = postfix_regex[i]
            op_exist = token in ops
            if(op_exist == False):
                tokens.append(token)

        return list(dict.fromkeys(tokens))

    def stringToArray(self,string):
        '''
        
        El segundo método, "stringToArray", toma una cadena de texto y la convierte en una lista eliminando los espacios en blanco.

        '''
        result = string.replace('',' ').split(' ')
        result.pop(0)
        result.pop()
        return result

    def isOperand(self,character):
        """
        Retorna TRUE si el caracter ingresado es un alfanumerico, FALSE de lo contrario
        *@param ch: el caracter a ser probado
        """
        if character.isalnum() or character == "ε" or character == "#":
            return True
        return False