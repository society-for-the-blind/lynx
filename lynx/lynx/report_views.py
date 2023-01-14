import csv
import logging

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render

from .forms import BillingReportForm, SipDemographicReportForm, SipCSFReportForm, VolunteerReportForm, Volunteer
from .support_functions import (get_fiscal_year, boolean_transform, dictfetchall, plan_evaluation, assess_evaluation,
                                is_assessed)

logger = logging.getLogger(__name__)


@login_required
def billing_report(request):
    form = BillingReportForm()
    if request.method == 'POST':
        form = BillingReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            month = data.get('month')
            year = data.get('year')

            if month == 'all':
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT CONCAT(c.first_name, ' ', c.last_name) as name, sa.agency as service_area, 
                                        auth.authorization_type, auth.authorization_number, auth.id as authorization_id,
                                        ln.billed_units, auth.billing_rate, CONCAT(oa.first_name, ' ', oa.last_name, 
                                        ' - ', oa.company) as outside_agency
                                        FROM lynx_authorization as auth
                                        LEFT JOIN lynx_contact as c on c.id = auth.contact_id
                                        LEFT JOIN lynx_lessonnote as ln  on ln.authorization_id = auth.id
                                        LEFT JOIN lynx_intakeservicearea as sa on auth.intake_service_area_id = sa.id
                                        LEFT JOIN lynx_contact as oa on auth.outside_agency_id = oa.id
                                        where extract(year FROM date) = '%s'
                                        order by c.last_name, c.first_name, sa.agency;""" % (year,))
                    auth_set = dictfetchall(cursor)
            else:
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT CONCAT(c.first_name, ' ', c.last_name) as name, sa.agency as service_area, 
                                        auth.authorization_type, auth.authorization_number, auth.id as authorization_id,
                                        ln.billed_units, auth.billing_rate, CONCAT(oa.first_name, ' ', oa.last_name, 
                                        ' - ', oa.company) as outside_agency
                                        FROM lynx_authorization as auth
                                        LEFT JOIN lynx_contact as c on c.id = auth.contact_id
                                        LEFT JOIN lynx_lessonnote as ln  on ln.authorization_id = auth.id
                                        LEFT JOIN lynx_intakeservicearea as sa on auth.intake_service_area_id = sa.id
                                        LEFT JOIN lynx_contact as oa on auth.outside_agency_id = oa.id
                                        where extract(month FROM date) = '%s' and extract(year FROM date) = '%s'
                                        order by c.last_name, c.first_name, sa.agency;""" % (month, year))
                    auth_set = dictfetchall(cursor)

            reports = {}
            total_amount = 0
            total_hours = 0
            for report in auth_set:
                authorization_number = report['authorization_id']
                if report['billing_rate'] is None:
                    report['billing_rate'] = 0
                billing_rate = float(report['billing_rate'])
                if authorization_number in reports.keys():
                    if report['authorization_type'] == 'Hours':
                        if report['billed_units'] and report['billed_units'] is not None and \
                                reports[authorization_number]['billed_time']:
                            reports[authorization_number]['billed_time'] = (float(report['billed_units']) / 4) + float(
                                reports[authorization_number]['billed_time'])
                            loop_amount = billing_rate * (float(report['billed_units']) / 4)
                            reports[authorization_number]['amount'] = (
                                    billing_rate * float(reports[authorization_number]['billed_time']))
                        elif report['billed_units']:
                            reports[authorization_number]['billed_time'] = float(report['billed_units']) / 4
                            loop_amount = billing_rate * (float(report['billed_units']) / 4)
                            reports[authorization_number]['amount'] = billing_rate * float(
                                reports[authorization_number]['billed_time'])
                    if report['authorization_type'] == 'Classes':
                        if report['billed_units'] and reports[authorization_number]['billed_time']:
                            reports[authorization_number]['billed_time'] = 1 + float(
                                reports[authorization_number]['billed_time'])
                            reports[authorization_number]['amount'] = billing_rate + reports[authorization_number][
                                'amount']
                            loop_amount = billing_rate
                        elif report['billed_units']:
                            reports[authorization_number]['billed_time'] = 1
                            reports[authorization_number]['amount'] = loop_amount = billing_rate
                    # total_amount += loop_amount
                else:
                    service_area = report['service_area']
                    authorization_type = report['authorization_type']
                    outside_agency = report['outside_agency']
                    client = report['name']
                    billed_units = report['billed_units']
                    if billed_units is None:
                        billed_units = 0
                    rate = str(billing_rate)

                    billed_time = 0
                    if report['authorization_type'] == 'Hours':
                        billed_time = float(billed_units) / 4
                        amount = billing_rate * float(billed_time)
                    elif report['authorization_type'] == 'Classes':
                        if billed_units:
                            amount = billing_rate
                            billed_time = 1
                        else:
                            amount = 0
                            billed_time = 0
                    else:
                        amount = 0

                    # total_amount += amount
                    auth = {'service_area': service_area, 'authorization_number': report['authorization_number'],
                            'authorization_type': authorization_type, 'outside_agency': outside_agency, 'rate': rate,
                            'client': client, 'billed_time': billed_time, 'amount': amount}
                    reports[authorization_number] = auth

            filename = "Core Lynx Excel Billing - " + month + " - " + year
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'

            writer = csv.writer(response)
            writer.writerow(
                ['Client', 'Service Area', 'Authorization', 'Authorization Type', 'Billed Time', 'Billing Rate',
                 'Amount', 'Payment Source'])

            for key, value in reports.items():
                in_hours = '0'
                if value['billed_time']:
                    in_hours = float(value['billed_time'])
                    total_hours += in_hours
                if value['amount']:
                    total_amount += value['amount']

                writer.writerow([value['client'], value['service_area'], value['authorization_number'],
                                 value['authorization_type'], in_hours, value['rate'], value['amount'],
                                 value['outside_agency']])

            writer.writerow(['', '', '', '', total_hours, '', '$' + str(total_amount), ''])

            return response

    return render(request, 'lynx/billing_report.html', {'form': form})


@login_required
def sip_demographic_report(request):
    form = SipDemographicReportForm()
    if request.method == 'POST':
        form = SipDemographicReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            month = data.get('month')
            year = data.get('year')

            fiscal_months = ['10', '11', '12', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            fiscal_year = get_fiscal_year(year)

            first = True
            month_string = ''
            for month_no in fiscal_months:
                if month_no == month:
                    break
                else:
                    if first:
                        month_string = """SELECT client.id FROM lynx_sipnote AS sip 
                        LEFT JOIN lynx_contact AS client ON client.id = sip.contact_id 
                        WHERE fiscal_year  = '%s' and (extract(month FROM sip.note_date) = %s""" % (
                            fiscal_year, month_no)
                        first = False
                    else:
                        month_string = month_string + ' or extract(month FROM sip.note_date) = ' + month_no

            if len(month_string) > 0:
                month_string = " and c.id not in (" + month_string + '))'

            with connection.cursor() as cursor:
                cursor.execute("""SELECT CONCAT(c.last_name, ', ', c.first_name) as name, c.id as id, 
                int.intake_date as date, int.age_group, int.gender, int.ethnicity, int.degree, int.eye_condition, 
                int.eye_condition_date, int.education, int.living_arrangement, int.residence_type, int.dialysis, 
                int.stroke, int.seizure, int.heart, int.arthritis, int.high_bp, int.neuropathy, int.pain, int.asthma,
                int.cancer, int.musculoskeletal, int.alzheimers, int.allergies, int.mental_health, int.substance_abuse, 
                int.memory_loss, int.learning_disability, int.geriatric, int.dexterity, int.migraine, int.referred_by, 
                int.hearing_loss,  c.first_name, c.last_name, int.birth_date
                FROM lynx_sipnote ls
                LEFT JOIN lynx_contact as c  on c.id = ls.contact_id
                LEFT JOIN lynx_intake as int  on int.contact_id = c.id
                WHERE c.id != 111 and extract(month FROM ls.note_date) = %s and extract(year FROM ls.note_date) = '%s' 
                    and c.sip_client is true %s
                ORDER BY c.last_name, c.first_name;""" % (month, year, month_string))
                client_set = dictfetchall(cursor)

            filename = "Core Lynx Excel Billing - " + month + " - " + year
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'

            writer = csv.writer(response)
            writer.writerow(
                ['Client Name', 'First Name', 'Last Name', 'Age Group', 'Gender', 'Birth Date', 'Race/Ethnicity',
                 'Visual Impairment at Time of Intake', 'Major Cause of Visual Impairment',
                 'Non-Visual Impairment', 'On-Set of Significant Vision Loss', 'Highest Level of Education Completed',
                 'Type of Living Arrangement', 'Setting of Residence', 'Source of Referral'])

            client_ids = []
            for client in client_set:
                if client['id'] in client_ids:
                    continue
                impairments = ''
                client_ids.append(client['id'])
                if client['dialysis']:
                    impairments += 'Dialysis, '
                if client['stroke']:
                    impairments += 'Stroke, '
                if client['seizure']:
                    impairments += 'Seizure, '
                if client['heart']:
                    impairments += 'Cardiovascular, '
                if client['arthritis']:
                    impairments += 'Arthritis, '
                if client['high_bp']:
                    impairments += 'Hypertension, '
                if client['hearing_loss']:
                    impairments += 'Hearing Loss, '
                if client['neuropathy']:
                    impairments += 'Neuropathy, '
                if client['pain']:
                    impairments += 'Pain, '
                if client['asthma']:
                    impairments += 'Asthma, '
                if client['cancer']:
                    impairments += 'Cancer, '
                if client['musculoskeletal']:
                    impairments += 'Musculoskeletal, '
                if client['alzheimers']:
                    impairments += 'Alzheimers, '
                if client['allergies']:
                    impairments += 'Allergies, '
                if client['mental_health']:
                    impairments += 'Mental Health, '
                if client['substance_abuse']:
                    impairments += 'Substance Abuse, '
                if client['memory_loss']:
                    impairments += 'Memory Loss, '
                if client['learning_disability']:
                    impairments += 'Learning Disability, '
                if client['geriatric']:
                    impairments += 'Other Geriatric, '
                if client['dexterity']:
                    impairments += 'Mobility, '
                if client['migraine']:
                    impairments += 'Migraine, '

                if impairments:
                    impairments = impairments[:-2]

                writer.writerow(
                    [client['name'], client['first_name'], client['last_name'], client['age_group'], client['gender'],
                     client['birth_date'], client['ethnicity'], client['degree'], client['eye_condition'], impairments,
                     client['eye_condition_date'], client['education'], client['living_arrangement'],
                     client['residence_type'], client['referred_by']])

            return response

    return render(request, 'lynx/sip_demographic_report.html', {'form': form})


@login_required
def sip_quarterly_report(request):
    form = SipCSFReportForm()
    return render(request, 'lynx/sip_quarterly_report.html', {'form': form})


@login_required
def sip_csf_services_report(request):
    form = SipCSFReportForm()
    if request.method == 'POST':
        form = SipCSFReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            quarter = data.get('quarter')
            year = data.get('year')
            fiscal_year = get_fiscal_year(year)

            with connection.cursor() as cursor:
                query = """SELECT CONCAT(c.last_name, ', ', c.first_name) as name, c.id as id, ls.fiscal_year, 
                ls.vision_screening, ls.treatment, ls.at_devices, ls.at_services, ls.orientation, ls.communications, 
                ls.dls, ls.support, ls.advocacy, ls.counseling, ls.information, ls.services, addr.county, ls.note_date,
                ls.independent_living, sp.living_plan_progress, sp.community_plan_progress, sp.ila_outcomes, 
                sp.at_outcomes, ls.class_hours
                    FROM lynx_sipnote as ls
                    left JOIN lynx_contact as c on c.id = ls.contact_id
                    inner join lynx_address as addr on c.id= addr.contact_id
                    left JOIN lynx_sipplan as sp on sp.id = ls.sip_plan_id
                    where  fiscal_year = '%s' 
                    and quarter <= %d 
                    and c.sip_client is true 
                    order by c.last_name, c.first_name;""" % (fiscal_year, int(quarter))
                cursor.execute(query)
                note_set = dictfetchall(cursor)

            filename = "SIP Quarterly Services Report - Q" + str(quarter) + " - " + str(fiscal_year)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'
            writer = csv.writer(response)
            writer.writerow(["Program Participant", "$ Total expenditures from all sources of program funding",
                             "Vision  Assessment (Screening/Exam/evaluation)",
                             "$ Cost of Vision Assessment", "Surgical or Therapeutic Treatment",
                             "$ Cost of Surgical/ Therapeutic Treatment",
                             "$ Total expenditures from all sources of program funding",
                             "Received AT Devices or Services B2", "$ Total for AT Devices",
                             "$ Total for AT Services", "AT Goal Outcomes",
                             "$ Total expenditures from all sources of program funding", "Received IL/A Services",
                             "Received O&M", "Received Communication Skills", "Received Daily Living Skills",
                             "Received Advocacy training",
                             "Received Adjustment Counseling", "Received I&R", "Received Other Services",
                             "IL/A Service Goal Outcomes", "$ Total expenditures from all sources of program funding",
                             "Received Supportive Service", "# of Cases Assessed", "Living Situation Outcomes",
                             "Home and Community involvement Outcomes"])

            client_ids = []
            aggregated_data = {}
            for note in note_set:
                client_id = note['id']
                if client_id not in client_ids:
                    client_ids.append(client_id)
                    aggregated_data[client_id] = {}
                    aggregated_data[client_id]['client_name'] = note['name']

                if quarter not in aggregated_data[client_id]:
                    aggregated_data[client_id][quarter] = {}
                    aggregated_data[client_id][quarter]['independent_living'] = boolean_transform(
                        note['independent_living'])
                    aggregated_data[client_id][quarter]['vision_screening'] = boolean_transform(
                        note['vision_screening'])
                    aggregated_data[client_id][quarter]['treatment'] = boolean_transform(note['treatment'])
                    aggregated_data[client_id][quarter]['at_devices'] = boolean_transform(note['at_devices'])
                    aggregated_data[client_id][quarter]['at_services'] = boolean_transform(note['at_services'])
                    aggregated_data[client_id][quarter]['orientation'] = boolean_transform(note['orientation'])
                    aggregated_data[client_id][quarter]['communications'] = boolean_transform(note['communications'])
                    aggregated_data[client_id][quarter]['dls'] = boolean_transform(note['dls'])
                    aggregated_data[client_id][quarter]['support'] = boolean_transform(note['support'])
                    aggregated_data[client_id][quarter]['advocacy'] = boolean_transform(note['advocacy'])
                    aggregated_data[client_id][quarter]['counseling'] = boolean_transform(note['counseling'])
                    aggregated_data[client_id][quarter]['information'] = boolean_transform(note['information'])
                    aggregated_data[client_id][quarter]['services'] = boolean_transform(note['services'])
                    aggregated_data[client_id][quarter]['living_plan_progress'] = plan_evaluation(
                        note['living_plan_progress'])
                    aggregated_data[client_id][quarter]['community_plan_progress'] = plan_evaluation(
                        note['community_plan_progress'])
                    aggregated_data[client_id][quarter]['at_outcomes'] = assess_evaluation(note['at_outcomes'])
                    aggregated_data[client_id][quarter]['ila_outcomes'] = assess_evaluation(note['ila_outcomes'])
                    ila_outcomes = aggregated_data[client_id][quarter]['ila_outcomes']
                    at_outcomes = aggregated_data[client_id][quarter]['at_outcomes']
                    aggregated_data[client_id][quarter]['assessed'] = is_assessed(ila_outcomes, at_outcomes)
                    if aggregated_data[client_id][quarter]['at_services'] == "Yes" or \
                            aggregated_data[client_id][quarter]['at_devices'] == "Yes":
                        aggregated_data[client_id][quarter]['at_devices_services'] = "Yes"
                    else:
                        aggregated_data[client_id][quarter]['at_devices_services'] = "No"
                else:
                    if boolean_transform(note['vision_screening']) == "Yes":
                        aggregated_data[client_id][quarter]['vision_screening'] = "Yes"
                    if boolean_transform(note['independent_living']) == "Yes":
                        aggregated_data[client_id][quarter]['independent_living'] = "Yes"
                    if boolean_transform(note['treatment']) == "Yes":
                        aggregated_data[client_id][quarter]['treatment'] = "Yes"
                    if boolean_transform(note['at_devices']) == "Yes" or boolean_transform(
                            note['at_services']) == "Yes":
                        aggregated_data[client_id][quarter]['at_devices_services'] = "Yes"
                    if boolean_transform(note['orientation']) == "Yes":
                        aggregated_data[client_id][quarter]['orientation'] = "Yes"
                    if boolean_transform(note['communications']) == "Yes":
                        aggregated_data[client_id][quarter]['communications'] = "Yes"
                    if boolean_transform(note['dls']) == "Yes":
                        aggregated_data[client_id][quarter]['dls'] = "Yes"
                    if boolean_transform(note['support']) == "Yes":
                        aggregated_data[client_id][quarter]['support'] = "Yes"
                    if boolean_transform(note['advocacy']) == "Yes":
                        aggregated_data[client_id][quarter]['advocacy'] = "Yes"
                    if boolean_transform(note['counseling']) == "Yes":
                        aggregated_data[client_id][quarter]['counseling'] = "Yes"
                    if boolean_transform(note['information']) == "Yes":
                        aggregated_data[client_id][quarter]['information'] = "Yes"
                    if boolean_transform(note['services']) == "Yes":
                        aggregated_data[client_id][quarter]['services'] = "Yes"
                    if note['living_plan_progress']:
                        aggregated_data[client_id][quarter]['living_plan_progress'] = plan_evaluation(
                            note['living_plan_progress'], aggregated_data[client_id][quarter]['living_plan_progress'])
                    if note['community_plan_progress']:
                        aggregated_data[client_id][quarter]['community_plan_progress'] = plan_evaluation(
                            note['community_plan_progress'],
                            aggregated_data[client_id][quarter]['community_plan_progress'])
                    if note['at_outcomes']:
                        aggregated_data[client_id][quarter]['at_outcomes'] = assess_evaluation(note['at_outcomes'],
                                                                                               aggregated_data[
                                                                                                   client_id][quarter][
                                                                                                   'at_outcomes'])
                    if note['ila_outcomes']:
                        aggregated_data[client_id][quarter]['ila_outcomes'] = assess_evaluation(note['ila_outcomes'],
                                                                                                aggregated_data[
                                                                                                    client_id][quarter][
                                                                                                    'ila_outcomes'])
                    if note['ila_outcomes'] and note['at_outcomes']:
                        aggregated_data[client_id][quarter]['assessed'] = is_assessed(
                            aggregated_data[client_id][quarter]['ila_outcomes'],
                            aggregated_data[client_id][quarter]['at_outcomes'])

            for key, value in aggregated_data.items():
                if '1' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['1']['at_devices_services'], "", "", value['1']['at_outcomes'], "",
                                     value['1']['independent_living'], value['1']['orientation'],
                                     value['1']['communications'], value['1']['dls'], value['1']['advocacy'],
                                     value['1']['counseling'], value['1']['information'], value['1']['services'],
                                     value['1']['ila_outcomes'], "", value['1']['support'], value['1']['assessed'],
                                     value['1']['living_plan_progress'], value['1']['community_plan_progress']])
                if '2' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['2']['at_devices_services'], "", "", value['2']['at_outcomes'], "",
                                     value['2']['independent_living'], value['2']['orientation'],
                                     value['2']['communications'], value['2']['dls'], value['2']['advocacy'],
                                     value['2']['counseling'], value['2']['information'], value['2']['services'],
                                     value['2']['ila_outcomes'], "", value['2']['support'], value['2']['assessed'],
                                     value['2']['living_plan_progress'], value['2']['community_plan_progress']])
                if '3' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['3']['at_devices_services'], "", "", value['3']['at_outcomes'], "",
                                     value['3']['independent_living'], value['3']['orientation'],
                                     value['3']['communications'], value['3']['dls'], value['3']['advocacy'],
                                     value['3']['counseling'], value['3']['information'], value['3']['services'],
                                     value['3']['ila_outcomes'], "", value['3']['support'], value['3']['assessed'],
                                     value['3']['living_plan_progress'], value['3']['community_plan_progress']])
                if '4' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['4']['at_devices_services'], "", "", value['4']['at_outcomes'], "",
                                     value['4']['independent_living'], value['4']['orientation'],
                                     value['4']['communications'], value['4']['dls'], value['4']['advocacy'],
                                     value['4']['counseling'], value['4']['information'], value['4']['services'],
                                     value['4']['ila_outcomes'], "", value['4']['support'], value['4']['assessed'],
                                     value['4']['living_plan_progress'], value['4']['community_plan_progress']])

            return response

    return render(request, 'lynx/sip_quarterly_report.html', {'form': form})


@login_required
def sip_csf_demographic_report(request):
    form = SipCSFReportForm()
    if request.method == 'POST':
        form = SipCSFReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            quarter = data.get('quarter')
            year = data.get('year')
            fiscal_year = get_fiscal_year(year)

            with connection.cursor() as cursor:
                cursor.execute("""SELECT CONCAT(c.last_name, ', ', c.first_name) as name, c.id as id, int.age_group, 
                int.gender, int.ethnicity, int.degree, int.eye_condition, int.eye_condition_date, int.education, 
                int.living_arrangement, int.residence_type, addr.county, int.dialysis, int.stroke, int.seizure, 
                int.heart, int.arthritis, int.high_bp, int.neuropathy, int.pain, int.asthma, int.cancer, 
                int.musculoskeletal, int.alzheimers, int.allergies, int.mental_health, int.substance_abuse, 
                int.memory_loss, int.learning_disability, int.geriatric, int.dexterity, int.migraine, int.hearing_loss, 
                int.referred_by, ls.note_date, int.communication, int.other_ethnicity
                    FROM lynx_sipnote as ls
                    left JOIN lynx_contact as c on c.id = ls.contact_id
                    left JOIN lynx_intake as int on int.contact_id = c.id
                    inner join lynx_address as addr on c.id= addr.contact_id
                    where  fiscal_year = '%s' 
                    and quarter = %d 
                    and c.sip_client is true 
                    and c.id not in 
                        (SELECT contact_id FROM lynx_sipnote AS sip WHERE quarter < %d and fiscal_year = '%s')
                    order by c.last_name, c.first_name;""" % (fiscal_year, int(quarter), int(quarter), fiscal_year))

                client_set = dictfetchall(cursor)

            filename = "SIP Quarterly Demographic Report - Q" + str(quarter) + " - " + str(fiscal_year)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'
            writer = csv.writer(response)
            writer.writerow(["Program Participant", "Individuals Served", "Age at Application", "Gender", "Race",
                             "Ethnicity", "Degree of Visual Impairment", "Major Cause of Visual Impairment",
                             "Hearing Impairment", "Mobility Impairment", "Communication Impairment",
                             "Cognitive or Intellectual Impairment", "Mental Health Impairment", "Other Impairment",
                             "Type of Residence", "Source of Referral", "County"])

            client_ids = []
            for client in client_set:
                client_id = client['id']
                if client_id not in client_ids:
                    client_ids.append(client_id)

                    # Translate impairments into the categories asked for
                    client['hearing_impairment'] = 'No'
                    client['mobility_impairment'] = 'No'
                    client['communication_impairment'] = 'No'
                    client['cognition_impairment'] = 'No'
                    client['mental_impairment'] = 'No'
                    client['other_impairment'] = 'No'
                    if client['hearing_loss']:
                        client['hearing_impairment'] = 'Yes'
                    if client['communication']:
                        client['communication_impairment'] = 'Yes'
                    if client['dialysis'] or client['migraine'] or client['geriatric'] or client['allergies'] or client[
                        'cancer'] or client['asthma'] or client['pain'] or client['high_bp'] or client['heart'] or \
                            client['stroke'] or client['seizure']:
                        client['other_impairment'] = 'Yes'
                    if client['arthritis'] or client['dexterity'] or client['neuropathy'] or client['musculoskeletal']:
                        client['mobility_impairment'] = 'Yes'
                    if client['alzheimers'] or client['memory_loss'] or client['learning_disability']:
                        client['cognition_impairment'] = 'Yes'
                    if client['mental_health'] or client['substance_abuse']:
                        client['mental_impairment'] = 'Yes'

                    # Distill gender options into the three asked for
                    if client["gender"] != 'Male' and client["gender"] != 'Female':
                        client["gender"] = "Did Not Self-Identify Gender"

                    # Sort out race/ethnicity
                    client["hispanic"] = "No"
                    hispanic = False
                    if client["ethnicity"] == "Hispanic or Latino" or client[
                        "other_ethnicity"] == "Hispanic or Latino" or client["ethnicity"] == "Two or More Races" or \
                            client["other_ethnicity"] == "Two or More Races":
                        client["hispanic"] = "Yes"
                        client["race"] = "2 or More Races"
                        hispanic = True

                    if client["other_ethnicity"] or hispanic:
                        client["race"] = "2 or More Races"
                    elif client["ethnicity"] == "Other":
                        client["race"] = "Did not self identify Race"
                    elif client["ethnicity"] == "Two or More Races":
                        client["race"] = "2 or More Races"
                    else:
                        client["race"] = client["ethnicity"]

                    # Sort out degree of impairment
                    if client['degree'] == "Totally Blind (NP or NLP)":
                        client['degree'] = "Totally Blind"
                    elif client['degree'] == "Legally Blind":
                        client['degree'] = "Legally Blind"
                    else:
                        client['degree'] = "Severe Vision Impairment"

                    # Sort out cause
                    ok_diagnosis = ["Cataracts", "Diabetic Retinopathy", "Glaucoma", "Macular Degeneration"]
                    if client['eye_condition'] not in ok_diagnosis:
                        client['eye_condition'] = "Other causes of visual impairment"

                    # Sort out residence
                    if client['residence_type'] == "Community Residential":
                        client['residence_type'] = "Senior Independent Living"
                    if client['residence_type'] == "Assisted Living":
                        client['residence_type'] = "Assisted Living Facility"
                    if client['residence_type'] == "Skilled Nursing Care":
                        client['residence_type'] = "Nursing Home"
                    if client['residence_type'] == "Senior Living":
                        client['residence_type'] = "Senior Independent Living"
                    if client['residence_type'] == ("Private Residence - apartment or home (alone, or with roommate, "
                                                    "personal care assistant, family, or other person)"):
                        client['residence_type'] = "Private Residence"

                    # sort of referral
                    ok_sources = ["Veterans Administration", "Family or Friend", "Senior Program",
                                  "Assisted Living Facility",
                                  "Nursing Home", "Independent Living Center", "Self-Referral", "Eye Care Provider",
                                  "Physician/ Medical Provider"]
                    if client['referred_by'] == "DOR" or client['referred_by'] == "Alta":
                        client['referred_by'] = "State VR Agency"
                    elif client['referred_by'] == "Physician":
                        client['referred_by'] = "Physician/ Medical Provider"
                    elif client['referred_by'] not in ok_sources:
                        client['referred_by'] = "Other"

                    # Find if case was before this fiscal year
                    if client["note_date"]:
                        # grab the date for the first note
                        year = int(year)
                        quarter = int(quarter)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                """SELECT id, note_date FROM lynx_sipnote where contact_id = '%s' 
                                order by id ASC LIMIT 1;""" % (client_id,))
                            note_set = dictfetchall(cursor)
                        note_year = int(note_set[0]["note_date"].year)
                        note_month = int(note_set[0]["note_date"].month)
                        if note_year > year:
                            client['served'] = "Case open between Oct. 1 - Sept. 30"
                        elif note_year == year:
                            if note_month >= 10:
                                client['served'] = "Case open between Oct. 1 - Sept. 30"
                            else:
                                client['served'] = "Case open prior to Oct. 1"
                        else:
                            client['served'] = "Case open prior to Oct. 1"
                    else:
                        client['served'] = "Unknown"

                    # Mark some referral sources as other
                    if client['referred_by']:
                        if (client['referred_by'] == "DOR" or client['referred_by'] == "Alta" or
                                client['referred_by'] == "Physician"):
                            client['referred_by'] = 'Other'

                    # Write demographic data to demo csv
                    writer.writerow(
                        [client["name"], client['served'], client['age_group'], client["gender"], client["race"],
                         client["hispanic"], client['degree'], client['eye_condition'], client['hearing_impairment'],
                         client['mobility_impairment'], client['communication_impairment'],
                         client['cognition_impairment'], client['mental_impairment'], client['other_impairment'],
                         client['residence_type'], client['referred_by'], client['county']])

            return response

    return render(request, 'lynx/sip_quarterly_report.html', {'form': form})


@login_required
def volunteers_report_month(request):
    form = VolunteerReportForm()
    if request.method == 'POST':
        form = VolunteerReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            start = data.get('start_date')
            end = data.get('end_date')
            volunteers = Volunteer.objects.raw("""SELECT lc.id, CONCAT(lc.last_name, ', ', lc.first_name) as name, 
                                                        SUM(volunteer_hours) as hours, 
                                                        EXTRACT(MONTH FROM volunteer_date) as month, 
                                                        EXTRACT(YEAR FROM volunteer_date) as year
                                                    FROM lynx_volunteer lv
                                                    JOIN lynx_contact lc ON lv.contact_id = lc.id
                                                    WHERE lc.volunteer_check is TRUE
                                                        AND volunteer_date >= %s::date
                                                        AND volunteer_date <= %s::date
                                                    GROUP BY lc.id, 
                                                             EXTRACT(MONTH FROM volunteer_date), 
                                                             EXTRACT(YEAR FROM volunteer_date)""", [start, end])

            filename = "Volunteer Report - " + start + " - " + end
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'

            writer = csv.writer(response)
            writer.writerow(['Volunteer Name', 'Date', 'Hours'])

            for vol in volunteers:
                name = vol.name
                MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July",
                          8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
                given_month = MONTHS[vol.month]
                date = given_month + ' ' + str(
                    int(vol.year))  # there's a weird decimal for the year, casting to int first to remove it
                hours = vol.hours
                writer.writerow([name, date, hours])

            return response

    return render(request, 'lynx/volunteer_report.html', {'form': form})


@login_required
def volunteers_report_program(request):
    form = VolunteerReportForm()
    if request.method == 'POST':
        form = VolunteerReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            start = data.get('start_date')
            end = data.get('end_date')
            volunteers = Volunteer.objects.raw("""SELECT lc.id,
                                                        CONCAT(lc.last_name, ', ', lc.first_name) as name,
                                                        SUM(lv.volunteer_hours) as hours,
                                                        lv.volunteer_type,
                                                        EXTRACT(MONTH FROM volunteer_date) as month,
                                                        EXTRACT(YEAR FROM volunteer_date) as year
                                                    FROM lynx_volunteer lv
                                                    JOIN lynx_contact lc ON lv.contact_id = lc.id
                                                    WHERE lc.volunteer_check is TRUE
                                                        AND lv.volunteer_date >= %s::date
                                                        AND lv.volunteer_date <= %s::date
                                                    GROUP BY lc.id,
                                                        lv.volunteer_type,
                                                        EXTRACT(MONTH FROM volunteer_date),
                                                        EXTRACT(YEAR FROM volunteer_date)""", [start, end])

            filename = "Volunteer Report - " + start + " - " + end
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'

            writer = csv.writer(response)
            writer.writerow(['Volunteer Name', 'Date', 'Program', 'Hours'])

            for vol in volunteers:
                name = vol.name
                MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July",
                          8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
                given_month = MONTHS[vol.month]
                date = given_month + ' ' + str(
                    int(vol.year))  # there's a weird decimal for the year, casting to int first to remove it
                hours = vol.hours
                program = vol.volunteer_type
                writer.writerow([name, date, program, hours])

            return response

    return render(request, 'lynx/volunteer_report.html', {'form': form})
