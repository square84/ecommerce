from django.core.exceptions import ImproperlyConfigured
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import Http404
from django.utils import timezone
# Create your views here.
from django_filters import FilterSet,CharFilter,NumberFilter

from .forms import VariationInventoryFormSet,ProductFilterForm
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

class ProductFilter(FilterSet):
    title = CharFilter(name='title',lookup_type='icontains',distinct=True)
    category = CharFilter(name='categories__title',lookup_type='icontains',distinct=True)
    category_id = CharFilter(name='categories__id',lookup_type='icontains',distinct=True)
    min_price = NumberFilter(name='variation__price',lookup_type='gte',distinct=True)
    max_price = NumberFilter(name='variation__price',lookup_type='lte',distinct=True)
    class Meta:
        model = Product
        fields = [
            'min_price',
            'max_price',
            'category',
            'title',
            'description',
        ]

def product_list(request):
    qs = Product.objects.all()
    ordering = request.GET.get("ordering")
    if ordering:
        qs = Product.objects.all().order_by(ordering)
    f = ProductFilter(request.GET, queryset=qs)
    return render(request,"products/product_list.html",{"object_list": f })

class FilterMixin(object):
    filter_class = None
    search_ordering_param = "ordering"

    def get_queryset(self,*args,**kwargs):
        try:
            qs = super(FilterMixin,self).get_queryset(*args,**kwargs)
            return qs
        except:
            raise ImproperlyConfigured("You must have a queryset in order to use the FilterMixin")

    def get_context_data(self,*args, **kwargs):
        context = super(FilterMixin,self).get_context_data(*args, **kwargs)
        qs = self.get_queryset()
        ordering = self.request.GET.get(self.search_ordering_param)
        if ordering:
            qs = qs.order_by(ordering)
        filter_class = self.filter_class
        if filter_class:
            f = filter_class(self.request.GET,queryset=qs)
            context["object_list"] = f
        return context



#Lista de Productos
class ProductListView(FilterMixin,ListView):
    model = Product
    queryset = Product.objects.all()
    filter_class = ProductFilter
    #informacion del objeto
    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView,self).get_context_data(*args, **kwargs)
        context["now"] = timezone.now()
        context["query"] = self.request.GET.get("q")
        context["filter_form"] = ProductFilterForm(data=self.request.GET or None)
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