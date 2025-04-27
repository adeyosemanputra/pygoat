from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from xml.sax import make_parser
from xml.sax.handler import feature_external_ges
from xml.dom.pulldom import START_ELEMENT, parseString
from .models import Comment

def xxe_home(request):
    return render(request, 'xxe.html')

def xxe_lab(request):
    return render(request, 'xxe_lab.html')

@csrf_exempt
def xxe_see(request):
    try:
        comment = Comment.objects.first()
        return render(request, 'xxe_lab.html', {"com": comment.comment if comment else ""})
    except:
        return render(request, 'xxe_lab.html', {"com": ""})

@csrf_exempt
def xxe_parse(request):
    parser = make_parser()
    parser.setFeature(feature_external_ges, True)
    doc = parseString(request.body.decode('utf-8'), parser=parser)
    
    for event, node in doc:
        if event == START_ELEMENT and node.tagName == 'text':
            doc.expandNode(node)
            text = node.toxml()
            
    startInd = text.find('>')
    endInd = text.find('<', startInd)
    text = text[startInd + 1:endInd:]
    
    comment, created = Comment.objects.get_or_create(id=1, defaults={'name': 'Anonymous'})
    comment.comment = text
    comment.save()

    return render(request, 'xxe_lab.html') 