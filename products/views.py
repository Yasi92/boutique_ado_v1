from audioop import reverse
from email import message
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category
from django.contrib import messages

from .forms import ProductForm

# Create your views here.


def all_products(request):
    '''A view to show all products, including sorting and search queries '''
    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction =None

    if request.GET:

        if 'sort' in request.GET:
            sortkey = request.GET['sort'] # Create the sortkey variable
            # Make a copy of it and call it sort, which we'll use later to construct current_sorting = f'{sort}_{direction}'
            sort = sortkey
            if sortkey == 'name': # If the field we want to sort on is 'name'...
                 # Let's actually sort (i.e. order_by) on one called 'lower_name', in order to ensure it doesn't order Z before a just because the Z is uppercase
                sortkey = 'lower_name'
                # Annotate all the products w/ a new field, lower_name=Lower('name') and sort based on it
                products = products.annotate(lower_name = Lower('name'))
            

            if sortkey == 'category':
                sortkey = 'category__name'


            if 'direction' in request.GET:
                direction = request.GET['direction']

                # by default the sorting is asc
                if direction == 'desc':
                    sortkey = f'-{sortkey}'

            products = products.order_by(sortkey)


        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)



        if 'q' in request.GET:
            # if the field is blank
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(description__icontains= query)
            products = products.filter(queries)

    # Now we still have sort = 'name' to construct current_sorting later
    # but we've sorted on a different field called lower_name
    current_sorting = f'{sort}_{direction}'

    context = {
        'products' : products,
        'search_term' : query,
        'current_categories' : categories,
        'current_sorting' :current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    '''A view to show individual product details '''
    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product' : product,
    }

    return render(request, 'products/product_detail.html', context)


def add_product(request):
    """ Add a product to the store """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('add_product'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)