from input.models import UserRole, RolePermission


class PermMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

    def process_request(self, request):
        roles = UserRole.objects.filter(user=request.user.id).values_list('role_id')
        perms = list(RolePermission.objects.filter(role_id__in=roles).values_list("permission__codename", flat=True))
        request.perm = perms
