import os
# import re
def ssrf_code_converter(code):
    list_input = code.split("\n")
    list_output = ['import os','def ssrf_lab(file):','    try:']
    extracted_code = []
    i = 7
    while i < (len(list_input)-5):
        extracted_code.append(list_input[i][8:])
        i += 1
    list_output= list_output + extracted_code
    list_output.append('        return {"blog":data}')
    list_output.append("    except:")
    list_output.append('        return {"blog": "No blog found"}')
    output_Code = "\n".join(list_output)

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "playground/ssrf/main.py")
    f = open(filename,"w")
    f.write(output_Code)
    f.close()
    return output_Code

# ssrf_code_converter(input_code)
def ssrf_html_input_extractor(code):
    params = []
    list_input = code.split("\n")
    tokens = list(map(lambda x : x.strip().split(' '), list_input))
    for i in range(len(tokens)):
        if tokens[i][0] == '<input':
            for j in range(len(tokens[i])):
                if tokens[i][j][:7] == 'value="':
                    params.append(tokens[i][j][7:-2])
    return params