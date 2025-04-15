import os
import json
import sys
import time

# Define the global dictionary of all types
allTypes = {}
# Define the global variable to store the operation result
operation_result = False


class Record: # store the records to append to the relevant json file
    def __init__(self, fields):  #contructor
        self.fields = fields

    def to_dict(self):  # convert the attibutes to dictionary format
        return self.fields


class Page:
    MAX_RECORDS = 10  # max number of records in single page

    def __init__(self): # constructor
        self.records = []

    @staticmethod
    def load_and_save(type_name, page_number, new_record):  # method to update a page
        path = Page.get_path(type_name, page_number)  # get the page path
        page_data = []  # initialize the page_data list

        if os.path.exists(path):  # check if page path exist
            with open(path, 'r') as file:  # open the page in read format
                try:
                    page_data = json.load(file)  # load the page_data
                except json.JSONDecodeError:
                    page_data = []

        page_data.append(new_record.to_dict())  # append the new record

        with open(path, 'w') as file:  # save the updated page_data
            json.dump(page_data, file)

    # this is the method used to load the page, remove the record and save the page
    @staticmethod
    def load_remove_and_save(type_name, page_number, key_value):
        path = Page.get_path(type_name, page_number)                # get the path of the page
        page_data = []

        if os.path.exists(path):                             # check if the path exists
            with open(path, 'r') as file:                    # open the file
                try:
                    page_data = json.load(file)              # load the file
                except json.JSONDecodeError:
                    page_data = []

            for tuple_value in page_data:                   # iterate through the page data
                if key_value in tuple_value[0]:             # check if the key value exists
                    page_data.remove(tuple_value)           # remove the key value

            with open(path, 'w') as file:                   # open the file
                json.dump(page_data, file)                  # dump the page data to the file

    # this method is used to check the record exist before and return the page # of the record if it exists
    # else return -1 which means there is no record with the given key_value
    @staticmethod
    def check_primary_key(type_name, key_value):
        page_name = f"{type_name}.json"  # define file name
        file_path = os.path.join("westerosArchives", type_name, page_name)  # get the file path
        page_data = []  # initialize the page_data list

        if os.path.exists(file_path):  # check if the path exists
            with open(file_path, 'r') as file:  # open the file
                try:
                    page_data = json.load(file)  # load the file
                except json.JSONDecodeError:
                    page_data = []

                for tuple_value in page_data:  # search the key value
                    if key_value in tuple_value[0]:
                        return tuple_value[1]  # return the page number if key_value exists already
        return -1  # if key_value does not exist return -1

    # this method returns the first available page number to add a record
    # if the file is full the method returns -1
    @staticmethod
    def first_slot(type_name):
        page_name = f"{type_name}.json"  # define file name
        file_path = os.path.join("westerosArchives", type_name, page_name)  # get the file path
        page_data = []  # initialize the page_data list

        if os.path.exists(file_path):  # check if the path exists
            with open(file_path, 'r') as file:  # open the file
                try:
                    page_data = json.load(file)  # load the file
                except json.JSONDecodeError:
                    page_data = []

                count = 10  # initialize the page count as full
                for i in range(File.MAX_PAGES):  # check each page for the available slots
                    if count < 10:  # check if there is an available slot in the previous page
                        return i-1  # returns the available page
                    count = 0  # reset the count to 0
                    for tuple_value in page_data:  # heck each item in the page
                        if i == tuple_value[1]:  # count the items in the page
                            count += 1
                            if count == Page.MAX_RECORDS:  # if page is full, skip to next page
                                break
        else:
            return 0  # if there is no records in the type, return page 0

        return -1  # if type file is full, returns -1

    @staticmethod
    def add_to_page(type_name, fields, key_order):
        global operation_result                         # to access the global variable
        key_value = fields[key_order]  # get the value of the primary_key

        check_keys = Page.check_primary_key(type_name, key_value)  # check the primary key exists

        if check_keys != -1:  # if duplicate, don`t add the record
            return

        page_number = Page.first_slot(type_name)  # find the first available slot

        if page_number == -1:  # if no available page, don`t add the record
            return

        operation_result = True                         # to set the operation result to true because the operation is successful

        new_record = Record(fields)  # create the record object
        Page.add_key(type_name, key_value, page_number)  # add the key to the reference table
        Page.load_and_save(type_name, page_number, new_record)  # append the record to the given page

    # this is the method used to remove the record from the page
    @staticmethod
    def remove_from_page(type_name, fields, key_order):
        global operation_result                         # to access the global variable
        key_value = fields[key_order]
        page_number = Page.check_primary_key(type_name, key_value)      # get the page number
        # check if the key value exists, otherwise print the error message
        if page_number == -1:
            return

        operation_result = True                         # to set the operation result to true because the operation is successful

        Page.delete_key(type_name, key_value)                           # call the delete key method from the page holding keys
        Page.load_remove_and_save(type_name, page_number, key_value)    # call the load remove and save method to remove the record from the page

    # this is the method to append a new key to the key-page id pair reference table of given type
    @staticmethod
    def add_key(type_name, key_value, page_number):
        page_name = f"{type_name}.json"  # define file name
        file_path = os.path.join("westerosArchives", type_name, page_name)  # get the file path
        page_data = []  # initialize the page_data list

        fields = [key_value, page_number]  # create the fields of the pair
        new_record = Record(fields)  # create the record object to add the reference table
        if os.path.exists(file_path):  # check if the path exists
            with open(file_path, 'r') as file:  # open the file
                try:
                    page_data = json.load(file)  # load the file
                except json.JSONDecodeError:
                    page_data = []

        page_data.append(new_record.to_dict())  # append the record

        with open(file_path, 'w') as file:  # open the file in write mode
            json.dump(page_data, file)   # save the file

    # this is the method used to delete the key from the page
    @staticmethod
    def delete_key(type_name, key_value):
        page_name = f"{type_name}.json"                                         # get the page name
        file_path = os.path.join("westerosArchives", type_name, page_name)      # get the file path
        page_data = []

        if os.path.exists(file_path):                       # check if the file exists
            with open(file_path, 'r') as file:              # open the file
                try:
                    page_data = json.load(file)             # load the file
                except json.JSONDecodeError:
                    page_data = []

            for tuple_value in page_data:                   # iterate through the page data
                if key_value in tuple_value[0]:             # check if the key value exists
                    page_data.remove(tuple_value)           # remove the key value

            with open(file_path, 'w') as file:              # open the file
                json.dump(page_data, file)                  # dump the page data to the file

    # this method is used to return the record details for the search command
    @staticmethod
    def search_given_page(type_name, value, page_number):
        key_order = allTypes[type_name].key_order  # get the key order of the type
        path = Page.get_path(type_name, page_number)  # get the page path

        if os.path.exists(path):  # check if the file exists
            with open(path, 'r') as file:  # open the file
                page_data = json.load(file)  # load the file

            for tuple_value in page_data:  # iterate through the page data
                if value in tuple_value[key_order]:  # find the record key equal to given value
                    return tuple_value  # return the record details
        return -1  # return -1 if record does not exist

    @staticmethod
    def get_path(type_name, page_number):  # get the page path for the given page number and type
        page_name = f"Page_{page_number}.json"
        return os.path.join("westerosArchives", type_name, page_name)


# this class is storing the functions for the type Files
class File:
    MAX_PAGES = 10000

    def __init__(self, type_name):  # constructor
        self.type_name = type_name

    # this method creates the File directory on the database
    def create_file(self):
        file_path = os.path.join("westerosArchives", self.type_name)  # get the path

        if not os.path.exists(file_path):  # check if the path exists
            os.makedirs(file_path)  # create the directory

    # this is the method used to add the record
    def new_record(self, fields):
        key_order = allTypes[self.type_name].key_order
        Page.add_to_page(self.type_name, fields, key_order)

    # this is the method used to erase the record
    def erase_record(self, fields):
        key_order = allTypes[self.type_name].key_order
        Page.remove_from_page(self.type_name, fields, key_order)


# this class stores the relevant function for the database types
class Type:
    MAX_FIELDS = 6  # set the max number of fields in a type as 6
    MAX_NAME_LENGTH = 12  # set the max type name length as 12
    MAX_FIELD_NAME_LENGTH = 20  # set the max field name length as 20

    def __init__(self, type_name, key_order):  # constructor
        self.type_name = type_name
        self.key_order = key_order
        self.fields = []
        self.type_file = File(type_name)

    # this method creates the type
    @staticmethod
    def create_type(details):
        global operation_result             # to access the global variable
        type_name = details[2]  # get the type name
        no_of_fields = int(details[3])  # get number of fields
        key_order = int(details[4]) - 1  # get the primary key order

        if type_name in allTypes:  # check if the type already exists
            return

        if no_of_fields > Type.MAX_FIELDS:  # check if the number of fields exceeds the character limit
            return

        if len(type_name) > Type.MAX_NAME_LENGTH:  # check if the type_name exceeds the character limit
            return

        for i in range(5, 5 + (no_of_fields * 2), 2):  # check if any of the field names exceeds the character limit
            if len(details[i]) > Type.MAX_FIELD_NAME_LENGTH:
                return

        operation_result = True                     # to set the operation result to true because the operation is successful

        new_type = Type(type_name, key_order)  # create the type object
        type_file = new_type.type_file

        type_file.create_file()  # create the type file folder

        # add to catalog
        list_as_str = ' '.join(details)
        list_as_str += '\n'
        append_to_catalog(list_as_str)

        # create the fields
        for i in range(5, 5 + (no_of_fields * 2), 2):
            field_name = details[i]
            field_type = details[i + 1]
            new_type.fields.append((field_name, field_type))

        # add type to allTypes list
        allTypes[type_name] = new_type

    # this is the method used to load the existing types from the previous runs
    @staticmethod
    def load_type(details):
        type_name = details[2]  # load the type name
        no_of_fields = int(details[3])  # load number of fields
        key_order = int(details[4]) - 1  # load the primary key order

        new_type = Type(type_name, key_order)  # load the type object

        # load the fields
        for i in range(5, 5 + (no_of_fields * 2), 2):
            field_name = details[i]
            field_type = details[i + 1]
            new_type.fields.append((field_name, field_type))

        # add type to allTypes list
        allTypes[type_name] = new_type

    # this is the method used to create the record
    @staticmethod
    def create_record(details):
        type_name = details[2]  # get the type name

        # check if the type name exists
        if type_name not in allTypes:
            return

        this_type = allTypes[type_name]   # get the type object
        key_input = details[this_type.key_order + 3]  # get the key input

        this_file = this_type.type_file  # get the file object
        this_file.new_record(details[3:])  # call the new_record method

    # this is the method used to delete the record
    @staticmethod
    def delete_record(details):
        type_name = details[2]                # get the type name

        # check if the type name exists, otherwise print the error message
        if type_name not in allTypes:
            return

        this_type = allTypes[type_name]                 # get the type object
        key_input = details[this_type.key_order + 3]    # get the key input

        this_file = this_type.type_file                 # get the file object
        this_file.erase_record(details[3:])             # call the erase record method


# method that parses the input file
def parse(file):
    next_line = file.readline()  # read the next line
    while next_line:

        global operation_result                     # to access the global variable
        operation_result = False                    # intialize the operation result to false because the default operation result is false, it will true when it is successful
        details = next_line.split()  # split the line

        # check the type of command
        # in case of create type
        if details[0] == 'create' and details[1] == 'type':
            Type.create_type(details)  # call the create_type method
            add_to_log(details)  # add the log of the command to the log file

        # in case of create record
        elif details[0] == 'create' and details[1] == 'record':
            Type.create_record(details)  # call the create_record method
            add_to_log(details)  # add the log of the command to the log file

        # in case of delete record
        elif details[0] == 'delete' and details[1] == 'record':
            Type.delete_record(details)                 # call the delete record method
            add_to_log(details)                         # add the log of the command to the log file

        # in case of search record
        elif details[0] == 'search' and details[1] == 'record':
            type_name = details[2]  # get the type name
            key_value = details[3]  # get the key_value
            page_number = Page.check_primary_key(type_name, key_value)  # get the record location

            # in case record does not exist
            if page_number == -1:
                add_to_log(details)
            # in case record exists
            else:
                my_record = Page.search_given_page(type_name, key_value, page_number)  # get the record details

                # add record to the output.txt file
                list_as_str = ' '.join(my_record)
                list_as_str += '\n'
                add_to_output(list_as_str)

                operation_result = True  # set operation result as true
                add_to_log(details)  # add the log of the command to the log file

        next_line = file.readline()  # Read the next line


# this is the method used to add the command to the log file
def add_to_log(command):
    command_as_str = ' '.join(command)                  # convert the command to string
    # create the log message consisting of time message, and the operation result
    log_message = str(int(time.time())) + ", " + command_as_str + ", " + (
        "success" if operation_result else "failure") + "\n"
    with open(log_path, 'a') as log_file:
        log_file.write(log_message)


# this is the method used to add the create type command details to the catalog file
def append_to_catalog(command):
    with open(catalog_path, 'a') as catalog_file:
        catalog_file.write(command)


# this is the method used to add the output details to the output file
def add_to_output(output):
    with open(output_path, 'a') as output_file:
        output_file.write(output)


# this is the method used to add pre-existing type details in the allTypes list
# at the start of each execution of the program
def sync_the_catalog(file):
    next_line = file.readline()  # read the next line
    while next_line:
        type_definition = next_line.split()  # split the line
        Type.load_type(type_definition)  # load the type
        next_line = file.readline()  # Read the next line


def main():
    filename = sys.argv[1]  # input file

    try:
        with open(catalog_path, 'r') as file:  # get the catalog file to load existing types
            sync_the_catalog(file) # call the sync_the_catalog method
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        with open(filename, 'r') as file:  # get the input file
            parse(file)  # call the parse method to read the commands
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # create the database directory if it does not exist
    if not os.path.exists("westerosArchives"):
        os.makedirs("westerosArchives")

    # create the catalog file if it does not exist
    catalog_name = f"catalog.txt"
    catalog_path = os.path.join("westerosArchives", catalog_name)
    with open(catalog_path, 'a'):
        pass

    # create the output file for each execution
    output_name = f"output.txt"
    output_path = os.path.join(output_name)
    with open(output_path, 'w'):
        pass

    # create the log file if it does not exist
    log_name = f"log.txt"
    log_path = os.path.join(log_name)
    with open(log_path, 'a'):
        pass

    main()  # call the main method
