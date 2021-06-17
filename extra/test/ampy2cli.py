import webrepl
import sys
import os

repl=webrepl.Webrepl(**{'host':'192.168.1.39','port':8266,'password':'1234'})

def get_files(source,dest):
    repl.get_file(source, dest)

def put_files(source,dest):
    repl.put_file(source, dest)

def del_file(filename):
    repl.sendcmd("import os; os.remove('"+filename+"')")

def file_content(filename):
    r=repl.get_file_content(filename)
    return r.decode()

def run_file(filename):
    repl.sendcmd(f"import utils,{filename};utils.reload({filename})")

def get_shell():
	while True:
		user_input = input(">>>")
		resp=repl.sendcmd(user_input)
		cleaned_output = "\n".join(resp.decode().strip().split("\n")[1:])
		print(cleaned_output)

def filelist():
    resp=repl.sendcmd("import os; os.listdir()")
    cleaned_output = "\n".join(resp.decode().strip().split("\n")[1:])
    print(cleaned_output)

if __name__ == '__main__':
    if sys.argv[1] == 'shell':
        get_shell()
    if sys.argv[1] == 'get':
        source = sys.argv[2]
        dest = sys.argv[3]
        get_files(source,dest)
    if sys.argv[1] == 'put':
        source = sys.argv[2]
        dest = sys.argv[3]
        put_files(source,dest)
    if sys.argv[1] == 'rm':
        filename = sys.argv[2]
        del_file(filename)
    if sys.argv[1]=='run':
        filename = sys.argv[2]
        pre,ext = os.path.splitext(filename)
        run_file(pre)
    if sys.argv[1]=='ls':
        filelist()

    


