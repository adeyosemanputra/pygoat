from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from ...models import tickits

# A11: Insecure Design Views
def a11(request):
    """View for A11: Insecure Design introduction."""
    return render(request, 'a11.html')

def gentckt():
    """Generate a random ticket code."""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@login_required
def a11_lab(request):
    """Lab for demonstrating insecure design patterns."""
    if request.method == "GET":
        tickets = list(tickits.objects.filter(user=request.user).values_list('tickit', flat=True))
        return render(request, "Lab/A11/a11_lab.html", {"tickets": tickets})
    
    elif request.method == "POST":
        tickets = list(tickits.objects.filter(user=request.user).values_list('tickit', flat=True))
        
        # Handle ticket generation
        if 'count' in request.POST:
            try:
                count = int(request.POST.get("count", 0))
                if (count + len(tickets)) <= 5:
                    new_tickets = []
                    for _ in range(count):
                        ticket_code = gentckt()
                        new_tickets.append(ticket_code)
                        tickits.objects.create(user=request.user, tickit=ticket_code)
                    
                    tickets.extend(new_tickets)
                    return render(request, "Lab/A11/a11_lab.html", {"tickets": tickets})
                else:
                    return render(request, "Lab/A11/a11_lab.html", {
                        "error": "You can have at most 5 tickets", 
                        "tickets": tickets
                    })
            except (ValueError, TypeError):
                pass
        
        # Handle ticket validation
        elif 'ticket' in request.POST:
            ticket = request.POST.get("ticket")
            sold_tickets = tickits.objects.count()
            
            if sold_tickets < 60:
                return render(request, "Lab/A11/a11_lab.html", {
                    "error": f"Wait until all tickets are sold ({60 - sold_tickets} tickets left)",
                    "tickets": tickets
                })
            else:
                if ticket in tickets:
                    return render(request, "Lab/A11/a11_lab.html", {
                        "error": "Congratulations, you figured out the flaw in Design.<br>"
                               "A better authentication should be used for checking the uniqueness of a user.",
                        "tickets": tickets
                    })
                else:
                    return render(request, "Lab/A11/a11_lab.html", {
                        "tickets": tickets,
                        "error": "Invalid ticket"
                    })
    
    return redirect('a11_lab')
