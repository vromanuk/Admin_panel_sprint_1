from members.models import Membership


def is_admin(user) -> bool:
    if getattr(user, "membership", None):
        return user.membership.role == Membership.Roles.MOVIES_ADMIN
    return True


def is_view_only(user) -> bool:
    if getattr(user, "membership", None):
        return user.membership.role == Membership.Roles.MOVIES_VIEW
    return True


def is_security_officer(user) -> bool:
    if getattr(user, "membership", None):
        return user.membership.role == Membership.Roles.SECURITY_OFFICER
    return True
