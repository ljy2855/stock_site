from user.models import *
def holding_stocks(request):
    if request.user.is_authenticated:
        stocks = HoldingStock.objects.filter(user=request.user)
        return {'holding_stocks': stocks}
    return {}

def user_info(request):
    if request.user.is_authenticated:
       
        return {'user_info': request.user.userprofile}
    return {}