from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

from datetime import datetime

class Region(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=30)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.name

class Icon(models.Model):
    ftype_choices=(
        ('arial', 'arial'),
        ('arial-unicode-ms', 'arial-unicode-ms'),
        ('times-new-roman','times-new-roman'),
    )

    id = models.AutoField(primary_key=True)
    part_no = models.CharField(max_length=20, default='xxxxxxxx')
    font_type = models.CharField(max_length=20, choices=ftype_choices, default='arial-unicode-ms')
    font_size = models.IntegerField(default=16)
    name = models.CharField(max_length=50, default='test')
    description = models.CharField(max_length=100, null=True, blank=True)

    # region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)

    cert_unit = models.CharField(max_length=20, default='test')
    # path = models.CharField(max_length=100, default='media/LOGO/')
    img_path = models.ImageField(upload_to='Icons', null=True)

    creator = models.CharField(max_length=20, null=True, blank=True)

    created = models.DateTimeField(auto_now=True)
    # updated_at = models.DateTimeField(auto_now=True)

    var_num = models.IntegerField(
        default=0,
        validators=[MaxValueValidator(3), MinValueValidator(0)]
    )
    coo_point_1 = models.CharField(max_length=20, null=True, blank=True)
    coo_point_2 = models.CharField(max_length=20, null=True, blank=True)
    coo_point_3 = models.CharField(max_length=20, null=True, blank=True)
    coo_point_1_var = models.CharField(max_length=20, null=True, blank=True)
    coo_point_2_var = models.CharField(max_length=20, null=True, blank=True)
    coo_point_3_var = models.CharField(max_length=20, null=True, blank=True)
    def __str__(self):
        return self.name

class Warning(models.Model):

    ftype_choices=(
        ('arial', 'arial'),
        ('arial-unicode-ms', 'arial-unicode-ms'),
        ('times-new-roman','times-new-roman'),
    )

    part_no = models.CharField(max_length=20, default='xxxxxxxx')
    font_type = models.CharField(max_length=20, choices=ftype_choices, default='arial-unicode-ms')
    font_size = models.IntegerField(default=16)
    name = models.CharField(max_length=50, default='test')
    description = models.CharField(max_length=100, null=True, blank=True)

    # region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)

    cert_unit = models.CharField(max_length=20, null=True, blank=True)
    # path = models.CharField(max_length=100, default='media/TEXT/')
    img_path = models.ImageField(upload_to='Warnings', null=True)

    creator = models.CharField(max_length=20, null=True, blank=True)

    created = models.DateTimeField(auto_now=True)
    # updated_at = models.DateTimeField(auto_now=True)

    var_num = models.IntegerField(
        default=0,
        validators=[MaxValueValidator(3), MinValueValidator(0)]
    )
    coo_point_1 = models.CharField(max_length=20, null=True, blank=True)
    coo_point_2 = models.CharField(max_length=20, null=True, blank=True)
    coo_point_3 = models.CharField(max_length=20, null=True, blank=True)
    coo_point_1_var = models.CharField(max_length=20, null=True, blank=True)
    coo_point_2_var = models.CharField(max_length=20, null=True, blank=True)
    coo_point_3_var = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name

class LabelSize(models.Model):
    category = models.CharField(max_length=10)
    img_path = models.ImageField(upload_to='LabelSizes', null=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.category

class CompanyLogo(models.Model):
    name = models.CharField(max_length=30)
    img_path = models.ImageField(upload_to='CompanyLogos', null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class MadeIn(models.Model):
    name = models.CharField(max_length=30)
    code_name = models.CharField(max_length=10, null=True, blank=True)
    img_path = models.ImageField(upload_to='MadeIns', null=True)
    created = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class Label(models.Model):
    part_no = models.CharField(max_length=30, default='xxxxxxxx')
    madein = models.ForeignKey(MadeIn, on_delete=models.SET_NULL, null=True, blank=True)
    project_name = models.CharField(max_length=30, null=True, blank=True)
    # server = models.BooleanField(default=True)
    label_size = models.ForeignKey(LabelSize, on_delete=models.CASCADE, null=True)
    creator = models.CharField(max_length=30, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.part_no

class Area(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    part_no = models.ForeignKey(Label, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(CompanyLogo, on_delete=models.SET_NULL, null=True, blank=True)
    rule_model_name = models.CharField(max_length=50, null=True, blank=True)
    madein_show = models.BooleanField(default=False)
    server = models.BooleanField()
    power_rating_1 = models.TextField(max_length=100, null=True, blank=True)
    power_rating_2 = models.CharField(max_length=100, null=True, blank=True)
    china_only = models.BooleanField(default=False)
    icons = models.ManyToManyField(Icon, null=True, blank=True)
    warnings = models.ManyToManyField(Warning, null=True, blank=True)
    model_name = models.CharField(max_length=50, null=True, blank=True)
    part_no_show = models.BooleanField(default=False)
    madein_code_show = models.BooleanField(default=False)
    area_coor = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return self.name
