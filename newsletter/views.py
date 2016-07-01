from django.shortcuts import render

from products.models import ProductFeatured,Product
from .forms import ContactForm,SignUpForm
from .models import SignUp

# Create your views here.
def home(request):
    title = "Sign Up Now"

    featured_image = ProductFeatured.objects.filter(active=True).order_by("?").first()
    products = Product.objects.all().order_by("?")[:6]
    products2 = Product.objects.all().order_by("?")[:6]
    #print request
    #if request.method == "POST":
    #    print request.POST
    form = SignUpForm(request.POST or None)
    context = {
        "title": title,
        "form" : form,
        "featured_image": featured_image,
        "products": products,
        "products2":products2
    }

    if form.is_valid():
        instance = form.save(commit=False)
        full_name = form.cleaned_data.get("full_name")
        if not full_name:
            full_name = "New full name"
        instance.full_name = full_name
        instance.save()
        context = {
            "title" : "Thank You"
        }

    return render(request,'home.html',context)


def contact(request):
    title = "Contact Us"
    form = ContactForm(request.POST or None)
    if form.is_valid():
        for key, value in form.cleaned_data.iteritems():
            print key, value
    context = {
        "form":form,
        "title": title,
    }
    return render(request,"forms.html",context)