def ssti_lab(request):
&emsp;if request.user.is_authenticated:
&emsp;&emsp;if request.method=="GET":
&emsp;&emsp;&emsp;users_blogs = Blogs.objects.filter(author=request.user)
&emsp;&emsp;&emsp;return render(request,"Lab_2021/A3_Injection/ssti_lab.html", {"blogs":users_blogs})
&emsp;&emsp;elif request.method=="POST":
&emsp;&emsp;&emsp;blog = request.POST["blog"]
&emsp;&emsp;&emsp;id = str(uuid.uuid4()).split('-')[-1]

&emsp;&emsp;&emsp;blog = filter_blog(blog)
&emsp;&emsp;&emsp;prepend_code = "{&#37; extends 'introduction/base.html' &#37;}\
&emsp;&emsp;&emsp;&emsp;{&#37; block content &#37;}{&#37; block title &#37;}\
&emsp;&emsp;&emsp;&emsp;<title>SSTI-Blogs</title>\
&emsp;&emsp;&emsp;&emsp;{&#37; endblock &#37;}"
&emsp;&emsp;&emsp;
&emsp;&emsp;&emsp;blog = prepend_code + blog + "{&#37; endblock &#37;}"
&emsp;&emsp;&emsp;new_blog = Blogs.objects.create(author = request.user, blog_id = id)
&emsp;&emsp;&emsp;new_blog.save() 
&emsp;&emsp;&emsp;dirname = os.path.dirname(__file__)
&emsp;&emsp;&emsp;filename = os.path.join(dirname, f"templates/Lab_2021/A3_Injection/Blogs/{id}.html")
&emsp;&emsp;&emsp;file = open(filename, "w+") 
&emsp;&emsp;&emsp;file.write(blog)
&emsp;&emsp;&emsp;file.close()
&emsp;&emsp;&emsp;return redirect(f'blog/{id}')
&emsp;else:
&emsp;&emsp;return redirect('login')