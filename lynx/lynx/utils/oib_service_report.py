from typing import List, Dict
from datetime import date
from django.db import models as ddm
from lynx import models as lm
from . import oib_quarterly_reports as luo

def get_number_of_services(start_date: date, end_date: date) -> List[Dict]:
    """
    Return a list of contacts with their services and counts between `start_date` and `end_date`.

    Each item has: contact_id, client_name, county, service_event_count, services (ordered by count desc)
    Implements the logic of the provided SQL using the Django ORM.
    """
    # rows similar to the CTE `rows` in the SQL
    rows_qs = (
        lm.OIBServiceEventOIBService.objects
        .filter(
            oib_service_event__date__gte=start_date,
            oib_service_event__date__lte=end_date,
        )
        .values(
            'oib_service_event__id',
            'oib_service_event__contacts__id',
            'oib_service_event__contacts__last_name',
            'oib_service_event__contacts__first_name',
            'oib_service_event__date',
            'oib_service__id',
            'oib_service__oib_service',
            'oib_service__long_name',
        )
        .annotate(count=ddm.Count('pk'))
        .order_by('oib_service_event__contacts__last_name', 'oib_service_event__contacts__first_name', '-count')
    )

    # Build intermediate mapping per contact
    contact_map: Dict[int, Dict] = {}
    for row in rows_qs:
        contact_id = row['oib_service_event__contacts__id']
        client_name = f"{row['oib_service_event__contacts__last_name']}, {row['oib_service_event__contacts__first_name']}"
        svc = {
            'id': row['oib_service__id'],
            'service_short': row['oib_service__oib_service'],
            'service_long': row['oib_service__long_name'],
            'count': row['count'],
        }
        entry = contact_map.setdefault(contact_id, {'client_name': client_name, 'services': [], 'event_dates': set(), '_event_ids': set()})
        entry['services'].append(svc)
        entry['event_dates'].add(row['oib_service_event__date'])
        entry['_event_ids'].add(row['oib_service_event__id'])

    # compute service_event_count
    for cid, entry in list(contact_map.items()):
        entry['service_event_count'] = len(entry.pop('_event_ids', set()))

    # latest address county per contact (distinct on contact_id by created desc)
    contact_ids = list(contact_map.keys())
    county_map: Dict[int, str] = {}
    if contact_ids:
        addr_qs = (
            lm.Address.objects
            .filter(contact_id__in=contact_ids)
            .order_by('contact_id', '-created')
            .distinct('contact_id')
            .values('contact_id', 'county')
        )
        for a in addr_qs:
            county_map[a['contact_id']] = a.get('county')

    # SIP contacts (active)
    sip_contact_ids = set(
        lm.ContactProgram.objects.filter(
            contact_id__in=contact_ids,
            program__program='SIP',
            end_date__isnull=True,
        ).values_list('contact_id', flat=True)
    )

    # Assemble final list applying the SIP filter from the SQL: include contact if not SIP OR service_event_count >= 1
    results: List[Dict] = []
    for cid, entry in sorted(contact_map.items(), key=lambda kv: kv[1]['client_name']):
        if cid in sip_contact_ids and entry.get('service_event_count', 0) < 1:
            continue
        results.append({
            'contact_id': cid,
            'client_name': entry['client_name'],
            'county': county_map.get(cid),
            'service_event_count': entry.get('service_event_count', 0),
            'event_dates': sorted(entry.get('event_dates', [])),
            'services': sorted(entry.get('services', []), key=lambda s: -s.get('count', 0)),
        })

    return results
