from django.shortcuts import redirect
from django.urls import reverse


EXEMPT_PREFIXES = (
    '/admin/',
    '/account_management/id-verification/',
    '/account_management/logout/',
    '/account_management/login/',
    '/account_management/password-reset/',
    '/account_management/reset/',
    '/accounts/',
    '/static/',
    '/media/',
)


class SellerIDVerificationMiddleware:
    """
    Restrict sellers to the ID verification page until their submission
    is approved. Pending and rejected sellers are redirected away from
    all other pages.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if (
            user.is_authenticated
            and not user.is_staff
            and getattr(user, 'user_type', None) == 'S'
        ):
            path = request.path_info
            if not any(path.startswith(prefix) for prefix in EXEMPT_PREFIXES):
                verification = getattr(user, 'id_verification', None)
                if verification is None or verification.status != 'approved':
                    return redirect(reverse('account_management:id_verification'))

        return self.get_response(request)