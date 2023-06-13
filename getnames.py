import glob

owners = [file for file in glob.glob("Database/*.bmp")]

f = open('names.txt', 'w')

exist = 0
x = []
for i in owners:
    name = i[0:len(i)-5]
    name = name +'3.bmp\n'
    name = name.split('/')
    name = name[1]
    if(x == []):
        x.append(name)
        
        print name
        f.write(name)
    else:
        exist = 0
        for j in x:
            if(name == j):
                exist = 1
                break
        if(exist == 0):
            x.append(name)
            f.write(name)
                
    

f.close() 



