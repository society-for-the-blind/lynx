from django.db import models as ddm
from datetime import date, datetime, timezone
from collections import OrderedDict
from lynx import models  as lm
from typing import Dict, List, NamedTuple, Optional, TypeAlias, Callable
from lynx.utils import xlsx

class OIBQuarter(NamedTuple):
    quarter_name: str
    grant_year_start: date
    quarter_start: date
    quarter_end: date

OIBQuarters : TypeAlias = Dict[str, OIBQuarter]
OIBClientsWithReportData : TypeAlias = Dict[int, Dict]

LynxOutcome : TypeAlias = str
OIBOutcome  : TypeAlias = str

def grant_year_for_date(as_of: date | None = None) -> int:
    a_date = as_of or date.today()
    if a_date.month >= 10:
        return a_date.year
    else:
        return a_date.year - 1

def get_oib_quarters(grant_year: int) -> OIBQuarters:
    grant_year_start = date(month=10, day=1, year=grant_year)
    return {
        "Q1": OIBQuarter(
            quarter_name="Q1",
            grant_year_start=grant_year_start,
            quarter_start=grant_year_start,
            quarter_end=date(month=12, day=31, year=grant_year),
        ),
        "Q2": OIBQuarter(
            quarter_name="Q2",
            grant_year_start=grant_year_start,
            quarter_start=date(month=1, day=1, year=grant_year + 1),
            quarter_end=date(month=3, day=31, year=grant_year + 1),
        ),
        "Q3": OIBQuarter(
            quarter_name="Q3",
            grant_year_start=grant_year_start,
            quarter_start=date(month=4, day=1, year=grant_year + 1),
            quarter_end=date(month=6, day=30, year=grant_year + 1),
        ),
        "Q4": OIBQuarter(
            quarter_name="Q4",
            grant_year_start=grant_year_start,
            quarter_start=date(month=7, day=1, year=grant_year + 1),
            quarter_end=date(month=9, day=30, year=grant_year + 1),
        ),
    }

def grant_start_date_for_grant_year(grant_year: int) -> date:
    return date(month=10, day=1, year=grant_year)

def get_oib_clients_with_at_least_2_service_events(as_of: date | None = None) -> OIBClientsWithReportData:
    """
    Returns a dict of OIB clients with services and outcomes data who participated in at least two (2) service events since the `as_of` date.

    ```
    Example data structure returned:
    {
        8234: {
            'client_name': 'Doe, John',
            'services': [
                {'id': 7, 'service_short': 'IR', 'service_long': 'Information and Referral', 'count': 1},
                {'id': 2, 'service_short': 'Comm', 'service_long': 'Communication Skills Training', 'count': 1},
                {'id': 0, 'service_short': 'AT', 'service_long': 'Assistive Technology Devices and Services', 'count': 1},
                {'id': 5, 'service_short': 'AC', 'service_long': 'Adjustment Counseling', 'count': 1},
            ],
            'latest_outcomes': {
                'AT Goal Outcome': {'choice': 'Assessed with improved independence', 'created': datetime.datetime(2026, 1, 12, 1, 7, 6, 467315, tzinfo=datetime.timezone.utc)},
                'IL/A Service Goal Outcome': {'choice': 'Assessed with improved independence', 'created': datetime.datetime(2026, 1, 12, 1, 7, 6, 467490, tzinfo=datetime.timezone.utc)},
                'Living Situation Outcome': {'choice': 'Plan complete, feeling more confident in ability to maintain living situation', 'created': datetime.datetime(2026, 1, 12, 1, 7, 6, 466767, tzinfo=datetime.timezone.utc)},
                'Home and Community Involvement Outcome': {'choice': 'Plan complete, feeling more confident in ability to maintain living situation', 'created': datetime.datetime(2026, 1, 12, 1, 7, 6, 466963, tzinfo=datetime.timezone.utc)},
                'Employment Outcome': {'choice': 'Not Interested in Employment', 'created': datetime.datetime(2026, 1, 12, 1, 7, 6, 467141, tzinfo=datetime.timezone.utc)},
            }
    }
    ```
    """
    end = as_of or date.today()
    start = lm.Contact._current_grant_start(end)

    rows = (
        lm.OIBServiceEventOIBService.objects
        .filter(
            oib_service_event__date__gte=start,
            oib_service_event__date__lte=end,
        )
        .values(
            'oib_service_event__id',
            'oib_service_event__contacts__id',
            'oib_service_event__contacts__last_name',
            'oib_service_event__contacts__first_name',
            'oib_service__id',
            'oib_service__oib_service',
            'oib_service__long_name',
        )
        .annotate(count=ddm.Count('pk'))
        .order_by(
            'oib_service_event__contacts__last_name',
            'oib_service_event__contacts__first_name',
            '-count'
        )
    )

    # result: OIBClientsWithReportData = {}
    result = {}
    for row in rows:
        contact_id = row['oib_service_event__contacts__id']
        client_name = f"{row['oib_service_event__contacts__last_name']}, {row['oib_service_event__contacts__first_name']}"
        service_data = {
            'id': row['oib_service__id'],
            'service_short': row['oib_service__oib_service'],
            'service_long': row['oib_service__long_name'],
            'count': row['count']
        }
        report_data = result.setdefault(contact_id, {
            'client_name': client_name,
            'services': [],
            '_event_ids': set(),    # temp set to collect unique event ids
        })
        report_data['services'].append(service_data)
        report_data['_event_ids'].add(row['oib_service_event__id'])
    
    # Convert temporary event id sets to counts and drop clients with <= 1 event
    for cid, entry in list(result.items()):
        entry['service_event_count'] = len(entry.pop('_event_ids', set()))

    # Keep only SIP-program clients who participated in more than one distinct service event;
    # ILP (or other programs) are not filtered by count.
    sip_contact_ids = set(
        lm.ContactProgram.objects.filter(
            contact_id__in=result.keys(),
            program__program="SIP",
            end_date__isnull=True,
        ).values_list('contact_id', flat=True)
    )

    result = {
        cid: entry
        for cid, entry in result.items()
        if cid not in sip_contact_ids or entry.get('service_event_count', 0) > 1
    }

    # Enrich `result` with the latest OIBOutcome per contact (choice text + created timestamp)
    contact_ids = list(result.keys())
    if contact_ids:
        # Get all outcome types so we can return the latest choice per type
        outcome_types = list(lm.OIBOutcomeType.objects.all().values('pk', 'oib_outcome_type'))

        # Build dynamic Subquery annotations: one pair (choice, created) per outcome type
        annotations: dict = {}
        for t in outcome_types:
            tpk = t['pk']
            outcome_sq = (
                lm.OIBOutcome.objects
                .filter(
                    contact=ddm.OuterRef('pk'),
                    oib_outcome_type_choice__oib_outcome_type=tpk,
                )
                .order_by('-created')
            )
            annotations[f'latest_outcome_choice_{tpk}'] = ddm.Subquery(
                outcome_sq.values('oib_outcome_type_choice__oib_outcome_choice__oib_outcome_choice')[:1]
            )
            annotations[f'latest_outcome_created_{tpk}'] = ddm.Subquery(
                outcome_sq.values('created')[:1]
            )

        contacts_qs = (
            lm.Contact.objects
            .filter(pk__in=contact_ids)
            .annotate(**annotations)
            .values('pk', *annotations.keys())
        )

        outcome_map = {}
        for c in contacts_qs:
            pk = c['pk']
            per_type = {}
            for t in outcome_types:
                tpk = t['pk']
                tname = t['oib_outcome_type']
                choice = c.get(f'latest_outcome_choice_{tpk}')
                created = c.get(f'latest_outcome_created_{tpk}')
                per_type[tname] = {'choice': choice, 'created': created}
            outcome_map[pk] = per_type

        default_per_type = {t['oib_outcome_type']: {'choice': None, 'created': None} for t in outcome_types}
        for cid, entry in result.items():
            entry['latest_outcomes'] = outcome_map.get(cid, default_per_type)

    # import pdb; pdb.set_trace()
    return result

def massage_services_and_outcomes(oib_clients: OIBClientsWithReportData):
    """
    Not using `demographics_err_msg_wrapper/5` because there is only a strict subset of values that need to be validated, whereas the captured demogratphics data and its structure can be wildly different than to what the OIB reports expect.

    Example data structure before massaging:
    ```
    (Pdb) result.get(8234).get('services')
    [{'id': 7, 'service_short': 'IR', 'service_long': 'Information and Referral', 'count': 1},
    {'id': 2, 'service_short': 'Comm', 'service_long': 'Communication Skills Training', 'count': 1},
    {'id': 0, 'service_short': 'AT', 'service_long': 'Assistive Technology Devices and Services', 'count': 1},
    {'id': 5, 'service_short': 'AC', 'service_long': 'Adjustment Counseling', 'count': 1}]
    (Pdb) result.get(8234).get('latest_outcomes')
    {'AT Goal Outcome': {'choice': 'Assessed with improved independence', 'created': datetime.datetime(2026, 1, 12, 1, 7, 6, 467315, tzinfo=datetime.timezone.utc)},
    'IL/A Service Goal Outcome': {'choice': 'Assessed with improved independence', 'created': datetime.datetime(2026, 1, 12, 1, 7, 6, 467490, tzinfo=datetime.timezone.utc)},
    'Living Situation Outcome': {'choice': 'Plan complete, feeling more confident in ability to maintain living situation', 'created': datetime.datetime(2026, 1, 12, 1, 7, 6, 466767, tzinfo=datetime.timezone.utc)},
    'Home and Community Involvement Outcome': {'choice': 'Plan complete, feeling more confident in ability to maintain living situation', 'created': datetime.datetime(2026, 1, 12, 1, 7, 6, 466963, tzinfo=datetime.timezone.utc)},
    'Employment Outcome': {'choice': 'Not Interested in Employment', 'created': datetime.datetime(2026, 1, 12, 1, 7, 6, 467141, tzinfo=datetime.timezone.utc)}}
    ```
    """

    for _cid, entry in oib_clients.items():
        new_services_outcomes_with_defaults = {
            "service_AT": "No",
            "outcome_AT": "|oib_outcome_error|NOT SET",
            "service_OM": "No",
            "service_communication": "No",
            "service_DLS": "No",
            "service_advocacy": "No",
            "service_counseling": "No",
            "service_IR": "No",
            "service_other": "No",
            "outcome_ILA": "|oib_outcome_error|NOT SET",
            "service_supportive": "No",
            # This is fixed; SFTB clients are always assessed.
            "case_status": "Assessed",
            "outcome_living_situation": "|oib_outcome_error|NOT SET",
            "outcome_home_community": "|oib_outcome_error|NOT SET",
            "outcome_employment": "|oib_outcome_error|NOT SET",
        }
        services = entry.get('services', [])

        for service_entry in services:
            service_short = service_entry.get('service_short')
            count = service_entry.get('count', 0)
            if service_short == 'AT':
                new_services_outcomes_with_defaults['service_AT'] = "Yes"
                if count >= 1:
                    new_services_outcomes_with_defaults['outcome_AT'] = "Yes"
            elif service_short == 'O&M':
                new_services_outcomes_with_defaults['service_OM'] = "Yes"
            elif service_short == 'Comm':
                new_services_outcomes_with_defaults['service_communication'] = "Yes"
            elif service_short == 'DLS':
                new_services_outcomes_with_defaults['service_DLS'] = "Yes"
            elif service_short == 'Advocacy':
                new_services_outcomes_with_defaults['service_advocacy'] = "Yes"
            elif service_short == 'AC':
                new_services_outcomes_with_defaults['service_counseling'] = "Yes"
            elif service_short == 'IR':
                new_services_outcomes_with_defaults['service_IR'] = "Yes"
            elif service_short == 'other IL/A':
                new_services_outcomes_with_defaults['service_other'] = "Yes"
            elif service_short == 'SS':
                new_services_outcomes_with_defaults['service_supportive'] = "Yes"

        latest_outcomes = entry.get('latest_outcomes', {})

        def get_validated_outcome(outcome_name: str, choice_map: Dict[LynxOutcome, OIBOutcome]) -> str:
            accepted_values = list(choice_map.values())
            lynx_outcome = latest_outcomes.get(outcome_name, {}).get('choice')
            outcome = choice_map.get(lynx_outcome)
            return oib_value_checker(accepted_values, outcome) if outcome else f"|oib_outcome_error|NOT SET"

        # TODO 2026_01_19_1119: These choice maps should be configuratble from the admin page
        choice_map_1 = {
            # "Not assessed": "Not Assessed",
            "Assessed with improved independence": "Assessed with Increased Independence",
            "Assessed and maintained independence": "Assessed and Maintained Independence",
            "Assessed with decreased independence": "Assessed with Decreased Independence",
        } 
        at_goal_outcome = get_validated_outcome('AT Goal Outcome', choice_map_1)
        new_services_outcomes_with_defaults['outcome_AT'] = at_goal_outcome

        ila_service_goal_outcome = get_validated_outcome('IL/A Service Goal Outcome', choice_map_1)
        new_services_outcomes_with_defaults['outcome_ILA'] = ila_service_goal_outcome

        choice_map_2 = {
            # "Plan not complete": "Plan Incomplete-Not Assessed",
            "Plan complete, feeling more confident in ability to maintain living situation": "Plan Completed - Reported feeling more confident in ability to maintain living situation",
            "Plan complete, no difference in ability to maintain living situation": "Plan Completed - Reported no difference in ability to maintain living situation",
            "Plan complete, feeling less confident in ability to maintain living situation": "Plan Completed - Reported feeling less confident in ability to maintain living situation",
        }
        living_situation_outcome = get_validated_outcome('Living Situation Outcome', choice_map_2)
        new_services_outcomes_with_defaults['outcome_living_situation'] = living_situation_outcome

        choice_map_3 = {
            # "Plan not complete": "Plan Incomplete-Not Assessed",
            "Plan complete, feeling more confident in ability to maintain living situation":"Plan Completed - Reported an increased ability to engage in customary activities ",
            "Plan complete, no difference in ability to maintain living situation":"Plan Completed - Reported no difference in ability to engage in customary activities ",
            "Plan complete, feeling less confident in ability to maintain living situation": "Plan Completed - Reported a decreased ability to engage in customary activities",
        }
        home_community_involvement_outcome = get_validated_outcome('Home and Community Involvement Outcome', choice_map_3)
        new_services_outcomes_with_defaults['outcome_home_community'] = home_community_involvement_outcome

        choice_map_4 = {
            "Not Interested in Employment": "Not Interested in Employment",
            "Less Likely to Seek Employment": "Less Likely to Seek Employment",
            "Unsure about Seeking Employment": "Unsure about Seeking Employment",
            "More Likely to Seek Employment": "More Likely to Seek Employment",
        }
        employment_outcome = get_validated_outcome('Employment Outcome', choice_map_4)
        new_services_outcomes_with_defaults['outcome_employment'] = employment_outcome

        entry.update(new_services_outcomes_with_defaults)

    return oib_clients

def attach_demographics(oib_clients: OIBClientsWithReportData, oib_quarter: OIBQuarter) -> OIBClientsWithReportData:
    """
    Attach demographic fields (age_group, case_open_date, gender) to each
    client entry in `oib_clients`.

    `gender` is normalized into one of three values: 'Female', 'Male', or
    'Did Not Self-Identify'. This groups various freeform or non-binary
    choices into a single non-identifying bucket.
    """
    # Attach latest Intake.age_group for each client (if available).
    # Use a single query to fetch the most recent intake per contact (Postgres DISTINCT ON).
    contact_ids = set(oib_clients.keys())
    if contact_ids:
        addr_qs = lm.Address.objects.filter(contact=ddm.OuterRef('contact')).order_by('-created')
        latest_intakes_with_address = (
            lm.Intake.objects
            .filter(contact_id__in=contact_ids)
            # ASIDE: The new "bulk_notes" implementation does not allow birth_date to be null;
            #        when adding a new client and intake without setting birth_date, the field
            #        is auto-set to the current date. If client was set for an OIB program (ILP,
            #        SIP, etc.), it will be unset as none of the age requirements are met.
            # BUT: the date of birth still can be None if someone deliberately removes the DOB
            #      values... Nonetheless, the client should still be shown, but with a validation
            #      error.
            # .exclude(birth_date__isnull=True)
            .order_by('contact_id', '-intake_date')
            .distinct('contact_id')
            .annotate(county=ddm.Subquery(addr_qs.values('county')[:1]))
        )
        query_map = {intake.contact_id: intake for intake in latest_intakes_with_address}
    else:
        query_map = {}

    new_oib_clients = massage_services_and_outcomes(oib_clients)

    for cid, entry in new_oib_clients.items():
        query = query_map.get(cid)

        entry['age_group'] = demographics_err_msg_wrapper(query, ['age_group'], lambda one_item_list, _y: one_item_list[0], "MISSING INTAKE", "MISSING AGE GROUP")
        
        gcod = lambda list_with_intake_date, _prop_error: _get_case_open_date(list_with_intake_date, oib_quarter.grant_year_start)
        entry['case_open_date'] = demographics_err_msg_wrapper(query, ['intake_date'], gcod, "MISSING INTAKE", "MISSING INTAKE DATE")

        entry['gender'] = demographics_err_msg_wrapper(query, ['gender'], _normalize_gender, "MISSING INTAKE", "MISSING GENDER")
        entry['race'] = demographics_err_msg_wrapper(query, ['ethnicity'], _normalize_race, "MISSING INTAKE", "MISSING RACE (nee ETHNICITY)")
        entry['ethnicity'] = demographics_err_msg_wrapper(query, ['other_ethnicity'], _normalize_ethnicity, "MISSING INTAKE", "MISSING ETHNICITY(nee OTHER_ETHNICITY)")
        entry['degree_of_visual_impairment'] = demographics_err_msg_wrapper(query, ['degree'], _normalize_degree_of_visual_impairment, "MISSING INTAKE", "MISSING DEGREE OF VISUAL IMPAIRMENT")
        entry['major_cause_of_visual_impairment'] = demographics_err_msg_wrapper(query, ['eye_condition', 'secondary_eye_condition'], _normalize_major_cause_of_visual_impairment, "MISSING INTAKE", "MISSING MAJOR CAUSE OF VISUAL IMPAIRMENT")
        entry['hearing_loss'] = demographics_err_msg_wrapper(query, ['hearing_loss', 'hearing_loss_notes'], _normalize_bool, "MISSING INTAKE", "MISSING IMPAIRMENT INFO")
        entry['mobility_impairment'] = demographics_err_msg_wrapper(query, ['mobility', 'mobility_notes'], _normalize_bool, "MISSING INTAKE", "MISSING IMPAIRMENT INFO")
        entry['communication_impairment'] = demographics_err_msg_wrapper(query, ['communication', 'communication_notes'], _normalize_bool, "MISSING INTAKE", "MISSING IMPAIRMENT INFO")
        entry['cognitive_impairment'] = demographics_err_msg_wrapper(query, ['stroke', 'stroke_notes', 'alzheimers', 'alzheimers_notes', 'memory_loss', 'memory_loss_notes', 'learning_disability', 'learning_disability_notes'], _normalize_bool, "MISSING INTAKE", "MISSING IMPAIRMENT INFO")
        entry['mental_health_impairment'] = demographics_err_msg_wrapper(query, ['mental_health'], _normalize_bool, "MISSING INTAKE", "MISSING IMPAIRMENT INFO")
        entry['other_impairments'] = demographics_err_msg_wrapper(query, ['diabetes', 'diabetes_notes', 'dialysis', 'dialysis_notes', 'seizure', 'seizure_notes', 'heart', 'heart_notes', 'arthritis', 'arthritis_notes', 'high_bp', 'high_bp_notes', 'neuropathy', 'neuropathy_notes', 'dexterity', 'dexterity_notes', 'migraine', 'migraine_notes', 'pain', 'pain_notes', 'asthma', 'asthma_notes', 'cancer', 'cancer_notes', 'musculoskeletal', 'musculoskeletal', 'musculoskeletal_notes', 'geriatric', 'geriatric_notes', 'allergies', 'other_medical', 'medical_notes'], _normalize_bool, "MISSING INTAKE", "MISSING IMPAIRMENT INFO")
        entry['residence_type'] = demographics_err_msg_wrapper(query, ['residence_type'], _normalize_residence_type, "MISSING INTAKE", "MISSING RESIDENCE INFO")
        entry['referral_source'] = demographics_err_msg_wrapper(query, ['referred_by'], _normalize_referral_source, "MISSING INTAKE", "MISSING REFERRAL SOURCE INFO")
        entry['residence_county'] = demographics_err_msg_wrapper(query, ['county'], _normalize_residence_county, "MISSING INTAKE", "MISSING ADDRESS COUNTY INFO")
        entry['vision_screening'] = demographics_err_msg_wrapper(query, ['mental_health'], _normalize_bool, "MISSING INTAKE", "MISSING IMPAIRMENT INFO")
        entry['vision_treatment'] = demographics_err_msg_wrapper(query, ['mental_health'], _normalize_bool, "MISSING INTAKE", "MISSING IMPAIRMENT INFO")

    # Return an OrderedDict sorted by the client's display name.
    return OrderedDict(sorted(new_oib_clients.items(), key=lambda kv: kv[1]['client_name']))

def oib_clients_with_report_data(oib_quarter: OIBQuarter) -> OIBClientsWithReportData:
    oib_clients = get_oib_clients_with_at_least_2_service_events(as_of=oib_quarter.quarter_end)
    attach_demographics(oib_clients, oib_quarter)
    return oib_clients

def split_oib_clients_by_report(oib_clients: OIBClientsWithReportData) -> Dict[str, OIBClientsWithReportData]:
    # Split OIB clients into separate reports by age group.
    oib_report_to_age_group = { 
        "18-24": "YIB",
        "25-34": "YIB",
        "35-44": "YIB",
        "45-54": "YIB",
        "55-64": "7OB",
        "65-74": "7OB",
        "75-84": "7OB",
        "85 and older": "7OB",
     }
    clients_by_oib_report_age_groups: Dict[str, List[str]] = {}
    for client_id, client_info in oib_clients.items():
        age_group = client_info.get('age_group')
        report_age_group = oib_report_to_age_group.get(age_group)
        if report_age_group:
            clients_by_oib_report_age_groups.setdefault(report_age_group, {})[client_id] = client_info

    return clients_by_oib_report_age_groups

# Think of this as matrix transposition: from rows of clients to columns of client attributes.
def transpose_report_data(ordered_oib_clients: OIBClientsWithReportData) -> List:
    _client_id, a_client_info = next(iter(ordered_oib_clients.items()))
    report_data_columns = list(a_client_info.keys())
    
    # Initialize a list for each column
    column_data = {key: [] for key in report_data_columns}
    
    for _client_id, client_info in ordered_oib_clients.items():
        for key in report_data_columns:
            value = client_info.get(key, '')
            column_data[key].append(value)
    
    # Return the column_data dictionary
    return column_data

# Example usage:
# ==============
# import lynx.utils.oib_quarterly_reports as luo; q1 = luo.get_oib_quarters(luo.grant_year_for_date()).get("Q1");
# { k: id for k, id in cs.items() if id.get('age_group') == '45-54' }
# sob = luo.split_oib_clients_by_report(csd)
# names, age_groups = luo.transpose_report_data(sob.get("7OB"))
# import lynx.utils.xlsx as x;  wbaf_7ob = x.load_xlsx_to_memory(template_7ob); print(*x.get_sheets(wbaf_7ob), sep="\n");
# _ = x.write_column( wba_files=wbaf_7ob, sheet_rid="rId4", start_cell=x.Cell(column='A', row=17), values=names)
# _ = x.write_column( wba_files=wbaf_7ob, sheet_rid="rId4", start_cell=x.Cell(column='C', row=17), values=age_groups)
# x.write_memory_to_xlsx(wbaf_7ob, "/tmp/aaa.xlsx")
def write_report(oib_quarter: OIBQuarter):
    report_templates = {
        "YIB": "sftb/xlsx_templates/YIB_Report_Data_Collection_Tool_2025_v2.xlsx",
        "7OB": "sftb/xlsx_templates/7-OB_Report_Data_Collection_Tool_2025_v2.xlsx",
    }
    report_sheet_rids = {
        "demographics": "rId4",
        "services": "rId5",
    }
    csd = oib_clients_with_report_data(oib_quarter)
    sob = split_oib_clients_by_report(csd)
    for report_type, clients in sob.items():
        wbaf = xlsx.load_xlsx_to_memory(report_templates[report_type])
        column_data = transpose_report_data(clients)

        demographics_columns = {
            'A': 'client_name',
            'B': 'case_open_date',
            'C': 'age_group',
            'D': 'gender',
            'E': 'race',
            'F': 'ethnicity',
            'G': 'degree_of_visual_impairment',
            'H': 'major_cause_of_visual_impairment',
            'I': 'hearing_loss',
            'J': 'mobility_impairment',
            'K': 'communication_impairment',
            'L': 'cognitive_impairment',
            'M': 'mental_health_impairment',
            'N': 'other_impairments',
            'O': 'residence_type',
            'P': 'referral_source',
            'Q': 'residence_county',
        }
        for col, key in demographics_columns.items():
            if key not in column_data:
                raise ValueError(f"Missing expected column data for key '{key}' in report type '{report_type}'.")
            xlsx.write_column(
                wba_files=wbaf,
                sheet_rid=report_sheet_rids["demographics"],
                start_cell=xlsx.Cell(column=col, row=17),
                values=column_data[key]
            )

        services_columns = {
            'B': 'vision_screening',
            'C': 'vision_treatment',
            'D': 'service_AT',
            'E': 'outcome_AT',
          # 'F': auto-calculated by Excel formula
            'G': 'service_OM',
            'H': 'service_communication',
            'I': 'service_DLS',
            'J': 'service_advocacy',
            'K': 'service_counseling',
            'L': 'service_IR',
            'M': 'service_other',
            'N': 'outcome_ILA',
            'O': 'service_supportive',
            'P': 'case_status',
            'Q': 'outcome_living_situation',
            'R': 'outcome_home_community',
            'S': 'outcome_employment',
        }
        for col, key in services_columns.items():
            if key not in column_data:
                raise ValueError(f"Missing expected column data for key '{key}' in report type '{report_type}'.")
            xlsx.write_column(
                wba_files=wbaf,
                sheet_rid=report_sheet_rids["services"],
                start_cell=xlsx.Cell(column=col, row=7),
                values=column_data[key]
            )

        xlsx.force_recalc_on_open(wbaf)

        timestamp = datetime.now(timezone.utc).strftime("%Y_%m_%d_%H%M%S")
        output_path = f"/tmp/OIB_Report_{oib_quarter.quarter_name}_{timestamp}_{report_type}.xlsx"
        xlsx.write_memory_to_xlsx(wbaf, output_path)

# import lynx.utils.oib_quarterly_reports as luo; q1 = luo.get_oib_quarters(luo.grant_year_for_date()).get("Q1"); luo.write_report(q1)

def demographics_err_msg_wrapper(query, fields: List[str], f: Callable[..., str], model_err: str, prop_err: str) -> str:
    """
    Helper for/within `attach_demographics/2` to coerce legacy, non-standard, etc. LYNX Intake data into values accepted by the OIB reports.
    
    + `f` is a normalization function
    """
    # TODO: Color any cells light red in the resulting workbook that has the string "|lynx_error|"
    error = "|lynx_DB_error|";
    if not query:
        return error + model_err

    for field in fields:
        if not hasattr(query, field):
            raise ValueError(f"DEV ERROR: input query does not have field '{field}'")

    model_lookups = [getattr(query, field, None) for field in fields]
    return f(model_lookups, f"{error}{prop_err}")

def oib_value_checker(accepted_values: List[str], value: str) -> str:
    error = "|oib_value_error|";
    if value not in accepted_values:
        return f"{error}{value}"
    return value

def _get_case_open_date(one_item_list, grant_year_start):
    intake_date = one_item_list[0]
    if intake_date < grant_year_start:
        return "Case open prior to Oct. 1"
    else:
        return "Case open between Oct. 1 - Sept. 30"

# Always returns a string (i.e., 'Did Not Self-Identify' if input is None or unrecognized)
def _normalize_gender(one_item_list: List[any], _prop_error: str) -> str:
    db_value = one_item_list[0]
    interim_value = ""
    # Handle None or empty values safely before calling string methods
    if db_value is None:
        interim_value = "Did Not Self-Identify"
    else:
        g = str(db_value).strip().lower()
        if not g:
            interim_value = "Did Not Self-Identify"
        elif g == 'female':
            interim_value = 'Female'
        elif g == 'male':
            interim_value = 'Male'
        else:
            interim_value = 'Did Not Self-Identify'

    return oib_value_checker(['Female', 'Male', 'Did Not Self-Identify'], interim_value)

# What the OIB report calls "race" is called "etnicity" by LYNX...
def _normalize_race(one_item_list: List[any], prop_error: str) -> str:
    db_value = one_item_list[0]
    interim_value = ""
    if not db_value:
        interim_value = prop_error
    elif db_value == "Two or More Races":
        interim_value = "2 or More Races"
    else:
        interim_value = db_value

    return oib_value_checker([
        "American Indian or Alaska Native",
        "Asian",
        "Black or African American",
        "Native Hawaiian or Pacific Islander",
        "White",
        "Did not self identify Race",
        "2 or More Races",
    ], interim_value)

# What the OIB report calls "ethnicity" is called "other_etnicity" by LYNX...
def _normalize_ethnicity(one_item_list: List[any], _prop_error: str) -> str:
    db_value = one_item_list[0]
    interim_value = ""
    if db_value == "Hispanic or Latino":
        interim_value = "Yes"
    else:
        interim_value = "No"

    return oib_value_checker(['Yes', 'No'], interim_value)

def _normalize_degree_of_visual_impairment(one_item_list: List[any], prop_error: str) -> str:
    db_value = one_item_list[0]
    interim_value = ""
    if not db_value:
        interim_value = prop_error
    elif db_value == "Low Vision":
        interim_value = "Legally Blind"
    elif db_value == "Totally Blind (NP or NLP)":
        interim_value = "Totally Blind"
    else:
        interim_value = db_value

    return oib_value_checker([
        'Totally Blind',
        'Legally Blind',
        'Severe Vision Impairment',
    ], interim_value)

def _normalize_major_cause_of_visual_impairment(model_lookups: List[any], prop_error: str) -> str:
    db_value = model_lookups.pop(0)
    interim_value = ""
    if not db_value:
        if len(model_lookups) == 0:
            interim_value = prop_error
        else:
            interim_value = _normalize_major_cause_of_visual_impairment(model_lookups, prop_error)
    elif db_value == "Other causes of visual impairment":
        interim_value = "Other causes"
    elif db_value == "Other":
        interim_value = "Other causes"
    elif db_value == "Uveitis":
        interim_value = "Other causes"
    elif db_value == "Retinopathy of Prematurity(ROP)":
        interim_value = "Other causes"
    else:
        interim_value = db_value

    return oib_value_checker([
        "Macular Degeneration",
        "Diabetic Retinopathy",
        "Glaucoma",
        "Cataracts",
        "Other causes"
    ], interim_value)

def _normalize_bool(model_lookups: List[any], prop_error: str) -> str:
    interim_value = ""
    if any(model_lookups):
        interim_value = "Yes"
    else:
        interim_value = "No"

    return oib_value_checker(['Yes', 'No'], interim_value)

def _normalize_residence_type(one_item_list: List[any], prop_error: str) -> str:
    db_value = one_item_list[0]
    interim_value = ""
    if not db_value:
        interim_value = prop_error
    elif db_value == "Skilled Nursing Care":
        interim_value = "Nursing Home"
    else:
        interim_value = db_value

    return oib_value_checker([
        "Private Residence",
        "Senior Independent Living",
        "Assisted Living Facility",
        "Nursing Home",
        "Homeless"
    ], interim_value)

def _normalize_referral_source(one_item_list: List[any], prop_error: str) -> str:
    db_value = one_item_list[0]
    interim_value = ""
    if not db_value:
        interim_value = prop_error
    elif db_value == "DOR":
        interim_value = "State VR Agency"
    else:
        interim_value = db_value

    return oib_value_checker([
        "Eye Care Provider",
        "Physician/ Medical Provider",
        "State VR Agency",
        "Social Service",
        "Veterans Administration",
        "Senior Program",
        "Assisted Living Facility",
        "Nursing Home",
        "Independent Living Center",
        "Family or Friend",
        "Self-Referral",
        "Other",
    ], interim_value)

def _normalize_residence_county(one_item_list: List[any], prop_error: str) -> str:
    db_value = one_item_list[0]
    interim_value = ""
    if not db_value:
        interim_value = prop_error
    else:
        interim_value = db_value

    return oib_value_checker([
        "Alameda", "Alpine", "Amador", "Butte", "Calaveras", "Colusa", "Contra Costa", "Del Norte", "El Dorado", "Fresno", "Glenn", "Humboldt", "Imperial", "Inyo", "Kern", "Kings", "Lake", "Lassen", "Los Angeles", "Madera", "Marin", "Mariposa", "Mendocino", "Merced", "Modoc", "Mono", "Monterey", "Napa", "Nevada", "Orange", "Placer", "Plumas", "Riverside", "Sacramento", "San Benito", "San Bernardino", "San Diego", "San Francisco", "San Joaquin", "San Luis Obispo", "San Mateo", "Santa Barbara", "Santa Clara", "Santa Cruz", "Shasta", "Sierra", "Siskiyou", "Solano", "Sonoma", "Stanislaus", "Sutter", "Tehama", "Trinity", "Tulare", "Tuolumne", "Ventura", "Yolo", "Yuba", 
    ], interim_value)