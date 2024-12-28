#!/usr/bin/python3
import subprocess


#This is script is userd to create a user and password on linux Rocky distributions
#When writting script for python you should 

def create_user(user_name, password=None): 

    try: # when writing a python program for linux make sure to put your code on try and except, in order to make sure the progrmming other things are working .
        # Add the user on the Rocky 8  
        subprocess.run(["sudo", "useradd", "-m", user_name], check=True) # Run fucntion allow you to use the command that you mainly user on linux to add user
        print(f"User '{username}' created successfully.")

        if password: # Giving password to suere is not mandatory hear so it is optional set a password on it.
            # Set the password
            subprocess.run(
                ["sudo", "chpasswd"],
                input=f"{user_name}:{password}".encode(),
                check=True
            ) # the encode function is used to change the given password to bytes becasue the python don't understand the plain text.
            print(f"Password for user '{username}' set successfully.")
        else:
            print("No password set for the user.")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing a command: {e}")
    e

if __name__ == "__main__":
    username = input("Enter the username to create: ").strip() # strip function is used to ignor the space, tab in your suername and password. if you want to have space , please don't user the strip() fucntion.
    user_pwd = input("Enter the password (leave blank for no password): ").strip()
    create_user(username, pwd if pwd else None)
