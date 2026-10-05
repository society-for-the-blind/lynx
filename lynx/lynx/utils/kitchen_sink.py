from datetime import date, timezone
import django.utils as du
from functools import reduce

# keep your existing pipe
def pipe(data, *funcs):
    return reduce(lambda acc, f: f(acc), funcs, data)

# use lambdas to bind the second arg y
# result = pipe(x,
#               lambda v: inc(v, y),
#               lambda v: db1(v, y))


# from functools import partial, wraps
# import inspect

# # A minimal partial (Python already has functools.partial)
# def simple_partial(func, /, *p_args, **p_kwargs):
#     return lambda *args, **kwargs: func(*p_args, *args, **{**p_kwargs, **kwargs})

# # A simple curry implementation (works best for plain positional functions,
# # no *args/**kwargs or complex defaults; use as a learning tool)
# def curry(func):
#     sig = inspect.signature(func)
#     pos_kinds = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
#     positional_count = sum(1 for p in sig.parameters.values() if p.kind in pos_kinds)

#     @wraps(func)
#     def _curried(*args, **kwargs):
#         if len(args) + len(kwargs) >= positional_count:
#             return func(*args, **kwargs)
#         return lambda *more_args, **more_kwargs: _curried(*(args + more_args), **{**kwargs, **more_kwargs})
#     return _curried

# # Usage examples with your `pipe`:
# # Using functools.partial to bind the second argument 'y' by keyword
# result = pipe(x,
#               partial(inc, y=y),   # creates a unary function that calls inc(x, y)
#               partial(db1, y=y))   # same for db1

# # Or using lambdas (what you already had)
# result = pipe(x,
#               lambda v: inc(v, y),
#               lambda v: db1(v, y))

# # Or using curry (if you prefer curried functions)
# # Note: curry(inc) => a function where you call inc_curried(a)(b)
# inc_curried = curry(inc)
# result = pipe(x,
#               lambda v: inc_curried(v)(y),
#               lambda v: curry(db1)(v)(y))

def get_grant_year(service_event=None):
    if not service_event or not service_event.date:
        date = du.timezone.now().date()
    else:
        date = service_event.date

    if date.month >= 10:
        return date.year
    else:
        return date.year - 1

def construct_plan_name(service_event=None, service_delivery_type_name=None, default=True):
    grant_year = get_grant_year(service_event)

    if default:
        plan_month_day = "10/01"
    else:
        plan_month_day = du.timezone.now().date().strftime("%m/%d")

    if service_event and service_event.oib_service_delivery_type:
        service_delivery_type_name = getattr(service_event.oib_service_delivery_type, 'oib_service_delivery_type', '')

    return f"{plan_month_day}/{grant_year} - {service_delivery_type_name or ''}"

def timedelta_to_hms(td):
    if not td:
        return None
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

DURATION_CHOICES = [
    ("00:15:00", "15 minutes"),
    ("00:30:00", "30 minutes"),
    ("00:45:00", "45 minutes"),
    ("01:00:00", "1 hour"),
    ("01:15:00", "1 hour 15 minutes"),
    ("01:30:00", "1 hour 30 minutes"),
    ("01:45:00", "1 hour 45 minutes"),
    ("02:00:00", "2 hours"),
    ("02:15:00", "2 hours 15 minutes"),
    ("02:30:00", "2 hours 30 minutes"),
    ("02:45:00", "2 hours 45 minutes"),
    ("03:00:00", "3 hours"),
    ("03:15:00", "3 hours 15 minutes"),
    ("03:30:00", "3 hours 30 minutes"),
    ("03:45:00", "3 hours 45 minutes"),
    ("04:00:00", "4 hours"),
    ("04:15:00", "4 hours 15 minutes"),
    ("04:30:00", "4 hours 30 minutes"),
    ("04:45:00", "4 hours 45 minutes"),
    ("05:00:00", "5 hours"),
    ("05:15:00", "5 hours 15 minutes"),
    ("05:30:00", "5 hours 30 minutes"),
    ("05:45:00", "5 hours 45 minutes"),
    ("06:00:00", "6 hours"),
    ("06:15:00", "6 hours 15 minutes"),
    ("06:30:00", "6 hours 30 minutes"),
    ("06:45:00", "6 hours 45 minutes"),
    ("07:00:00", "7 hours"),
    ("07:15:00", "7 hours 15 minutes"),
    ("07:30:00", "7 hours 30 minutes"),
    ("07:45:00", "7 hours 45 minutes"),
    ("08:00:00", "8 hours"),
]

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