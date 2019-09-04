from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
import random

from products.models import Product, Category, ProductImage


def products(request):
    # Get all products from the DB using the Product model
    products = Product.objects.all()  # <YOUR CODE HERE>

    # Get up to 4 `featured=true` Products to be displayed on top
    featured_products = Product.objects.filter(featured=True)  # <YOUR CODE HERE>
    featured_product = random.sample(set(featured_products), 4)
    return render(
        request,
        'products.html',
        context={'products': products, 'featured_products': featured_product}
    )


def create_product(request):
    # Get all categories from the DB
    categories = Category.objects.all()  # <YOUR CODE HERE>
    if request.method == 'GET':
        # Render 'create_product.html' template sending categories as context
        #return render(request, 'static_form.html')  # static_form is just used as an example
        return render(request, 'create_product.html', context={
            'categories': categories
        })
    elif request.method == 'POST':
        # Validate that all fields below are given in request.POST dictionary,
        # and that they don't have empty values.

        # If any errors, build an errors dictionary with the following format
        # and render 'create_product.html' sending errors and categories as context

        # errors = {'name': 'This field is required.'}


        fields = ['name', 'sku', 'price']
        errors = {}
        # <YOUR CODE HERE>
        for field in fields:
            value = request.POST.get(field)
            if not value:
                errors[field] = 'This field is required.'

        if errors:
            return render(request, 'create_product.html', context={
                'errors': errors,
                'categories': categories
            })

        # If no errors so far, validate each field one by one and use the same
        # errors dictionary created above in case that any validation fails

        # name validation: can't be longer that 100 characters
        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name can't be longer than 100 characters."

        # SKU validation: it must contain 8 alphanumeric characters
        # <YOUR CODE HERE>
        sku = request.POST.get('sku')
        if len(sku) < 8 or not sku.isalnum():
            errors['sku'] = "Must contain 8 alphanumeric characters."

        # Price validation: positive float lower than 10000.00
        # <YOUR CODE HERE>
        price = request.POST.get('price')
        price = float(int(price))
        if price < 0.0 or price > 10000.0:
            errors['price'] = "Price should be between 0 and 10000."

        # if any errors so far, render 'create_product.html' sending errors and
        # categories as context
        # <YOUR CODE HERE>
        if errors:
            return render(request, 'create_product.html', context={
                'errors': errors,
                'categories': categories
            })

        # If execution reaches this point, there aren't any errors.
        # Get category from DB based on category name given in payload.
        # Create product with data given in payload and proper category
        category = Category.objects.get(name=request.POST.get('category'))  # <YOUR CODE HERE>
        product = Product.objects.create(
            name=name,
            sku=sku,
            category=category,
            price=price,
            description=request.POST.get('description')
        )  # <YOUR CODE HERE>

        # Up to three images URLs can come in payload with keys 'image-1', 'image-2', etc.
        # For each one, create a ProductImage object with proper URL and product
        # <YOUR CODE HERE>

        image = []
        image.append(request.POST.get('image_1'))
        image.append(request.POST.get('image_2'))
        image.append(request.POST.get('image_3'))

        for i in image:
            if i:
                ProductImage.objects.create(
                    product=product,
                    url=i
                )

        # Redirect to 'products' view
        return redirect('products')


def edit_product(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)  # <YOUR CODE HERE>

    # Get all categories from the DB
    categories = Category.objects.all()  # <YOUR CODE HERE>
    if request.method == 'GET':
        # Render 'edit_product.html' template sending product, categories and
        # a 'images' list containing all product images URLs.

        # images = ['http://image/1', 'http://image/2', ...]
        #return render(request, 'static_form.html')  # static_form is just used as an example
        image = ProductImage.objects.filter(product=product)

        images = []
        for i in image:
            images.append(i.url)

        return render(request, 'edit_product.html', context={
            'product': product,
            'categories': categories,
            'images': images
        })

    elif request.method == 'POST':
        # Validate following fields that come in request.POST in the very same
        # way that you've done it in create_product view
        fields = ['name', 'sku', 'price']
        errors = {}
        # <YOUR CODE HERE>
        image = ProductImage.objects.filter(product=product)
        images = []
        for i in image:
            images.append(i.url)

        for field in fields:
            value = request.POST.get(field)
            if not value:
                errors[field] = "This field is required."

        if errors:
            return render(request, 'edit_product.html', context={
                'product': product,
                'categories': categories,
                'errors': errors,
                'images': images
            })

        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name can't be longer than 100 characters."

        sku = request.POST.get('sku')
        if len(sku) < 8 or not sku.isalnum():
            errors['sku'] = "Must contain 8 alphanumeric characters."

        price = request.POST.get('price')
        fprice = float(price)

        if fprice < 0 or fprice > 10000:
            errors['price'] = "Price should be between 0 and 10000."

        if errors:
            return render(request, 'edit_product.html', context={
                'product': product,
                'categories': categories,
                'errors': errors,
                'images': images
            })

        # If execution reaches this point, there aren't any errors.
        # Update product name, sku, price and description from the data that
        # come in request.POST dictionary.
        # Consider that ALL data is given as string, so you might format it
        # properly in some cases.
        product.name = name  # <YOUR CODE HERE>
        product.sku = sku
        product.price = price
        product.description = request.POST.get('description')
        # Get proper category from the DB based on the category name given in
        # payload. Update product category.
        category = Category.objects.get(name=request.POST.get('category'))  # <YOUR CODE HERE>
        product.category = category
        product.save()

        # For updating the product images URLs, there are a couple of things that
        # you must consider:
        # 1) Create a ProductImage object for each URL that came in payload and
        #    is not already created for this product.
        # 2) Delete all ProductImage objects for URLs that are created but didn't
        #    come in payload
        # 3) Keep all ProductImage objects that are created and also came in payload
        # <YOUR CODE HERE>
        images = []
        images.append(request.POST.get('image-1'))
        images.append(request.POST.get('image-2'))
        images.append(request.POST.get('image-3'))

        for i in images:
            if i:
                ProductImage.objects.create(product=product, url=i)

        # ProductImage.objects.filter(product=product).delete()
        existimages = ProductImage.objects.filter(product=product)
        for i in existimages:
            if i.url not in images:
                ProductImage.objects.filter(url=i.url).delete()

        # Redirect to 'products' view
        return redirect('products')


def delete_product(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)  # <YOUR CODE HERE>
    if request.method == 'GET':
        # render 'delete_product.html' sending product as context
        return render(request, 'delete_product.html', context={'product': product})  # <YOUR CODE HERE>
    elif request.method == "POST":
        # Delete product and redirect to 'products' view
        product.delete()
        return redirect('products')  # <YOUR CODE HERE>


def toggle_featured(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)  # <YOUR CODE HERE>

    # Toggle product featured flag
    # <YOUR CODE HERE>
    if product.featured:
        product.featured = False
    else:
        product.featured = True
    product.save()
    # Redirect to 'products' view
    return redirect('products')
