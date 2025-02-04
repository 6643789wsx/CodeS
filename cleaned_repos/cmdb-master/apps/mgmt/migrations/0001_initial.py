from __future__ import unicode_literals

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0008_alter_user_username_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("name", models.CharField(max_length=10, verbose_name="姓名")),
                (
                    "position",
                    models.CharField(blank=True, max_length=20, verbose_name="职位"),
                ),
            ],
            options={
                "verbose_name": "用户",
                "verbose_name_plural": "用户",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20, verbose_name="部门名")),
                ("level", models.SmallIntegerField(verbose_name="级别")),
                (
                    "create_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mgmt.Department",
                        verbose_name="上级部门",
                    ),
                ),
            ],
            options={
                "verbose_name": "部门",
                "verbose_name_plural": "部门",
            },
        ),
        migrations.CreateModel(
            name="Field",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20, verbose_name="字段名")),
                (
                    "alias",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=20,
                        null=True,
                        verbose_name="别名",
                    ),
                ),
                (
                    "readme",
                    models.TextField(
                        blank=True, default="", null=True, verbose_name="自述"
                    ),
                ),
                (
                    "type",
                    models.SmallIntegerField(
                        choices=[
                            (0, "string"),
                            (1, "integer"),
                            (2, "floating"),
                            (3, "datetime"),
                            (4, "date"),
                            (5, "boolean"),
                            (6, "Ip"),
                        ],
                        verbose_name="字段类型",
                    ),
                ),
                (
                    "is_multi",
                    models.BooleanField(default=False, verbose_name="是否为多值字段"),
                ),
                ("required", models.BooleanField(default=False, verbose_name="是否必填")),
            ],
        ),
        migrations.CreateModel(
            name="Permission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, unique=True, verbose_name="权限名"),
                ),
                ("alias", models.CharField(max_length=100, verbose_name="权限别名")),
            ],
            options={
                "verbose_name": "权限",
                "verbose_name_plural": "权限",
            },
        ),
        migrations.CreateModel(
            name="Table",
            fields=[
                (
                    "name",
                    models.CharField(
                        max_length=20,
                        primary_key=True,
                        serialize=False,
                        verbose_name="表名",
                    ),
                ),
                (
                    "alias",
                    models.CharField(
                        max_length=20, null=True, unique=True, verbose_name="别名"
                    ),
                ),
                ("readme", models.TextField(blank=True, default="", verbose_name="自述")),
                (
                    "creation_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="创建者",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="field",
            name="table",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="fields",
                to="mgmt.Table",
                verbose_name="字段",
            ),
        ),
        migrations.AddField(
            model_name="department",
            name="permissions",
            field=models.ManyToManyField(
                blank=True,
                related_name="departments",
                to="mgmt.Permission",
                verbose_name="所有权限",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="departments",
            field=models.ManyToManyField(
                blank=True,
                related_name="users",
                to="mgmt.Department",
                verbose_name="部门集",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="permissions",
            field=models.ManyToManyField(
                blank=True,
                related_name="users",
                to="mgmt.Permission",
                verbose_name="权限集",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="department",
            unique_together=set([("name", "parent")]),
        ),
    ]
