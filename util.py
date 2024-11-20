import json
import builtins as b
import os

builtin_types = [t for t in b.__dict__.values() if isinstance(t, type)]
json_not_serializable_types = ["Import", "Module"]


def check_if_object_isbuiltin(variable):
    for t in builtin_types:
        if isinstance(variable, t) is True:
            print(f"types {type(variable)} = {t}")
            return True
    return False


def recursive_serialization(dict_obj):

    print(f"{dict_obj=}\n")

    for key, value in dict_obj.items():

        if isinstance(value, list):
            for i, item in enumerate(value):
                if "__dict__" in dir(item):
                    value[i] = recursive_serialization(item.__dict__)

        if isinstance(value, dict):
            for inner_key, inner_value in value.items():
                if "__dict__" in dir(inner_value):
                    value[inner_key] = recursive_serialization(inner_value.__dict__)

        if "__dict__" in dir(value):
            dict_obj[key] = recursive_serialization(value.__dict__)

    return dict_obj

def dump_to_json(dict_obj, filename):

    # for key, value in dict_obj.items():
    #     if "__dict__" in dir(value):
    #         initial_value
            # if "__class__" in dir(value):
            #     if value.__class__.__name__ not in json_not_serializable_types:
            #         print(f"not serialize value: {value} / type = {value.__class__.__name__}")
            #         dict_obj[key] = value.__dict__
            #     else:
            #         dict_obj[key] = value.__str__()

    serialized_obj = recursive_serialization(dict_obj)

    print(f"{serialized_obj=}")

    with open(filename, "w") as f:
        json.dump(serialized_obj, f, indent=4)



def create_csv_file_if_not_exists(filename, columns: list[str]):
    if os.path.exists(filename) is False:
        with open(filename, "w") as f:
            columns_str = iterable_to_csv_row(columns)
            f.write(columns_str)


def add_row_to_dataFrame(df, row):
    i = df.shape[0]
    df.loc[i, :] = row


def iterable_to_csv_row(iterable):
    row = ""
    for i in iterable:
        row += str(i) + ","
    
    row = row.rstrip(",")
    row += "\n"
    return row
