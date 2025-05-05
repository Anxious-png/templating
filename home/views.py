from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import *
from .forms import *
from plotly.offline import plot
import plotly.graph_objs as go
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from .models import BRANCH_CHOICES

# Create your views here.
    

           
               

def homepage(request):
    products = Produce.objects.all()
    return render(request, 'home/index.html', {'products': products})
    

def receipt(request):
    if request.user.is_manager or request.user.is_salesagent:
        sales = Sale.objects.filter(branch=request.user.branch)
    else:
        sales = sales.objects.all()
    sales = Sale.objects.all().order_by('-id')
    print(f"Number of sales found: {sales.count()}")
    return render(request, 'home/receipt.html', {'sales': sales})
def receipt_detail(request, receipt_id):
    #getting all registered stock in our data base
     try:
        receipt = Sale.objects.get(id=receipt_id)
        return render(request, 'home/receipt_detail.html',{'receipt': receipt})
     except Sale.DoesNotExist:
        messages.error(request, "Receipt not found!")
        return redirect('receipt')

def addsales(request, pk):
    issued_sale = get_object_or_404(Sale, id=pk)

    if request.method == 'POST':
        salesform = SaleForm(request.POST)
        if salesform.is_valid():
            quantity_sold = salesform.cleaned_data['quantity']
            
            if quantity_sold > issued_sale.quantity:
                salesform.add_error('quantity', 'Not enough stock available.')
            else:
                new_sale = salesform.save(commit=False)
                new_sale.produce = issued_sale.produce
                new_sale.price = issued_sale.produce.price_per_kg
                new_sale.save()
                
                issued_sale.quantity -= quantity_sold
                issued_sale.save()

                return redirect('receipt')
    else:
        salesform = SaleForm()

    return render(request, 'home/addsales.html', {'issued_sale': issued_sale, 'salesform': salesform})
def allsales(request):
    if request.user.is_manager or request.user.is_salesagent:
        sales = Sale.objects.filter(branch=request.user.branch)
    else:
        sales = Sale.objects.all().order_by('-id')
    return render(request, 'home/allsales.html', {'sales': sales})
def sale_detail(request, sale_id):
    
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'home/sale_detail.html', {'sale': sale})


def procurement_list(request):
    if request.user.is_manager or request.user.is_salesagent:
        procurements = Procurement.objects.filter(branch=request.user.branch)
    else:

        procurements = Procurement.objects.all()
    return render(request, 'home/procurement.html', {'procurements': procurements})

def procure(request):

    procurements = Procurement.objects.all()
    return render(request, 'home/procure.html', {'procurements': procurements})


def procurement_create(request):
    if request.method == 'POST':
        form = ProcurementForm(request.POST)
        if form.is_valid():
            procurement = form.save(commit=False)
            procurement.recorded_by = request.user
            procurement.save()
            return redirect('procurement_list')
    else:
        form = ProcurementForm()
    return render(request, 'home/procurement_form.html', {'form': form})

def procurement_edit(request, pk):
    procurement = get_object_or_404(Procurement, pk=pk)
    if request.method == 'POST':
        form = ProcurementForm(request.POST, instance=procurement)
        if form.is_valid():
            form.save()
            return redirect('procurement_list')
    else:
        form = ProcurementForm(instance=procurement)
    return render(request, 'home/procurement_form.html', {'form': form})

def procurement_delete(request, pk):
    procurement = get_object_or_404(Procurement, pk=pk)
    if request.method == 'POST':
        procurement.delete()
        return redirect('procurement_list')
    return render(request, 'home/procurement_confirm_delete.html', {'procurement': procurement})

    

def allstock(request):
    if request.user.is_manager or request.user.is_salesagent:
     stock = Stock.objects.filter(branch=request.user.branch)
    else:
     stock = Stock.objects.all()
    return render(request, 'home/allstock.html', {'stock': stock})

def stock_detail(request, stock_id):
    # Fetch the stock item based on stock_id
    stock = Stock.objects.get(id=stock_id)
    stock = get_object_or_404(Stock, id=stock_id)
    return render(request, 'home/stock_detail.html', {'stock': stock})

def issue_item(request, pk):
    issued_stock = Stock.objects.get(id=pk)
    salesform = SaleForm(request.POST)
    if request.method =='POST':
        if salesform.is_valid():
            new_sale = salesform.save(commit=False)
            new_sale.produce = issued_stock.produce
            new_sale.price = issued_stock.produce.price_per_kg
            new_sale.save()
            quantity_sold = salesform.cleaned_data['quantity']
            issued_stock.tonnage_kgs -= quantity_sold
            issued_stock.save()

            print("issued Produce:", issued_stock.produce)
            print("Quantity Sold:", quantity_sold)
            print("Remaining Stock:", issued_stock.tonnage_kgs)
            return redirect('receipt')
    return render(request, 'home/issue_item.html', {'issued_stock': issued_stock, 'salesform': salesform})

def addstock(request, pk):
    issued_item = Stock.objects.get(id=pk)

    if request.method == 'POST':
        form = UpdateStockForm(request.POST)
        if form.is_valid():
            added_quantity = int(request.POST.get('received_quantity'))  # Get the received quantity
            issued_item.tonnage_kgs += added_quantity  # Add to tonnage
            issued_item.save()  # Save the changes
            return redirect('allstock')  # Redirect to a page that shows all stock
    else:
        form = UpdateStockForm(instance=issued_item)  # Initialize the form with the existing data

    return render(request, 'home/addstock.html', {'form': form})



def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  
            if user.is_owner:
                return redirect('/dashboard3')
            elif user.is_salesagent:
                return redirect('/dashboard2')
            elif user.is_manager:
                return redirect('/dashboard')
            else:
                return redirect('/dashboard')  # optional fallback
        else:
            # Invalid login
            form = AuthenticationForm()
            return render(request, 'home/login.html', {
                'form': form,
                'title': 'Login',
                'error': 'Invalid username or password'
            })

    else:
        form = AuthenticationForm()
        

        return render(request, 'home/login.html', {'form': form, 'title': 'Login'})



        #checking if the user is manager
        
def signup(request):
    if request.method == 'POST':
        form = UserCreation(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            return redirect('/login')
        else:
            return render(request, 'home/signup.html', {'form': form})
    else:
        form = UserCreation()
        return render(request, 'home/signup.html', {'form': form})
    

def dashboard(request):
    return render(request, 'home/dashboard.html')

def creditsale(request):
    
    credits = CreditSale.objects.all()
    return render(request, 'home/creditsale.html', {'credits': credits})
def credit_detail(request, credit_id):
    credit_sale = get_object_or_404(CreditSale, id=credit_id)
    payments = credit_sale.payments.all()

    if request.method == 'POST':
        form = CreditPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.credit_sale = credit_sale
            payment.received_by = request.user # Ensure you're using custom profile
            payment.save()
            return redirect('credit_detail', credit_id=credit_id)
    else:
        form = CreditPaymentForm()

    context = {
        'credit_sale': credit_sale,
        'payments': payments,
        'form': form,
    }
    return render(request, 'home/credit_detail.html', context)

def credit_list(request):
    if request.user.is_manager or request.user.is_salesagent:
      credits = CreditSale.objects.filter(branch=request.user.branch)
    else:
      credits = CreditSale.objects.all()
    return render(request, 'home/credit_list.html',{'credits': credits})

def add_credit_sale(request):
    if request.method == 'POST':
        form = CreditSaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('credit_list')  # Redirect to the list of credit sales
    else:
        form = CreditSaleForm()
    return render(request, 'home/add_credit_sale.html', {'form': form})
@login_required
def manager(request):
    user = request.user
    
    if not user.is_manager:
        return redirect('some_permission_denied_page')  # optional

    branch = user.branch  # Branch assigned to manager
    produce_list = Produce.objects.all()
    branch_stock = []

    for produce in produce_list:
        stock = Stock.objects.filter(produce=produce, branch=branch).first()
        stock_quantity = stock.quantity if stock else 0
        branch_stock.append({
            'produce': produce,
            'quantity': stock_quantity,
            'branch': branch,
        })

    return render(request, 'home/dashboard.html', {
        'branch_stock': branch_stock,
        'branch': branch,
    })
    
        

    
def salesagent(request):
    stock = Stock.objects.first()  
    return render(request, 'home/dashboard2.html' , {'stock': stock})
# views.py

def owner(request):
    # Total Sales and Tonnage
    total_sales = Sale.objects.aggregate(total=Sum('amount_paid_ugx'))['total'] or 0
    total_tonnage = Sale.objects.aggregate(total=Sum('quantity'))['total'] or 0
    total_credit = CreditSale.objects.aggregate(total=Sum('amount_due_ugx'))['total'] or 0
    available_stock = Stock.objects.aggregate(total=Sum('tonnage_kgs'))['total'] or 0
    stock = Stock.objects.all().order_by('-last_updated')[:3]
    context = {
        'total_sales': total_sales,
        'total_tonnage': total_tonnage,
        'total_credit': total_credit,
        'available_stock': available_stock,
        'stock': stock
    }
    return render(request, 'home/dashboard3.html', context)



class StockDeleteView(DeleteView):
    model = Stock
    template_name = 'home/stock_confirm_delete.html'
    success_url = reverse_lazy('allstock')


def custom_logout(request):
    logout(request)
    return render(request,'home/logout.html')

def reports(request):
    stock_summary = (
    Stock.objects
    .values('branch', 'produce__name')
    .annotate(total_quantity=Sum('quantity'), total_tonnage=Sum('tonnage_kgs'))
)
    sales_summary = (
    Sale.objects
    .values('branch', 'produce__name')
    .annotate(
        total_quantity_sold=Sum('quantity'),
        total_revenue=Sum('amount_paid_ugx'),
        sales_count=Count('id')
    )
)
    credit_summary = CreditSale.objects.values(
    'branch', 'produce__name', 'buyer_name', 'amount_due_ugx', 'is_paid', 'due_date'
)
    context = {
        'stock_summary': stock_summary,
        'sales_summary': sales_summary,
        'credit_summary': credit_summary,
    }
    return render(request, 'home/reports.html', context)
    

def allsales(request):
    sales = Sale.objects.all()
    return render(request, 'home/allsales.html', {'sales': sales})


def stock_edit(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = UpdateStockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            return redirect('allstock')
    else:
        form = UpdateStockForm(instance=stock)
    return render(request, 'home/addstock.html', {'form': form})
    
    

    