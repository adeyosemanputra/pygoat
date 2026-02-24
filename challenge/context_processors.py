from .models import UserChallenge

def challenge_status(request):
    if request.user.is_authenticated:
        # Fetches all challenge names that this specific user has solved
        solved_labs = UserChallenge.objects.filter(
            user=request.user, 
            is_solved=True
        ).values_list('challenge__name', flat=True)
        
        # Returns a dictionary like {'business_logic_lab': True}
        return {'challenge_status': {name: True for name in solved_labs}}
    return {'challenge_status': {}}
