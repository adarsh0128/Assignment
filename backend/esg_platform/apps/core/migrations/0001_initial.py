import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]
    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True)),
                ("slug", models.SlugField(max_length=120, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("username", models.CharField(error_messages={"unique": "A user with that username already exists."}, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.", max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name="username")),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active.", verbose_name="active")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("role", models.CharField(choices=[("admin", "Admin"), ("analyst", "Analyst"), ("auditor", "Auditor")], default="analyst", max_length=20)),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="users", to="core.organization")),
            ],
            options={"abstract": False},
            managers=[("objects", django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(
            name="Facility",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("country", models.CharField(max_length=2)),
                ("city", models.CharField(max_length=120)),
                ("external_id", models.CharField(blank=True, max_length=80)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="facilities", to="core.organization")),
            ],
        ),
        migrations.CreateModel(
            name="PlantMapping",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("plant_code", models.CharField(max_length=30)),
                ("source_system", models.CharField(default="SAP", max_length=40)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("facility", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="plant_mappings", to="core.facility")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="plant_mappings", to="core.organization")),
            ],
        ),
        migrations.AddIndex(model_name="user", index=models.Index(fields=["organization", "role"], name="user_org_role_idx")),
        migrations.AddIndex(model_name="facility", index=models.Index(fields=["organization", "name"], name="facility_org_name_idx")),
        migrations.AddIndex(model_name="plantmapping", index=models.Index(fields=["organization", "plant_code"], name="plant_org_code_idx")),
        migrations.AddConstraint(model_name="facility", constraint=models.UniqueConstraint(fields=("organization", "name", "city"), name="facility_org_name_city_uniq")),
        migrations.AddConstraint(model_name="plantmapping", constraint=models.UniqueConstraint(fields=("organization", "plant_code"), name="plant_mapping_org_code_uniq")),
    ]
