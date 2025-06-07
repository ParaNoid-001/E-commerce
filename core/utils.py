from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from core.permission_config import PERMISSION_CONFIG

def assign_permission(user,role):
    role_permission = PERMISSION_CONFIG.get(role,{})
    for model, permissions in role_permission.items():
        content_type = ContentType.objects.get_for_model(model)
        for perm_codename in permissions:
            permission = Permission.objects.get(content_type=content_type, 
                                                codename=f"{perm_codename}_{model._meta.model_name}")
            user.user_permissions.add(permission)
            