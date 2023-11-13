import re

class ReturnObject:
    # Clase para manejar el retorno de las funciones de traducción
    def __init__(self, ignore: bool, to_return: str, ending_c_bracket: bool = False) -> None:
        # ignore: indica si se debe ignorar el procesamiento adicional
        # to_return: la cadena de texto a retornar
        # ending_c_bracket: indica si se debe agregar un corchete de cierre en C++
        self.ignore = ignore
        self.to_return = to_return
        self.add_ending_c_bracket = ending_c_bracket

# Diccionario para mapear operandos de Python a C++
python_to_cpp_operands = {
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "%": "%",
    "**": "pow",
    "==": "==",
    "!=": "!=",
    "<": "<",
    ">": ">",
    "<=": "<=",
    ">=": ">=",
    "and": "&&",
    "or": "||",
    "not": "!",
}

# Conjunto para llevar un registro de las variables declaradas
registered_variables = set()

def translate_operands(line):
    # Traduce comentarios y operandos
    if line.startswith("#"):
        # Traduce comentarios
        line = line.replace(f"#", f"//")
        # Agrega espacio de siguiente línea
        line += "\n"
        return ReturnObject(ignore=True, to_return=line)
    
    # Itera sobre los operandos de Python y los traduce a C++
    for py_operand, cpp_operand in python_to_cpp_operands.items():
        line = line.replace(f" {py_operand} ", f" {cpp_operand} ")
    return ReturnObject(ignore=False, to_return=line)

def translate_variables(line):
    # Traduce declaraciones de variables
    if "=" in line:
        # Elimina el salto de línea
        line = line.replace("\n", "")
        # Divide la línea en el signo de igual
        line_parts = line.split("=")
        # Si la línea tiene más de dos partes, es una declaración de variable
        if len(line_parts) == 2:
            var_name, var_value = line_parts

            # Determina el tipo de la variable y traduce la declaración
            if var_value.strip().isdigit():
                line = f"int {var_name} = {var_value};\n"
            elif var_value.strip().replace('.', '', 1).isdigit():
                line = f"double {var_name} = {var_value};\n"
            elif var_value.strip().startswith('"') and var_value.strip().endswith('"'):
                line = f'std::string {var_name} = {var_value};\n'
            else:
                # Si la variable ya está registrada, es una asignación
                if var_name in registered_variables:
                    line = f'{line}\n'
                else:
                    # Si no, es una declaración de variable
                    line = f"auto {var_name} = {var_value};\n"
            # Registra la variable
            registered_variables.add(var_name)
            
    return ReturnObject(ignore=False, to_return=line)

def built_in_functions(line):
    # Traduce funciones integradas de Python, como print
    line = re.sub(r'^\s*print\(', 'cout << ', line)
    line = re.sub(r'\)$', ' << endl;\n', line)
    return ReturnObject(ignore=False, to_return=line)

def translate_line(line):
    # Procesa la línea para realizar la traducción
    obj = translate_operands(line)
    if not obj.ignore:
        # Traduce variables
        obj = translate_variables(obj.to_return)
    if not obj.ignore:
        # Traduce funciones integradas
        obj = built_in_functions(obj.to_return)
    
    # Asigna la línea traducida
    line = obj.to_return
    if not obj.ignore:
        stripped_line = line.strip()
        # Añade punto y coma si es necesario
        if (
            stripped_line and
            not stripped_line.endswith('{') and 
            not stripped_line.endswith('}') and 
            not stripped_line.endswith(';') and 
            not stripped_line.startswith('#') and
            not stripped_line.endswith(';')
            ):
            line = line.rstrip() + ';\n'

    # Agrega corchetes de cierre si es necesario
    if obj.add_ending_c_bracket:
        line = line + '\n}\n'
    return line

def translate_python_to_cpp(input_file, output_file):
    # Lee el archivo Python y escribe el archivo C++ traducido
    with open(input_file, "r") as file:
        lines = file.readlines()

    with open(output_file, "w") as file:
        # Escribe el encabezado del archivo C++
        file_head = "#include <iostream>\n#include <string>\nusing namespace std;\n\nint main() {\n\n"
        file.write(file_head)

        for line in lines:
            line = line.strip()
            # Ignora ciertas líneas como definiciones de funciones y estructuras de control
            if (not line.startswith("#") and 
                not line.startswith("def") and
                not line.startswith("if") and
                not line.startswith("else") and
                not line.startswith("while") and
                not line.startswith("for")
                ):
                # Sustituimos los espacios en blanco
                line = re.sub(r'\s+', '', line)
            if not line or line == "\n":
                continue
            
            # Traduce la línea
            translated_line = translate_line(line)

            # Escribe la línea traducida en el archivo
            file.write("\t" + translated_line)
        
        # Escribe el pie del archivo C++
        file.write("\treturn 0;\n}")
        

# Corre si el archivo es ejecutado directamente
if __name__ == "__main__":
    # Ejecuta la funcion principal
    translate_python_to_cpp("test.py", "test.cpp")
