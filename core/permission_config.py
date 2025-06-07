from product.models import Product

PERMISSION_CONFIG = {
    "customer":{
        Product:["view"],
        # order:[]
    },
    "seller":{
        Product:["view","add","change","delete"],
        # order:[]
    }
}