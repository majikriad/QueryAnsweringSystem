import os 
Predicates = {}

class dataset:
    current_path= os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_path)
    def get_resource(self):
        # current_path= os.path.dirname(os.path.realpath(__file__))
        # os.chdir(current_path)
        
        Rfile=open(".\\Resources.txt",'r')
        Resources=Rfile.read().split('\n')
        return Resources

    #def get_Predicates():
    def get_Predicates(self):
        Pfile=open(".\\Property.txt",'r')
        lines=Pfile.read().splitlines()
        for line in lines:
            sline=line.split('\t')
            key=sline.pop(0)
            Predicates[key]=sline
        return Predicates

if __name__=='__main__':
    print(os.getcwd())
