from rest_framework import status

from utilities.testing import ViewTestCases, create_tags, post_data

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import DNSSECPolicy, DNSSECKeyTemplate
from netbox_dns.choices import (
    DNSSECPolicyDigestChoices,
    DNSSECPolicyStatusChoices,
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
)


class DNSSECPolicyViewTestCase(
    ModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = DNSSECPolicy

    @classmethod
    def setUpTestData(cls):
        cls.dnssec_key_templates = (
            DNSSECKeyTemplate(
                name="csk-template1",
                type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            ),
            DNSSECKeyTemplate(
                name="csk-template2",
                type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.ED25519,
            ),
            DNSSECKeyTemplate(
                name="ksk-template1",
                type=DNSSECKeyTemplateTypeChoices.TYPE_KSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            ),
            DNSSECKeyTemplate(
                name="ksk-template2",
                type=DNSSECKeyTemplateTypeChoices.TYPE_KSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.ED25519,
            ),
            DNSSECKeyTemplate(
                name="zsk-template1",
                type=DNSSECKeyTemplateTypeChoices.TYPE_ZSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            ),
            DNSSECKeyTemplate(
                name="zsk-template2",
                type=DNSSECKeyTemplateTypeChoices.TYPE_ZSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.ED25519,
            ),
        )
        DNSSECKeyTemplate.objects.bulk_create(cls.dnssec_key_templates)

        cls.dnssec_policies = (
            DNSSECPolicy(
                name="Test Policy 4",
                status=DNSSECPolicyStatusChoices.STATUS_ACTIVE,
                dnskey_ttl=3600,
                purge_keys=7776000,
                publish_safety=3600,
                retire_safety=3600,
                signatures_jitter=43200,
                signatures_refresh=432000,
                signatures_validity=1209600,
                signatures_validity_dnskey=1209600,
                max_zone_ttl=86400,
                zone_propagation_delay=300,
                create_cdnskey=True,
                cds_digest_types=[DNSSECPolicyDigestChoices.SHA256],
                parent_ds_ttl=86400,
                parent_propagation_delay=3600,
                use_nsec3=True,
                nsec3_iterations=None,
                nsec3_opt_out=False,
                nsec3_salt_size=None,
            ),
            DNSSECPolicy(
                name="Test Policy 5",
            ),
            DNSSECPolicy(
                name="Test Policy 6",
                max_zone_ttl=43200,
                create_cdnskey=True,
                use_nsec3=False,
            ),
        )
        DNSSECPolicy.objects.bulk_create(cls.dnssec_policies)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "Test Policy 1",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "dnskey_ttl": 3600,
            "purge_keys": 7776000,
            "publish_safety": 3600,
            "retire_safety": 3600,
            "signatures_jitter": 43200,
            "signatures_refresh": 432000,
            "signatures_validity": 1209600,
            "signatures_validity_dnskey": 1209600,
            "max_zone_ttl": 86400,
            "zone_propagation_delay": 300,
            "create_cdnskey": True,
            "cds_digest_types": [DNSSECPolicyDigestChoices.SHA256],
            "parent_ds_ttl": 86400,
            "parent_propagation_delay": 3600,
            "use_nsec3": True,
            "nsec3_iterations": None,
            "nsec3_opt_out": False,
            "nsec3_salt_size": None,
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "Update Description",
            "status": DNSSECPolicyStatusChoices.STATUS_INACTIVE,
            "dnskey_ttl": 7200,
            "purge_keys": 7776999,
            "publish_safety": 7200,
            "retire_safety": 7200,
            "signatures_jitter": 43299,
            "signatures_refresh": 432999,
            "signatures_validity": 1209699,
            "signatures_validity_dnskey": 1209699,
            "max_zone_ttl": 86499,
            "zone_propagation_delay": 600,
            "create_cdnskey": False,
            "cds_digest_types": [DNSSECPolicyDigestChoices.SHA384],
            "parent_ds_ttl": 86499,
            "parent_propagation_delay": 7200,
            "use_nsec3": False,
            "nsec3_iterations": 1,
            "nsec3_opt_out": True,
            "nsec3_salt_size": 32,
        }

        cls.csv_data = (
            "name,status,dnskey_ttl,max_zone_ttl,create_cdnskey,use_nsec3",
            f"Test Policy 1,{DNSSECPolicyStatusChoices.STATUS_ACTIVE},86400,43200,true,true",
            "Test Policy 2,,86400,43200,false,true",
            f"Test Policy 3,{DNSSECPolicyStatusChoices.STATUS_INACTIVE},43200,86400,true,false",
        )

        cls.csv_update_data = (
            "id,description,use_nsec3,create_cdnskey",
            f"{cls.dnssec_policies[0].pk},Test Description 1,true,true",
            f"{cls.dnssec_policies[1].pk},Test Description 2,false,false",
        )

    maxDiff = None

    def test_ksk_zsk(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[4]

        self.add_permissions(
            "netbox_dns.change_dnssecpolicy",
            "netbox_dns.view_dnsseckeytemplate",
        )

        request_data = {
            "name": policy.name,
            "key_templates": [
                key_template1.pk,
                key_template2.pk,
            ],
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "max_zone_ttl": 424242,
        }
        request = {
            "path": self._get_url("edit", instance=policy),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_302_FOUND)

        policy.refresh_from_db()

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertIn(key_template2, policy.key_templates.all())
        self.assertEqual(policy.max_zone_ttl, 424242)

    def test_csk(self):
        policy = self.dnssec_policies[0]

        key_template = self.dnssec_key_templates[0]

        policy = self.dnssec_policies[0]

        self.add_permissions(
            "netbox_dns.change_dnssecpolicy",
            "netbox_dns.view_dnsseckeytemplate",
        )

        request_data = {
            "name": policy.name,
            "key_templates": [
                key_template.pk,
            ],
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "max_zone_ttl": 424242,
        }
        request = {
            "path": self._get_url("edit", instance=policy),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_302_FOUND)

        policy.refresh_from_db()

        self.assertIn(key_template, policy.key_templates.all())
        self.assertEqual(policy.max_zone_ttl, 424242)

    def test_csk_ksk_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[2]

        self.add_permissions(
            "netbox_dns.change_dnssecpolicy",
            "netbox_dns.view_dnsseckeytemplate",
        )

        request_data = {
            "name": policy.name,
            "key_templates": [
                key_template1.pk,
                key_template2.pk,
            ],
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "max_zone_ttl": 424242,
        }
        request = {
            "path": self._get_url("edit", instance=policy),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_csk_zsk_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[4]

        self.add_permissions(
            "netbox_dns.change_dnssecpolicy",
            "netbox_dns.view_dnsseckeytemplate",
        )

        request_data = {
            "name": policy.name,
            "key_templates": [
                key_template1.pk,
                key_template2.pk,
            ],
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "max_zone_ttl": 424242,
        }
        request = {
            "path": self._get_url("edit", instance=policy),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_csk_csk_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[1]

        self.add_permissions(
            "netbox_dns.change_dnssecpolicy",
            "netbox_dns.view_dnsseckeytemplate",
        )

        request_data = {
            "name": policy.name,
            "key_templates": [
                key_template1.pk,
                key_template2.pk,
            ],
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "max_zone_ttl": 424242,
        }
        request = {
            "path": self._get_url("edit", instance=policy),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_ksk_ksk_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[3]

        self.add_permissions(
            "netbox_dns.change_dnssecpolicy",
            "netbox_dns.view_dnsseckeytemplate",
        )

        request_data = {
            "name": policy.name,
            "key_templates": [
                key_template1.pk,
                key_template2.pk,
            ],
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "max_zone_ttl": 424242,
        }
        request = {
            "path": self._get_url("edit", instance=policy),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_zsk_zsk_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[4]
        key_template2 = self.dnssec_key_templates[5]

        self.add_permissions(
            "netbox_dns.change_dnssecpolicy",
            "netbox_dns.view_dnsseckeytemplate",
        )

        request_data = {
            "name": policy.name,
            "key_templates": [
                key_template1.pk,
                key_template2.pk,
            ],
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "max_zone_ttl": 424242,
        }
        request = {
            "path": self._get_url("edit", instance=policy),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_ksk_zsk_different_algorithm_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[5]

        self.add_permissions(
            "netbox_dns.change_dnssecpolicy",
            "netbox_dns.view_dnsseckeytemplate",
        )

        request_data = {
            "name": policy.name,
            "key_templates": [
                key_template1.pk,
                key_template2.pk,
            ],
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "max_zone_ttl": 424242,
        }
        request = {
            "path": self._get_url("edit", instance=policy),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)
