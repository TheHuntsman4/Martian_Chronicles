import os
def get_file_name():
    file_list=[]
    for filename in os.listdir("images2"):
        file_list.append(filename)
    print(file_list)
get_file_name()

 