import os
def ssrf_lab(file):
    try:
        tb = ['secret.txt']
        if file in tb:
            return {"blog" : "No blog found"}
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, file)
        file = open(filename,"r")
        data = file.read()
        return {"blog":data}
    except:
        return {"blog": "No blog found"}