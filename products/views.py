from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import Http404
from django.utils import timezone
# Create your views here.
from .forms import VariationInventoryFormSet
from .mixins import StaffRequiredMixin,LoginRequiredMixin
from .models import Product,Variation,Category


#Vistas basadas en clases


class CategoryListView(ListView):
    model = Category
    queryset = Category.objects.all()
    template_name = "products/product_list.html"

class CategoryDetailView(DetailView):
    model = Category

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetailView,self).get_context_data(*args, **kwargs)
        obj = self.get_object()
        product_set = obj.product_set.all()
        default_products = obj.default_category.all()
        products = (product_set | default_products).distinct()
        context["products"] = products
        return context

#Vista para el inventario
#Se agrega el mixin Staff que esta en mixins.py
class VariationListView(StaffRequiredMixin,ListView):
    model = Variation
    queryset = Variation.objects.all()

    #informacion del objeto
    def get_context_data(self, *args, **kwargs):
        context = super(VariationListView,self).get_context_data(*args, **kwargs)
        #Nos traemos el formset hecho en forms.py
        context["formset"] = VariationInventoryFormSet(queryset=self.get_queryset())
    #    print context
        return context

    #hacemos el queryset para filtar solo por el producto seleccionado en products
    def get_queryset(self,*args, **kwargs):
        product_pk = self.kwargs.get("pk")
        if product_pk:
            product = get_object_or_404(Product, pk = product_pk)
            queryset = Variation.objects.filter(product=product)
        return queryset

    #Funcion que se ejectuta al darle update al inventario
    def post(self,request,*args, **kwargs):
        #Nos traemos el formset
        formset = VariationInventoryFormSet(request.POST,request.FILES)
        print request.POST
        #validamos
        if formset.is_valid():
            formset.save(commit=False)
            #Recorremos los formset ya que son varios
            for form in formset:

                new_item = form.save(commit=False)
                #if new_item.title:
                product_pk = self.kwargs.get("pk")
                product = get_object_or_404(Product, pk=product_pk)
                new_item.product = product
                new_item.save()

            messages.success(request,"Your inventory and pricing has been updated")
            return redirect("products")
        return Http404

#Lista de Productos
class ProductListView(ListView):
    model = Product
    queryset = Product.objects.all()

    #informacion del objeto
    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView,self).get_context_data(*args, **kwargs)
        context["now"] = timezone.now()
        context["query"] = self.request.GET.get("q")
        print context
        return context

    def get_queryset(self,*args, **kwargs):
        qs = super(ProductListView,self).get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        if query:
            qs = self.model.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
            #Para que no marque error con el precio
            try:
                qs2 = self.model.objects.filter(
                    Q(price=query)
                )
                #Evalua una u otra, usa distinct para que no ponga doble
                qs = (qs | qs2).distinct()
            except:
                pass
        return qs

#Detalle del Producto

import random
class ProductDetailView(DetailView):
    #Seleccionamos el modelo
    model = Product
    #template_name = "<appname>/<modelname>_detail.html"

    #Recuerda context_data es para poner mas context, aqui nos traemos el get_related del Manager
    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView,self).get_context_data(*args, **kwargs)
        #instance trae el objecto con self.get_object
        instance = self.get_object()
        # get_related fue creado en el Manager
        context["related"] = sorted(Product.objects.get_related(instance)[:6],key= lambda x : random.random())
        print context["related"]
        return context


def product_detail_view_func(request,id):
    #Buscamos el producto
    #product_instance = Product.objects.get(id=id)

    #para un error 404
    product_instance = get_object_or_404(Product,id=id)

    #Es lo mismo que user get_object_or_404
    try:
        product_instance = Product.objects.get(id=id)
    except Product.DoesNotExist:
        raise Http404
    except:
        raise Http404

    #Nombre del template
    template = "products/product_detail.html"
    context = {
        "object": product_instance
    }

    return render (request,template,context)