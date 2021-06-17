import os

# def list_files(startpath):
#     for root, dirs, files in os.walk(startpath):
#         level = root.replace(startpath, '').count(os.sep)
#         indent = ' ' * 4 * (level)
#         print('{}{}/'.format(indent, os.path.basename(root)))
#         subindent = ' ' * 4 * (level + 1)
#         for f in files:
#             print('{}{}'.format(subindent, f))


# def tree_printer(root):
#     for root, dirs, files in os.walk(root):
#         for d in dirs:
#             print(os.path.join(root, d))    
#         for f in files:
#             print(os.path.join(root, f))


def subdir_maker(path):
	for root, dirs, files in os.walk(path):
	    print('root:', root)

	    for dir in dirs:
	        print('dir:',os.path.join(root,dir))

	    for file in files:
	        print('file:',os.path.join(root,file))


path="/home/gaurav/Documents/ampy2/projects"
# list_files(path)
subdir_maker(path)