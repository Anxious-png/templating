from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import *
from .forms import *
from plotly.offline import plot
import plotly.graph_objs as go
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView
from django.urls import reverse_lazy

# Create your views here.
    

           
               

def homepage(request):
    branches = Branch.objects.all()
    produce_stock = {}

    # Fetching stock data for each produce in each branch
    for produce in Produce.objects.all():
        branch_stock = []
        for branch in branches:
            # Assuming you have a relationship between Branch and Produce for stock quantity
            stock = produce.stock_set.filter(branch=branch).first()
            stock_amount = stock.quantity if stock else 0
            branch_stock.append({'branch': branch, 'quantity': stock_amount})
        

        produce_stock[produce] = branch_stock
    print(produce_stock)

    return render(request, 'home/index.html', {
        'branches': branches,
        'produce_stock': produce_stock,
    })

def receipt(request):
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

def addsales(request):
    return render(request, 'home/addsales.html')

def allsales(request):
    sales = Sale.objects.all().order_by('-id')
    return render(request, 'home/allsales.html', {'sales': sales})

def procurement_list(request):

    procurements = Procurement.objects.all()
    return render(request, 'home/procurement.html', {'procurements': procurements})

def procurement_create(request):
    if request.method == 'POST':
        form = ProcurementForm(request.POST)
        if form.is_valid():
            procurement = form.save(commit=False)
            procurement.recorded_by = request.user.userprofile
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

def addstock(request,pk):
    issued_item = Stock.objects.get(id=pk)
    form = UpdateStockForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            added_quantity = int(request.POST['received_quantity'])
            issued_item.tonnage_kgs += added_quantity
            issued_item.save()
            #to add to the remaining stock quantity is increasing
            print(added_quantity)
            print(issued_item.tonnage_kgs)
            return redirect('allstock')
    return render(request, 'home/addstock.html', {'form': form })

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
def credit_detail(request, pk):
 credit_sale = get_object_or_404(CreditSale, pk=pk)
 return render(request, 'home/credit_detail.html', {'credit_sale': credit_sale})

def credit_list(request):
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
def manager(request):
    branches = Branch.objects.all()
    produce_stock = {}

    # Fetching stock data for each produce in each branch
    for produce in Produce.objects.all():
        branch_stock = []
        for branch in branches:
            # Assuming you have a relationship between Branch and Produce for stock quantity
            stock = produce.stock_set.filter(branch=branch).first()
            stock_amount = stock.quantity if stock else 0
            branch_stock.append({'branch': branch, 'quantity': stock_amount})
        

        produce_stock[produce] = branch_stock
    print(produce_stock)

    return render(request, 'home/dashboard.html', {
        'branches': branches,
        'produce_stock': produce_stock,
    })

    
def salesagent(request):
    return render(request, 'home/dashboard2.html')
# views.py

def owner(request):
    # Total Sales and Tonnage
    total_sales = Sale.objects.aggregate(total=Sum('amount_paid_ugx'))['total'] or 0
    total_tonnage = Sale.objects.aggregate(total=Sum('quantity'))['total'] or 0
    total_credit = CreditSale.objects.aggregate(total=Sum('amount_due_ugx'))['total'] or 0
    available_stock = Stock.objects.aggregate(total=Sum('tonnage_kgs'))['total'] or 0

    # Monthly Sales Data
    monthly_sales = (
        Sale.objects
        .values('date__month')
        .annotate(total=Sum('amount_paid_ugx'))
        .order_by('date__month')
    )
    months = [f"Month {item['date__month']}" for item in monthly_sales]
    sales_totals = [item['total'] for item in monthly_sales]

    # Branch-wise Sales Data
    branch_sales = (
        Sale.objects
        .values('branch')
        .annotate(total=Sum('amount_paid_ugx'))
        .order_by('branch')
    )
    branches = [item['branch'] for item in branch_sales]
    branch_totals = [item['total'] for item in branch_sales]

    # Generate Monthly Sales Bar Chart
    sales_bar = go.Bar(x=months, y=sales_totals, marker_color='blue')
    sales_fig = go.Figure(data=[sales_bar])
    sales_fig.update_layout(title='Monthly Sales (UGX)', xaxis_title='Month', yaxis_title='Sales')
    sales_chart = plot(sales_fig, output_type='div')

    # Generate Branch-wise Sales Pie Chart
    branch_pie = go.Pie(labels=branches, values=branch_totals)
    branch_fig = go.Figure(data=[branch_pie])
    branch_fig.update_layout(title='Sales by Branch')
    branch_chart = plot(branch_fig, output_type='div')

    context = {
        'total_sales': total_sales,
        'total_tonnage': total_tonnage,
        'total_credit': total_credit,
        'available_stock': available_stock,
        'sales_chart': sales_chart,
        'branch_chart': branch_chart,
    }
    return render(request, 'home/dashboard3.html', context)



class StockDeleteView(DeleteView):
    model = Stock
    template_name = 'home/stock_confirm_delete.html'
    success_url = reverse_lazy('allstock')