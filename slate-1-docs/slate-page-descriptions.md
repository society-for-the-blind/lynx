# SLATE pages

This   document  follows   the   structure  of   the
main    SLATE   page,    whenever   possible    (see
below).   Hidden    URLs   are    documented   under
"[Miscellaneous](#user-content-miscellaneous)".

[aspx-to-cs.txt](./aspx-to-cs.txt)     shows     the
mappings between the `.aspx`  templates and the .NET
sources.


## Overview

SLATE is mainly used by  CORE, because all the terms
and  workflows follow  the CORE  processes (billing,
client schedules and data, etc.).

SIP workflows have never  been added, therefore most
of their  day-to-day is  tracked on paper  and Excel
sheets. SIP operates though  state funds and grants,
and have  entirely different  reporting requirements
with no billing (if I understood that correctly).

## SLATE main page headings (and index for this document)

> [**Administration Tools:**](#user-content-administration-tools)
>
> + [Authorizations](#user-content-authorizations)
> + [Database Users](#user-content-database-users)
> + [Class Information (AKA service areas)](#class-information-aka-service-areas)
> + [Intake Service List](#user-content-intake-service-list)
> + [Service Groups](#user-content-service-groups)
> + [Payment Sources](#user-content-payment-sources)
> + [Outreach Types](#user-content-outreach-types)
> + [Client Merge](#user-content-client-merge)
>
> [**Instructor Tools:**](#user-content-instructor-tools)
>
> + [Lesson Notes](#user-content-lesson-notes)
> + [Progress Reports](#user-content-progress-reports)
> + [Waiting List](#user-content-waiting-list)
> + [Client Schedules](#user-content-client-schedules)
> + [Billing](#user-content-billing)
> + [Volunteer Hours](#user-content-volunteer-hours)
> + [Volunteer Schedules](#user-content-volunteer-schedules)
> + [Outside Agency Contact Report](#user-content-outside-agency-contact-report)
> + [Instructional Time Taught this Month](#user-content-instructional-time-taught-this-month)
>
> [**Staff Tools:**](#user-content-staff-tools)
>
> + [Intakes and Contacts](#user-content-intakes-and-contacts)
> + [New Intake](#user-content-new-intake)
> + [Student Plan](#user-content-student-plan)
> + [Reports](#user-content-reports)
> + [Add an Authorization](#user-content-add-an-authorization)
> + [Add Contact](#user-content-add-contact)
>
> [**Footer:**](#user-content-footer)
>
> + [Main Page](#user-content-main-page)
> + [Logout](#user-content-login-logout-and-change-password)
> + [Change Password](#user-content-login-logout-and-change-password)

[**Miscellaneous**](#user-content-miscellaneous)

## Administration Tools

### Authorizations

Authorizations are only used by CORE to identify a billing period and service area. Its main properties are:

+ **authorization number**

  Authorizations  have unique  identifiers, mostly  of
  the format "NMED123456789",  because the majority of
  the  clients  are  sponsored by  the  Department  of
  Rehabilitation  (DOR). This  format  is supplied  by
  them,  but there  are other  sources as  well (e.g.,
  Alta  California, Veterans  Affairs) with  different
  formats or no ID at all.

+ **dates of service**

  The period  of time when  the client has  to receive
  the services  requested, denoted  by a start  and an
  end date.

  TODO: The dates can be  amended, and then we usually
  get an  updated authorization, but I  can't remember
  whether the authorization number changes or not. Ask
  Shane.

+ **client's name**

+ **counselor's name**

  The   counselor's  name   with  the   name  of   the
  organization,   that   grants   the   authorization,
  forms    the    payment   source.    See    [Payment
  Sources](#user-content-payment-sources).

+ **description of required services**

  Shows the service area  (see [Class Information (AKA
  service   areas)](#class-information-aka-service-areas)),
  the   units  of   service  (classes   or  individual
  training), the number of units and the unit price.

For  example,  Kilgore   Troutman  is  scheduled  to
receive  27  classes  of Assistive  Technology  (AT)
training  from 1/1/2019  to  3/1/2019  for the  unit
price of $85.

Therefore an individual, who  is authorized to learn
AT,  Orientation  &  Mobility  (O&M),  Daily  Living
Skills (ILS,  as in  Independent Living  Skills) and
Braille, will have 4 authorizations.

SIP  has no  use  for  authorizations, because  they
get  funding   from  the   state  (Title   VII)  and
through  various  grants.  They have  quarterly  and
yearly  reporting obligations.  The closest  to CORE
authorizations is the Plan  For Service report ("one
for every  client per  grant year on  first visit").
More on SIP in a different document.

**Notes**:

+ SIP clients can also be CORE clients. If a person is
  over 55, they can receive  SIP services even if they
  are also supported by DOR.

+ It  should  be   possible  to  enter  authorizations
  without an authorization number. Sometimes paperwork
  is slow, but a client needs to start training and we
  know that  she is going to  receive an authorization
  from an outside agency.

#### [/sfb/app/authorizations.aspx](https://slate.societyfortheblind.org/sfb/app/authorizations.aspx)

##### Description

Display service authorizations for CORE clients.

##### Used by

+ CORE
+ Volunteers

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbIntake
+ twbServiceAreaAuthorization
+ twbWaitingList

##### Queries

```
"SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey LEFT JOIN twbAuthorization On twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbIntake on twbIntake.ContactKey = twbContact.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0 " + str3 + " AND twbAuthorization.AuthorizationKey IN (SELECT twbAuthorization.AuthorizationKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbCCR On twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey WHERE twbCCR.MemberKey = ", this.Request.Cookies["Member"]["MemberID"], " UNION SELECT twbAuthorization.AuthorizationKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbWaitingList On twbWaitingList.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey WHERE twbWaitingList.MemberKey = ", this.Request.Cookies["Member"]["MemberID"], ")" }; + " ORDER BY Name", selectConnection).Fill(dataSet, "Clients");
```

#### [/sfb/app/view-authorizations.aspx?ContactKey=1234](https://slate.societyfortheblind.org/sfb/app/view-authorizations.aspx?ContactKey=1234)

##### Description

Show all authorizations for a particular client.

##### Used by

+ CORE
+ Volunteers

##### DB tables touched

+ twbauthorization
+ twbauthorizationtype
+ twbcontact
+ twbservicearea
+ twbserviceareaauthorization

##### Queries

```
                    str3 = "SELECT DISTINCT (AuthorizationID + ' - ' + CAST(Agency As Varchar(25)) + ' (' + CAST(StartDate As Varchar(11)) + ' - ' + CAST(EndDate As Varchar(11)) + ') ' + CAST(TotalHours As varchar(12)) + ' ' + twbAuthorizationType.AuthorizationTypeCode + ', ' + ServiceArea) As 'Name', twbAuthorization.AuthorizationKey, StartDate  FROM twbAuthorization  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE ContactKey = " + Conversions.ToString(num) + " AND HoursRemaining <> 0 AND EndDate >= DATEADD(month,-1,GETDATE()) ORDER BY StartDate DESC, Name";
                }
                else
                {
                    this.selAuthorType.SelectedIndex = 1;
                    str3 = "SELECT DISTINCT (AuthorizationID + ' - ' + CAST(Agency As Varchar(25)) + ' (' + CAST(StartDate As Varchar(11)) + ' - ' + CAST(EndDate As Varchar(11)) + ') ' + CAST(TotalHours As varchar(12)) + ' ' + twbAuthorizationType.AuthorizationTypeCode + ', ' + ServiceArea) As 'Name', twbAuthorization.AuthorizationKey, StartDate  FROM twbAuthorization  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE ContactKey = " + Conversions.ToString(num) + " ORDER BY StartDate DESC, Name";
                }
                DataSet dataSet = new DataSet();
                new OleDbDataAdapter(str3, selectConnection).Fill(dataSet, "Authorizations");
                DataView view = new DataView(dataSet.Tables["Authorizations"]);
                this.selAuthorizations.DataSource = view;
                this.selAuthorizations.DataValueField = "AuthorizationKey";
                this.selAuthorizations.DataTextField = "Name";
                this.Page.DataBind();
                OleDbCommand command = new OleDbCommand("SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact WHERE ContactKey = " + Conversions.ToString(num), selectConnection);
```

#### [/sfb/app/view-authorization.aspx?AuthorKey=12345](https://slate.societyfortheblind.org/sfb/app/view-authorization.aspx?AuthorKey=12345)

##### Description

Show a specific authorization.

##### Used by

+ CORE
+ Volunteers

##### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
OleDbCommand command = new OleDbCommand("SELECT *, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Caseworker' FROM twbAuthorization INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.CaseworkerID WHERE AuthorizationKey = " + Conversions.ToString(num), connection);
command.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact WHERE ContactKey = " + Conversions.ToString(num2);
string selectCommandText = "SELECT ServiceArea FROM twbServiceArea INNER JOIN twbServiceAreaAuthorization On twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey WHERE AuthorizationKey = " + Conversions.ToString(num);
command.CommandText = "SELECT BillingName FROM twbServiceArea INNER JOIN twbAuthorization On twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE AuthorizationKey = " + Conversions.ToString(num);
new OleDbDataAdapter("SELECT ('<a href=''view-lesson-note.aspx?CCRKey=' + CAST(CCRKey AS VARCHAR(9)) + '''>' + CAST(LessonDate AS VARCHAR(11)) + '</a>') AS 'Lesson Date', dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits) AS 'Billed Time', AuthorizationTypeCode as 'Authorization Type', ('$' + CAST(RateHourly As varchar(11))) As 'Rate', BillingName AS 'Service Area' FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType ON twbAuthorizationType.AuthorizationTypeID = twbAuthorization.AuthorizationTypeID INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE twbServiceAreaAuthorization.AuthorizationKey = " + Conversions.ToString(num), connection).Fill(set, "ThisCCR");
```

#### [/sfb/app/new-authorization.aspx?ContactKey=1234](https://slate.societyfortheblind.org/sfb/app/new-authorization.aspx?ContactKey=1234)

##### Description

Add new authorization for client.

##### Used by

+ CORE
+ Volunteers

##### DB tables touched

+ twbContact
+ twbContactType
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization
+ twbServicePlan
+ twbServicePlanGoals

##### Queries

```
this.outClient.InnerHtml = Conversions.ToString(new OleDbCommand("SELECT (FirstName + ' ' + LastName) As 'Name' FROM twbContact WHERE ContactKey = " + Conversions.ToString(num), connection).ExecuteScalar());
                new OleDbDataAdapter("SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType = 'Outside Agency' AND ContactValue <> 0 ORDER BY Name", connection).Fill(dataSet, "Caseworkers");
                                                new OleDbDataAdapter("SELECT BillingName, ServiceArea, ServiceAreaKey, (BillingName + ' ($' + CAST(BillingRate As Varchar(6)) + ')') As BillingRate, BillingRate As Rate FROM twbServiceArea WHERE Deleted = 0 ORDER BY BillingName", connection).Fill(set2, "SAs");
                                                                        strArray[10] = "); SELECT @@Identity;";
                                                                                        command2.CommandText = "SELECT DISTINCT MemberEmail FROM twbMember WHERE ServiceAreaKey IN (" + str7 + ")";

```

#### [/sfb/app/edit-authorization.aspx?AuthorKey=12345](https://slate.societyfortheblind.org/sfb/app/edit-authorization.aspx?AuthorKey=12345)

##### Description

Edit existing authorization.

##### Used by

+ CORE
+ Volunteers

##### DB tables touched

+ twbAuthorization
+ twbContact
+ twbContactType
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
                    strArray = new string[] { "UPDATE twbServiceAreaAuthorization SET ServiceAreaKey = ", this.selServiceAreas.Value, " WHERE ServiceAreaAuthorizationKey IN (SELECT TOP 1 ServiceAreaAuthorizationKey FROM twbServiceAreaAuthorization WHERE AuthorizationKey = ", Conversions.ToString(num6), ")" };
                    command2.CommandText = "SELECT ContactKey FROM twbAuthorization WHERE AuthorizationKey = " + Conversions.ToString(num6);
                new OleDbDataAdapter("SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType = 'Outside Agency' AND ContactValue <> 0 ORDER BY Name", selectConnection).Fill(dataSet, "Caseworkers");
                                new OleDbDataAdapter("SELECT BillingName, ServiceArea, ServiceAreaKey, (BillingName + ' ($' + CAST(BillingRate As Varchar(6)) + ')') As BillingRate, BillingRate As Rate FROM twbServiceArea WHERE Deleted = 0 ORDER BY BillingName", selectConnection).Fill(set3, "SAs");
                                new OleDbDataAdapter("SELECT BillingName, ServiceAreaKey, (BillingName + ' ($' + CAST(BillingRate As Varchar(6)) + ')') As BillingRate, BillingRate As Rate FROM twbServiceArea WHERE Deleted = 0 ORDER BY BillingName", selectConnection).Fill(set2, "SAs");
                                OleDbCommand command = new OleDbCommand("SELECT * FROM twbAuthorization WHERE AuthorizationKey = " + Conversions.ToString(num), selectConnection);
                                command.CommandText = "SELECT TOP 1 ServiceAreaKey FROM twbServiceAreaAuthorization WHERE AuthorizationKey = " + Conversions.ToString(num);
                                command.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name' FROM twbContact WHERE ContactKey = " + Conversions.ToString(num2);
                                command.CommandText = "SELECT * FROM twbServiceAreaAuthorization WHERE AuthorizationKey = " + Conversions.ToString(num);
```

#### /sfb/app/del-authorization.aspx?AuthorKey=12345

##### Description

Delete authorization.

##### Used by

+ CORE
+ Volunteers

##### DB tables touched

+ twbAuthorization
+ twbContact

##### Queries

```
            new OleDbCommand("DELETE FROM twbAuthorization WHERE AuthorizationKey = " + Conversions.ToString(num), connection).ExecuteNonQuery();
                OleDbDataReader reader = new OleDbCommand("SELECT AuthorizationID, Agency, HoursRemaining, HoursUsed, AuthorizationTypeID, Absences, (twbContact.LastName + ', ' + twbContact.FirstName + ' ' + twbContact.MiddleName) As 'Name' FROM twbAuthorization INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.ContactKey WHERE AuthorizationKey = " + Conversions.ToString(num), connection).ExecuteReader();
```

#### [/sfb/app/authorization-search.aspx](https://slate.societyfortheblind.org/sfb/app/authorization-search.aspx)

##### Description

Filter authorizations.

##### Used by

+ CORE
+ Volunteers

##### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbContact
+ twbContactType
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
            strArray = new string[] { "SELECT DISTINCT ('<a href=''edit-authorization.aspx?AuthorKey=' + CAST(twbAuthorization.AuthorizationKey AS VARCHAR(6)) + '''>' + AuthorizationID + '</a>') As 'AuthorizationID', (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name', AuthorizationTypeCode, ServiceArea, AuthorizationID, twbServiceArea.ServiceAreaKey, (LastName + ' ' + FirstName + ' ' + MiddleName) As 'NoShow' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorizationType ON twbAuthorizationType.AuthorizationTypeID = twbAuthorization.AuthorizationTypeID INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE ContactType <> 'Outside Agency'", str4, str10, str7, str, " ORDER BY ", this.ViewState["sortField"].ToString(), " ", this.ViewState["sortDirection"].ToString() };
                                new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "ServiceAreas");
```

### Database Users

#### [/sfb/app/db-users.aspx](https://slate.societyfortheblind.org/sfb/app/db-users.aspx)

##### Description

Manage SLATE users.

##### Used by

+ admins

##### DB tables touched

+ twbMember
+ twbMemberGroup

##### Queries

```
                new OleDbDataAdapter("SELECT (MemberLastName + ', ' + MemberFirstName + ' - ' + UserName + ' : ' + GroupName) As 'Name', MemberKey  FROM twbMember INNER JOIN twbMemberGroup ON twbMember.MemberGroupKey = twbMemberGroup.MemberGroupKey WHERE Deleted = 0 ORDER BY Name", selectConnection).Fill(dataSet, "Members");
```

#### [/sfb/app/new-db-user.aspx](https://slate.societyfortheblind.org/sfb/app/new-db-user.aspx)

##### Description

Add new SLATE user.

##### Used by

+ admins

##### DB tables touched

+ twbContact
+ twbContactType
+ twbEmployee
+ twbMember
+ twbMemberGroup
+ twbServiceArea

##### Queries

```
            objArgs.IsValid = Conversions.ToInteger(new OleDbCommand("SELECT Count(MemberKey) FROM twbMember WHERE UserName LIKE '" + this.txtUserName.Value + "' AND Deleted = 0", connection).ExecuteScalar()) <= 0;
                    OleDbCommand command = new OleDbCommand(Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("INSERT INTO twbMember (UserName, Password, MemberGroupKey, Deleted, MemberEmail, MemberFirstName, MemberLastName, ServiceAreaKey) VALUES ('", this.DBReady(this.txtUserName.Value)), "', '"), right), "', "), this.selMemberGroup.Value), ", 0, '"), this.DBReady(this.txtEmail.Value)), "', '"), this.DBReady(this.txtFirstName.Value)), "', '"), this.DBReady(this.txtLastName.Value)), "', "), this.selSAs.Value), ")")), connection);
                        command.CommandText = Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("UPDATE twbEmployee SET MemberKey = (SELECT MemberKey FROM twbMember WHERE UserName = '", this.DBReady(this.txtUserName.Value)), "') WHERE ContactKey = "), this.selEmployees.Value));
                new OleDbDataAdapter("SELECT GroupName, MemberGroupKey  FROM twbMemberGroup ORDER BY GroupName", selectConnection).Fill(dataSet, "Clients");
                new OleDbDataAdapter("SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbEmployee ON twbEmployee.ContactKey = twbContact.ContactKey WHERE ContactType = 'Outside Agency' AND ContactValue <> 0 AND MemberKey Is Null ORDER BY Name", selectConnection).Fill(set2, "Employees");
                new OleDbDataAdapter("SELECT ServiceArea, ServiceAreaKey  FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(set3, "SAs");
```

#### [/sfb/app/edit-db-user.aspx?MemberKey=12](https://slate.societyfortheblind.org/sfb/app/edit-db-user.aspx?MemberKey=12)

##### Description

Edit SLATE user information.

##### Used by

+ admins

##### DB tables touched

+ twbContact
+ twbContactType
+ twbEmployee
+ twbMember
+ twbMemberGroup
+ twbServiceArea

##### Queries

```
                objArgs.IsValid = Conversions.ToInteger(new OleDbCommand("SELECT Count(MemberKey) FROM twbMember WHERE UserName LIKE '" + this.txtUserName.Value + "' AND Deleted = 0", connection).ExecuteScalar()) <= 0;
                    OleDbCommand command2 = new OleDbCommand(str4, connection);
                        command2.CommandText = Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("UPDATE twbEmployee SET MemberKey = (SELECT MemberKey FROM twbMember WHERE UserName = '", this.DBReady(this.txtUserName.Value)), "') WHERE ContactKey = "), this.selEmployees.Value));
                OleDbCommand command = new OleDbCommand("SELECT UserName, MemberEmail, MemberLastName, MemberFirstName, MemberGroupKey, ServiceAreaKey, PasswordReset FROM twbMember WHERE MemberKey = " + Conversions.ToString(num2), connection);
                new OleDbDataAdapter("SELECT GroupName, MemberGroupKey  FROM twbMemberGroup ORDER BY GroupName", connection).Fill(dataSet, "Clients");
                new OleDbDataAdapter("SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbEmployee ON twbEmployee.ContactKey = twbContact.ContactKey WHERE ContactType = 'Outside Agency' AND ContactValue <> 0 AND (MemberKey Is Null OR MemberKey = " + Conversions.ToString(num2) + ") ORDER BY Name", connection).Fill(set2, "Employees");
                new OleDbDataAdapter("SELECT ServiceArea, ServiceAreaKey  FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", connection).Fill(set3, "SAs");
                    command.CommandText = "SELECT ContactKey FROM twbEmployee WHERE MemberKey = " + Conversions.ToString(num2);
```

#### /del_db_user.aspx

##### Description

Delete SLATE user.

##### Used by

+ admins

##### DB tables touched

+ twbMember

##### Queries

```
            new OleDbCommand("UPDATE twbMember SET Deleted = -1 WHERE MemberKey = " + Conversions.ToString(num), connection).ExecuteNonQuery();
                OleDbDataReader reader = new OleDbCommand("SELECT UserName, MemberEmail, (MemberLastName + ', ' + MemberFirstName) As 'Name' FROM twbMember WHERE MemberKey = " + Conversions.ToString(num), connection).ExecuteReader();
```

### Class Information (AKA service areas)

The title says "Class  Information", but it actually
shows  items designated  as "service  areas" in  the
database (in `twbServiceArea`). We only use a subset
of this  list that  refer to the  teaching programs,
and only  when we  add authorizations (see  the list
below).

No one knows the original  meaning of the term as we
have never used it internally, and some of the items
seem  random  (e.g.,  Veterans Affairs).  A  closely
related (and similarly haphazard) list is in [Intake
Service List](#user-content-intake-service-list) (in
`twbServices`), that shows  services provided by SIP
(see below), that should  probably be in the service
areas  list  here,  as  they  are  also  related  to
teaching/training.

The list of entries that  are currently used by CORE
and SIP respectively:

1. SIP

  + 6 day Retreat
  + Support group or community integration activity
  + One day programs or home visits

2. CORE

  + Assistive Technology Assessment
  + Assistive Technology Training - Group
  + Assistive Technology Training - Individual
  + Communications (Braille) Assessment
  + Communications (Braille) Training - Group
  + Communications (Braille) Training - Individual
  + Daily Living Skills Assessment
  + daily Living Skills Training - Individual
  + Orientation & Mobility Evaluation
  + Orientation & Mobility Training - Individual

#### [/sfb/app/service-areas.aspx](https://slate.societyfortheblind.org/sfb/app/service-areas.aspx)

##### Description

List all service areas.

##### Used by

+ CORE

##### DB tables touched

+ twbServiceArea

##### Queries

```
                new OleDbDataAdapter("SELECT ServiceArea, ServiceAreaKey  FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "SAs");
```

#### [/sfb/app/new-sa.aspx](https://slate.societyfortheblind.org/sfb/app/new-sa.aspx)

##### Description

Add new service area.

##### Used by

+ CORE

##### DB tables touched

Couldn't find any. See below.

##### Queries

Couldn't   find  any,   but   (a)   it  should   use
`twbServiceArea` and (b) there  was a large chunk of
interesting code  in `new_sa.cs`  so this may  be an
unsuccessful reverse engineering.

#### [/sfb/app/edit-sa.aspx?SAKey=12](https://slate.societyfortheblind.org/sfb/app/edit-sa.aspx?SAKey=12)

##### Description

Edit existing service area.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbServiceArea
+ twbServiceAreaQuestions

##### Queries

```
                    OleDbCommand command2 = new OleDbCommand(string.Concat(strArray), connection);
                OleDbCommand command = new OleDbCommand("SELECT ServiceArea, BillingName, BillingRate, AuthorizationRequired FROM twbServiceArea WHERE ServiceAreaKey = " + Conversions.ToString(num), connection);
                command.CommandText = "SELECT Active, QuestionTxt FROM twbServiceAreaQuestions WHERE ServiceAreaKey = " + Conversions.ToString(num) + " ORDER BY QuestionNum";
```

#### /sfb/app/del-sa.aspx

##### Description

Delete service area.

##### Used by

+ CORE

##### DB tables touched

+ twbServiceArea

##### Queries

```
            new OleDbCommand("UPDATE twbServiceArea SET Deleted = -1 WHERE ServiceAreaKey = " + Conversions.ToString(num), connection).ExecuteNonQuery();
                this.outName.InnerHtml = Conversions.ToString(new OleDbCommand("SELECT ServiceArea FROM twbServiceArea WHERE ServiceAreaKey = " + Conversions.ToString(num), connection).ExecuteScalar());
```

### Intake Service List

This should be  a list of all  the services provided
by  SFTB  (used  on  the [3rd  page  of  the  client
intake](TODO: add link)) and "outside services" (see
the [4th  page of  client intake](TODO:  add link)).
The double quotes  mean that I am  not entirely sure
what  "outside  services"  refers to,  but  probably
anything other than what SFTB provides.

Both outside  and inside  services supposed to  be a
running  list of  items on  a client's  intake under
"Society Services" and "Outside Blindness Services",
but  rarely  see  those updated  (or  even  included
during intake). SIP definitely uses it because there
are items here, that should be in service areas
(see documented in [Class Information](#class-information-aka-service-areas)).

TODO: Ask Shane and Pat.

(Intake also doubles as client profile. See [Intakes
and Contacts](#user-content-intakes-and-contacts).)

#### [/sfb/app/services.aspx?Type=Outside](https://slate.societyfortheblind.org/sfb/app/services.aspx?Type=Outside)

(Or [/sfb/app/services.aspx?Type=Inside](https://slate.societyfortheblind.org/sfb/app/services.aspx?Type=Inside).)

##### Description

See under [Intake Service List](#user-content-intake-service-list).

##### Used by

+ CORE
+ SIP

##### DB tables touched

+ twbServices

##### Queries

```
                string selectCommandText = (str3 != "Outside") ? "SELECT (CAST(ServicesKey As Varchar(9)) + '|' + CAST(DisplayPrecedence As Varchar(9))) As ServicesKey, (ServicesGroup + ' ' + Name) As Name FROM twbServices WHERE Inside = 1 ORDER BY DisplayPrecedence, ServicesGroup" : "SELECT (CAST(ServicesKey As Varchar(9)) + '|' + CAST(DisplayPrecedence As Varchar(9))) As ServicesKey, (ServicesGroup + ' ' + Name) As Name FROM twbServices WHERE Outside = 1 ORDER BY DisplayPrecedence, ServicesGroup";
                new OleDbCommand("UPDATE twbServices SET DisplayPrecedence = " + Conversions.ToString((double) (Conversions.ToDouble(this.selServices.Value.Substring(startIndex, this.selServices.Value.Length - startIndex)) + 1.0)) + " WHERE ServicesKey = " + this.selServices.Value.Substring(0, index), connection).ExecuteNonQuery();
                new OleDbCommand("UPDATE twbServices SET DisplayPrecedence = " + Conversions.ToString((double) (Conversions.ToDouble(this.selServices.Value.Substring(startIndex, this.selServices.Value.Length - startIndex)) - 1.0)) + " WHERE ServicesKey = " + this.selServices.Value.Substring(0, index), connection).ExecuteNonQuery();
```

#### [/sfb/app/new-service.aspx](https://slate.societyfortheblind.org/sfb/app/new-service.aspx)

##### Description

Add new service.

##### Used by

In theory:

+ CORE
+ SIP

In practice: no one.

##### DB tables touched

+ twbServices

##### Queries

```
                new OleDbDataAdapter("SELECT DISTINCT ServicesGroup FROM twbServices WHERE ServicesGroup <> '' ORDER by ServicesGroup", selectConnection).Fill(dataSet, "Groups");
                    new OleDbCommand(Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("INSERT INTO twbServices (Name, ServicesGroup, Inside, Outside, VolunteerArea, DisplayPrecedence) VALUES ('", this.DBReady(this.txtName.Value)), "', '"), right), "', "), num), ", "), num2), ", '"), this.selVolunteerAreas.Value), "', 1)")), connection).ExecuteNonQuery();
```

#### [/sfb/app/edit-service.aspx?ServiceKey=12](https://slate.societyfortheblind.org/sfb/app/edit-service.aspx?ServiceKey=12)

##### Description

Edit service.

##### Used by

In theory:

+ CORE
+ SIP

In practice: no one.

##### DB tables touched

+ twbServices

##### Queries

```
                    new OleDbCommand(Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("UPDATE twbServices SET Name = '", this.DBReady(this.txtName.Value)), "', ServicesGroup = '"), str4), "', Inside = "), num2), ", Outside = "), num3), ", VolunteerArea = '"), this.selVolunteerAreas.Value), "' WHERE ServicesKey = "), right)), connection).ExecuteNonQuery();
                new OleDbDataAdapter("SELECT DISTINCT ServicesGroup FROM twbServices WHERE ServicesGroup <> '' ORDER by ServicesGroup", selectConnection).Fill(dataSet, "Groups");
                OleDbDataReader reader = new OleDbCommand("SELECT * FROM twbServices WHERE ServicesKey = " + Conversions.ToString(num), selectConnection).ExecuteReader();
```

#### /sfb/del-service.aspx

##### Description

Delete service.

##### Used by

In theory:

+ CORE
+ SIP

In practice: no one.

##### DB tables touched

+ twbServices

##### Queries

```
                this.outName.InnerHtml = Conversions.ToString(new OleDbCommand("SELECT ServicesGroup + ' ' + Name FROM twbServices WHERE ServicesKey = " + Conversions.ToString(num), connection).ExecuteScalar());
```

### Service Groups

Just   a   different   view   of   [Intake   Service
List](#user-content-intake-service-list); can't even
add a new group here,  only in the previous section,
and it also uses `twbServices` table only.

#### [/sfb/app/service-groups.aspx](https://slate.societyfortheblind.org/sfb/app/service-groups.aspx)

##### Description

Show service groups.

##### Used by

No one.

##### DB tables touched

+ twbServices

##### Queries

```
                new OleDbDataAdapter("SELECT DISTINCT ServicesGroup As Name FROM twbServices WHERE ServicesGroup <> '' ORDER by ServicesGroup", selectConnection).Fill(dataSet, "Services");
```

#### /sfb/app/edit-service-group.aspx

##### Description

Edit service group name.

##### Used by

No one.

##### DB tables touched

+ twbServices

##### Queries

```
                    new OleDbCommand(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject("UPDATE twbServices SET ServicesGroup = '", this.DBReady(Strings.Trim(this.txtName.Value))), "' WHERE ServicesGroup = '"), HttpUtility.UrlDecode(str)), "'")), connection).ExecuteNonQuery();
```

#### /sfb/app/del-service-group.aspx

##### Description

Delete service group with all its services.

##### Used by

No one.

##### DB tables touched

+ twbServices

##### Queries

```
            new OleDbCommand("UPDATE twbServices SET ServicesGroup = '' WHERE ServicesGroup = '" + HttpUtility.UrlDecode(str) + "'", connection).ExecuteNonQuery();
```

### Payment Sources

The list  shows individuals (counselors)  with their
associated  organization  as   payment  sources.  In
reality, the  payment sources are  the organizations
themselves  (e.g.,  DOR,  VA),   but  I  guess  this
is  a  shortcut  to  associate a  counselor  and  an
organization to an authorization in a single step.

See [Authorizations](#user-content-authorizations).

#### [/sfb/app/payment-sources.aspx](https://slate.societyfortheblind.org/sfb/app/payment-sources.aspx)

##### Description

See description under [Payment Sources](#user-content-payment-sources) above.

##### Used by

+ CORE

##### DB tables touched

+ twbContact
+ twbContactType

##### Queries

```
                new oledbdataadapter("select distinct twbcontact.contactkey, (lastname + ', ' + firstname + ' ' + middlename + ' - ' + company + ';') as 'name' from twbcontact inner join twbcontacttype on twbcontact.contactkey = twbcontacttype.contactkey where contacttype like 'outside agency' and contactvalue <> 0 order by name", selectconnection).fill(dataset, "clients");
```

#### [/sfb/app/new-payment-source.aspx](https://slate.societyfortheblind.org/sfb/app/new-payment-source.aspx)

##### Description



Add new payment source.

##### Used by

+ CORE

##### DB tables touched

+ twbContactType
+ twbEmployee
+ twbEmployeeGroup
+ twbGroup

##### Queries

```
                new OleDbDataAdapter("SELECT GroupKey, GroupName FROM twbGroup ORDER BY GroupName", selectConnection).Fill(dataSet, "Groups");
                            OleDbCommand command = new OleDbCommand("spwbAddTPP", connection);
                                command.CommandText = Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT TOP 1 GroupKey FROM twbGroup WHERE GroupName = '", this.DBReady(this.txtGroup.Value)), "'"));
```

#### /sfb/app/confirm-payment-source.aspx

##### Description

Submit new payment source form.

##### Used by



+ CORE

##### DB tables touched

+ twbContact
+ twbEmployee
+ twbEmployeeGroup
+ twbGroup

##### Queries

```
            OleDbCommand command = new OleDbCommand("SELECT * FROM twbContact WHERE twbContact.ContactKey = " + Conversions.ToString(num), connection);
            command.CommandText = "SELECT * FROM twbEmployee WHERE ContactKey = " + Conversions.ToString(num);
            command.CommandText = "SELECT GroupName FROM twbGroup INNER JOIN twbEmployeeGroup on twbEmployeeGroup.GroupKey = twbGroup.GroupKey WHERE ContactKey =" + Conversions.ToString(num);
```

#### [/sfb/app/view-payment-source.aspx?ContactKey=1234](https://slate.societyfortheblind.org/sfb/app/view-payment-source.aspx?ContactKey=1234)

##### Description



View payment source.

##### Used by

+ CORE

##### DB tables touched

+ twbContact
+ twbEmployee
+ twbEmployeeGroup
+ twbGroup

##### Queries

```
            OleDbCommand command = new OleDbCommand("SELECT * FROM twbContact WHERE twbContact.ContactKey = " + Conversions.ToString(num), connection);
            command.CommandText = "SELECT * FROM twbEmployee WHERE ContactKey = " + Conversions.ToString(num);
            command.CommandText = "SELECT GroupName FROM twbGroup INNER JOIN twbEmployeeGroup on twbEmployeeGroup.GroupKey = twbGroup.GroupKey WHERE ContactKey =" + Conversions.ToString(num);
```

#### [/sfb/app/edit-payment-source.aspx?ContactKey=1234](https://slate.societyfortheblind.org/sfb/app/edit-payment-source.aspx?ContactKey=1234)

##### Description

Edit payment source.

##### Used by

+ CORE

##### DB tables touched

+ twbContact

##### Queries

```
                OleDbDataReader reader = new OleDbCommand("SELECT * FROM twbContact WHERE twbContact.ContactKey = " + Conversions.ToString(num), connection).ExecuteReader();
                    OleDbCommand command2 = new OleDbCommand("spwbEditTPP", connection) {
```

#### /sfb/app/del-payment-source.aspx

##### Description

Delete payment source.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbContact
+ twbEmployeeGroup

##### Queries

```
            OleDbCommand command = new OleDbCommand("DELETE FROM twbContact WHERE twbContact.ContactKey = " + Conversions.ToString(num) + " AND ContactKey NOT IN (SELECT DISTINCT CaseworkerID from twbAuthorization)", connection);
            command.CommandText = "DELETE FROM twbEmployeeGroup WHERE ContactKey = " + Conversions.ToString(num) + " AND ContactKey NOT IN (SELECT DISTINCT CaseworkerID from twbAuthorization)";
                OleDbDataReader reader = new OleDbCommand("SELECT * FROM twbContact WHERE twbContact.ContactKey = " + Conversions.ToString(num), connection).ExecuteReader();
```

### Outreach Types

Looking at the list items, I would say that it was designed for the Low Vision Clinic and SIP, but I have never seem them used.

TODO: Ask.

#### [/sfb/app/outreach.aspx](https://slate.societyfortheblind.org/sfb/app/outreach.aspx)

##### Description

List of outreach types.

##### Used by

None?

##### DB tables touched

+ twbOutreach

##### Queries

```
                new OleDbDataAdapter("SELECT OutreachKey, OutreachName FROM twbOutreach WHERE Deleted = 0 ORDER BY OutreachName", selectConnection).Fill(dataSet, "Outreach");
```

#### [/sfb/app/new-outreach.aspx](https://slate.societyfortheblind.org/sfb/app/new-outreach.aspx)

##### Description

Add new outreach type.

##### Used by

None?

##### DB tables touched

+ twbOutreach

##### Queries

```
                    new OleDbCommand(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject("INSERT INTO twbOutreach (OutreachName, Deleted) VALUES ('", this.DBReady(this.txtName.Value)), "', 0)")), connection).ExecuteNonQuery();
```

#### [/sfb/app/edit-outreach.aspx?OutreachKey=12](https://slate.societyfortheblind.org/sfb/app/edit-outreach.aspx?OutreachKey=12)

##### Description

Edit outreach type.

##### Used by

None?

##### DB tables touched

+ twbOutreach

##### Queries

```
                this.txtName.Value = Conversions.ToString(new OleDbCommand("SELECT OutreachName FROM twbOutreach WHERE OutreachKey = " + Conversions.ToString(num), connection).ExecuteScalar());
                    new OleDbCommand(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject("UPDATE twbOutreach SET OutreachName = '", this.DBReady(this.txtName.Value)), "' "), "WHERE OutreachKey = "), right)), connection).ExecuteNonQuery();
```

#### /sfb/app/del-outreach.aspx

##### Description

Delete outreach type.

##### Used by

None?

##### DB tables touched

+ twbOutreach

##### Queries

```
            new OleDbCommand("UPDATE twbOutreach SET Deleted = -1 WHERE OutreachKey = " + Conversions.ToString(num), connection).ExecuteNonQuery();
                this.outName.InnerHtml = Conversions.ToString(new OleDbCommand("SELECT OutreachName FROM twbOutreach WHERE OutreachKey = " + Conversions.ToString(num), connection).ExecuteScalar());
```

### Client Merge

I didn't even know this existed. Probably used to remove duplicates.

#### [/sfb/app/client-merge.aspx](https://slate.societyfortheblind.org/sfb/app/client-merge.aspx)

##### Description

Probably to remove duplicates.

##### Used by

None?

##### DB tables touched

+ twbContact
+ twbContactType

##### Queries

```
            new OleDbDataAdapter("SELECT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';' + '(' + CAST(twbContact.ContactKey AS varchar(9)) + ')') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0 ORDER BY Name", selectConnection).Fill(dataSet, "Clients");
```

#### /sfb/app/client-merge-confirm.aspx

##### Description

Submit request to merge two client records.

##### Used by

None?

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbClientMedical
+ twbContact
+ twbContactOutreach
+ twbContactType
+ twbEmergencyContact
+ twbEmployee
+ twbEmployeeGroup
+ twbIntake
+ twbIntakeBilling
+ twbIntakeVolunteer
+ twbLog
+ twbMonthlyHours
+ twbScheduleVolunteer
+ twbServiceAreaAnswers
+ twbServiceAreaLessons
+ twbServicePlan
+ twbVolunteerHours

##### Queries

```
            OleDbCommand command = new OleDbCommand("UPDATE twbAuthorization SET ContactKey = " + Conversions.ToString(num2) + "WHERE twbAuthorization.ContactKey = " + Conversions.ToString(num), connection);
            command.CommandText = "DELETE FROM twbClientMedical WHERE twbClientMedical.ContactKey = " + Conversions.ToString(num);
            command.CommandText = "DELETE FROM twbContactOutreach WHERE twbContactOutreach.ContactKey = " + Conversions.ToString(num);
            command.CommandText = "DELETE FROM twbContactType WHERE twbContactType.ContactKey = " + Conversions.ToString(num);
            command.CommandText = "DELETE FROM twbEmergencyContact WHERE twbEmergencyContact.ContactKey = " + Conversions.ToString(num);
            command.CommandText = "DELETE FROM twbEmployee WHERE twbEmployee.ContactKey = " + Conversions.ToString(num);
            command.CommandText = "DELETE FROM twbEmployeeGroup WHERE twbEmployeeGroup.ContactKey = " + Conversions.ToString(num);
            command.CommandText = "DELETE FROM twbIntake WHERE twbIntake.ContactKey = " + Conversions.ToString(num);
            command.CommandText = "DELETE FROM twbIntakeVolunteer WHERE twbIntakeVolunteer.ContactKey = " + Conversions.ToString(num);
            command.CommandText = "DELETE FROM twbScheduleVolunteer WHERE twbScheduleVolunteer.ContactKey = " + Conversions.ToString(num);
            command.CommandText = "DELETE FROM twbServiceAreaAnswers WHERE twbServiceAreaAnswers.ContactKey = " + Conversions.ToString(num);
            command.CommandText = "DELETE FROM twbServicePlan WHERE twbServicePlan.ContactKey = " + Conversions.ToString(num);
            command.CommandText = "DELETE FROM twbContact WHERE twbContact.ContactKey = " + Conversions.ToString(num);
                OleDbCommand command = new OleDbCommand("SELECT * FROM twbContact WHERE twbContact.ContactKey = " + Conversions.ToString(num), connection);
                command.CommandText = "SELECT * FROM twbContact WHERE twbContact.ContactKey = " + Conversions.ToString(num2);
```

## Instructor Tools

### Lesson Notes

A lesson note belongs to a specific authorization. It logs the activity with the client and attendance, and also serves as the basic unit for billing.

#### [/sfb/app/lesson-notes.aspx?SAKey=0&Expired=False&MyClients=False](https://slate.societyfortheblind.org/sfb/app/lesson-notes.aspx?SAKey=0&Expired=False&MyClients=False)

##### Description

Show lesson notes based on whatever options are chosen on the first page. These will show up in query parameters:

+ Show My Clients Only (`MyClients=False` if unchecked, show every lesson note for every client)

+ Show Expired Authorizations (`Expired=False` if unchecked, show lesson notes for only active authorizations)

+ Service Area dropdown (`SAKey=0` if all is selected)

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbContactType
+ twbServiceArea
+ twbServiceAreaAuthorization
+ twbWaitingList

##### Queries

```
                new OleDbDataAdapter("SELECT ServiceArea, ServiceAreaKey  FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "SAs");
                    strArray = new string[] { " AND twbAuthorization.AuthorizationKey IN (SELECT twbAuthorization.AuthorizationKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbCCR On twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey WHERE twbCCR.MemberKey = ", this.Request.Cookies["Member"]["MemberID"], " UNION SELECT twbAuthorization.AuthorizationKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbWaitingList On twbWaitingList.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey WHERE twbWaitingList.MemberKey = ", this.Request.Cookies["Member"]["MemberID"], ")" };
                    strArray = new string[] { "SELECT DISTINCT twbServiceAreaAuthorization.ServiceAreaAuthorizationKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' (' + CAST(StartDate As Varchar(11)) + ' - ' + CAST(EndDAte As Varchar(11)) + ') ' + CAST(ROUND(HoursRemaining, 4) As Varchar(9)) + ' ' + twbAuthorizationType.AuthorizationTypeCode + ', ' + AuthorizationID) As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization On twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE ", str4, "ContactType = 'Client' AND ContactValue <> 0 AND ServiceAreaKey = ", this.selSAs.Value, str6, " ORDER BY Name" };
                    strArray = new string[] { "SELECT DISTINCT twbServiceAreaAuthorization.ServiceAreaAuthorizationKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' (' + CAST(StartDate As Varchar(11)) + ' - ' + CAST(EndDAte As Varchar(11)) + '): '  + ServiceArea + ', ' + CAST(ROUND(HoursRemaining, 4) As Varchar(9)) + ' ' + twbAuthorizationType.AuthorizationTypeCode + ', ' + AuthorizationID) As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization On twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbServiceArea On twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey WHERE ", str4, "ContactType = 'Client' AND ContactValue <> 0 ", str6, " ORDER BY Name" };
```

#### [/sfb/app/view-lesson-notes.aspx?SAAKey=12345](https://slate.societyfortheblind.org/sfb/app/view-lesson-notes.aspx?SAAKey=12345)

##### Description

View all lesson notes belonging to a specific authorization.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
            OleDbCommand command = new OleDbCommand("SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As Name, ServiceArea, AuthorizationID, AuthorizationTypeID, EndDate, StartDate, TotalHours, HoursUsed, HoursRemaining FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num6), connection);
            string[] strArray = new string[] { "SELECT CAST(dbo.GetInstructionalHoursUsedForClass(AuthorizationKey, BilledUnits) As Float(2)) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE twbCCR.ServiceAreaAuthorizationKey = ", Conversions.ToString(num6), " AND LessonDate >= CAST('", Conversions.ToString(num3), "' + '/1/' + '", Conversions.ToString(year), "' AS DATETIME) AND LessonDate < CAST('", Conversions.ToString(num4), "' + '/1/' + '" };
                new OleDbDataAdapter("SELECT (CAST(twbCCR.LessonDate AS varchar(11)) + ' ' + MemberLastName + ', ' + MemberFirstName + ' (' + CAST(CAST(twbCCR.BilledUnits AS int) AS varchar(10)) + ' Units) - ' + AuthorizationID) AS 'Name', twbCCR.CCRKey FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbMember ON twbMember.MemberKey = twbCCR.MemberKey WHERE twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = " + Conversions.ToString(num6) + " ORDER BY LessonDate DESC, ModifiedDate", connection).Fill(dataSet, "CCRs");
```

#### /sfb/app/del-lesson-note.aspx

##### Description

Delete a lesson note.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbServiceAreaAuthorization

##### Queries

```
            OleDbCommand command = new OleDbCommand("DELETE FROM twbCCR WHERE CCRKey = " + Conversions.ToString(num), connection);
                string cmdText = "SELECT * FROM twbCCR WHERE CCRKey = " + Conversions.ToString(num);
                OleDbCommand command = new OleDbCommand(cmdText, connection);
                    command.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name' FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + this.hidSAAKey.Value;
```

#### [/sfb/app/view-lesson-note.aspx?CCRKey=123456](https://slate.societyfortheblind.org/sfb/app/view-lesson-note.aspx?CCRKey=123456)

##### Description

Show a lesson note. "Instructional Units" and "Billed Units" under section "Lesson Note:" show the instructional time broken down into 15 minute increments. For example, if it says 8, it means 2 hours.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
                OleDbCommand command = new OleDbCommand("SELECT DISTINCT (MemberFirstName + ' ' + MemberLastName) As MemberName FROM twbMember INNER JOIN twbCCR ON twbCCR.MemberKey = twbMember.MemberKey WHERE CCRKey = " + Conversions.ToString(num), connection);
                command.CommandText = "SELECT * FROM twbCCR WHERE CCRKey = " + Conversions.ToString(num);
                command.CommandText = "SELECT DISTINCT (MemberFirstName + ' ' + MemberLastName) As MemberName FROM twbMember WHERE MemberKey = " + Conversions.ToString(num3);
                command.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name', twbContact.ContactKey, CaseworkerID, AuthorizationID, AuthorizationTypeID, BillingName as ServiceArea, EndDate, StartDate, TotalHours, HoursUsed, HoursRemaining, (SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.CaseworkerID = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + str + ") As 'PaymentSource' FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE ServiceAreaAuthorizationKey = " + str;
                string[] strArray = new string[] { "SELECT CAST(dbo.GetInstructionalHoursUsedForClass(AuthorizationKey, BilledUnits) As Float(2)) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE twbCCR.ServiceAreaAuthorizationKey = ", str, " AND LessonDate >= CAST('", Conversions.ToString(num4), "' + '/1/' + '", Conversions.ToString(year), "' AS DATETIME) AND LessonDate < CAST('", Conversions.ToString(num5), "' + '/1/' + '" };
                command.CommandText = "SELECT twbCCR.CCRKey, LessonDate FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbMember ON twbMember.MemberKey = twbCCR.MemberKey WHERE twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = " + str + " ORDER BY LessonDate";
```

#### [/sfb/app/new-lesson-note.aspx?SAAKey=12345](https://slate.societyfortheblind.org/sfb/app/new-lesson-note.aspx?SAAKey=12345)

##### Description

Add a new lesson note.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbIntake
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization
+ twbServicePlanGoals

##### Queries

```
                    OleDbCommand command2 = new OleDbCommand("spwbAddLessonNotes", connection);
                        command2.CommandText = "SELECT Absences, twbAuthorization.AuthorizationKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = " + Conversions.ToString(num17);
                            command2.CommandText = "SELECT Email FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.CaseworkerID = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num17);
                    command2.CommandText = "SELECT TotalHours, HoursUsed, HoursRemaining, AuthorizationTypeID FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num17);
                        command2.CommandText = "SELECT MemberEmail FROM twbMember WHERE MemberKey = " + this.Request.Cookies["Member"]["MemberID"];
                            command2.CommandText = "SELECT twbAuthorization.AuthorizationKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num17);
                            command2.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'ContactName' FROM twbAuthorization INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.ContactKey WHERE AuthorizationKey = " + Conversions.ToString(num18);
                            command2.CommandText = "SELECT BillingName FROM twbServiceArea INNER JOIN twbAuthorization ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE AuthorizationKey = " + Conversions.ToString(num18);
                    command2.CommandText = "SELECT twbIntake.MemberKey, (LastName + ', ' + FirstName) As 'Name', twbIntake.ContactKey FROM twbIntake INNER JOIN twbContact ON twbContact.ContactKey = twbIntake.ContactKey INNER JOIN twbAuthorization ON twbIntake.ContactKey = twbAuthorization.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num17);
                        command2.CommandText = "SELECT Email FROM twbContact INNER JOIN twbAuthorization ON twbContact.ContactKey = twbAuthorization.CaseworkerID INNER JOIN twbServiceAreaAuthorization On twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num17);
                OleDbCommand command = new OleDbCommand("SELECT Waiting FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num3), connection);
                strArray = new string[] { "SELECT COUNT(twbServicePlanGoals.ServicePlanGoalKey) FROM twbServicePlanGoals WHERE twbServicePlanGoals.MemberKey = ", this.Request.Cookies["Member"]["MemberID"], " AND Point = 2 AND twbServicePlanGoals.ServiceAreaKey = (SELECT ServiceAreaKey FROM twbServiceAreaAuthorization WHERE ServiceAreaAuthorizationKey = ", Conversions.ToString(num3), ")" };
                    command.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name', AuthorizationID, twbAuthorization.AuthorizationKey, AuthorizationTypeID, BillingName As ServiceArea, EndDate, StartDate, TotalHours, HoursUsed, HoursRemaining FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num3);
                                    strArray = new string[] { "SELECT CAST(SUM(dbo.GetInstructionalHoursUsedForClass(AuthorizationKey, InstructionalUnits)) As Float(2)) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE twbCCR.ServiceAreaAuthorizationKey = ", Conversions.ToString(num3), " AND LessonDate >= CAST('", Conversions.ToString(num8), "' + '/1/' + '", Conversions.ToString(year), "' AS DATETIME) AND LessonDate < CAST('", Conversions.ToString(num9), "' + '/1/' + '" };
```

### Progress Reports

Monthly progress report for each authorization to be included in the billing printoutat the end of each month. Serves no other role in billing.

#### [/sfb/app/progress-reports.aspx?All=True&Display=Expire](https://slate.societyfortheblind.org/sfb/app/progress-reports.aspx?All=True&Display=Expire)

##### Description

Show all progress reports based on the criteria given on the initial page. There is one line item for each authorization number.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
                    string[] strArray = new string[] { "SELECT DISTINCT twbCCR.ServiceAreaAuthorizationKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + '; (' + BillingName + '): ' + AuthorizationID + ' - ' + CAST(StartDate AS varchar(11)) + ' (' + DayPhone + '): ' + CAST(ROUND(HoursRemaining, 4) As Varchar(9)) + ' hrs' ) As 'Name', StartDate FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey INNER JOIN twbCCR ON twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey WHERE ", str5, "ContactType = 'Client' AND ContactValue <> 0 AND MemberKey = ", str, " ORDER BY StartDate DESC" };
                    str6 = "SELECT DISTINCT twbCCR.ServiceAreaAuthorizationKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + '; (' + BillingName + '): ' + AuthorizationID + ' - ' + CAST(StartDate AS varchar(11)) + ' (' + DayPhone + '): ' + CAST(ROUND(HoursRemaining, 4) As Varchar(9)) + ' hrs' ) As 'Name', StartDate FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey INNER JOIN twbCCR ON twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey WHERE " + str5 + "ContactType = 'Client' AND ContactValue <> 0 ORDER BY StartDate DESC";
```

#### [/sfb/app/view-progress-reports.aspx?SAAKey=12345](https://slate.societyfortheblind.org/sfb/app/view-progress-reports.aspx?SAAKey=12345)

##### Description

Show all monthly progress reports for a specific authorization.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbContact
+ twbProgress
+ twbServiceAreaAuthorization

##### Queries

```
                OleDbCommand command = new OleDbCommand("SELECT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name' FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKEy = " + Conversions.ToString(num2), connection);
                command.CommandText = "SELECT AuthorizationID FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num2);
                new OleDbDataAdapter("SELECT DISTINCT ProgressKey, CAST(DATENAME(month, ProgressDate) + ' ' + CAST(YEAR(ProgressDate) As varchar(4)) As varchar(20)) As 'Date', ProgressDate FROM twbProgress WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num2) + " ORDER BY ProgressDate DESC", connection).Fill(dataSet, "ProgressReports");
```

#### /sfb/app/del_progress_report.aspx

##### Description

Delete a progress report.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbMember
+ twbProgress
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
            OleDbCommand command = new OleDbCommand("DELETE FROM twbProgress WHERE ProgressKey = " + Conversions.ToString(num), connection);
                OleDbCommand command = new OleDbCommand("SELECT ServiceAreaAuthorizationKey, ProgressDate FROM twbProgress WHERE ProgressKey = " + Conversions.ToString(num5), connection);
                string[] strArray = new string[] { "SELECT DISTINCT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name', ServiceArea, AuthorizationTypeID, CAST((SELECT SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits)) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE twbServiceArea.ServiceAreaKey = (SELECT ServiceAreaKey FROM twbServiceAreaAuthorization WHERE ServiceAreaAuthorizationKey = ", str2, ") AND twbAuthorization.ContactKey IN (SELECT ContactKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = ", str2, ") AND LessonDate >= CAST('", Conversions.ToString(num2), "' + '/1/' + '", Conversions.ToString(year), "' AS DATETIME) AND LessonDate < CAST('" };
                strArray[12] = "' AS DATETIME)) As Float) As 'Time Taught', CAST(MONTH(GETDATE()) AS VARCHAR(3)) As 'Month Number', (MemberFirstName + ' ' + MemberLastName) As 'Instructor', twbAuthorization.CaseworkerID FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbCCR on twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey INNER JOIN twbMember on twbCCR.MemberKey = twbMember.MemberKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey WHERE twbCCR.ServiceAreaAuthorizationKey = ";
                        command.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact WHERE ContactKey = " + str;
```

#### [/sfb/app/edit-progress-report.aspx?PRKey=12345](https://slate.societyfortheblind.org/sfb/app/edit-progress-report.aspx?PRKey=12345)

##### Description

Edit a progress report.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbMember
+ twbProgress
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
                    OleDbCommand command2 = new OleDbCommand("spwbEditProgressReport", connection) {
                OleDbCommand command = new OleDbCommand("SELECT * FROM twbProgress WHERE ProgressKey = " + Conversions.ToString(num), connection);
                    strArray = new string[] { "SELECT DISTINCT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name', ServiceArea, AuthorizationID, AuthorizationTypeID, EndDate, StartDate, TotalHours, HoursUsed, HoursRemaining, CAST((SELECT dbo.GetInstructionalHoursUsedForClass(auth.AuthorizationKey, SUM(BilledUnits)) FROM twbCCR WHERE twbCCR.ServiceAreaAuthorizationKey = ", str4, " AND LessonDate >= CAST('", Conversions.ToString(num3), "' + '/1/' + '", Conversions.ToString(year), "' AS DATETIME) AND LessonDate < CAST('", Conversions.ToString(num4), "' + '/1/' + '" };
                    strArray[10] = "' AS DATETIME)) As Float) As 'Time Taught', CAST(MONTH(GETDATE()) AS VARCHAR(3)) As 'Month Number', (MemberFirstName + ' ' + MemberLastName) As 'Instructor', auth.CaseworkerID FROM twbContact INNER JOIN twbAuthorization auth ON auth.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = auth.AuthorizationKey INNER JOIN twbCCR on twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey INNER JOIN twbMember on twbCCR.MemberKey = twbMember.MemberKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey WHERE twbCCR.ServiceAreaAuthorizationKey = ";
                            command.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact WHERE ContactKey = " + str3;
```

#### [/sfb/app/view-progress-report.aspx?PRKey=12345](https://slate.societyfortheblind.org/sfb/app/view-progress-report.aspx?PRKey=12345)

##### Description

Show a progress report.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbEmployeeGroup
+ twbGroup
+ twbMember
+ twbProgress
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
            OleDbCommand command = new OleDbCommand("SELECT * FROM twbProgress WHERE ProgressKey = " + Conversions.ToString(num5), connection);
            command.CommandText = "SELECT GroupName FROM twbGroup INNER JOIN twbEmployeeGroup on twbEmployeeGroup.GroupKey = twbGroup.GroupKey INNER JOIN twbAuthorization ON twbAuthorization.CaseworkerID = twbEmployeeGroup.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE twbServiceAreaAuthorization.ServiceAreaAuthorizationKey =" + str2;
                strArray = new string[] { "SELECT DISTINCT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name', BillingName As ServiceArea, AuthorizationID, AuthorizationTypeID, EndDate, StartDate, TotalHours, HoursUsed, HoursRemaining, CAST((SELECT SUM(dbo.GetInstructionalHoursUsedForClass(AuthorizationKey, BilledUnits)) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE twbCCR.ServiceAreaAuthorizationKey = ", str2, " AND LessonDate >= CAST('", Conversions.ToString(num2), "' + '/1/' + '", Conversions.ToString(year), "' AS DATETIME) AND LessonDate < CAST('", Conversions.ToString(num3), "' + '/1/' + '" };
                strArray[10] = "' AS DATETIME)) As Float) As 'Time Taught', (MemberFirstName + ' ' + MemberLastName) As 'Instructor', twbAuthorization.CaseworkerID FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbCCR on twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey INNER JOIN twbMember on twbCCR.MemberKey = twbMember.MemberKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE twbCCR.ServiceAreaAuthorizationKey = ";
                strArray = new string[] { "SELECT DISTINCT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name', BillingName As ServiceArea, AuthorizationID, AuthorizationTypeID, EndDate, StartDate, TotalHours, HoursUsed, HoursRemaining, CAST((SELECT SUM(dbo.GetInstructionalHoursUsedForClass(AuthorizationKey, BilledUnits)) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE twbCCR.ServiceAreaAuthorizationKey = ", str2, " AND LessonDate >= CAST('", Conversions.ToString(num2), "' + '/1/' + '", Conversions.ToString(year), "' AS DATETIME) AND LessonDate < CAST('", Conversions.ToString(num3), "' + '/1/' + '" };
                strArray[10] = "' AS DATETIME)) As Float) As 'Time Taught', (MemberFirstName + ' ' + MemberLastName) As 'Instructor', twbAuthorization.CaseworkerID FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbCCR on twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey INNER JOIN twbMember on twbCCR.MemberKey = twbMember.MemberKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE twbCCR.ServiceAreaAuthorizationKey = ";
            command.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact WHERE ContactKey = " + str;
```

#### [/sfb/app/new-progress-report.aspx?SAAKey=12345](https://slate.societyfortheblind.org/sfb/app/new-progress-report.aspx?SAAKey=12345)

##### Description

Add a monthly progress report for a specific authorization.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbEmployeeGroup
+ twbGroup
+ twbMember
+ twbProgress
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
            string[] strArray = new string[] { "SELECT ProgressKey FROM twbProgress WHERE ServiceAreaAuthorizationKey = ", Conversions.ToString(Conversions.ToInteger(this.Request.QueryString["SAAKey"])), " AND ProgressDate = '", Conversions.ToString(Conversions.ToDate(this.selMonth.Value + "/1/" + this.hidYear.Value)), "'" };
            objArgs.IsValid = !Conversions.ToBoolean(new OleDbCommand(string.Concat(strArray), connection).ExecuteScalar());
                    OleDbCommand command2 = new OleDbCommand("spwbAddProgressReport", connection) {
                OleDbCommand command = new OleDbCommand("SELECT GroupName FROM twbGroup INNER JOIN twbEmployeeGroup on twbEmployeeGroup.GroupKey = twbGroup.GroupKey INNER JOIN twbAuthorization ON twbAuthorization.CaseworkerID = twbEmployeeGroup.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE twbServiceAreaAuthorization.ServiceAreaAuthorizationKey =" + Conversions.ToString(num4), connection);
                    strArray = new string[] { "SELECT DISTINCT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name', ServiceArea, AuthorizationTypeID, CAST(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, (SELECT SUM(BilledUnits) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbEmployeeGroup on twbEmployeeGroup.ContactKey = twbAuthorization.CaseworkerID WHERE twbServiceArea.ServiceAreaKey = (SELECT ServiceAreaKey FROM twbServiceAreaAuthorization WHERE ServiceAreaAuthorizationKey = ", Conversions.ToString(num4), ") AND twbAuthorization.ContactKey IN (SELECT ContactKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = ", Conversions.ToString(num4), ") AND LessonDate >= CAST('", this.selMonth.Value, "' + '/1/' + '", Conversions.ToString(year), "' AS DATETIME) AND LessonDate < CAST('" };
                    strArray[12] = "' AS DATETIME))) As Float) As 'Time Taught', (MemberFirstName + ' ' + MemberLastName) As 'Instructor', twbAuthorization.CaseworkerID FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbCCR on twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey INNER JOIN twbMember on twbCCR.MemberKey = twbMember.MemberKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey WHERE twbCCR.ServiceAreaAuthorizationKey = ";
                    strArray = new string[] { "SELECT DISTINCT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name', ServiceArea, AuthorizationTypeID, CAST(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, (SELECT SUM(BilledUnits) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE twbServiceArea.ServiceAreaKey = (SELECT ServiceAreaKey FROM twbServiceAreaAuthorization WHERE ServiceAreaAuthorizationKey = ", Conversions.ToString(num4), ") AND twbAuthorization.ContactKey IN (SELECT ContactKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = ", Conversions.ToString(num4), ") AND LessonDate >= CAST('", this.selMonth.Value, "' + '/1/' + '", Conversions.ToString(year), "' AS DATETIME) AND LessonDate < CAST('" };
                    strArray[12] = "' AS DATETIME))) As Float) As 'Time Taught', (MemberFirstName + ' ' + MemberLastName) As 'Instructor', twbAuthorization.CaseworkerID FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbCCR on twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey INNER JOIN twbMember on twbCCR.MemberKey = twbMember.MemberKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey WHERE twbCCR.ServiceAreaAuthorizationKey = ";
                            command.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact WHERE ContactKey = " + str4;
                            strArray = new string[] { "SELECT InstructionalUnits FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE twbServiceArea.ServiceAreaKey = (SELECT ServiceAreaKey FROM twbServiceAreaAuthorization WHERE ServiceAreaAuthorizationKey = ", Conversions.ToString(num4), ") AND twbAuthorization.ContactKey IN (SELECT ContactKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = ", Conversions.ToString(num4), ") AND LessonDate >= CAST('", this.selMonth.Value, "' + '/1/' + '", Conversions.ToString(year), "' AS DATETIME) AND LessonDate < CAST('" };
```

### Waiting List

TODO: Ask Shane. I'm not familiar of how he uses this functionality and was uncomfortable randomly clicking around. I guess the basic idea is to take a note of future clients when we'll have the capacity to schedule services for them.

#### [/sfb/app/waiting-list.aspx](https://slate.societyfortheblind.org/sfb/app/waiting-list.aspx)

##### Description

Show people on the waiting list.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
                new OleDbDataAdapter("SELECT ServiceArea, ServiceAreaKey  FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "SAs");
                    str5 = "SELECT DISTINCT ServiceAreaAuthorizationKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' (' + DayPhone + '): '  + ServiceArea + ' [' + CAST(StartDate AS varchar(11)) + ' - ' + CAST(EndDate AS varchar(11)) + ']') As 'Name', StartDate FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization On twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbServiceArea On twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey WHERE " + str4 + str6 + " ContactType = 'Client' AND ContactValue <> 0 ORDER BY StartDate";
                    string[] strArray = new string[] { "SELECT DISTINCT ServiceAreaAuthorizationKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' (' + DayPhone + '): ' + ServiceArea + ' [' + CAST(StartDate AS varchar(11)) + ' - ' + CAST(EndDate AS varchar(11)) + ']') As 'Name', StartDate FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization On twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbServiceArea On twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey WHERE ", str4, str6, " ContactType = 'Client' AND ContactValue <> 0 AND twbServiceArea.ServiceAreaKey = ", this.selSAs.Value, " ORDER BY StartDate" };
                        str5 = Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT (MemberLastName + ', ' + MemberFirstName) FROM twbMember INNER JOIN twbCCR ON twbCCR.MemberKey = twbMember.MemberKey WHERE twbCCR.ServiceAreaAuthorizationKey = ", current["ServiceAreaAuthorizationKey"]));
                        OleDbCommand command = new OleDbCommand(str5, selectConnection);
```

#### /sfb/app/assign-waiting-list.aspx

##### Description

TODO: Ask Shane.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbContact
+ twbMember
+ twbSchedule
+ twbServiceArea
+ twbServiceAreaAuthorization
+ twbWaitingList

##### Queries

```
                    string cmdText = "SELECT WaitingListKey FROM twbWaitingList WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num5);
                    OleDbCommand command2 = new OleDbCommand(cmdText, connection) {
                        command2.CommandText = "UPDATE twbAuthorization SET Waiting = 0 WHERE AuthorizationKey = (SELECT AuthorizationKey FROM twbServiceAreaAuthorization WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num5) + ")";
                        command2.CommandText = "UPDATE twbAuthorization SET Waiting = -1 WHERE AuthorizationKey = (SELECT AuthorizationKey FROM twbServiceAreaAuthorization WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num5) + ")";
                        command2.CommandText = "SELECT Email FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.CaseworkerID = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num5);
                            command2.CommandText = "SELECT twbAuthorization.AuthorizationKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = " + Conversions.ToString(num5);
                OleDbCommand command = new OleDbCommand("SELECT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name', AuthorizationID, AuthorizationTypeID, DayPhone,  ServiceArea, HoursUsed, StartDate, HoursRemaining, EndDate, Waiting, twbServiceAreaAuthorization.ServiceAreaKey, (SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Caseworker' FROM twbContact WHERE twbContact.ContactKey = twbAuthorization.CaseworkerID) As 'Caseworker', CaseworkerID FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE twbServiceAreaAuthorization.ServiceAreaAuthorizationKey =" + Conversions.ToString(num3), connection);
                    command.CommandText = "SELECT (MemberLastName + ', ' + MemberFirstName) As 'MemberName' FROM twbMember INNER JOIN twbWaitingList ON twbMember.MemberKey = twbWaitingList.MemberKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num3);
                                command.CommandText = "SELECT * FROM twbWaitingList INNER JOIN twbSchedule ON twbSchedule.WaitingListKey = twbWaitingList.WaitingListKey WHERE ServiceAreaAuthorizationKey = " + Conversions.ToString(num3);
```

### Client Schedules

Supposed to be used for planning for the daily schedules of clients, and checking whether there is capacity for new clients. In reality Shane uses Excel for scheduling, and inputs the finished schedule. There is a report (see [Client Schedule Report](https://slate.societyfortheblind.org/sfb/app/report-cschedule.aspx)) to list schedule information, but there is no option to break it down to show clients in a class for example.

An excerpt from an invoice:

> **Schedule Information:**
> Monday: 8:00 am, 10:00 am
> Wednesday: 8:00 am, 10:00 am
> Friday: 8:00 am, 10:00 am

The only difference between this page and the [Waiting List](#user-content-waiting-list) above is that initial page contains the query parameter `Type=Scheduled`.

TODO: Ask Shane for more.

### Billing

Shows all clients who had active authorizations in a given month (one authorization per line), and therefore may have consumed services.

The current layout isn't the best, and here's why:

#### The billing process

1. Shane changes the month on the initial page to match
   the  previous month,  and looks  at each  line items
   individually. At the bottom of each entry there is a
   table showing  the "Lesson  Date" and  "Billed Time"
   among others, and he makes sure that the billed time
   units  match reality  (e.g., if  it zero,  make sure
   that  student  was  absent by  checking  the  lesson
   notes)

2. I  visit   every  line   item  and  print   out  the
   corresponding   progress   report  ("View   Progress
   Report") and invoice ("View Invoice").

3. Minda enters  the data from the  hard copies into
   QuickBooks.

#### [/sfb/app/billing.aspx](https://slate.societyfortheblind.org/sfb/app/billing.aspx)

##### Description

Show clients with active authorizations in a given month.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbContactType
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
                new OleDbDataAdapter("SELECT DISTINCT twbAuthorization.AuthorizationKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + '; (' + BillingName + ') - ' + CAST(ROUND(HoursRemaining, 4) As varchar(10)) + ' ' + twbAuthorizationType.AuthorizationTypeCode + ' remaining') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization On twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorizationType On twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbServiceArea On twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey INNER JOIN twbCCR On twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey WHERE ContactType = 'Client' AND ContactValue <> 0" + str2 + " ORDER BY Name", selectConnection).Fill(dataSet, "Clients");
```

#### [/sfb/app/view-billing.aspx?AuthKey=12345&Month=2&Year=2019](https://slate.societyfortheblind.org/sfb/app/view-billing.aspx?AuthKey=12345&Month=2&Year=2019)

##### Description

Shows the billing information for a specific authorization.

The "Billed Time" in the table at the bottom is generated from "Billed Units" in lesson notes. There are five buttons below the table, but only "Update Billing Address" and "View Invoice" will be covered in the following sections as the others all pertain to progress reports, and those have been discussed in [Progress Reports](#user-content-progress-reports).

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbEmployee
+ twbIntakeBilling
+ twbMember
+ twbMonthlyHours
+ twbProgress
+ twbSchedule
+ twbServiceArea
+ twbServiceAreaAuthorization
+ twbWaitingList

##### Queries

```
            string[] strArray = new string[] { "SELECT ProgressKey FROM twbProgress INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbProgress.ServiceAreaAuthorizationKey WHERE DATEPART(month, ProgressDate)= ", str, " AND DATEPART(year, ProgressDate) = ", Conversions.ToString(year), " AND AuthorizationKey = ", Conversions.ToString(num) };
            string selectCommandText = "SELECT Top 1 ServiceAreaAuthorizationKey FROM twbServiceAreaAuthorization  WHERE AuthorizationKey = " + Conversions.ToString(num);
                OleDbCommand command = new OleDbCommand("SELECT AuthorizationID, AuthorizationTypeID, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As Name, TotalHours, CaseworkerID FROM twbAuthorization INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.ContactKey WHERE AuthorizationKey = " + Conversions.ToString(num), connection);
                    OleDbDataReader reader2 = new OleDbCommand("SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As MemberName, Hours FROM twbContact INNER JOIN twbMonthlyHours ON twbMonthlyHours.ContactKey = twbContact.ContactKey WHERE twbContact.ContactKey = " + this.hidCaseworkerKey.Value, connection).ExecuteReader();
                    new OleDbDataAdapter("SELECT DISTINCT (MemberFirstName + ' ' + MemberLastName) As MemberName FROM twbMember INNER JOIN twbCCR ON twbCCR.MemberKey = twbMember.MemberKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE twbAuthorization.AuthorizationKey = " + Conversions.ToString(num), connection).Fill(dataSet, "Instructors");
                    string[] strArray = new string[] { "SELECT ISNULL(dbo.GetInstructionalHoursUsedForClass(auth.AuthorizationKey, BilledUnits), 0) + ISNULL((SELECT dbo.GetInstructionalHoursUsedForClass(auth.AuthorizationKey, BilledUnits) FROM twbIntakeBilling INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbIntakeBilling.AuthorizationKey INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE EnteredDate >= CAST('", str2, "' AS DATETIME) AND EnteredDate < CAST('", str4, "' AS DATETIME) AND twbIntakeBilling.AuthorizationKey = ", Conversions.ToString(num), "),0)  As 'BilledHours' FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization auth ON auth.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE LessonDate >= CAST('", str2, "' AS DATETIME) AND LessonDate < CAST('" };
                    command.CommandText = "SELECT * FROM twbEmployee WHERE ContactKey = " + this.hidCaseworkerKey.Value;
                    strArray = new string[] { "SELECT '<a href=\"view-lesson-note.aspx?CCRKey=' +CAST(CCRKey As varchar(15)) + '\">' + CAST(LessonDate AS VARCHAR(11)) + '</a>' AS 'Lesson Date', dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits) AS 'Billed Time', ('$' + CAST(RateHourly As varchar(11))) As 'Rate', BillingName AS 'Service Area', AuthorizationTypeCode FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType ON twbAuthorizationType.AuthorizationTypeID = twbAuthorization.AuthorizationTypeID INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE LessonDate >= CAST('", str2, "' AS DATETIME) AND LessonDate < CAST('", str4, "' AS DATETIME) AND twbServiceAreaAuthorization.AuthorizationKey = ", Conversions.ToString(num), " UNION ALL SELECT CAST(EnteredDate AS VARCHAR(11)) AS 'Lesson Date', dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits) AS 'Billed Time', ('$' + CAST(RateHourly As varchar(11))) As 'Rate', (BillingName + ' - Intake Billing') AS 'Service Area', AuthorizationTypeCode FROM twbIntakeBilling INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbIntakeBilling.AuthorizationKey INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType ON twbAuthorizationType.AuthorizationTypeID = twbAuthorization.AuthorizationTypeID INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE EnteredDate >= CAST('", str2, "' AS DATETIME) AND EnteredDate < CAST('" };
                    command.CommandText = "SELECT twbSchedule.* FROM twbSchedule INNER JOIN twbWaitingList ON twbWaitingList.WaitingListKey = twbSchedule.WaitingListKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbWaitingList.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE twbAuthorization.AuthorizationKey = " + Conversions.ToString(num);
            string[] strArray = new string[] { "SELECT ProgressKey FROM twbProgress INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbProgress.ServiceAreaAuthorizationKey WHERE DATEPART(month, ProgressDate)= ", str, " AND DATEPART(year, ProgressDate) = ", Conversions.ToString(year), " AND AuthorizationKey = ", Conversions.ToString(num) };
```
#### [/sfb/app/billing-address.aspx?ContactKey=1234&AuthKey=12345](https://slate.societyfortheblind.org/sfb/app/billing-address.aspx?ContactKey=1234&AuthKey=12345)

##### Description

Update billing address.

##### Used by

+ CORE

##### DB tables touched

+ twbEmployee

##### Queries

```
                OleDbDataReader reader = new OleDbCommand(Conversions.ToString(Operators.ConcatenateObject("SELECT * FROM twbEmployee WHERE ContactKey = ", right)), connection).ExecuteReader();
                    new OleDbCommand(cmdText, connection).ExecuteNonQuery();
```

#### [/sfb/app/invoice.aspx?AuthKey=12345&Month=2&Year=2018](https://slate.societyfortheblind.org/sfb/app/invoice.aspx?AuthKey=12345&Month=2&Year=2018)

##### Description

Show monthly invoice for an authorization.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbEmployee
+ twbIntakeBilling
+ twbMember
+ twbMonthlyHours
+ twbSchedule
+ twbServiceArea
+ twbServiceAreaAuthorization
+ twbWaitingList

##### Queries

```
            OleDbCommand command = new OleDbCommand("SELECT AuthorizationID, twbAuthorization.AuthorizationTypeID, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As Name, TotalHours, (SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';')  As 'MemberName' FROM twbContact INNER JOIN twbAuthorization ON twbContact.ContactKey = twbAuthorization.CaseworkerID WHERE AuthorizationKey = " + Conversions.ToString(num) + ") As 'MemberName', Hours, CaseworkerID FROM twbAuthorization INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.ContactKey INNER JOIN twbMonthlyHours ON twbMonthlyHours.ContactKey = twbAuthorization.CaseworkerID WHERE AuthorizationKey = " + Conversions.ToString(num), connection);
                new OleDbDataAdapter("SELECT DISTINCT (MemberFirstName + ' ' + MemberLastName) As MemberName, MemberEmail FROM twbMember INNER JOIN twbCCR ON twbCCR.MemberKey = twbMember.MemberKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE twbAuthorization.AuthorizationKey = " + Conversions.ToString(num), connection).Fill(dataSet, "Instructors");
                string[] strArray = new string[] { "SELECT ISNULL(SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits)), 0)  + ISNULL((SELECT SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits)) FROM twbIntakeBilling INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbIntakeBilling.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE EnteredDate >= CAST('", str3, "' AS DATETIME) AND EnteredDate < CAST('", str5, "' AS DATETIME) AND twbIntakeBilling.AuthorizationKey = ", Conversions.ToString(num), "), 0)  As 'BilledHours' FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE LessonDate >= CAST('", str3, "' AS DATETIME) AND LessonDate < CAST('" };
                command.CommandText = "SELECT * FROM twbEmployee WHERE ContactKey = " + Conversions.ToString(num2);
                strArray = new string[] { "SELECT CAST(LessonDate AS VARCHAR(11)) AS 'LessonDate', twbAuthorizationType.AuthorizationTypeCode as AuthType, dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits) AS 'BilledHours', ('$' + CAST(RateHourly As varchar(11))) As 'HourlyRate', BillingName AS 'ServiceArea' FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey WHERE LessonDate >= CAST('", str3, "' AS DATETIME) AND LessonDate < CAST('", str5, "' AS DATETIME) AND twbServiceAreaAuthorization.AuthorizationKey = ", Conversions.ToString(num), " UNION ALL SELECT CAST(EnteredDate AS VARCHAR(11)) AS 'LessonDate', twbAuthorizationType.AuthorizationTypeCode as AuthType, dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits) AS 'BilledHours', ('$' + CAST(RateHourly As varchar(11))) As 'HourlyRate', (BillingName + ' - Intake Billing') AS 'ServiceArea' FROM twbIntakeBilling INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbIntakeBilling.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID WHERE EnteredDate >= CAST('", str3, "' AS DATETIME) AND EnteredDate < CAST('" };
                command.CommandText = "SELECT twbSchedule.* FROM twbSchedule INNER JOIN twbWaitingList ON twbWaitingList.WaitingListKey = twbSchedule.WaitingListKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbWaitingList.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE twbAuthorization.AuthorizationKey = " + Conversions.ToString(num);
```
### Volunteer Hours

Not used at all. Not documenting it any further as it wouldn't reflect current practices by the Resource Development department.

### Volunteer Schedules

Not  used at  all.  Not documenting  it any  further
as  it wouldn't  reflect  current  practices by  the
Resource Development department.

### Outside Agency Contact Report

Basically for looking up payment sources (i.e., counselor + organization).

#### [/sfb/app/report-psi.aspx](https://slate.societyfortheblind.org/sfb/app/report-psi.aspx)

##### Description

See main description.

##### Used by

Probably CORE.

##### DB tables touched

+ twbContact
+ twbContactType
+ twbEmergencyContact

##### Queries

```
            new OleDbDataAdapter("SELECT DISTINCT ('<a href=''mailto:' + Email + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';' + '</a>') As 'Name', (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As NameSort, (Address1 + '<br>' + Address2 + '<br>' + City + '<br>' + State + '<br>' + Zip) As 'Contact', (SELECT (ECName + '<br>Rel: ' + Relationship + '<br>' + 'Day Phone: ' + ECDayPhone + '<br>Evening Phone: ' + ECEveningPhone + '<br>Other Phone: ' + ECOtherPhone) As 'EAddress' FROM twbEmergencyContact WHERE twbEmergencyContact.ContactKey = twbContact.ContactKey) As 'EmContact', ContactType, Crossstreets As 'Cross', ('Day Phone: ' + DayPhone + '<br>Evening Phone: ' + EveningPhone + '<br>Other Phone: ' + OtherPhone) As 'Phone' FROM twbContact INNER JOIN twbContactType On twbContactType.ContactKey = twbContact.ContactKey WHERE ContactType = 'Outside Agency' AND ContactValue <> 0 ORDER BY " + this.ViewState["sortField"].ToString() + " " + this.ViewState["sortDirection"].ToString(), selectConnection).Fill(dataSet, "Results");
```

### Instructional Time Taught this Month

#### [/sfb/app/view-hours.aspx](https://slate.societyfortheblind.org/sfb/app/view-hours.aspx)

##### Description

Shows instructional time taught for the logged in user.

##### Used by

No one?

##### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
                string[] strArray = new string[] { "SELECT SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits)) As 'Billed Time', SUM(BilledUnits) As 'BilledUnits', SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, InstructionalUnits)) As 'Instructional Time', SUM(InstructionalUnits) As 'InstructionalUnits' FROM twbCCR INNER JOIN twbServiceAreaAuthorization on twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization on twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE MemberKey = ", this.Request.Cookies["Member"]["MemberID"], " AND LessonDate >= '", str3, "' AND LessonDate < '", str2, "' " };
                OleDbDataReader reader = new OleDbCommand(string.Concat(strArray), connection).ExecuteReader();
                strArray = new string[] { "SELECT CAST(LessonDate AS VARCHAR(11)) AS 'Lesson Date', twbAuthorizationType.AuthorizationTypeCode As 'Authorization Type', dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits) AS 'Billed Time', BilledUnits As 'Billed Units', dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, InstructionalUnits) AS 'Instructional Time', InstructionalUnits As 'Instructional Units', ServiceArea AS 'Service Area', (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Client' FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType on twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.ContactKey WHERE twbCCR.MemberKey = ", this.Request.Cookies["Member"]["MemberID"], " AND LessonDate >= '", str3, "' AND LessonDate < '", str2, "' UNION ALL SELECT CAST(LessonDate AS VARCHAR(11)) AS 'Lesson Date', twbAuthorizationType.AuthorizationTypeCode As 'Authorization Type', dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits) AS 'Billed Time', BilledUnits As 'Billed Units', dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, InstructionalUnits) AS 'Instructional Time', InstructionalUnits As 'Instructional Units', ServiceArea AS 'Service Area', (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Client' FROM twbCCR INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbCCR.ServiceAreaKey INNER JOIN twbServiceAreaAuthorization ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType on twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbContact ON twbContact.ContactKey = twbCCR.ContactKey WHERE twbCCR.MemberKey = ", this.Request.Cookies["Member"]["MemberID"], " AND LessonDate >= '" };
```

## Staff Tools

### Intakes and Contacts

Intakes and contacts are used interchangeably. Every new client, payment source, SLATE user etc., comes through [New Intake](#user-content-new-intake).

The biggest issue, especially pressing for SIP, is that there is no way to mark contacts (and later filter them) based on special events, such as when a client moves outside SFTB's service are, dies, etc. Pat notes these by changing the "Day Phone" section to 000-000-0000, and putting a note in "Contact Change Notes", but this is really hard to maintain.

#### [/sfb/app/intakes.aspx](https://slate.societyfortheblind.org/sfb/app/intakes.aspx)

##### Description

Show all clients.

##### Used by

+ CORE
+ SIP
+ Resource Development

##### DB tables touched

+ twbContact
+ twbContactType
+ twbIntake

##### Queries

```
                string[] strArray = new string[] { "SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + '; (' + ", str8, " + ') ' + CAST(IntakeDate As Varchar(11))) As 'Name', ", str6, " FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbIntake on twbIntake.ContactKey = twbContact.ContactKey WHERE ", str3, " AND ContactValue <> 0", str2, " ORDER BY " };
```

#### /sfb/app/del-intake.aspx

##### Description

Delete a contact and intake.

##### Used by

+ CORE
+ SIP
+ Resource Development

##### DB tables touched

+ twbContact

##### Queries

```
            OleDbCommand command = new OleDbCommand("DELETE FROM twbContact WHERE twbContact.ContactKey = " + Conversions.ToString(num), connection);
                OleDbDataReader reader = new OleDbCommand("SELECT * FROM twbContact WHERE twbContact.ContactKey = " + Conversions.ToString(num), connection).ExecuteReader();
```

#### [/sfb/app/new-intake.aspx](https://slate.societyfortheblind.org/sfb/app/new-intake.aspx)

##### Description

Same as [New Intake](#user-content-new-intake).

#### [/sfb/app/edit-intake.aspx?ContactKey=1234](https://slate.societyfortheblind.org/sfb/app/edit-intake.aspx?ContactKey=1234)

##### Description

Edit an intake/contact.

##### Used by

+ CORE
+ SIP
+ Resource Development

##### DB tables touched

+ twbClientMedical
+ twbContact
+ twbContactType
+ twbDemographics
+ twbEmergencyContact
+ twbIntake
+ twbIntakeServices
+ twbMember
+ twbServices

##### Queries

```
                objArgs.IsValid = Conversions.ToInteger(new OleDbCommand("SELECT Count(ContactKey) FROM twbContact WHERE SSN LIKE '" + this.txtSSN.Value + "'", connection).ExecuteScalar()) <= 0;
                    OleDbCommand command3 = new OleDbCommand("spwbEditContact", connection) {
                    command3.CommandText = "DELETE FROM twbContactType WHERE ContactKey = " + Conversions.ToString(num);
                OleDbCommand command = new OleDbCommand("SELECT * FROM twbContact INNER JOIN twbIntake ON twbContact.ContactKey = twbIntake.ContactKey WHERE twbContact.ContactKey = " + Conversions.ToString(num), connection);
                                    OleDbDataReader reader3 = new OleDbCommand(Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT MemberFirstName, MemberLastName FROM twbMember WHERE MemberKey = ", reader["MemberKey"])), connection2).ExecuteReader();
                                command.CommandText = "SELECT ContactType FROM twbContactType WHERE ContactKey = " + Conversions.ToString(num) + " AND ContactValue <> 0";
```

#### [/sfb/app/view-intake.aspx?ContactKey=1234](https://slate.societyfortheblind.org/sfb/app/view-intake.aspx?ContactKey=1234)

##### Description

View an intake/contact.

##### Used by

+ CORE
+ SIP
+ Resource Development

##### DB tables touched

+ twbClientMedical
+ twbContact
+ twbDemographics
+ twbEmergencyContact
+ twbIntake
+ twbIntakeServices
+ twbMember
+ twbServices

##### Queries

```
                OleDbCommand command = new OleDbCommand("SELECT * FROM twbContact INNER JOIN twbIntake ON twbContact.ContactKey = twbIntake.ContactKey WHERE twbContact.ContactKey = " + Conversions.ToString(num), connection);
                    OleDbDataReader reader2 = new OleDbCommand(Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT MemberFirstName, MemberLastName FROM twbMember WHERE MemberKey = ", reader["MemberKey"])), connection2).ExecuteReader();
                command.CommandText = "SELECT * FROM twbClientMedical INNER JOIN twbContact ON twbClientMedical.ContactKey = twbContact.ContactKey WHERE twbContact.ContactKey = " + Conversions.ToString(num);
                        string cmdText = Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT (twbContact.LastName + ', ' + twbContact.FirstName + ' ' + twbContact.MiddleName) As 'Name'  FROM twbContact WHERE twbContact.ContactKey = ", reader["CaseworkerKey"]));
                        str2 = Conversions.ToString(new OleDbCommand(cmdText, connection3).ExecuteScalar());
                command.CommandText = "SELECT * FROM twbEmergencyContact INNER JOIN twbContact ON twbEmergencyContact.ContactKey = twbContact.ContactKey WHERE twbContact.ContactKey = " + Conversions.ToString(num);
                command.CommandText = "SELECT * FROM twbDemographics WHERE ContactKey =" + Conversions.ToString(num);
                command.CommandText = "SELECT * FROM twbIntake INNER JOIN twbContact ON twbIntake.ContactKey = twbContact.ContactKey WHERE twbContact.ContactKey = " + Conversions.ToString(num);
                string selectCommandText = "SELECT twbServices.Name FROM twbServices INNER JOIN twbIntakeServices ON twbIntakeServices.ServicesKey = twbServices.ServicesKey WHERE twbIntakeServices.ServiceType = 'Inside' AND twbIntakeServices.IntakeKey = " + Conversions.ToString(num);
                selectCommandText = "SELECT twbServices.Name FROM twbServices INNER JOIN twbIntakeServices ON twbIntakeServices.ServicesKey = twbServices.ServicesKey WHERE twbIntakeServices.ServiceType = 'Outside' AND twbIntakeServices.IntakeKey = " + Conversions.ToString(num);
```

### New Intake

#### [/sfb/app/new-intake.aspx](https://slate.societyfortheblind.org/sfb/app/new-intake.aspx)

##### Description

Add new contact (client, payment source, volunteer, etc.). Below is a snapshot of each intake page with short description of non-trivial fields. Each page has a checkbox at the top saying "This contact is also a Payment Source".

###### Page 1

+ Information Entered by
+ Date Entered
+ **Active**

  Probably  not  used  because  it is  always  set  to
  active.

+ Intake Date
+ First Name
+ Middle Initial
+ Last Name
+ Company
+ Address1
+ Address2
+ Suite or apt number
+ City
+ State
+ Zip
+ County
+ **SIR Region**

  TODO: Ask Pat.

+ **Nearest major cross street**

  TODO: Ask Pat and Shane.

+ Daytime Phone
+ Evening Phone
+ Other Phone
+ Email Address
+ **Remove from mailing list**

  Allow clients to opt out from the mailed newsletters.

+ Gender
+ Select an Ethnicity
+ Birthdate
+ **Social Security Number**

  We are not collecting any, therefore not needed.

+ **Preferred contact medium for mailings**

  TODO: Ask Kathleen and Pat whether this is still pertinent.

+ Criminal History:

  ```text
  Have you ever been convicted of a crime/felony?
    If "Other", please specify:
    If yes, what and when did the convictions occur? What county did this conviction occur in?
  Are you currently on parole?
    If yes, what are you on parole for?
  Is there any other information regarding your criminal history that we should know about?
  ```

###### Page 2

**Emergency Contact Information**
+ Emergency Contact Name
+ Relationship to Client
+ Day Phone
+ Evening Phone
+ Pager/Other Phone

**Medical Information**
+ Cause of Visual Impairment
+ Date of onset of blindness
+ Other relevant medical or physical conditions
+ Diabetic
+ Hearing loss
+ Difficulty walking

**Previous services**
+ Agency
+ Blindness skills learned thus far
+ When served

**Other**
+ Referred by
+ Are you a veteran?
+ Current client of
+ Name of Payment Source

**TITLE VII Demographics**
+ Highest Level of Education Completed
+ Type of Living Arrangement

  ```text
  Live Alone
  Live with Spouse (NOTE: we use this for any family living arrangement)
  Live with Personal Care Assistant
  Live with Other
  Data not recorded
  ```

+ Setting of Residence

  ```text
  Private Residence - apartment or home (alone, or with roommate, personal care assistant, family, or other person)
  Community Residential
  Assisted Living Center
  Nursing Home or Long Term Care Facility
  Other
  Data not recorded
  ```

+ Visual Impairment at Time of Intake (as reported by the individual)

###### Page 3

A list of checkboxes showing services provided by Society For The Blind:

**Low Vision Clinic**
+ full evaluation
+ shorter demo appointment

**Youth Enrichment Program**
+ Blind Olympics
+ Transportation to or from the Society

**Youth Enrichment Program**
+ Monthly event
+ Weekend Technology retreat
+ Summer Camp
+ Goal Ball

**Store Tour**
+ Blindness Product Seminar

**Counseling/Social Work**
+ Individual counseling
+ Family Support Seminar or counseling
+ Diabetes Education and Management
+ Blindness Discussion Group

**Cane Travel**
+ Full Curriculum
+ route only

**Braille**
+ Full Curriculum
+ Nemith code

**Career Development Program**
+ ACE Program
+ VEP
+ EMPOWER 30 day evaluation

**Senior Impact Project**
+ 6 day Retreat
+ Support group or community integration activity
+ One day programs or home visits

**Independent Living Skills**
+ Full Curriculum
+ Personal Organization Class

**Personal Volunteer Program**
+ reading
+ shopping

**Adaptive Technology Program**
+ Full curriculum
+ Typing
+ Screen reading programs

**Adaptive Technology Program**
+ Stand alone scanners
+ Screen Magnification
+ Note-Takers or Digital recording devices

**Rehabilitation Technology Services**
+ Installing adaptive software
+ Marking/adapting workplace environment
+ Custom Software Scripting

###### Page 4

A list of checkboxes showing services provided by outside blindness services. Rendering it as code to keep indentations, because it is hard to decide whether there are headings or the sublevels are just random.

```text
 Social Security Benefits counseling
 Regional Transit
Paratransit
    Mobility Training
 DMV parking placard
 Apply for Department of Rehabilitation
Department of Rehabilitation
    Client Assistance Program
Veterans Administration
    Local options
    Palo Alto Center
 Blindness consumer groups
 Access news/ Newsline
 Talking Book Library
 Appliance/device dial marking
 Utility Disabled discount Programs
 In-Home Supportive Services
outdoor and recreation programs
    Tandem bicycling groups
    Skiing Groups
 Tapes/videos about blindness
 Reading list on blindness
 Blindness listservs, websites and newsgroups
 Braille Forum and Monitor
 Free 411 service
 CTAP California Telephone Access Program
 Other services you are interested in
 Advocacy
 Volunteer for the society
```

+ **Work completed**

  This is used  by CORE and SIP, as a  rolling list of
  notes, but it is almost impossible to maintain as it
  is a simple text box.

+ **Notes**

  Similar to "Work completed" above.

TODO: Ask  Shane and Pat  for more info on  the last
      two textboxes.

###### Page 5

Summary page for the previous four pages.

##### Used by

+ CORE
+ SIP

##### DB tables touched

+ twbClientMedical
+ twbContact
+ twbContactType
+ twbDemographics
+ twbEmergencyContact
+ twbEmployee
+ twbIntake
+ twbIntakeServices
+ twbServices

##### Queries

```
            objArgs.IsValid = Conversions.ToInteger(new OleDbCommand("SELECT Count(ContactKey) FROM twbContact WHERE SSN LIKE '" + this.txtSSN.Value + "'", connection).ExecuteScalar()) <= 0;
                                new OleDbDataAdapter("SELECT (LastName + ', ' + FirstName + ' - ' + Company) As 'Name', twbContact.ContactKey FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType LIKE 'Outside Agency' AND ContactValue <> 0 ORDER BY Name", selectConnection).Fill(dataSet, "Caseworkers");
                            string cmdText = "SELECT ServicesKey, Name, ServicesGroup FROM twbServices WHERE Inside = 1 ORDER BY DisplayPrecedence, ServicesGroup";
                            OleDbDataReader reader = new OleDbCommand(cmdText, connection).ExecuteReader();
                        OleDbCommand command2 = new OleDbCommand("SELECT MAX(ServicesKey) FROM twbServices WHERE Inside = 1", connection);
                        command2.CommandText = "SELECT ServicesKey, Name, ServicesGroup FROM twbServices WHERE Outside = 1 ORDER BY DisplayPrecedence, ServicesGroup";
                                OleDbCommand command5 = new OleDbCommand("spwbAddContact", connection);
                            OleDbCommand command3 = new OleDbCommand("SELECT MAX(ServicesKey) FROM twbServices WHERE Outside = 1", connection);
                                        string cmdText = "SELECT (twbContact.LastName + ', ' + twbContact.FirstName + ' ' + twbContact.MiddleName) As 'Name'  FROM twbContact WHERE twbContact.ContactKey = " + this.hidSelCaseworker.Value;
                                        str18 = Conversions.ToString(new OleDbCommand(cmdText, connection5).ExecuteScalar());
                                    string selectCommandText = "SELECT twbServices.Name FROM twbServices WHERE twbServices.ServicesKey IN (" + this.hidInsideServices.Value + ")";
                                    selectCommandText = "SELECT twbServices.Name FROM twbServices WHERE twbServices.ServicesKey IN (" + this.hidOutsideServices.Value + ")";
```

### Student Plan

TODO: Ask Shane, but apparently this is being used. Documenting pages below without adding anything to the descriptions for now.

#### [/sfb/app/student-plan.aspx?Expired=False&MyClients=False](https://slate.societyfortheblind.org/sfb/app/student-plan.aspx?Expired=False&MyClients=False)

##### Description


##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbServiceAreaAuthorization
+ twbWaitingList

##### Queries

```
                    string[] strArray = new string[] { " AND twbAuthorization.AuthorizationKey IN (SELECT twbAuthorization.AuthorizationKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbCCR On twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey WHERE twbCCR.MemberKey = ", this.Request.Cookies["Member"]["MemberID"], " UNION SELECT twbAuthorization.AuthorizationKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbWaitingList On twbWaitingList.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey WHERE twbWaitingList.MemberKey = ", this.Request.Cookies["Member"]["MemberID"], ")" };
                new OleDbDataAdapter("SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name'  FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey  INNER JOIN twbAuthorization On twbAuthorization.ContactKey = twbContact.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0 " + str3 + str5 + " ORDER BY Name", selectConnection).Fill(dataSet, "Clients");
```

#### [/sfb/app/edit-student-plan.aspx?ContactKey=1234](https://slate.societyfortheblind.org/sfb/app/edit-student-plan.aspx?ContactKey=1234)

##### Description


##### Used by

+ CORE

##### DB tables touched

+ twbContact
+ twbServiceArea
+ twbServicePlan
+ twbServicePlanGoals

##### Queries

```
                        OleDbCommand command2 = new OleDbCommand("SELECT ServicePlanKey FROM twbServicePlan WHERE ContactKey = " + this.hidContactKey.Value, connection);
                            command2.CommandText = "SELECT ServicePlanKey FROM twbServicePlan WHERE ContactKey = " + this.hidContactKey.Value;
                OleDbCommand command = new OleDbCommand("SELECT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name' FROM twbContact WHERE twbContact.ContactKey =" + Conversions.ToString(num), connection);
                                command.CommandText = "SELECT * FROM twbServicePlan WHERE ContactKey = " + Conversions.ToString(num);
                                    string selectCommandText = "SELECT Goal, ServiceArea, Point, '' As GoalType, twbServicePlanGoals.Completion, CAST(twbServicePlanGoals.StartDate As Varchar(11)) As StartDate, CAST(twbServicePlanGoals.EndDate As Varchar(11)) As EndDate, ('<a href=\"edit-goal.aspx?SPGKey=' + CAST(ServicePlanGoalKey AS varchar(9)) + '\">Edit</a>') As 'Edit', ('<a href=\"del-goal.aspx?SPGKey=' + CAST(ServicePlanGoalKey AS varchar(9)) + '\">Delete</a>') As 'Delete'  FROM twbServicePlanGoals INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServicePlanGoals.ServiceAreaKey INNER JOIN twbServicePlan ON twbServicePlanGoals.ServicePlanKey = twbServicePlan.ServicePlanKey WHERE ContactKey = " + Conversions.ToString(num);
```

#### [/sfb/app/student-plan-report.aspx?ContactKey=1234](https://slate.societyfortheblind.org/sfb/app/student-plan-report.aspx?ContactKey=1234)

##### Description


##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbContact
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization
+ twbServicePlan
+ twbServicePlanGoals

##### Queries

```
            OleDbCommand command = new OleDbCommand("SELECT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name' FROM twbContact WHERE twbContact.ContactKey =" + Conversions.ToString(num), connection);
            command.CommandText = "SELECT DISTINCT (FirstName + ' ' + MiddleName + ' ' + LastName + ' - ' + Company + ';') As MemberName FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.CaseworkerID = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE twbAuthorization.ContactKey = " + Conversions.ToString(num);
            string selectCommandText = "SELECT twbServicePlan.*, CAST(twbServicePlan.StartDate As varchar(11)) As StartDateV, CAST(twbServicePlan.EndDate As varchar(11)) As EndDateV FROM twbServicePlan WHERE ContactKey = " + Conversions.ToString(num);
            selectCommandText = "SELECT twbServicePlanGoals.*, CAST(twbServicePlanGoals.StartDate As varchar(11)) As StartDateV, CAST(twbServicePlanGoals.EndDate As varchar(11)) As EndDateV, '' As ComBool, '' As ComTimeBool, twbServiceArea.ServiceArea FROM twbServicePlanGoals INNER JOIN twbServiceArea ON twbServicePlanGoals.ServiceAreaKey = twbServiceArea.ServiceAreaKey INNER JOIN twbServicePlan ON twbServicePlanGoals.ServicePlanKey = twbServicePlan.ServicePlanKey WHERE ContactKey = " + Conversions.ToString(num) + " AND Point = 1 ORDER BY twbServiceArea.ServiceArea";
            selectCommandText = "SELECT twbServicePlanGoals.*, (MemberLastName + ', ' + MemberFirstName) As 'Instructor', CAST(twbServicePlanGoals.StartDate As varchar(11)) As StartDateV, CAST(twbServicePlanGoals.EndDate As varchar(11)) As EndDateV, '' As ComBool, '' As ComTimeBool, twbServiceArea.ServiceArea FROM twbServicePlanGoals INNER JOIN twbServiceArea ON twbServicePlanGoals.ServiceAreaKey = twbServiceArea.ServiceAreaKey INNER JOIN twbServicePlan ON twbServicePlanGoals.ServicePlanKey = twbServicePlan.ServicePlanKey INNER JOIN twbMember ON twbServicePlanGoals.MemberKey = twbMember.MemberKey WHERE ContactKey = " + Conversions.ToString(num) + " AND Point = 2 ORDER BY twbServiceArea.ServiceArea";
            selectCommandText = "SELECT twbServicePlanGoals.*, (MemberLastName + ', ' + MemberFirstName) As 'Instructor', CAST(twbServicePlanGoals.StartDate As varchar(11)) As StartDateV, CAST(twbServicePlanGoals.EndDate As varchar(11)) As EndDateV, '' As ComBool, '' As ComTimeBool, twbServiceArea.ServiceArea FROM twbServicePlanGoals INNER JOIN twbServiceArea ON twbServicePlanGoals.ServiceAreaKey = twbServiceArea.ServiceAreaKey INNER JOIN twbServicePlan ON twbServicePlanGoals.ServicePlanKey = twbServicePlan.ServicePlanKey INNER JOIN twbMember ON twbServicePlanGoals.MemberKey = twbMember.MemberKey WHERE ContactKey = " + Conversions.ToString(num) + " AND Point = 3 ORDER BY twbServiceArea.ServiceArea";
```

### Reports


#### Client Reports

##### [Clients - general search](https://slate.societyfortheblind.org/sfb/app/intake-search.aspx)

###### Description

Find a client based on the following criteria:

+ Keywords
+ Client
+ Contact Type
+ Volunteer Type
+ Outreach Type
+ Payment Source
+ Intake Date Start
+ Intake Date End
+ Lesson Date Start Month
+ Lesson Date End Month
+ Client Age
+ Older Than
+ Younger Than
+ Hours Taught At Least
+ Hours Taught Not More Than
+ Classes Taught At Least
+ Classes Taught Not More Than
+ Units Taught At Least
+ Units Taught Not More Than
+ Number of Absences At Least
+ Gender
+ Select an Ethnicity
+ SIR Region
+ Zip Code
+ County
+ Preferred medium
+ Cause of Visual Impairment
+ Onset of blindness since
+ Current client of?
+ Special Circumstance
+ Society Service
+ Outside Blindness Service

###### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbClientMedical
+ twbClientMedical")
+ twbContact
+ twbContactOutreach
+ twbContactType
+ twbEmergencyContact
+ twbIntake
+ twbIntakeServices
+ twbIntakeServices")
+ twbIntakeVolunteer
+ twbOutreach
+ twbServiceAreaAuthorization
+ twbServices

###### Queries

```
            strArray = new string[] { "SELECT DISTINCT ('<a href=''mailto:' + Email + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';' + '</a>') As 'Name', (Address1 + '<br>' + Address2 + '<br>' + Suite + '<br>' + City + '<br>' + State + '<br>' + Zip) As 'Contact', (LastName + FirstName + MiddleName + Company) As NameSort, (SELECT (ECName + '<br>Rel: ' + Relationship + '<br>' + 'Day Phone: ' + ECDayPhone + '<br>Evening Phone: ' + ECEveningPhone + '<br>Other Phone: ' + ECOtherPhone) As 'EAddress' FROM twbEmergencyContact WHERE twbEmergencyContact.ContactKey = twbContact.ContactKey) As 'EmContact', ('<a href=''edit-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>Edit</a> or <a href=''view-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>View</a>') As 'More Info', Crossstreets As 'Cross', ('Day Phone: ' + DayPhone + '<br>Evening Phone: ' + EveningPhone + '<br>Other Phone: ' + OtherPhone) As 'Phone', (CAST(twbAuthorization.NotesTxt As VARCHAR(255))) As NotesTxt, CASE WHEN Active = 0 THEN 'No' ELSE 'Yes' END As Active FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbIntake ON twbIntake.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey ", str11, str19, "WHERE", str6, str9, str2, str13, str14 };
                                new OleDbDataAdapter("SELECT OutreachKey, OutreachName FROM twbOutreach WHERE Deleted = 0 ORDER BY OutreachName", selectConnection).Fill(dataSet, "Outreach");
                                OleDbCommand command = new OleDbCommand("SELECT ServicesKey, Name, ServicesGroup FROM twbServices WHERE Inside = 1 ORDER BY DisplayPrecedence, ServicesGroup", selectConnection);
                                        command.CommandText = "SELECT ServicesKey, Name, ServicesGroup FROM twbServices WHERE Outside = 1 ORDER BY DisplayPrecedence, ServicesGroup";
                                                new OleDbDataAdapter("SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As ContactName FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbIntake on twbIntake.ContactKey = twbContact.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0 ORDER BY ContactName", selectConnection).Fill(set2, "Clients");
                                                new OleDbDataAdapter("SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As ContactName FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType = 'Outside Agency' AND ContactValue <> 0 ORDER BY ContactName", selectConnection).Fill(set3, "Clients");
```

##### [Clients by Payment Source](https://slate.societyfortheblind.org/sfb/app/report-cbyc.aspx)

###### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbEmployeeGroup
+ twbGroup
+ twbServiceAreaAuthorization

###### Queries

```
            string[] strArray = new string[] { "SELECT DISTINCT ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', Company, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As NameSort, CaseworkerID FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbCCR ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey ", str3, "WHERE ContactType = 'Client' AND ContactValue <> 0", str2, " AND LessonDate >= CAST('", Conversions.ToString(num2), "' + '/1/' + '" };
                        new OleDbDataAdapter("SELECT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContactType.ContactKey = twbContact.ContactKey WHERE ContactType = 'Outside Agency' AND ContactValue <> 0 ORDER BY Name", selectConnection).Fill(dataSet, "Clients");
                        new OleDbDataAdapter("SELECT GroupKey, GroupName FROM twbGroup ORDER BY GroupName", selectConnection).Fill(set2, "Groups");
```

##### [Clients by month and instructor](https://slate.societyfortheblind.org/sfb/app/report-cbym.aspx)

###### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbMember
+ twbMemberGroup
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            strArray = new string[] { "SELECT DISTINCT ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', AuthorizationID As 'ID', CAST(LessonDate AS Varchar(11)) As 'Date', ServiceArea, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As NameSort, LessonDate, twbServiceArea.ServiceAreaKey, MemberKey FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbCCR ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE ContactType = 'Client' AND ContactValue <> 0 ORDER BY ", this.ViewState["sortField"].ToString(), " ", this.ViewState["sortDirection"].ToString() };
                new OleDbDataAdapter("SELECT twbMember.MemberKey, (MemberLastName + ', ' + MemberFirstName) As 'Name' FROM twbMember INNER JOIN twbMemberGroup ON twbMemberGroup.MemberGroupKey = twbMember.MemberGroupKey WHERE Deleted = 0 ORDER BY Name", selectConnection).Fill(dataSet, "Instructors");
                        new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(set2, "ServiceAreas");
```

##### [Clients by referral](https://slate.societyfortheblind.org/sfb/app/report-cbyr.aspx)

###### Description

Find clients by the referral source.

###### DB tables touched

+ twbClientMedical
+ twbContact
+ twbContactType

###### Queries

```
            string[] strArray = new string[] { "SELECT DISTINCT ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name',  ReferredBy As 'Referral', (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As NameSort, ReferredBy FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbClientMedical ON twbClientMedical.ContactKey = twbContact.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0 ORDER BY ", this.ViewState["sortField"].ToString(), " ", this.ViewState["sortDirection"].ToString() };
```

##### [Clients by Service Area](https://slate.societyfortheblind.org/sfb/app/report-cbys.aspx)

###### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            strArray = new string[] { "SELECT DISTINCT ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', ServiceArea, (SELECT (LastName + ', ' + FirstName + ' - ' + Company) As 'Name' FROM twbContact WHERE ContactKey = CaseworkerID) As 'OutsideSource', CAST(StartDate As varchar(11)) As 'Start', CAST(EndDate As varchar(11)) As 'EndDate', (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As NameSort,  twbServiceArea.ServiceAreaKey, StartDate, CaseworkerID FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey INNER JOIN twbCCR ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE ContactType = 'Client' AND ContactValue <> 0", str3, " AND LessonDate >= CAST('", Conversions.ToString(num2), "' + '/1/' + '", Conversions.ToString(num5), "' AS DATETIME)  AND LessonDate < CAST('" };
                        new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "ServiceAreas");
```

##### [Client Chronology Report](https://slate.societyfortheblind.org/sfb/app/report-ccr.aspx)

###### Description

Shows certain events in chronological order.

###### DB tables touched

+ twbContact
+ twbContactType

###### Queries

```
                new OleDbDataAdapter("SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContactType.ContactKey = twbContact.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0 ORDER BY Name", selectConnection).Fill(dataSet, "Clients");
```

##### [Client Emails](https://slate.societyfortheblind.org/sfb/app/report-email.aspx)

###### Description

Find email address of client, if there's any.

###### DB tables touched

+ twbClientMedical
+ twbClientMedical")
+ twbContact
+ twbContactOutreach
+ twbContactType
+ twbEmergencyContact
+ twbIntake
+ twbIntakeServices
+ twbIntakeVolunteer
+ twbOutreach
+ twbServices

###### Queries

```
            strArray = new string[] { "SELECT DISTINCT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name', Email, (Address1 + '<br>' + Address2 + '<br>' + City + '<br>' + State + '<br>' + Zip) As 'Contact', (SELECT (ECName + '<br>Rel: ' + Relationship + '<br>' + 'Day Phone: ' + ECDayPhone + '<br>Evening Phone: ' + ECEveningPhone + '<br>Other Phone: ' + ECOtherPhone) As 'EAddress' FROM twbEmergencyContact WHERE twbEmergencyContact.ContactKey = twbContact.ContactKey) As 'EmContact', ('<a href=''edit-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>Edit</a> or <a href=''view-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>View</a>') As 'More Info', Crossstreets As 'Cross', ('Day Phone: ' + DayPhone + '<br>Evening Phone: ' + EveningPhone + '<br>Other Phone: ' + OtherPhone) As 'Phone' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbIntake ON twbIntake.ContactKey = twbContact.ContactKey ", str7, str14, "WHERE", str5, str6, str, str9, str10 };
                                new OleDbDataAdapter("SELECT OutreachKey, OutreachName FROM twbOutreach WHERE Deleted = 0 ORDER BY OutreachName", selectConnection).Fill(dataSet, "Outreach");
                                OleDbCommand command = new OleDbCommand("SELECT ServicesKey, Name, ServicesGroup FROM twbServices WHERE Inside = 1 ORDER BY DisplayPrecedence, ServicesGroup", selectConnection);
                                        command.CommandText = "SELECT ServicesKey, Name, ServicesGroup FROM twbServices WHERE Outside = 1 ORDER BY DisplayPrecedence, ServicesGroup";
```

##### [Clients time taught](https://slate.societyfortheblind.org/sfb/app/report-cbyh.aspx)

###### Description

Shows how much (billed) time has been taught in a given period.

###### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbContactType
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            string[] strArray = new string[] { "SELECT DISTINCT ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', 0.00 As 'HoursTaught', ('<a href=''view-lesson-notes.aspx?SAAKey=' + CAST(twbServiceAreaAuthorization.ServiceAreaAuthorizationKey As varchar(7)) + '''>' + AuthorizationID + '</a>') As 'Authorization', ServiceArea, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As NameSort, AuthorizationID As AuthorizationSort, twbAuthorizationType.AuthorizationTypeCode as AuthType, CCRKey, twbServiceArea.ServiceAreaKey, twbContact.ContactKey  FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey INNER JOIN twbCCR ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE LessonDate >= CAST('", Conversions.ToString(num3), "' + '/1/' + '", Conversions.ToString(num6), "' AS DATETIME) AND LessonDate < CAST('", Conversions.ToString(num4), "' + '/1/' + '" };
            strArray[14] = "/app/view-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', 0.00 As 'HoursTaught', 'None' As 'Authorization', ('<a href=''view-sa-lesson-notes.aspx?ContactKey=' + CAST(twbCCR.ContactKey As varchar(7)) + '''>' + ServiceArea  + '</a>') As ServiceArea, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As NameSort, 'None' As AuthorizationSort, '' as AuthType, CCRKey, twbServiceArea.ServiceAreaKey, twbContact.ContactKey  FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbCCR ON twbCCR.ContactKey = twbContact.ContactKey INNER JOIN twbServiceArea ON twbCCR.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE LessonDate >= CAST('";
                    selectCommandText = !Conversions.ToBoolean(Microsoft.VisualBasic.CompilerServices.Operators.NotObject(Microsoft.VisualBasic.CompilerServices.Operators.CompareObjectEqual(current["Authorization"], "None", false))) ? Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits)) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE CCRKey = ", current["CCRKey"]), " AND LessonDate >= CAST('"), num3), "' + '/1/' + '"), num6), "' AS DATETIME) "), "AND LessonDate < CAST('"), num4), "' + '/1/' + '"), num5), "' AS DATETIME)")) : Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits)) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE CCRKey = ", current["CCRKey"]), " AND twbAuthorization.ContactKey = "), current["ContactKey"]), " AND LessonDate >= CAST('"), num3), "' + '/1/' + '"), num6), "' AS DATETIME) "), "AND LessonDate < CAST('"), num4), "' + '/1/' + '"), num5), "' AS DATETIME)"));
                    OleDbCommand command = new OleDbCommand(selectCommandText, selectConnection);
                        new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "ServiceAreas");
                        new OleDbDataAdapter("SELECT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContactType.ContactKey = twbContact.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0 ORDER BY Name", selectConnection).Fill(set, "Clients");
```

##### [Client contact information](https://slate.societyfortheblind.org/sfb/app/report-cci.aspx)

###### Description

Find contact and emergency contact information for a client.

###### DB tables touched

+ twbContact
+ twbContactType
+ twbEmergencyContact
+ twbIntake

###### Queries

```
            strArray = new string[] { "SELECT DISTINCT ('<a href=''mailto:' + Email + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';' + '</a>') As 'Name', (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As NameSort, (Address1 + '<br>' + Address2 + '<br>' + Suite + '<br>' + City + '<br>' + State + '<br>' + Zip) As 'Contact', (SELECT (ECName + '<br>Rel: ' + Relationship + '<br>' + 'Day Phone: ' + ECDayPhone + '<br>Evening Phone: ' + ECEveningPhone + '<br>Other Phone: ' + ECOtherPhone) As 'EAddress' FROM twbEmergencyContact WHERE twbEmergencyContact.ContactKey = twbContact.ContactKey) As 'EmContact', ContactType, Crossstreets As 'Cross', ('Day Phone: ' + DayPhone + '<br>Evening Phone: ' + EveningPhone + '<br>Other Phone: ' + OtherPhone) As 'Phone' FROM twbContact INNER JOIN twbContactType On twbContactType.ContactKey = twbContact.ContactKey INNER JOIN twbIntake On twbIntake.ContactKey = twbContact.ContactKey WHERE ContactValue <> 0", str4, str3, str, " ORDER BY ", this.ViewState["sortField"].ToString(), " ", this.ViewState["sortDirection"].ToString() };
```

##### [Client Schedule Report](https://slate.societyfortheblind.org/sfb/app/report-cschedule.aspx)

###### Description

Shows the instructional schedule of the queried clients.

###### Used by

+ CORE

###### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbMember
+ twbSchedule
+ twbServiceArea
+ twbServiceAreaAuthorization
+ twbWaitingList

###### Queries

```
                    str13 = Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.AddObject(str13, Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(" UNION SELECT DISTINCT '", current), "' As Day, ScheduleKey, "), left), " AS DayNumber, "), current), "ScheduleStart As StartTime, "), current), "ScheduleEnd As EndTime, "), "(LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name', "), "(AuthorizationID + '<br>' + ServiceArea) As 'Authorization', twbWaitingList.WaitingListKey, twbServiceAreaAuthorization.ServiceAreaAuthorizationKey, '' As Instructors, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As FullName "), "FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey "), "INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey "), "INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey "), "INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey "), "INNER JOIN twbWaitingList ON twbWaitingList.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey "), "INNER JOIN twbSchedule ON twbWaitingList.WaitingListKey = twbSchedule.WaitingListKey "), "WHERE ContactType = 'Client' AND ContactValue <> 0 "), str8), str11), str9), right)));
                    str13 = Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT DISTINCT (MemberLastName + ',' + MemberFirstName) As 'Name' FROM twbMember INNER JOIN twbCCR ON twbCCR.MemberKey = twbMember.MemberKey WHERE twbCCR.ServiceAreaAuthorizationKey = ", current["ServiceAreaAuthorizationKey"]), " ORDER BY Name"));
                    OleDbDataReader reader = new OleDbCommand(str13, selectConnection).ExecuteReader();
                new OleDbDataAdapter("SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name', twbContact.ContactKey FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0", selectConnection).Fill(dataSet, "Clients");
                new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(set2, "ServiceAreas");
```

##### [Clients with authorizations who have not been taught](https://slate.societyfortheblind.org/sfb/app/report-cbya.aspx)

###### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbContact
+ twbContactType
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            string[] strArray = new string[] { "SELECT DISTINCT ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', twbAuthorizationType.AuthorizationTypeCode as AuthType, TotalHours As 'HoursAuthor', AuthorizationID As 'ID', (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As NameSort, CAST(StartDate As Varchar(11)) As 'Start', CAST(EndDate As Varchar(11)) As 'EndDate', twbServiceArea.ServiceAreaKey FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE EndDate > CAST(CAST(MONTH(DATEADD(m, -1, GETDATE())) AS VARCHAR(2)) + '/' + '1' + '/' + CAST(YEAR(DATEADD(m, -1, GETDATE())) AS VARCHAR(4)) AS DATETIME) AND ContactType = 'Client' AND ContactValue <> 0 AND HoursUsed = 0 ORDER BY ", this.ViewState["sortField"].ToString(), " ", this.ViewState["sortDirection"].ToString() };
                new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "ServiceAreas");
```

##### [Client monthly unit totals](https://slate.societyfortheblind.org/sfb/app/report-cunit.aspx)

###### Description

Sample line:

> <table cellspacing="0" cellpadding="5" border="0" id="tabResults" style="border-collapse:collapse;"> <tbody><tr align="left" style="background-color:Gainsboro;font-weight:bold;"> <td><a href="javascript:__doPostBack('tabResults$ctl02$ctl00','')">Client Name</a></td><td><a href="javascript:__doPostBack('tabResults$ctl02$ctl01','')">Authorization</a></td><td><a href="javascript:__doPostBack('tabResults$ctl02$ctl02','')">Authorization Type</a></td><td><a href="javascript:__doPostBack('tabResults$ctl02$ctl03','')">Instructor</a></td><td><a href="javascript:__doPostBack('tabResults$ctl02$ctl04','')">Instructional Units</a></td><td><a href="javascript:__doPostBack('tabResults$ctl02$ctl05','')">Billed Units</a></td> </tr><tr valign="top" style="white-space:nowrap;"> <td><a href="/sfb/app/view-intake.aspx?ContactKey=2962">Aceves, Gloria </a><br>Total Instructional Units: 16<br>Total Billed Units: 16</td><td><a href="/sfb/app/view-authorization.aspx?AuthorKey=11826">NMED533537805 </a></td><td>Classes</td><td>Gray, Paul</td><td>16</td><td>16</td> </tr> </tbody></table>

Similar to "Client Taught Time Report", but a bit more detailed. To compare:

> <table cellspacing="0" cellpadding="5" border="0" id="tabResults" style="border-collapse:collapse;"> <tbody><tr align="left" style="background-color:Gainsboro;font-weight:bold;"> <td><a href="javascript:__doPostBack('tabResults$ctl02$ctl00','')">Name</a></td><td align="center"><a href="javascript:__doPostBack('tabResults$ctl02$ctl01','')">Time Taught</a></td><td align="center"><a href="javascript:__doPostBack('tabResults$ctl02$ctl02','')">Authorization Type</a></td><td><a href="javascript:__doPostBack('tabResults$ctl02$ctl03','')">ID</a></td><td><a href="javascript:__doPostBack('tabResults$ctl02$ctl04','')">Service Area</a></td> </tr><tr valign="top" style="white-space:nowrap;"> <td><a href="/sfb/app/view-intake.aspx?ContactKey=2962">Aceves, Gloria </a><br>Total Billed Time: 4<br>Total Billed Units: 16</td><td align="center">1</td><td align="center">Classes</td><td><a href="view-lesson-notes.aspx?SAAKey=11892">NMED533537805 </a></td><td>Assistive Technology Training - Group</td> </tr> </tbody></table>

###### Used by

+ CORE

###### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbContactType
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            strArray = new string[] { "SELECT DISTINCT ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', twbAuthorizationType.AuthorizationTypeCode as AuthType, ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-authorization.aspx?AuthorKey=' + CAST(twbAuthorization.AuthorizationKey AS VARCHAR(6)) + '''>' + AuthorizationID + '</a>') As 'AuthorizationID', (SELECT SUM(InstructionalUnits) FROM twbCCR WHERE ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey ", right, " ) As 'InstructionalUnits', (SELECT SUM(BilledUnits) FROM twbCCR WHERE ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey ", right, " ) As 'BilledUnits', (MemberLastName + ', ' + MemberFirstName) As Instructor, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As NameSort, AuthorizationID As 'AuthorizationSort', twbAuthorization.ContactKey FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbCCR ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbMember ON twbMember.MemberKey = twbCCR.MemberKey WHERE ContactType = 'Client' AND ContactValue <> 0 " };
            strArray[13] = "/app/view-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', '' as AuthKey, 'None' As 'AuthorizationID', (SELECT SUM(InstructionalUnits) FROM twbCCR WHERE ContactKey = twbContact.ContactKey ";
            strArray[15] = " ) As 'InstructionalUnits', (SELECT SUM(BilledUnits) FROM twbCCR WHERE ContactKey = twbContact.ContactKey ";
            strArray[0x11] = " ) As 'BilledUnits', (MemberLastName + ', ' + MemberFirstName) As Instructor, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As NameSort, 'None' As 'AuthorizationSort', twbCCR.ContactKey FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbCCR ON twbCCR.ContactKey = twbContact.ContactKey INNER JOIN twbMember ON twbMember.MemberKey = twbCCR.MemberKey WHERE ContactType = 'Client' AND ContactValue <> 0 ";
                    OleDbCommand command = new OleDbCommand(Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT SUM(BilledUnits) As BilledUnits, SUM(InstructionalUnits) As InstructionalUnits  FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE(twbAuthorization.ContactKey = ", current["ContactKey"]), ") "), right)), selectConnection);
                    selectCommandText = Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT SUM(BilledUnits) As BilledUnits, SUM(InstructionalUnits) As InstructionalUnits FROM twbCCR WHERE(twbCCR.ContactKey = ", current["ContactKey"]), ") "), right));
                        new OleDbDataAdapter("SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContactType.ContactKey = twbContact.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0 ORDER BY Name", selectConnection).Fill(dataSet, "Clients");
```

##### [Client Goals Report](https://slate.societyfortheblind.org/sfb/app/report-sp.aspx)

###### Description

This is related to [Student Plan](#user-content-student-plan).

TODO: Ask Shane.

###### Used by

+ CORE

###### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbIntake
+ twbMember
+ twbMemberGroup
+ twbServiceArea
+ twbServiceAreaAuthorization
+ twbServicePlan
+ twbServicePlanGoals

###### Queries

```
            strArray = new string[] { "SELECT DISTINCT ('<a href=''edit-student-plan.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';' + '</a>') As 'Name', (LastName + FirstName + MiddleName + Company) As NameSort, ServiceArea, twbServicePlanGoals.StartDate, CAST(twbServicePlanGoals.StartDate As Varchar(11)) As Start, twbServicePlanGoals.Completion, '' As ComBool, twbServicePlanGoals.Completed, Point, '' As GoalType FROM twbContact INNER JOIN twbServicePlan ON twbContact.ContactKey = twbServicePlan.ContactKey INNER JOIN twbServicePlanGoals ON twbServicePlanGoals.ServicePlanKey = twbServicePlan.ServicePlanKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServicePlanGoals.ServiceAreaKey ", str6, str4, str5, " ORDER BY ", this.ViewState["sortField"].ToString(), " ", this.ViewState["sortDirection"].ToString() };
                        new OleDbDataAdapter("SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As ContactName FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbIntake on twbIntake.ContactKey = twbContact.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0 ORDER BY ContactName", selectConnection).Fill(dataSet, "Clients");
                        new OleDbDataAdapter("SELECT DISTINCT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As ContactName FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType = 'Outside Agency' AND ContactValue <> 0 ORDER BY ContactName", selectConnection).Fill(set3, "Clients");
                        new OleDbDataAdapter("SELECT twbMember.MemberKey, (MemberLastName + ', ' + MemberFirstName) As 'Name' FROM twbMember INNER JOIN twbMemberGroup ON twbMemberGroup.MemberGroupKey = twbMember.MemberGroupKey WHERE Deleted = 0 ORDER BY Name", selectConnection).Fill(set, "Instructors");
                        new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(set4, "ServiceAreas");
```

##### [Export Data to Excel](https://slate.societyfortheblind.org/sfb/app/export-data.aspx)

###### Description

Export basic contact information.

###### DB tables touched

+ twbContact
+ twbContactOutreach
+ twbContactType
+ twbIntake
+ twbIntakeServices
+ twbIntakeServices")
+ twbIntakeVolunteer
+ twbOutreach
+ twbServices

###### Queries

```
                        new OleDbDataAdapter("SELECT OutreachKey, OutreachName FROM twbOutreach WHERE Deleted = 0 ORDER BY OutreachName", selectConnection).Fill(dataSet, "Outreach");
                        OleDbCommand command = new OleDbCommand("SELECT ServicesKey, Name, ServicesGroup FROM twbServices WHERE Inside = 1 ORDER BY DisplayPrecedence, ServicesGroup", selectConnection);
                                command.CommandText = "SELECT ServicesKey, Name, ServicesGroup FROM twbServices WHERE Outside = 1 ORDER BY DisplayPrecedence, ServicesGroup";
                strArray = new string[] { "SELECT DISTINCT FirstName, LastName, Company, Address1, Address2, Suite, City, State, Zip, DayPhone, EveningPhone, Email, '", str16, "' As 'Type', CASE WHEN IsNull(BadAddress,1) = 0 THEN 'yes' ELSE 'no' END As BadAddress, CASE WHEN IsNull(Deceased,1) = 0 THEN 'yes' ELSE 'no' END As Deceased, CASE WHEN IsNull(DoNotContact,1) = 0 THEN 'yes' ELSE 'no' END As RemoveFromMailing, CASE WHEN IsNull(DoNotContact2,1) = 0 THEN 'yes' ELSE 'no' END As DoNotContact  FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbIntake ON twbIntake.ContactKey = twbContact.ContactKey ", str11, str18, "WHERE", str7, str12, str8 };
                OleDbDataReader reader2 = new OleDbCommand(string.Concat(strArray), connection).ExecuteReader();
```

##### [Export Lesson Data to Excel](https://slate.societyfortheblind.org/sfb/app/export-lesson-billing.aspx)

###### Description

Supposed to be listing a running table for each client, similar to the one at the bottom of "Billing Information". The format is spot on, but the generated file is useless because for each lesson it prints the entire number of hours for the authorization, instead of only the billed time for the lesson.

###### Used by

No one.

###### DB tables touched

+ twbA
+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbIntakeBilling
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
                        new OleDbDataAdapter("SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name', twbContact.ContactKey FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0", selectConnection).Fill(dataSet, "Clients");
                        new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(set2, "ServiceAreas");
                strArray = new string[] { "SELECT DISTINCT LessonDate, twbAuthorization.ContactKey, FirstName, LastName, BillingName, AuthorizationID, twbAuthorization.AuthorizationTypeID, twbAuthorization.SABillingKey,  (SELECT ISNULL(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, SUM(BilledUnits)),0) + ISNULL((SELECT dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits)  FROM twbIntakeBilling  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbIntakeBilling.AuthorizationKey  INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey  INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey  WHERE EnteredDate >= CAST('6/1/2007' AS DATETIME) AND EnteredDate < CAST('7/1/2007' AS DATETIME)  AND twbIntakeBilling.AuthorizationKey = twbAuthorization.AuthorizationKey  ),0)  As 'BilledHours'  FROM twbCCR  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey  INNER JOIN twbAuthorization twbA ON twbA.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey  WHERE ", str7, " AND twbA.AuthorizationKey = twbAuthorization.AuthorizationKey  ) As 'BilledHours',  ('$' + CAST(RateHourly As varchar(11))) As 'HourlyRate',  (SELECT (ISNULL(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, SUM(BilledUnits)),0) + ISNULL(  (SELECT SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits))  FROM twbIntakeBilling  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbIntakeBilling.AuthorizationKey  INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey  INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey  WHERE ", str8, " AND twbIntakeBilling.AuthorizationKey = twbAuthorization.AuthorizationKey  ),0)) * MAX(RateHourly)  As 'Amount'  FROM twbCCR  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey  INNER JOIN twbAuthorization twbA ON twbA.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey  WHERE ", str7, " AND twbA.AuthorizationKey = twbAuthorization.AuthorizationKey  ) As 'Amount',  (SELECT (FirstName + ' ' + LastName + ' - ' + Company) As 'Caseworker'  FROM twbContact  INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey  WHERE ContactType = 'Outside Agency' AND twbContact.ContactKey = twbAuthorization.CaseworkerID) As 'Caseworker'  FROM twbAuthorization  INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.ContactKey  INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey  INNER JOIN twbCCR ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey  WHERE ", str7, str4 };
                OleDbDataReader reader = new OleDbCommand(cmdText, connection).ExecuteReader();
```

##### [Export Billing Data to Excel](https://slate.societyfortheblind.org/sfb/app/export-billing.aspx)

###### Description

Export billing information with summary lines for each client.

###### Used by

No one.

###### DB tables touched

+ twbA
+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbContactType
+ twbIntakeBilling
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
                        new OleDbDataAdapter("SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name', twbContact.ContactKey FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0", selectConnection).Fill(dataSet, "Clients");
                        new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(set2, "ServiceAreas");
                strArray = new string[] { "SELECT DISTINCT twbAuthorizationType.AuthorizationTypeCode, twbAuthorization.ContactKey, FirstName, LastName, BillingName, AuthorizationID, twbAuthorization.SABillingKey,  (SELECT ISNULL((SUM(BilledUnits) / 4),0) + ISNULL((SELECT (BilledUnits / 4)  FROM twbIntakeBilling  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbIntakeBilling.AuthorizationKey  INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey  INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey  WHERE EnteredDate >= CAST('6/1/2007' AS DATETIME) AND EnteredDate < CAST('7/1/2007' AS DATETIME)  AND twbIntakeBilling.AuthorizationKey = twbAuthorization.AuthorizationKey  AND twbAuthorization.AuthorizationTypeID = 1  ),0)  As 'BilledHours'  FROM twbCCR  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey  INNER JOIN twbAuthorization twbA ON twbA.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey  WHERE ", str7, " AND twbA.AuthorizationKey = twbAuthorization.AuthorizationKey  AND twbAuthorization.AuthorizationTypeID = 1  ) As 'BilledHours',  ('$' + CAST(RateHourly As varchar(11))) As 'HourlyRate',  (SELECT (ISNULL((SUM(BilledUnits) / 4),0) + ISNULL(  (SELECT (SUM(BilledUnits) / 4)  FROM twbIntakeBilling  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbIntakeBilling.AuthorizationKey  INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey  INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey  WHERE ", str8, " AND twbIntakeBilling.AuthorizationKey = twbAuthorization.AuthorizationKey  AND twbAuthorization.AuthorizationTypeID = 1  ),0)) * MAX(RateHourly)  As 'Amount'  FROM twbCCR  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey  INNER JOIN twbAuthorization twbA ON twbA.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey  WHERE ", str7, " AND twbA.AuthorizationKey = twbAuthorization.AuthorizationKey  AND twbAuthorization.AuthorizationTypeID = 1  ) As 'Amount',  (SELECT (FirstName + ' ' + LastName + ' - ' + Company) As 'Caseworker'  FROM twbContact  INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey  WHERE ContactType = 'Outside Agency' AND twbContact.ContactKey = twbAuthorization.CaseworkerID) As 'Caseworker'  FROM twbAuthorization  INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.ContactKey  INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey  INNER JOIN twbCCR ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey  INNER JOIN twbAuthorizationType ON twbAuthorizationType.AuthorizationTypeID = twbAuthorization.AuthorizationTypeID  WHERE ", str7, str4 };
                strArray = new string[] { "SELECT DISTINCT twbAuthorizationType.AuthorizationTypeCode, twbAuthorization.ContactKey, FirstName, LastName, BillingName, AuthorizationID, twbAuthorization.SABillingKey,  (SELECT ISNULL((SUM(BilledUnits) / 4),0) + ISNULL((SELECT (BilledUnits / 4)  FROM twbIntakeBilling  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbIntakeBilling.AuthorizationKey  INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey  INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey  WHERE EnteredDate >= CAST('6/1/2007' AS DATETIME) AND EnteredDate < CAST('7/1/2007' AS DATETIME)  AND twbIntakeBilling.AuthorizationKey = twbAuthorization.AuthorizationKey  AND twbAuthorization.AuthorizationTypeID = 2  ),0)  As 'BilledHours'  FROM twbCCR  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey  INNER JOIN twbAuthorization twbA ON twbA.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey  WHERE ", str7, " AND twbA.AuthorizationKey = twbAuthorization.AuthorizationKey  AND twbAuthorization.AuthorizationTypeID = 2  ) As 'BilledHours',  ('$' + CAST(RateHourly As varchar(11))) As 'HourlyRate',  (SELECT (ISNULL((SUM(BilledUnits) / 4),0) + ISNULL(  (SELECT (SUM(BilledUnits) / 4)  FROM twbIntakeBilling  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbIntakeBilling.AuthorizationKey  INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey  INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey  WHERE ", str8, " AND twbIntakeBilling.AuthorizationKey = twbAuthorization.AuthorizationKey  AND twbAuthorization.AuthorizationTypeID = 2  ),0)) * MAX(RateHourly)  As 'Amount'  FROM twbCCR  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey  INNER JOIN twbAuthorization twbA ON twbA.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey  WHERE ", str7, " AND twbA.AuthorizationKey = twbAuthorization.AuthorizationKey  AND twbAuthorization.AuthorizationTypeID = 2  ) As 'Amount',  (SELECT (FirstName + ' ' + LastName + ' - ' + Company) As 'Caseworker'  FROM twbContact  INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey  WHERE ContactType = 'Outside Agency' AND twbContact.ContactKey = twbAuthorization.CaseworkerID) As 'Caseworker'  FROM twbAuthorization  INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.ContactKey  INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey  INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey  INNER JOIN twbCCR ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey  INNER JOIN twbAuthorizationType ON twbAuthorizationType.AuthorizationTypeID = twbAuthorization.AuthorizationTypeID  WHERE ", str7, str4 };
                OleDbDataReader reader = new OleDbCommand(cmdText, connection).ExecuteReader();
```

##### [Demographics Export](https://slate.societyfortheblind.org/sfb/app/export-demographics.aspx)

###### Description

Exports a CSV file where clients in a given period are categorized by certain demographic properties.

TODO: Ask Pat, whether they are using this for their reports.

###### Used by

SIP?

###### DB tables touched

+ twbServiceArea

###### Queries

```
                strArray = new string[] { "SELECT ServiceArea, AuthorizationTypeID, SUM(iHours) AS TotalHours, COUNT(ContactKey) As TotalClients FROM vwbClientHoursByMonth INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = vwbClientHoursByMonth.ServiceAreaKey WHERE MOnthYear BETWEEN '", time2.ToShortDateString(), "' AND '", time.ToShortDateString(), "' GROUP BY ServiceArea, AuthorizationTypeID ORDER BY ServiceArea, AuthorizationTypeID" };
                OleDbCommand command = new OleDbCommand(string.Concat(strArray), connection);
```

##### [Plan for Service Export](https://slate.societyfortheblind.org/sfb/app/export-planforservice.aspx)

###### Description

The vocabulary ("Plan For Service", "Master List", etc.) is for SIP, but I'm not sure whether it is used at all.

TODO: Ask Pat.

###### Used by

SIP?

###### DB tables touched

+ twbContact
+ twbIntake
+ twbPFSDelivery
+ twbPFSImpairments
+ twbPFSServices
+ twbPlanForService

###### Queries

```
                            OleDbCommand command2 = new OleDbCommand(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject((((((((((((("UPDATE twbPlanForService SET PlanDate = '" + str5 + "', PlanType = '") + str12 + "', PrePost = ") + Conversions.ToString(num22) + ", GrantRegion = '") + str8 + "', Age = '") + str3 + "', Ethnicity = '") + str7 + "', Impairment = '") + str9 + "', Cause = '") + str4 + "', Onset = '") + str11 + "', Education = '") + str6 + "', Living = '") + str10 + "', Residence = '") + str14 + "', Referral = '") + str13 + "', NotesTxt = '", this.DBReady(this.txtOtherNotes.Value)), "' WHERE PFSKey = "), this.txtPFSKey.Value)), connection);
                            OleDbCommand command3 = new OleDbCommand(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject((((((((((((("INSERT INTO twbPlanForService (PlanDate, PlanType, PrePost, GrantRegion, Age, Ethnicity, Impairment, Cause, Onset, Education, Living, Residence, Referral, NotesTxt, IntakeKey) VALUES ('" + str5 + "', '") + str12 + "', ") + Conversions.ToString(num22) + ", '") + str8 + "', '") + str3 + "', '") + str7 + "', '") + str9 + "', '") + str4 + "', '") + str11 + "', '") + str6 + "', '") + str10 + "', '") + str14 + "', '") + str13 + "', '", this.DBReady(this.txtOtherNotes.Value)), "', "), this.txtIntakeKey.Value), "); SELECT @@Identity")), connection);
                reader = new OleDbCommand("SELECT (LastName + ', ' + FirstName) As ClientName, twbIntake.IntakeKey, IntakeDate, BirthDate, Region, twbPlanForService.*, twbPFSDelivery.*, twbPFSServices.*, twbPFSImpairments.* FROM twbContact INNER JOIN twbIntake ON twbContact.ContactKey = twbIntake.ContactKey LEFT JOIN twbPlanForService ON twbPlanForService.IntakeKey = twbIntake.IntakeKey LEFT JOIN twbPFSServices ON twbPFSServices.PFSKey = twbPlanForService.PFSKey LEFT JOIN twbPFSDelivery ON twbPFSDelivery.PFSKey = twbPlanForService.PFSKey LEFT JOIN twbPFSImpairments ON twbPFSImpairments.PFSKey = twbPlanForService.PFSKey WHERE twbContact.ContactKey = " + this.Request.QueryString["ContactKey"], connection).ExecuteReader();
```

#### Absences

##### [Absences by Client Report](https://slate.societyfortheblind.org/sfb/app/report-asbyc.aspx)

###### Description

Shows how much absences a client had per service area, authorization and instructor.

###### Used by

CORE?

###### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            strArray = new string[] { "SELECT DISTINCT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name', AuthorizationID As AuthorizationSort, ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-authorization.aspx?AuthorKey=' + CAST(twbAuthorization.AuthorizationKey AS VARCHAR(6)) + '''>' + AuthorizationID + '</a>') As 'Authorization', twbAuthorization.AuthorizationKey, (SELECT COUNT(CCRKey) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE Absent = 0 AND twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey ", str3, " ) As Absences, AuthorizationID, (MemberLastName + ', ' + MemberFirstName) As Instructor, ServiceArea FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey INNER JOIN twbCCR ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbMember ON twbMember.MemberKey = twbCCR.MemberKey WHERE ContactType = 'Client' AND ContactValue <> 0", str, str3, " ORDER BY ", this.ViewState["sortField"].ToString() };
            this.outTotal.InnerHtml = Conversions.ToString(new OleDbCommand("SELECT DISTINCT COUNT(Absent) As 'AbsenceTotal' FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbContact ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0 AND Absent = 0" + str + str3, selectConnection).ExecuteScalar());
                new OleDbDataAdapter("SELECT twbContact.ContactKey, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType = 'Client' AND ContactValue <> 0 ORDER BY Name", selectConnection).Fill(dataSet, "Clients");
```

##### [Absences by Instructor Report](https://slate.societyfortheblind.org/sfb/app/report-asbyi.aspx)

###### Description

Shows how much client absences there were for an instructor per service area and authorization.

###### Used by

CORE?

###### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbContactType
+ twbMember
+ twbMemberGroup
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            strArray = new string[] { "SELECT DISTINCT (MemberLastName + ', ' + MemberFirstName) As 'Name',  AuthorizationID As AuthorizationSort, ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-authorization.aspx?AuthorKey=' + CAST(twbAuthorization.AuthorizationKey AS VARCHAR(6)) + '''>' + AuthorizationID + '</a>') As 'Authorization', twbAuthorization.AuthorizationKey, (SELECT COUNT(CCRKey) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE Absent = 0 AND twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey ", str2, " ) As Absences, AuthorizationID, ServiceArea FROM twbMember INNER JOIN twbCCR ON twbMember.MemberKey = twbCCR.MemberKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE twbMember.MemberKey > 0 ", str5, str2, " ORDER BY ", this.ViewState["sortField"].ToString() };
            this.outTotal.InnerHtml = Conversions.ToString(new OleDbCommand("SELECT DISTINCT COUNT(Absent) As 'AbsenceTotal' FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbContact ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbMember ON twbMember.MemberKey = twbCCR.MemberKey WHERE ContactType = 'Client' AND ContactValue <> 0 AND Absent = 0" + str5 + str2, selectConnection).ExecuteScalar());
                new OleDbDataAdapter("SELECT twbMember.MemberKey, (MemberLastName + ', ' + MemberFirstName) As 'Name' FROM twbMember INNER JOIN twbMemberGroup ON twbMemberGroup.MemberGroupKey = twbMember.MemberGroupKey WHERE Deleted = 0 ORDER BY Name", selectConnection).Fill(dataSet, "Instructors");
```

#### Instructor Reports

##### [Instructors by Client](https://slate.societyfortheblind.org/sfb/app/report-ibyc.aspx)

###### Description

Show all instructors a client ever had.

###### Used by

CORE?

###### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbMember
+ twbServiceAreaAuthorization

###### Queries

```
            string[] strArray = new string[] { "SELECT DISTINCT (MemberLastName + ', ' + MemberFirstName) As 'Name', MemberEmail FROM twbMember INNER JOIN twbCCR ON twbMember.MemberKey = twbCCR.MemberKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.ContactKey WHERE twbContact.LastName Like '%", this.txtClient.Value, "%' OR twbContact.FirstName Like '%", this.txtClient.Value, "%' OR twbContact.MiddleName Like '%", this.txtClient.Value, "%' ORDER BY ", this.ViewState["sortField"].ToString(), " " };
```

##### [Instructor by Service Area Report](https://slate.societyfortheblind.org/sfb/app/report-ibys.aspx)

###### Description

List all lesson for all authorizations in a service area by instructor.

###### Used by

CORE?

###### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            new OleDbDataAdapter("SELECT DISTINCT (MemberLastName + ', ' + MemberFirstName) As 'Name', AuthorizationID As 'ID', twbAuthorizationType.AuthorizationTypeCode as AuthType, CAST(LessonDate As varchar(11)) As 'Date', InstructionalUnits As 'InstrUnits', (CAST(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, InstructionalUnits) As Float) ) As 'InstrHrs', BilledUnits, dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits) As 'BilledHrs', twbServiceArea.ServiceAreaKey, ServiceArea, LessonDate FROM twbMember INNER JOIN twbCCR ON twbMember.MemberKey = twbCCR.MemberKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey ORDER BY " + this.ViewState["sortField"].ToString() + " " + this.ViewState["sortDirection"].ToString(), selectConnection).Fill(dataSet, "Results");
                        new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "ServiceAreas");
```

##### [Instructor Time Taught Report](https://slate.societyfortheblind.org/sfb/app/report-ihours.aspx)

###### Description

List hours tought by instructor per authorization.

###### Used by

CORE?

###### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbMember
+ twbMemberGroup
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            strArray = new string[] { "SELECT (MemberLastName + ', ' + MemberFirstName) As 'Name', AuthorizationID As IDSort, twbAuthorizationType.AuthorizationTypeCode as AuthType, ('<a href=''view-lesson-notes.aspx?SAAKey=' + CAST(twbServiceAreaAuthorization.ServiceAreaAuthorizationKey As varchar(7)) + '''>' + AuthorizationID + '</a>') As 'ID', ServiceArea, SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, InstructionalUnits)) As 'InstrHrs', SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits)) As 'BilledHrs', twbMember.MemberKey FROM twbMember INNER JOIN twbCCR ON twbMember.MemberKey = twbCCR.MemberKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE ", str6, str2, "GROUP BY (MemberLastName + ', ' + MemberFirstName), ServiceArea, AuthorizationID, twbMember.MemberKey, twbServiceAreaAuthorization.ServiceAreaAuthorizationKey, AuthorizationID,twbAuthorizationType.AuthorizationTypeCode  UNION SELECT (MemberLastName + ', ' + MemberFirstName) As 'Name', CAST(twbCCR.ServiceAreaAuthorizationKey As varchar(12)) As IDSort, twbAuthorizationType.AuthorizationTypeCode as AuthType, CAST(twbCCR.ServiceAreaAuthorizationKey As varchar(6)) As 'ID', ('<a href=''view-sa-lesson-notes.aspx?ContactKey=' + CAST(twbCCR.ContactKey As varchar(7)) + '''>' + ServiceArea  + '</a>') As ServiceArea, SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, InstructionalUnits )) As 'InstrHrs', SUM(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits)) As 'BilledHrs', twbMember.MemberKey FROM twbMember INNER JOIN twbCCR ON twbMember.MemberKey = twbCCR.MemberKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbContact ON twbCCR.ContactKey = twbContact.ContactKey INNER JOIN twbServiceArea ON twbCCR.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE ", str6, str2, "GROUP BY (MemberLastName + ', ' + MemberFirstName), ServiceArea, twbMember.MemberKey, CAST(twbCCR.ServiceAreaAuthorizationKey As varchar(6)), twbCCR.ContactKey, twbCCR.ServiceAreaAuthorizationKey, twbAuthorizationType.AuthorizationTypeCode ORDER BY ", this.ViewState["sortField"].ToString(), " " };
                        new OleDbDataAdapter("SELECT twbMember.MemberKey, (MemberLastName + ', ' + MemberFirstName) As 'Name' FROM twbMember INNER JOIN twbMemberGroup ON twbMemberGroup.MemberGroupKey = twbMember.MemberGroupKey ORDER BY Name", selectConnection).Fill(dataSet, "Instructors");
                        new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(set2, "ServiceAreas");
```

##### [Instructor Productivity Report](https://slate.societyfortheblind.org/sfb/app/report-iproduct.aspx)

###### Description

Appears to be broken.

###### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization
+ twbServiceAreaLessons

###### Queries

```
                new OleDbDataAdapter("SELECT ServiceAreaKey, BillingName FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "ServiceAreas");
```

##### [Instructor Schedule Report](https://slate.societyfortheblind.org/sfb/app/report-ischedule.aspx)

###### Description

Shows instructor schedules. Very limited, does not show dates.

###### Used by

CORE?

###### DB tables touched

+ twbAuthorization
+ twbContact
+ twbMember
+ twbSchedule
+ twbServiceArea
+ twbServiceAreaAuthorization
+ twbWaitingList

###### Queries

```
                    str13 = Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.AddObject(str13, Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(" UNION SELECT DISTINCT '", current), "' As Day, ScheduleKey, "), left), " AS DayNumber, "), current), "ScheduleStart As StartTime, "), current), "ScheduleEnd As EndTime, "), "(MemberLastName + ', ' + MemberFirstName) As 'Name', "), "ServiceArea, twbWaitingList.WaitingListKey, twbServiceAreaAuthorization.ServiceAreaAuthorizationKey, '' As Clients "), "FROM twbMember INNER JOIN twbWaitingList ON twbWaitingList.MemberKey = twbMember.MemberKey "), "INNER JOIN twbServiceAreaAuthorization ON twbWaitingList.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey "), "INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey "), "INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey "), "INNER JOIN twbSchedule ON twbWaitingList.WaitingListKey = twbSchedule.WaitingListKey "), "WHERE twbMember.Deleted = 0 "), str8), str11), str9), right)));
                    str13 = Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT DISTINCT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name' FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey WHERE twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = ", current["ServiceAreaAuthorizationKey"]), " ORDER BY Name"));
                    OleDbDataReader reader = new OleDbCommand(str13, selectConnection).ExecuteReader();
                new OleDbDataAdapter("SELECT (MemberLastName + ', ' + MemberFirstName) As 'Name', MemberKey FROM twbMember ORDER by Name", selectConnection).Fill(dataSet, "Instructors");
                new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(set2, "ServiceAreas");
```

##### [Instructor Units Taught Report](https://slate.societyfortheblind.org/sfb/app/report-iunits.aspx)

###### Description

Same as "Instructor time Taught" above, but the values in the last two columns are multiplied by 4.

(Instructional|Billed) Units = 4 x (Instructional|Billed) Time

##### [Instructional Time Taught this Month](https://slate.societyfortheblind.org/sfb/app/view-hours.aspx)

###### Description

Same as [Instructional Time Taught this Month](#user-content-instructional-time-taught-this-month).

##### [Outside Agency Contact Report](https://slate.societyfortheblind.org/sfb/app/report-psi.aspx)

###### Description

Same as [Outside Agency Contact Report](#user-content-outside-agency-contact-report).

##### [Class Report](https://slate.societyfortheblind.org/sfb/app/report-classes.aspx)

###### Description

Shows the same information as "Instructor time Taught" by service area.

###### Used by

CORE?

###### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            new OleDbDataAdapter("SELECT DISTINCT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Client', (MemberLastName + ', ' + MemberFirstName) As 'Instructor', twbAuthorizationType.AuthorizationTypeCode as AuthType, AuthorizationID As 'ID', ServiceArea, CAST(LessonDate As varchar(11)) As 'Date', (CAST(dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, InstructionalUnits) As Float)) As 'InstrHrs', dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, BilledUnits) As 'BilledHrs', twbServiceArea.ServiceAreaKey, LessonDate FROM twbMember INNER JOIN twbCCR ON twbMember.MemberKey = twbCCR.MemberKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey INNER JOIN twbAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.ContactKey ORDER BY " + this.ViewState["sortField"].ToString() + " " + this.ViewState["sortDirection"].ToString(), selectConnection).Fill(dataSet, "Results");
                        new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "ServiceAreas");
```

##### [Service Area Report](https://slate.societyfortheblind.org/sfb/app/report-sa.aspx)

###### Description

Supposed to be showing all authorizations per service area, but it is useless as it does not show authorization numbers.

###### Used by

No one.

###### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbContact
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            new OleDbDataAdapter("SELECT DISTINCT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Client', CAST(StartDate As varchar(11)) As 'Start', CAST(EndDate As varchar(11)) As 'EndDate', DATEDIFF(d, GETDATE(), EndDate) As 'DaysRemaining', TotalHours As 'HoursAuthor', AuthorizationTypeCode, twbServiceArea.ServiceAreaKey FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE (HoursUsed < TotalHours OR TotalHours = 0) AND EndDate >= GETDATE() ORDER BY " + this.ViewState["sortField"].ToString() + " " + this.ViewState["sortDirection"].ToString(), selectConnection).Fill(dataSet, "Results");
                new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "ServiceAreas");
```

#### Authorization Reports

##### [Expiring Authorizations Report](https://slate.societyfortheblind.org/sfb/app/report-aexpire.aspx)

###### Description

List authorizations that are about to expire via expiration parameters.

###### Used by

CORE?

###### DB tables touched

Reverse engineering this compiled binary was unsuccessful, hence no data.

##### [Authorizations by Client](https://slate.societyfortheblind.org/sfb/app/report-abyc.aspx)

###### Description

Show all authorizations for clients.

###### Used by

CORE?

###### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            string[] strArray = new string[] { "SELECT DISTINCT ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-authorization.aspx?AuthorKey=' + CAST(twbAuthorization.AuthorizationKey As Varchar(9)) + '''>' + AuthorizationID + '</a>') As 'ID', (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Client', twbAuthorizationType.AuthorizationTypeCode As 'AuthType', (SELECT (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Caseworker' FROM twbContact WHERE twbContact.ContactKey = twbAuthorization.CaseworkerID) As 'Source', AuthorizationID As IDSort, CAST(StartDate As varchar(11)) As 'Dates', TotalHours As 'HrsAuth', '' As Instructor, (SELECT dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, SUM(BilledUnits)) FROM twbCCR WHERE twbCCR.ServiceAreaAuthorizationKey =twbServiceAreaAuthorization .ServiceAreaAuthorizationKey) As 'HrsUsed', twbContact.ContactKey, CAST(EndDate As varchar(11)) As 'EndDate', ServiceArea, ServiceAreaAuthorizationKey, twbServiceArea.ServiceAreaKey  FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE ", str2, "(HoursUsed < TotalHours OR TotalHours = 0) ORDER BY ", this.ViewState["sortField"].ToString(), " ", this.ViewState["sortDirection"].ToString() };
                    selectCommandText = Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT DISTINCT (MemberLastName + ', ' + MemberFirstName) As 'Name' FROM twbMember INNER JOIN twbCCR ON twbMember.MemberKey = twbCCR.MemberKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = ", current["ServiceAreaAuthorizationKey"]));
                    OleDbCommand command = new OleDbCommand(selectCommandText, selectConnection);
                new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "ServiceAreas");
```

##### [Authorizations by Service Area Report](https://slate.societyfortheblind.org/sfb/app/report-abys.aspx)

###### Description

Show authorizations by service area. (This is what "Service Areas" report in "Instructor Reports" was supposed to be doing.)

###### Used by

CORE?

###### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbServiceArea
+ twbServiceAreaAuthorization

###### Queries

```
            strArray = new string[] { "SELECT DISTINCT ('<a href=''/", ConfigurationManager.AppSettings["SiteRoot"], "/app/view-authorization.aspx?AuthorKey=' + CAST(twbAuthorization.AuthorizationKey As Varchar(9)) + '''>' + AuthorizationID + '</a>') As 'ID', (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Client', twbAuthorizationType.AuthorizationTypeCode As 'AuthType', CAST(StartDate As varchar(11)) As 'Start', CAST(EndDate As varchar(11)) As 'EndDate', TotalHours As 'HrsAuth', AuthorizationID As IDSort, (SELECT dbo.GetInstructionalHoursUsedForClass(twbAuthorization.AuthorizationKey, SUM(BilledUnits)) FROM twbCCR WHERE twbCCR.ServiceAreaAuthorizationKey =twbServiceAreaAuthorization .ServiceAreaAuthorizationKey) As HrsUsed, twbServiceArea.ServiceAreaKey, ServiceArea, StartDate FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorizationType ON twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceAreaAuthorization.ServiceAreaKey = twbServiceArea.ServiceAreaKey WHERE ", str3, "HoursUsed < TotalHours OR TotalHours = 0 ORDER BY ", this.ViewState["sortField"].ToString(), " ", this.ViewState["sortDirection"].ToString() };
                        new OleDbDataAdapter("SELECT ServiceAreaKey, ServiceArea FROM twbServiceArea WHERE Deleted = 0 ORDER BY ServiceArea", selectConnection).Fill(dataSet, "ServiceAreas");
```

#### Volunteer Reports

Not used at all. Not documenting it any further as it wouldn't reflect current practices by the Resource Development department.

#### [Audit Log](https://slate.societyfortheblind.org/sfb/app/report-audit.aspx)

##### Description

Shows any changes in chronological order for any "Intakes", "Lesson Notes", and "Progress Reports".

##### Used by

CORE?

##### DB tables touched

+ twbLog
+ twbMember

##### Queries

```
            strArray = new string[] { "SELECT twbLog.*, '' As Entity, 0 As EntitySort, '' As Member FROM twbLog WHERE ", str, str2, str6, " ORDER BY ", this.ViewState["sortField"].ToString(), " ", this.ViewState["sortDirection"].ToString() };
                    object left = new OleDbCommand(Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject("SELECT (MemberLastName + ', ' + MemberFirstName) As 'Name' FROM twbMember WHERE MemberKey = ", current["MemberKey"])), selectConnection).ExecuteScalar();
```

### Add an Authorization

Supposed to be a shortcut to add authorizations, but it is not used.

### Add Contact

I don't think anyone uses this, because new clients are added through [New Intake](#user-content-new-intake), and the rest of the checkboxes don't apply:

+ donors, volunteers are not tracked in SLATE
+ not sure what "Outreach" refers to
+ payment source can't be added by itself, only in combination with another checkbox.

TODO: Ask Pat and Shane to make sure.

## Footer

### Main Page

### [/sfb/app/default.aspx](https://slate.societyfortheblind.org/sfb/app/default.aspx)

#### Description

Main page.

#### Used by

+ All.

#### DB tables touched

None.

### (Login,) Logout, and Change Password

### /sfb/app/login.aspx

#### Description

Used for login, logout, and password change for users via query parameters:

+ https://slate.societyfortheblind.org/sfb/app/login.aspx?Logout=True
+ https://slate.societyfortheblind.org/sfb/app/login.aspx?ChangePassword=True

#### Used by

+ All

#### DB tables touched

+ twbMember

#### Queries

```
                string[] strArray = new string[] { "Select MemberGroupKey, MemberFirstName, MemberLastName, MemberKey  FROM twbMember WHERE UserName = '", userName, "' AND Password = '", FormsAuthentication.HashPasswordForStoringInConfigFile(Conversions.ToString(this.DBReady(this.txtPwd.Value)), "MD5"), "' AND Deleted = 0" };
                    OleDbCommand command2 = new OleDbCommand(cmdText, connection);
                    OleDbDataReader reader = new OleDbCommand(cmdText, connection).ExecuteReader();
                        command2.CommandText = Conversions.ToString(Operators.ConcatenateObject("SELECT PasswordReset FROM twbMember WHERE MemberKey = ", reader["MemberKey"]));
                                    command2.CommandText = Conversions.ToString(Operators.ConcatenateObject("SELECT Password FROM twbMember WHERE MemberKey = ", reader["MemberKey"]));
```


#### [/sfb/app/edit-lesson-note.aspx?CCRKey=123456](https://slate.societyfortheblind.org/sfb/app/edit-lesson-note.aspx?CCRKey=123456)

##### Description

Edit a lesson note.

##### Used by

+ CORE

##### DB tables touched

+ twbAuthorization
+ twbCCR
+ twbContact
+ twbMember
+ twbServiceArea
+ twbServiceAreaAuthorization

##### Queries

```
                object obj3 = new OleDbCommand(cmdText, connection).ExecuteScalar();
                    OleDbCommand command2 = new OleDbCommand(Conversions.ToString(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject(Microsoft.VisualBasic.CompilerServices.Operators.ConcatenateObject((((((("UPDATE twbCCR SET ModifiedBy = " + this.Request.Cookies["Member"]["MemberID"] + ", ModifiedDate = '") + Conversions.ToString(DateTime.Today) + "', LessonDate = '") + str6 + "', Absent = ") + this.selAbsent.Value + ", InstructionalUnits = ") + this.txtInstUnits.Value + ", BilledUnits = ") + this.txtBilledUnits.Value + ", TotalStudents = ") + this.txtNumStudents.Value + ", SuccessesTxt = '", this.DBReady(this.txtSuccesses.Value)), "', ObstaclesTxt = '"), this.DBReady(this.txtObstacles.Value)), "', RecommendationsTxt = '"), this.DBReady(this.txtRecomendations.Value)), "' WHERE CCRKey = "), right)), connection);
                    command2.CommandText = "SELECT TotalHours, HoursUsed, HoursRemaining, AuthorizationTypeID FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbCCR ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE twbCCR.CCRKey = " + Conversions.ToString(right);
                        command2.CommandText = "SELECT MemberEmail FROM twbMember WHERE MemberKey = " + this.hidMemberKey.Value;
                            command2.CommandText = "SELECT twbAuthorization.AuthorizationKey FROM twbAuthorization INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + this.hidSAAKey.Value;
                            command2.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'ContactName' FROM twbAuthorization INNER JOIN twbContact ON twbContact.ContactKey = twbAuthorization.ContactKey WHERE AuthorizationKey = " + Conversions.ToString(num16);
                            command2.CommandText = "SELECT BillingName FROM twbServiceArea INNER JOIN twbAuthorization ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE AuthorizationKey = " + Conversions.ToString(num16);
                        command2.CommandText = "SELECT Email FROM twbContact INNER JOIN twbAuthorization ON twbContact.ContactKey = twbAuthorization.CaseworkerID INNER JOIN twbServiceAreaAuthorization On twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey WHERE ServiceAreaAuthorizationKey = " + this.hidSAAKey.Value;
                OleDbCommand command = new OleDbCommand("SELECT DISTINCT (MemberFirstName + ' ' + MemberLastName) As MemberName FROM twbMember INNER JOIN twbCCR ON twbCCR.MemberKey = twbMember.MemberKey WHERE CCRKey = " + Conversions.ToString(num), connection);
                command.CommandText = "SELECT * FROM twbCCR WHERE CCRKey = " + Conversions.ToString(num);
                command.CommandText = "SELECT DISTINCT (MemberFirstName + ' ' + MemberLastName) As MemberName FROM twbMember WHERE MemberKey = " + Conversions.ToString(num5);
                command.CommandText = "SELECT (LastName + ', ' + FirstName + ' ' + MiddleName) As 'Name', EndDate, StartDate, AuthorizationID, AuthorizationTypeID, BillingName As ServiceArea, TotalHours, HoursUsed, HoursRemaining FROM twbContact INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.AuthorizationKey = twbAuthorization.AuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbAuthorization.SABillingKey WHERE ServiceAreaAuthorizationKey = " + str;
                                strArray = new string[] { "SELECT SUM(CAST(dbo.GetInstructionalHoursUsedForClass(twbServiceAreaAuthorization.AuthorizationKey, InstructionalUnits) As Float(2))) FROM twbCCR INNER JOIN twbServiceAreaAuthorization ON twbServiceAreaAuthorization.ServiceAreaAuthorizationKey = twbCCR.ServiceAreaAuthorizationKey WHERE twbCCR.ServiceAreaAuthorizationKey = ", str, " AND LessonDate >= CAST('", Conversions.ToString(num6), "' + '/1/' + '", Conversions.ToString(year), "' AS DATETIME) AND LessonDate < CAST('", Conversions.ToString(num7), "' + '/1/' + '" };
```

#### []()

##### Description


##### Used by


##### DB tables touched


##### Queries

```
```

#### []()

##### Description


##### Used by


##### DB tables touched


##### Queries

```
```

#### []()

##### Description


##### Used by


##### DB tables touched


##### Queries

```
```

## Miscellaneous

### [/sfb/app/search.aspx?Search=&Type=Authorizations](https://slate.societyfortheblind.org/sfb/app/search.aspx?Search=&Type=Authorizations)

#### Description

`search.aspx` seems to be  a generic search function
for  different   entities  (lesson   notes,  waiting
list,  authorizations  and  clients)  on  their  own
page (`authorizations.aspx`,  etc.), but it  is only
limited to  a single  keyword. More  complex queries
can  be  made  via the  "Advanced  Search"  buttons,
taking the user to  specialized pages for the entity
(`authorization-search.aspx`, etc.).

#### Used by

All.

#### DB tables touched

+ twbAuthorization
+ twbAuthorizationType
+ twbCCR
+ twbContact
+ twbContactType
+ twbMember
+ twbOutreach
+ twbServiceArea
+ twbServiceAreaAuthorization

#### Queries

```
                str3 = "SELECT DISTINCT ('<a href=''edit-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', City, (LastName + ' ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'NoShow'  FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType LIKE 'Client' AND ContactValue <> 0  UNION SELECT DISTINCT ('<a href=''edit-brief-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name',  City, (LastName + ' ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'NoShow'  FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType <> 'Client' AND ContactValue <> 0 AND ContactType <> 'Third Party'  AND twbContact.ContactKey NOT IN (SELECT twbContact.ContactKey   FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey  WHERE ContactType LIKE 'Client' AND ContactValue <> 0) ORDER BY NoShow";
                str3 = "SELECT DISTINCT ('<a href=''view-sa.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', Company, (LastName + ' ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'NoShow' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType <> 'Outside Agency'";
                str3 = "SELECT DISTINCT ('<a href=''assign-waiting-list.aspx?SAAKey=' + CAST(twbServiceAreaAuthorization.ServiceAreaAuthorizationKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', AuthorizationID As 'Authorization', ServiceArea,  CAST(StartDate As VARCHAR(11)) AS StartDate, (LastName + ' ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'NoShow' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization On twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization On twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbServiceArea On twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey WHERE EndDate > CAST(CAST(MONTH(DATEADD(m, -1, GETDATE())) AS VARCHAR(2)) + '/' + '1' + '/' + CAST(YEAR(DATEADD(m, -1, GETDATE())) AS VARCHAR(4)) AS DATETIME) AND ContactType = 'Client' AND ContactValue <> 0";
                str3 = "SELECT DISTINCT ('<a href=''edit-lesson-note.aspx?CCRKey=' + CAST(CCRKey AS VARCHAR(6)) + '''>' + CAST(LessonDate As varchar(11)) + '</a>') As LessonDate, (LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'Name', AuthorizationID, ServiceArea, (LastName + ' ' + FirstName + ' ' + MiddleName + ' ' + Company + ';') As 'NoShow', LessonDate As LessonDateSort  FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbServiceAreaAuthorization ON twbAuthorization.AuthorizationKey = twbServiceAreaAuthorization.AuthorizationKey INNER JOIN twbCCR ON twbCCR.ServiceAreaAuthorizationKey = twbServiceAreaAuthorization.ServiceAreaAuthorizationKey INNER JOIN twbServiceArea ON twbServiceArea.ServiceAreaKey = twbServiceAreaAuthorization.ServiceAreaKey WHERE ContactType LIKE 'Client' AND ContactValue <> 0  ";
                str3 = "SELECT DISTINCT ('<a href=''edit-outreach.aspx?OutreachKey=' + CAST(OutreachKey AS VARCHAR(6)) + '''>' + OutreachName + '</a>') As 'Name', OutreachName As 'NoShow' FROM twbOutreach WHERE Deleted = 0";
                str3 = "SELECT DISTINCT ('<a href=''edit-intake.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', Company, (LastName + ' ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'NoShow' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey WHERE ContactType LIKE 'Outside Agency'";
                str3 = "SELECT DISTINCT ('<a href=''edit-sa.aspx?SAKey=' + CAST(ServiceAreaKey AS VARCHAR(6)) + '''>' + ServiceArea + '</a>') As 'Name', ServiceArea As 'NoShow' FROM twbServiceArea WHERE Deleted = 0";
                str3 = "SELECT DISTINCT ('<a href=''edit-db-user.aspx?MemberKey=' + CAST(MemberKey AS VARCHAR(6)) + '''>' + MemberLastName + ', ' + MemberFirstName + '</a>') As 'Name', UserName, MemberEmail, (MemberLastName + ' ' + MemberFirstName) As 'NoShow' FROM twbMember WHERE Deleted = 0";
                str3 = "SELECT DISTINCT ('<a href=''view-billing.aspx?AuthKey=' + CAST(AuthorizationKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', CAST(EndDate As VARCHAR(11)) As 'EndDate', (CAST(ROUND(HoursRemaining, 4) As varchar(10))) AS 'HoursRemaining', AuthorizationTypeCode, (LastName + ' ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'NoShow' FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization On twbAuthorization.ContactKey = twbContact.ContactKey INNER JOIN twbAuthorizationType On twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID WHERE ContactType = 'Client' AND ContactValue <> 0";
                str3 = "SELECT DISTINCT ('<a href=''view-authorizations.aspx?ContactKey=' + CAST(twbContact.ContactKey AS VARCHAR(6)) + '''>' + LastName + ', ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';</a>') As 'Name', AuthorizationID, (LastName + ' ' + FirstName + ' ' + MiddleName + ' - ' + Company + ';') As 'NoShow', AuthorizationTypeCode FROM twbContact INNER JOIN twbContactType ON twbContact.ContactKey = twbContactType.ContactKey INNER JOIN twbAuthorization ON twbContact.ContactKey = twbAuthorization.ContactKey INNER JOIN twbAuthorizationType On twbAuthorization.AuthorizationTypeID = twbAuthorizationType.AuthorizationTypeID WHERE ContactType <> 'Outside Agency'";
```


---------------------------

**VIM helpers**

```vim
g!/\vOleDbCommand|FROM/d
%s/twb/\rtwb/g | g!/^twb/d | %s/^\(twb.\{-}\)[\. ].*$/+ \1/
sort u
```
