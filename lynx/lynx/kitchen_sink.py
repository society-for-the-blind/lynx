from datetime import date
from . import models as lm

def program_age_violations(contact, proposed_birth_date):
    """
    Module-level helper returning a list of dicts for active memberships that
    would violate program age bounds for the given proposed_birth_date.
    Keys: program (program code), requirements (string), age_on_start (int),
    contactprogram_id (int).
    """
    violations = []
    if not proposed_birth_date or not contact:
        return violations

    active_memberships = contact.contactprogram_set.filter(end_date__isnull=True).select_related('program')
    # compute current age from proposed_birth_date (use today's date)
    today = date.today()
    current_age = today.year - proposed_birth_date.year - (
        (today.month, today.day) < (proposed_birth_date.month, proposed_birth_date.day)
    )

    for cp in active_memberships:
        p = cp.program
        # interpret -1 as unbounded
        min_ok = (p.min_age == -1) or (current_age >= p.min_age)
        max_ok = (p.max_age == -1) or (current_age <= p.max_age)
        if not (min_ok and max_ok):
            bounds = []
            if p.min_age != -1:
                bounds.append(f">= {p.min_age}")
            if p.max_age != -1:
                bounds.append(f"<= {p.max_age}")
            violations.append({
                'program': p.program,
                'requirements': " & ".join(bounds) or "No bounds",
                'age_on_start': current_age,
                'contactprogram_id': cp.pk,
            })
    return violations