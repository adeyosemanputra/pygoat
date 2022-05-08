import os
def ssrf_lab(file):
    try:
        filter = ["templates/Lab/ssrf/blogs/blog1.txt","templates/Lab/ssrf/blogs/blog2.txt","templates/Lab/ssrf/blogs/blog3.txt","templates/Lab/ssrf/blogs/blog4.txt"]
        if file not in filter:
            return {"blog" : "No blog found"}
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, file)
        file = open(filename,"r")
        data = file.read()
        return {"blog":data}
    except:
        return {"blog": "No blog found"}