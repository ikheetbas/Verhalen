from typing import Dict

from django.http import QueryDict
from django.test import TestCase

from rm.constants import NEGOMETRIX
from rm.models import System
from rm.view_util import create_addition_dataset_filter


class ViewUtilTests(TestCase):

    def setUp(self):
        System.objects.get_or_create(name=NEGOMETRIX)

    def test_create_addition_dataset_filter(self):

        params = {'active': 'True', 'system': 'Negometrix'}

        system_id = System.objects.get(name=NEGOMETRIX).id
        expected_filter = {'active': 'True',
                           'interface_call__interface_definition__system_id': system_id}

        result_filter = create_addition_dataset_filter(params)

        self.assertEqual(result_filter, expected_filter)