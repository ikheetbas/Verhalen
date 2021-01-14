from django.contrib.auth.models import Group, Permission
from django.db.models.functions import Now
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from openpyxl import Workbook, load_workbook

from .constants import ERROR_MSG_FILE_DEFINITION_ERROR, ERROR, OK
from .interface_file_util import check_file_and_interface_type
from .models import Contract, InterfaceCall
from django.db.utils import IntegrityError

from .interface_file import check_file_is_excel_file, check_file_has_excel_extension, is_valid_header_row, \
    get_mandatory_field_positions, get_headers_from_sheet, get_fields_with_their_position, mandatory_fields_present
from .negometrix import register_contract, NegometrixInterfaceFile


def setUpUserWithInterfaceCallAndContract(self, superuser=True, group_name=None):
    """
    When called without parameters, you get a superuser
    """
    if superuser:
        self.user = _create_superuser()
    else:
        self.user = _create_user(group_name=group_name)

    self.client.force_login(self.user)

    self.interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                      status='TestStatus',
                                                      filename='Text.xls',
                                                      system='TestSysteem')
    self.contract_1 = Contract.objects.create(contract_nr='NL-123',
                                              seq_nr=0,
                                              description='Test Contract',
                                              contract_owner='T. Ester',
                                              interface_call=self.interfaceCall,
                                              contract_name='Test contract naam')


def _create_superuser(username="john", password="doe", **kwargs):
    user = get_user_model().objects.create(username=username,
                                           is_superuser=True,
                                           is_active=True,
                                           **kwargs
                                           )
    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()
    user.save()
    return user

def _create_user(username="john", password="doe", group_name=None, **kwargs):
    user = get_user_model().objects.create(username=username,
                                           is_active=True,
                                           **kwargs
                                           )
    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()

    if group_name:
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            message = f"Group {group_name} can not be found"
            raise Exception(message)
        user.groups.add(group)

    user.save()

    return user


class ContractTest(TestCase):

    def setUp(self):
        setUpUserWithInterfaceCallAndContract(self)

    def test_homepage(self):
        c = self.client
        response = c.get("/")
        self.assertEqual(response.status_code, 200)

    def test_contract(self):
        expected = 'NL-123: Test contract naam'
        self.assertEqual(self.contract_1.__str__(), expected)

    def test_one_interface_call_on_page(self):
        response = self.client.get('/interfacecalls')
        self.assertContains(response, 'TestStatus')
        self.assertContains(response, 'TestSysteem')

    def test_one_contract_on_interface_call_page(self):
        response = self.client.get(f'/interfacecall/{self.interfaceCall.pk}/')
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester')

    def test_two_contract_on_interface_call_page(self):
        Contract.objects.create(contract_nr='NL-345',
                                seq_nr=1,
                                description='Test Contract 2',
                                contract_owner='T. Ester',
                                interface_call=self.interfaceCall)
        response = self.client.get(f'/interfacecall/{self.interfaceCall.pk}/')
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=2)

        self.assertContains(response, 'NL-345')
        self.assertContains(response, 'Test Contract 2')

    def test_create_contract_without_parent(self):
        try:
            Contract.objects.create(contract_nr="NL-123")
        except IntegrityError as exception:
            expected = "null value in column \"interface_call_id\" " \
                       "violates not-null constraint"
            self.assertTrue(expected in exception.__str__())


class ExcelTests(TestCase):

    # Excel file extension

    def test_not_an_excel_file_extension(self):
        filename = 'test.txt'
        try:
            check_file_has_excel_extension(filename)
        except Exception as ex:
            self.assertTrue("Bestand heeft geen excel extensie" in ex.__str__())

    def test_an_excel_file_extension_xls(self):
        filename = 'test.xls'
        self.assertTrue(check_file_has_excel_extension(filename))

    def test_an_excel_file_extension_XLS(self):
        filename = 'test.XLS'
        self.assertTrue(check_file_has_excel_extension(filename))

    def test_an_excel_file_extension_xlsx(self):
        filename = 'test.xlsx'
        self.assertTrue(check_file_has_excel_extension(filename))

    def test_an_excel_file_extension_XLSX(self):
        filename = 'test.XLSX'
        self.assertTrue(check_file_has_excel_extension(filename))

    # Test on really being an Excel file, so can it be read as Workbook?

    def test_not_an_excelfile(self):
        file = open("rm/test/resources/aPdfWithExcelExtension.xls", "rb")
        print(f'type of file: {type(file)}')
        try:
            is_excel = check_file_is_excel_file(file)
        except Exception as ex:
            self.assertTrue("Het openen van dit bestand als excel bestand"
                            " geeft een foutmelding" in ex.__str__())

    def test_an_excelfile_xlsx(self):
        file = open("rm/test/resources/a_valid_excel_file.xlsx", "rb")
        print(f'type of file: {type(file)}')
        is_excel = check_file_is_excel_file(file)
        self.assertTrue(is_excel)

    # Test valid headers

    def test_valid_header_row_exact(self):
        self.assertTrue(is_valid_header_row(found_headers=('x', 'y', 'z'),
                                            mandatory_headers=('x', 'z')))

    def test_valid_header_row_case_sensitive(self):
        self.assertTrue(is_valid_header_row(found_headers=('X', 'y', 'z'),
                                            mandatory_headers=('x', 'z')))

    def test_invalid_header_row(self):
        self.assertFalse(is_valid_header_row(found_headers=('a', 'b', 'z'),
                                             mandatory_headers=('x', 'z')))

    # Test handle uploaded excel file

    def test_check_excel_file_invalid_headers(self):
        try:
            interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                         status='TestStatus',
                                                         filename='valid_excel_without_headers.xlsx')
            file = "rm/test/resources/valid_excel_without_headers.xlsx"
            check_file_and_interface_type(file, interfaceCall)
        except Exception as ex:
            self.assertTrue("File can not be recognized" in ex.__str__(),
                            f"We got another exception than expected, received: {ex.__str__()}")
        else:
            self.assertTrue(False, "No Exception, while expected because file has no headers")

    def test_check_valid_negometrix_excel_file(self):
        interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                     status='TestStatus',
                                                     filename='test_register_contract.xlsx')
        file = "rm/test/resources/test_register_contract.xlsx"
        excelInterfaceFile = check_file_and_interface_type(file, interfaceCall)
        self.assertTrue(isinstance(excelInterfaceFile, NegometrixInterfaceFile))

    def test_upload_valid_negometrix_excel_file_2_valid_rows(self):
        interfaceCall = InterfaceCall.objects.create(
            date_time_creation=Now(),
            status='TestStatus',
            filename='test_upload_valid_negometrix_excel_file_2_valid_rows.xlsx')
        file = "rm/test/resources/test_upload_valid_negometrix_excel_file_2_valid_rows.xlsx"
        excelInterfaceFile = check_file_and_interface_type(file, interfaceCall)
        self.assertTrue(isinstance(excelInterfaceFile, NegometrixInterfaceFile))

        excelInterfaceFile.process()

        contracten = interfaceCall.contracten.all()
        self.assertEqual(len(contracten),2)

        contract1 = contracten[0]
        self.assertEqual(contract1.contract_nr, '44335')
        contract2 = contracten[1]
        self.assertEqual(contract2.contract_nr, '44336')

        received_data = interfaceCall.received_data.all()
        self.assertEqual(len(received_data),3)


    def test_upload_valid_negometrix_excel_file_2_valid_rows_1_invalid_row(self):
        interfaceCall = InterfaceCall.objects.create(
            date_time_creation=Now(),
            status='TestStatus',
            filename='test_upload_valid_negometrix_excel_file_2_valid_rows_1_invalid_row.xlsx')
        file = "rm/test/resources/test_upload_valid_negometrix_excel_file_2_valid_rows_1_invalid_row.xlsx"
        excelInterfaceFile = check_file_and_interface_type(file, interfaceCall)
        self.assertTrue(isinstance(excelInterfaceFile, NegometrixInterfaceFile))

        excelInterfaceFile.process()

        contracten = interfaceCall.contracten.all()
        self.assertEqual(len(contracten),2)

        contract1 = contracten[0]
        self.assertEqual(contract1.contract_nr, '44335')
        contract2 = contracten[1]
        self.assertEqual(contract2.contract_nr, '44337')

        received_data = interfaceCall.received_data.all()
        self.assertEqual(len(received_data),4)
        self.assertEqual(received_data[0].status, OK)
        self.assertEqual(received_data[1].status, OK)
        self.assertEqual(received_data[2].status, ERROR)
        self.assertEqual(received_data[3].status, OK)

    #  Test generic database functions

    def test_get_field_positions(self):

        found_headers = ['Header 1', "just a field", 'Header x', 'and another']
        defined_headers = dict(
            header_01="Header 1",
            zomaarwat="something",
            header_x="Header x",
        )
        field_positions = get_fields_with_their_position(found_headers,
                                                         defined_headers)

        expected_field_opsitions = dict(
            header_01=0,
            header_x=2,
        )
        self.assertEqual(len(field_positions), 2)
        self.assertEqual(field_positions, expected_field_opsitions)

    def test_get_mandatory_field_positions_valid_situation(self):
        mandatory_fields = ("x", "z")
        field_positions = {"x": 1, "y": 2, "z": 4}
        positions = get_mandatory_field_positions(mandatory_fields,
                                                  field_positions)
        expected = [1, 4]
        self.assertEqual(positions, expected)

    def test_get_mandatory_field_postions_invalid_situation(self):
        mandatory_fields = ("x", "z")
        field_positions = {"x": 1, "y": 2, "b": 3}
        try:
            get_mandatory_field_positions(mandatory_fields,
                                          field_positions)
        except Exception as ex:
            self.assertEqual(ex.__str__(), ERROR_MSG_FILE_DEFINITION_ERROR)

    def test_mandatory_fields_present(self):
        mandatory_field_positions = [2, 3]
        row_values = ["nul", "een", "twee", "drie", "vier"]
        self.assertTrue(mandatory_fields_present(mandatory_field_positions,
                                                 row_values))

    def test_mandatory_fields_not_present_1_pos(self):
        mandatory_field_positions = [3]
        row_values = ["nul", "een", "twee", None, "vier"]
        self.assertFalse(mandatory_fields_present(mandatory_field_positions,
                                                  row_values))

    def test_mandatory_fields_not_present_1_ok_1_not(self):
        mandatory_field_positions = [2, 3]
        row_values = ["nul", "een", "twee", None, "vier"]
        self.assertFalse(mandatory_fields_present(mandatory_field_positions,
                                                  row_values))

    def test_get_headers(self):
        file = open("rm/test/resources/test_get_headers.xlsx", "rb")
        workbook: Workbook = load_workbook(file)
        sheet = workbook.active
        headers = get_headers_from_sheet(sheet)
        expected = ("HEADER 1", "HEADER 2", None, "HEADER 4")
        self.assertEqual(headers, expected)

    def test_register_contract(self):
        row_nr = 4
        file = open("rm/test/resources/test_register_contract.xlsx", "rb")
        workbook: Workbook = load_workbook(file)
        sheet = workbook.active
        count = 1
        values_row_4 = []
        for row_values in sheet.iter_rows(min_row=1,
                                          min_col=1,
                                          values_only=True):
            if count == 4:
                values_row_4 = row_values
                break
            count += 1

        interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                     status='TestStatus',
                                                     filename='test_register_contract.xlsx')

        fields_with_position = dict(database_nr=0,
                                    contract_nr=1,
                                    contract_status=2,
                                    description=3,
                                    )

        mandatory_field_positions = (1, 2)
        mandatory_fields = ('a_field', 'another_field')

        status, msg = register_contract(row_nr, values_row_4, interfaceCall, fields_with_position,
                                        mandatory_field_positions)

        expected_status = ERROR

        self.assertEqual(status, expected_status)

class LoginRequiredTests(TestCase):
    """
    All pages require login, except the login page
    """

    def test_login_required_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse('account_login')+ "?next=/")

    def test_login_required_upload_page(self):
        response = self.client.get(reverse("upload"))
        self.assertRedirects(response, reverse('account_login') + "?next=/upload/")



class RoleBasedAuthorizationSuperuserTests(TestCase):

    def setUp(self):
        setUpUserWithInterfaceCallAndContract(self)

    def test_superuser_sees_upload_button(self):
        response = self.client.get(reverse("interface_call_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload file')

    def test_superuser_can_access_upload_form(self):
        response = self.client.get(reverse("upload"))
        self.assertEqual(response.status_code, 200)

    def test_superuser_sees_contracts_of_interfaceCall(self):
        response = self.client.get(f'/interfacecall/{self.interfaceCall.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=1)


def print_permissions_and_groups():
    all_permissions = Permission.objects.all()
    print("--------------------------------------")
    print("           PERMISSIONS")
    print("--------------------------------------")
    for permission in all_permissions:
        print(f"Found permission: {permission.codename}")
    print("--------------------------------------")

    all_groups = Group.objects.all()
    print("--------------------------------------")
    print("           GROUPS")
    print("--------------------------------------")
    for group in all_groups:
        print(f"Found group: {group.name}")
        permissions = group.permissions.all()
        if len(permissions) == 0:
            print("- has no permissions")
        for permission in permissions:
            print(f"- has permission: {permission.codename}")
    print("--------------------------------------")


class RoleBasedAuthorizationClusterLeadTests(TestCase):

    def setUp(self):
        setUpUserWithInterfaceCallAndContract(self, superuser=False, group_name="Cluster Lead")
        #print_permissions_and_groups()

    def test_cluster_lead_sees_no_upload_button(self):
        response = self.client.get(reverse("interface_call_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Upload file')

    def test_cluster_lead_can_not_access_upload_form(self):
        response = self.client.get(reverse("upload"))
        self.assertEqual(response.status_code, 403)

    def test_cluster_lead_has_view_contract_permissions(self):
        permissions = self.user.user_permissions.all()
        self.assertTrue(self.user.has_perm('rm.view_contract'))

    def test_cluster_lead_sees_contracts_of_interfaceCall(self):
        response = self.client.get(f'/interfacecall/{self.interfaceCall.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=1)

class RoleBasedAuthorizationBuyerTests(TestCase):


    def setUp(self):
        setUpUserWithInterfaceCallAndContract(self, superuser=False, group_name="Buyer")

    def test_buyer_sees_upload_button(self):
        response = self.client.get(reverse("interface_call_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload file')

    def test_buyer_can_access_upload_form(self):
        response = self.client.get(reverse("upload"))
        self.assertEqual(response.status_code, 200)

    def test_buyer_has_the_right_permissions(self):
        permissions = self.user.user_permissions.all()
        self.assertTrue(self.user.has_perm('rm.view_contract'))
        self.assertTrue(self.user.has_perm('rm.upload_contract_file'))
        self.assertTrue(self.user.has_perm('rm.call_contract_interface'))

    def test_buyer_sees_contracts_of_interfaceCall(self):
        response = self.client.get(f'/interfacecall/{self.interfaceCall.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=1)


