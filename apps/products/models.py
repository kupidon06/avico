from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from decimal import Decimal

class Media(models.Model):
    """Modèle permettant d'attacher différents médias à plusieurs types d'objets."""
    IMAGE = 'image'
    VIDEO = 'video'
    DOCUMENT = 'document'

    MEDIA_TYPES = [
        (IMAGE, 'Image'),
        (VIDEO, 'Vidéo'),
        (DOCUMENT, 'Document'),
    ]

    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default=IMAGE)
    file = models.FileField(upload_to="uploads/media/")

    # Configuration pour lier ce modèle à n'importe quel autre modèle
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.media_type} - {self.file.name}"

class Category(models.Model):
    """Catégories de produits (exemple : Volaille, Grains, Oeufs)."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    medias = GenericRelation(Media)  # Ajout de la relation avec Media

    def __str__(self):
        return self.name

class Product(models.Model):
    """Produit générique avec des unités et des remises."""
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    medias = GenericRelation(Media)  # Ajout de la relation avec Media

    def __str__(self):
        return self.name

class Discount(models.Model):
    """Remises pouvant être appliquées aux unités de produit."""
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Pourcentage de réduction (ex: 10 pour 10%)")

    def apply_discount(self, price):
        """Calcule le prix après application de la remise."""
        return price * (1 - self.percentage / Decimal(100))

    def __str__(self):
        return f"{self.name} - {self.percentage}%"

class ProductUnit(models.Model):
    """Unités de vente pour un produit, chacune avec un prix spécifique."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="units")

    name = models.CharField(max_length=100, help_text="Ex: Petit casier, Grand sac")

    quantity = models.PositiveIntegerField(help_text="Quantité par unité (ex: 10 œufs)")

    # Utilisation de DecimalField pour éviter les erreurs d'arrondi
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix de cette unité")

    description = models.TextField(blank=True)

    # Remises applicables
    discounts = models.ManyToManyField(Discount, blank=True)

    # Ajout de la relation avec Media
    medias = GenericRelation(Media, related_query_name="product_units")

    def apply_discounts(self):
        """Applique toutes les remises et retourne le prix final."""
        discounted_price = Decimal(self.price)
        for discount in self.discounts.all():
            discounted_price = discount.apply_discount(discounted_price)
        return discounted_price.quantize(Decimal("0.01"))  # Arrondi à 2 décimales

    def __str__(self):
        return f"{self.name} ({self.quantity}) - {self.price} €"
