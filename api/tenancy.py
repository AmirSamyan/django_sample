from __future__ import annotations

from dataclasses import dataclass

from django.http import Http404
from merchant.models import Merchant


@dataclass(frozen=True)
class MerchantContext:
    merchant: Merchant


def resolve_merchant(*, request, merchant_id: str) -> Merchant:
    try:
        merchant = Merchant.objects.get(merchant_id=merchant_id, is_active=True, is_approved=True)
    except Merchant.DoesNotExist as e:
        raise Http404("Merchant not found") from e

    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return merchant

    # SUPER_ADMIN can operate across merchants.
    if getattr(user, "role", None) == getattr(user, "Role", None).SUPER_ADMIN:
        return merchant

    if getattr(user, "merchant_id", None) != merchant.id:
        raise Http404("Merchant not found")

    return merchant
