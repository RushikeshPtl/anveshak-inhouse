from .models import Role

def get_user_role(self):
    user = self.request.user
    account_id = user.id
    role_obj = Role.objects.filter(account_id=account_id).first()
    if role_obj is None:
        return 'user'
    elif role_obj.is_admin:
        return 'admin'
    elif role_obj.is_reviewer:
        return 'reviewer'
    elif role_obj.is_content_writer:
        return 'content writer'
    elif role_obj.is_author:
        return 'author'


    
    





    