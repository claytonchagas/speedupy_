import ast, os, os.path

class Experiment():
    def __init__(self, experiment_base_dir):
        self.__experiment_base_dir = experiment_base_dir
        self.__scripts = {}
    

    def add_script(self, script):
        self.__scripts[script.name] = script
    

    #####DEBUG#####
    def print(self):
        print("###EXPERIMENT###")
        print("experiment_base_dir:", self.__experiment_base_dir)
        print("scripts:")
        for script in self.__scripts.values():
            script.print()


    @property
    def experiment_base_dir(self):
        return self.__experiment_base_dir


    @property
    def scripts(self):
        return self.__scripts


class Script():
    def __init__(self, name = "", AST = None, import_commands = set(), functions = {}, function_graph = None):
        self.__name = name
        self.__AST = AST
        self.__import_commands = import_commands
        self.__functions = functions
        self.__function_graph = function_graph


    def script_name_to_script_path(self, script_name):
            script_path = script_name[0]
            for i in range(1, len(script_name), 1):
                letter = script_name[i]
                if((letter == "." and script_path[-1] != ".") or
                (letter != "." and script_path[-1] == ".")):
                    script_path += os.sep + letter
                else:
                    script_path += letter
            script_path += ".py" if script_path[-1] != "." else os.sep + "__init__.py"
            return os.path.normpath(os.path.join(os.path.dirname(self.__name), script_path))


    def import_command_to_imported_scripts_names(self, import_command):
        imported_scripts_names = []
        if(isinstance(import_command, ast.Import)):
            for alias in import_command.names:
                imported_scripts_names.append(self.script_name_to_script_path(alias.name))

        elif(isinstance(import_command, ast.ImportFrom)):
            imported_script_name = import_command.level * "." + import_command.module if import_command.module is not None else import_command.level * "."
            imported_scripts_names.append(self.script_name_to_script_path(imported_script_name))
            
        return imported_scripts_names

    
    def get_imported_scripts(self):
        imported_scripts = []
        for import_command in self.__import_commands:
            imported_scripts += self.import_command_to_imported_scripts_names(import_command)
        return imported_scripts

    
    def get_user_defined_imported_scripts(self, experiment_base_dir):
        imported_scripts = self.get_imported_scripts()
        user_defined_imported_scripts = []
        for imported_script in imported_scripts:
            if is_an_user_defined_script(imported_script, experiment_base_dir):
                user_defined_imported_scripts.append(imported_script)
        return user_defined_imported_scripts

    
    def get_import_command_of_function(self, function_name):
        if(function_name.find(".") == -1):
            for import_command in self.__import_commands:
                if(isinstance(import_command, ast.ImportFrom)):
                    for alias in import_command.names:
                        function_imported_name = alias.asname if alias.asname is not None else alias.name
                        if(function_imported_name == function_name):
                            return import_command
        else:
            script_name = function_name[:function_name.rfind(".")]
            for import_command in self.__import_commands:
                if(isinstance(import_command, ast.Import)):
                    for alias in import_command.names:
                        script_imported_name = alias.asname if alias.asname is not None else alias.name
                        if(script_imported_name == script_name):
                            return import_command
        return None

    #MAYBE IN THE FUTURE "get_original_name_of_script_imported_with_import" AND 
    #"get_original_name_of_function_imported_with_import_from" CAN BE COLLAPSED
    #IN ONE FUNCTION
    def get_original_name_of_script_imported_with_import(self, import_command, function_name):
        script_name = function_name[:function_name.rfind(".")]
        for alias in import_command.names:
            script_imported_name = alias.asname if alias.asname is not None else alias.name
            if(script_imported_name == script_name):
                return alias.name
        return None

    
    def get_original_name_of_function_imported_with_import_from(self, import_from_command, function_name):
        for alias in import_from_command.names:
            function_imported_name = alias.asname if alias.asname is not None else alias.name
            if(function_imported_name == function_name):
                return alias.name
        return None

    
    def get_function(self, function_name):
        if(function_name in self.__functions):
            return self.__functions[function_name]
        return None


    ###DEBUG####
    def print(self):
        print("#####SCRIPT#####")
        print("Name:", self.__name)
        print("AST:", self.__AST)
        print("Import Commands:", self.__import_commands)
        print("Functions:", self.__functions)
        print("Function Graph:")
        if(self.__function_graph is not None):
            for function in self.__function_graph:
                print(3*" ", function.qualname, function)
                for link in self.__function_graph[function]:
                    print(6*" ", link.qualname, link)


    @property
    def name(self):
        return self.__name
    

    @name.setter
    def name(self, name):
        self.__name = name


    @property
    def AST(self):
        return self.__AST


    @AST.setter
    def AST(self, AST):
        self.__AST = AST


    @property
    def import_commands(self):
        return self.__import_commands
    

    @import_commands.setter
    def import_commands(self, import_commands):
        self.__import_commands = import_commands


    @property
    def functions(self):
        return self.__functions


    @functions.setter
    def functions(self, functions):
        self.__functions = functions
    

    @property
    def function_graph(self):
        return self.__function_graph
 

    @function_graph.setter
    def function_graph(self, function_graph):
        self.__function_graph = function_graph


def get_all_init_scripts_implicitly_imported(imported_script, experiment_base_dir):
    init_scripts_implicitly_imported = set()
    if(imported_script.rfind(os.sep) != -1):
        current_init_script_path = imported_script[0:imported_script.rfind(os.sep) + 1] + "__init__.py"
        while(current_init_script_path != "__init__.py"):
            if(os.path.exists(get_script_path(current_init_script_path, experiment_base_dir))):
                init_scripts_implicitly_imported.add(current_init_script_path)
            current_init_script_path = current_init_script_path.split(os.sep)
            current_init_script_path.pop(-2)
            current_init_script_path = os.sep.join(current_init_script_path)
    return init_scripts_implicitly_imported


def create_experiment_function_graph(user_script_path):
    def script_already_analized(script):
        return script in scripts_analized

    experiment_base_dir, user_script_name = os.path.split(user_script_path)
    
    experiment = Experiment(experiment_base_dir)
    scripts_analized = {}
    scripts_to_be_analized = [user_script_name]
    while(len(scripts_to_be_analized) > 0):
        script_name = scripts_to_be_analized.pop(0)
        
        script_AST = python_code_to_AST(get_script_path(script_name, experiment_base_dir))
        if(script_AST is None):
            raise RuntimeError

        script_ASTSearcher = ASTSearcher(script_AST)
        script_ASTSearcher.search()

        if(script_name == user_script_name):
            script_name = "__main__"

        for function_name in script_ASTSearcher.functions:
            script_ASTSearcher.functions[function_name].qualname = function_name
        
        script = Script(script_name, script_AST, script_ASTSearcher.import_commands, script_ASTSearcher.functions)
        experiment.add_script(script)

        imported_scripts = script.get_imported_scripts()        
        for imported_script in imported_scripts:
            if(is_an_user_defined_script(imported_script, experiment_base_dir) and
            not script_already_analized(imported_script)):
                scripts_to_be_analized.append(imported_script)
                for init_scripts in get_all_init_scripts_implicitly_imported(imported_script, experiment_base_dir):
                    if(is_an_user_defined_script(init_scripts, experiment_base_dir) and
                    not script_already_analized(init_scripts)):
                        scripts_to_be_analized.append(init_scripts)

        scripts_analized[script_name] = script_ASTSearcher
    
    experimentFunctionGraphCreator = ExperimentFunctionGraphCreator(experiment)
    experimentFunctionGraphCreator.create_experiment_function_graph()
    return experimentFunctionGraphCreator.experiment_function_graph
    

def python_code_to_AST(file_name):
    try:
        #Opening file
        file = open(file_name, "r")

    except:
        print("Error while trying to open file!")
        print("Check if the file exists!")
        return None

    else:
        try:
            #Generating AST from Python code
            return ast.parse(file.read())

        except:
            print("Error while trying to generate AST from the Python code!")
            print("Check if your Python script is correctly writen.")
            return None


def get_script_path(script_name, experiment_base_dir):
    return os.path.join(experiment_base_dir, script_name)


def is_an_user_defined_script(imported_script, experiment_base_dir):
    return os.path.exists(get_script_path(imported_script, experiment_base_dir)) and imported_script.find("intpy") == -1


class ASTSearcher(ast.NodeVisitor):
    def __init__(self, AST):
        self.__AST = AST
        self.__import_commands = []
        self.__functions = {}


    def search(self):
        #Finding all declared functions and imported modules
        #in the AST

        self.__current_function = None
        self.__current_function_name = ""
        self.visit(self.__AST)


    def visit_Import(self, node):
        if(node not in self.__import_commands):
            self.__import_commands.append(node)
        self.generic_visit(node)


    def visit_ImportFrom(self, node):
        if(node not in self.__import_commands):
            self.__import_commands.append(node)
        self.generic_visit(node)


    def visit_ClassDef(self, node):
        """This function avoids that child nodes of a ClassDef node
        (ex.: class methods) be visited during search"""


    def visit_FunctionDef(self, node):
        previous_function_name = self.__current_function_name
        self.__current_function_name = node.name if self.__current_function_name == "" else self.__current_function_name + ".<locals>." + node.name
        previous_function = self.__current_function
        self.__current_function = node


        self.__functions[self.__current_function_name] = node

        self.generic_visit(node)


        self.__current_function = previous_function
        self.__current_function_name = previous_function_name


    @property
    def AST(self):
        return self.__AST


    @property
    def import_commands(self):
        return self.__import_commands


    @property
    def functions(self):
        return self.__functions


class ExperimentFunctionGraphCreator(ast.NodeVisitor):
    def __init__(self, experiment):
        self.__experiment = experiment
        self.__experiment_function_graph = {}

    
    def __initialize_script_function_graph(self, script, imported_scripts_names):
        script_function_graph = {}
        for imported_script_name in imported_scripts_names:
            script_function_graph.update(self.__experiment.scripts[imported_script_name].function_graph)
        for function in script.functions.values():
            script_function_graph[function] = set()
        return script_function_graph

    
    def create_experiment_function_graph(self):
        self.__experiment_function_graph = self.__create_script_function_graph("__main__")


    def __create_user_defined_imported_scripts_function_graphs(self, user_defined_imported_scripts):
        for user_defined_imported_script in user_defined_imported_scripts:
            self.__create_script_function_graph(user_defined_imported_script)


    def __create_script_function_graph(self, script_name):
        script = self.__experiment.scripts[script_name]

        user_defined_imported_scripts = script.get_user_defined_imported_scripts(self.__experiment.experiment_base_dir)
        print(f"{user_defined_imported_scripts}")
        
        self.__create_user_defined_imported_scripts_function_graphs(user_defined_imported_scripts)

        self.__script_function_graph = self.__initialize_script_function_graph(script, user_defined_imported_scripts)
        
        self.__current_script = script
        self.__current_function_name = ""
        self.__current_function = None
        self.visit(script.AST)
        
        script.function_graph = self.__script_function_graph
        return self.__script_function_graph


    def visit_ClassDef(self, node):
        """This function avoids that child nodes of a ClassDef node
        (ex.: class methods) be visited during search"""
        

    def visit_FunctionDef(self, node):
        previous_function_name = self.__current_function_name
        self.__current_function_name = node.name if self.__current_function_name == "" else self.__current_function_name + ".<locals>." + node.name
        previous_function = self.__current_function
        self.__current_function = node

        self.generic_visit(node)

        self.__current_function_name = previous_function_name
        self.__current_function = previous_function
    
    
    def visit_Call(self, node):
        def find_possible_functions_called(function_called_name):
            possible_functions_called = {}
            if(function_called_name.find(".") == -1):
                for function_name in self.__current_script.functions:
                    if(self.__current_script.functions[function_name].name == function_called_name):
                        possible_functions_called[function_name] = self.__current_script.functions[function_name]
                                
                import_command = self.__current_script.get_import_command_of_function(function_called_name)
                if(import_command is None):
                    return possible_functions_called

                imported_script_name = self.__current_script.import_command_to_imported_scripts_names(import_command)[0]
                if(not is_an_user_defined_script(imported_script_name, self.__experiment.experiment_base_dir)):
                    return possible_functions_called
                
                original_imported_function_name = self.__current_script.get_original_name_of_function_imported_with_import_from(import_command, function_called_name)
                try:
                    possible_functions_called[original_imported_function_name] = self.__experiment.scripts[imported_script_name].functions[original_imported_function_name]
                except:
                    #In this case the function called is a constructor to a class that was imported to the script
                    pass
                
            else:
                import_command = self.__current_script.get_import_command_of_function(function_called_name)
                if(import_command is None):
                    return possible_functions_called

                original_imported_script_name = self.__current_script.get_original_name_of_script_imported_with_import(import_command, function_called_name)
                
                imported_script_name = self.__current_script.script_name_to_script_path(original_imported_script_name)
                if(not is_an_user_defined_script(imported_script_name, self.__experiment.experiment_base_dir)):
                    return possible_functions_called
                
                possible_functions_called[function_called_name[function_called_name.rfind(".") + 1:]] = self.__experiment.scripts[imported_script_name].functions[function_called_name[function_called_name.rfind(".") + 1:]]

            return possible_functions_called


        def find_function_called(function_called_name, possible_functions_called):
            number_of_possible_functions_called = len(possible_functions_called)
            if(number_of_possible_functions_called == 0):
                return None
            elif(number_of_possible_functions_called == 1):
                return list(possible_functions_called.values())[0]
            else:
                #In this case there are two functions defined in the script
                #with the same name
                #Finding function defined in the smaller scope
                function_called = None
                function_called_name_prefix = self.__current_function_name + ".<locals>."
                while(function_called == None):
                    for possible_function_called_name in possible_functions_called:
                        if(function_called_name_prefix + function_called_name == possible_function_called_name):
                            function_called = self.__current_script.functions[possible_function_called_name]
                            break
                    
                    if(function_called_name_prefix == ""):
                        break

                    #The string in "function_called_name_prefix" always ends in a dot (".<locals>.")
                    #Hence, the last element of "function_called_name_prefix.split('.<locals>.')" will
                    #always be an empty string ("")
                    if(len(function_called_name_prefix.split(".<locals>.")) > 2):
                        function_called_name_prefix = function_called_name_prefix.split(".<locals>.")
                        function_called_name_prefix.pop(-2)
                        function_called_name_prefix = ".<locals>.".join(function_called_name_prefix)
                    else:
                        function_called_name_prefix = ""
                return function_called
        
        #Testing if this node represents a call to some function done inside another function
        if(self.__current_function_name != ""):
            function_called = None
            
            if(isinstance(node.func, ast.Name)):
                #In this case the function called can be either a function imported
                #with the command "from ... im  port ..." or a function declared by the
                #user in the file

                function_called_name = node.func.id
                possible_functions_called = find_possible_functions_called(function_called_name)
                function_called = find_function_called(function_called_name, possible_functions_called)
            
            elif(isinstance(node.func, ast.Attribute)):
                #In this case the function called is a function imported with the command
                #"import ..."

                #Building the name of the function called
                current_node = node.func
                function_called_name_parts = []
                while(isinstance(current_node, ast.Attribute)):
                    function_called_name_parts.append(current_node.attr)
                    current_node = current_node.value
                    print(current_node.__dict__)
                function_called_name_parts.append(current_node.id)

                function_called_name_parts.reverse()
                function_called_name = ".".join(function_called_name_parts)

                possible_functions_called = find_possible_functions_called(function_called_name)
                function_called = find_function_called(function_called_name, possible_functions_called)
            
            if(function_called != None):
                self.__script_function_graph[self.__current_function].add(function_called)

        self.generic_visit(node)


    @property
    def experiment_function_graph(self):
        return self.__experiment_function_graph


def get_source_code_executed(function, function_graph):
    list_of_graph_vertices_not_yet_processed = []
    list_of_graph_vertices_already_processed = []
    source_codes_executed = []
    for current_function_def_node in function_graph:
        if(current_function_def_node.qualname == function.__qualname__):
            list_of_graph_vertices_not_yet_processed.append(current_function_def_node)
            break

    while(len(list_of_graph_vertices_not_yet_processed) > 0):
        current_vertice = list_of_graph_vertices_not_yet_processed.pop(0)

        source_codes_executed.append(ast.unparse(current_vertice))

        for linked_vertice in function_graph[current_vertice]:
            if(linked_vertice not in list_of_graph_vertices_not_yet_processed and
            linked_vertice not in list_of_graph_vertices_already_processed and
            linked_vertice != current_vertice):
                list_of_graph_vertices_not_yet_processed.append(linked_vertice)
        
        list_of_graph_vertices_already_processed.append(current_vertice)
    
    return "\n".join(source_codes_executed)
