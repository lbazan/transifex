# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.core import serializers
from django.test.client import Client
from languages.models import Language
from resources.models import Resource, Translation
from txcommon.tests.base import BaseTestCase

try:
    import json
except ImportError:
    import simplejson as json

class PermissionsTest(BaseTestCase):
    """Test view permissions"""

    def seUp(self):
        super(ViewsTest, self).setUp()

    def test_anon(self):
        """
        Test anonymous user
        """
        # Test main lotte page
        page_url = reverse('translate_resource', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['anonymous'].get(page_url)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % page_url)

        # Create source language translation. This is needed to push
        # additional translations
        source_trans = Translation(source_entity=self.source_entity,
            language = self.language_en,
            string="foobar")
        source_trans.save()
        trans_lang = self.language.code
        trans = "foo"
        # Create new translation
        resp = self.client['anonymous'].post(reverse('push_translation',
            args=[self.project.slug, trans_lang,]),
            json.dumps({'strings':[{'id':source_trans.id,'translations':{ 'other': trans}}]}),
            content_type='application/json' )
        self.assertEqual(resp.status_code, 302)
        source_trans.delete()

        # Delete Translations
        resp = self.client['anonymous'].post(reverse(
            'resource_translations_delete',
            args=[self.project.slug, self.resource.slug,self.language.code]))
        self.assertEqual(resp.status_code, 403)

        # Check if resource gets deleted succesfully
        resp = self.client['anonymous'].get(reverse('resource_delete',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 403)

        # Check if user is able to access resource details
        resp = self.client['anonymous'].get(reverse('resource_detail',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 200)

        # Check if user is able to access resource edit
        resp = self.client['anonymous'].get(reverse('resource_edit',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 403)
        resp = self.client['anonymous'].post(reverse('resource_edit',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 403)

        # Check the popup
        resp = self.client['anonymous'].post(reverse('resource_actions',
            args=[self.project.slug, self.resource.slug, self.language_ar.code]))
        self.assertEqual(resp.status_code, 200)

        # Check the ajax view which returns more resources in project detail page.
        resp = self.client['anonymous'].post(reverse('project_resources',
            args=[self.project.slug, 5]))
        self.assertEqual(resp.status_code, 200)
        resp = self.client['anonymous'].post(reverse('project_resources_more',
            args=[self.project.slug, 5]))
        self.assertEqual(resp.status_code, 200)

        # Check that anonymous user is redirected to login page
        resp = self.client['anonymous'].get(reverse('clone_translate',
            args=[self.project.slug, self.resource.slug, self.language_en.code,
                  self.language.code]))
        self.assertEqual(resp.status_code, 302)

        # Check lock and get translation file perms
        resp = self.client['anonymous'].get(reverse('lock_and_download_translation',
            args=[self.project.slug, self.resource.slug, self.language.code]))
        self.assertEqual(resp.status_code, 302)

        # Check download file perms
        resp = self.client['anonymous'].get(reverse('download_translation',
            args=[self.project.slug, self.resource.slug, self.language.code]))
        self.assertEqual(resp.status_code, 302)


    def test_registered(self):
        """
        Test random registered user
        """

        # Test main lotte page
        page_url = reverse('translate_resource', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['registered'].get(page_url)
        self.assertEqual(resp.status_code, 403)

        # Create source language translation. This is needed to push
        # additional translations
        source_trans = Translation(source_entity=self.source_entity,
            language = self.language_en,
            string="foobar")
        source_trans.save()
        trans_lang = self.language.code
        trans = "foo"
        # Create new translation
        resp = self.client['registered'].post(reverse('push_translation',
            args=[self.project.slug, trans_lang,]),
            json.dumps({'strings':[{'id':source_trans.id,'translations':{ 'other': trans}}]}),
            content_type='application/json' )
        self.assertEqual(resp.status_code, 403)
        source_trans.delete()

        # Delete Translations
        resp = self.client['registered'].post(reverse(
            'resource_translations_delete',
            args=[self.project.slug, self.resource.slug,self.language.code]))
        self.assertEqual(resp.status_code, 403)

        # Check if resource gets deleted succesfully
        resp = self.client['registered'].get(reverse('resource_delete',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 403)

        # Check if user is able to access resource details
        resp = self.client['registered'].get(reverse('resource_detail',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 200)

        # Check if user is able to access resource edit
        resp = self.client['registered'].get(reverse('resource_edit',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 403)
        resp = self.client['registered'].post(reverse('resource_edit',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 403)

        # Check the popup
        resp = self.client['registered'].post(reverse('resource_actions',
            args=[self.project.slug, self.resource.slug, self.language_ar.code]))
        self.assertEqual(resp.status_code, 200)

        # Check the ajax view which returns more resources in project detail page.
        resp = self.client['registered'].post(reverse('project_resources',
            args=[self.project.slug, 5]))
        self.assertEqual(resp.status_code, 200)
        resp = self.client['registered'].post(reverse('project_resources_more',
            args=[self.project.slug, 5]))
        self.assertEqual(resp.status_code, 200)

        # Check clone language perms
        resp = self.client['registered'].get(reverse('clone_translate',
            args=[self.project.slug, self.resource.slug, self.language_en.code,
                  self.language.code]))
        self.assertEqual(resp.status_code, 403)

        # Check 'lock and get translation file' perms
        resp = self.client['registered'].get(reverse('lock_and_download_translation',
            args=[self.project.slug, self.resource.slug, self.language.code]))
        self.assertEqual(resp.status_code, 403)

        # Check download file perms
        resp = self.client['registered'].get(reverse('download_translation',
            args=[self.project.slug, self.resource.slug, self.language.code]))
        self.assertEqual(resp.status_code, 302)


    def test_team_member(self):
        """
        Test team_member permissions
        """

        # Test main lotte page
        page_url = reverse('translate_resource', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['team_member'].get(page_url)
        self.assertEqual(resp.status_code, 200)

        # Test main lotte page for other team. This should fail
        page_url = reverse('translate_resource', args=[
            self.project.slug, self.resource.slug, 'el'])
        resp = self.client['team_member'].get(page_url)
        self.assertEqual(resp.status_code, 403)

        # Create source language translation. This is needed to push
        # additional translations
        source_trans = Translation(source_entity=self.source_entity,
            language = self.language_en,
            string="foobar")
        source_trans.save()
        trans_lang = self.language.code
        trans = "foo"
        # Create new translation
        resp = self.client['team_member'].post(reverse('push_translation',
            args=[self.project.slug, trans_lang,]),
            json.dumps({'strings':[{'id':source_trans.id,'translations':{ 'other': trans}}]}),
            content_type='application/json' )
        self.assertEqual(resp.status_code, 200)

        # Create new translation in other team. Expect this to fail
        resp = self.client['team_member'].post(reverse('push_translation',
            args=[self.project.slug, 'ru']),
            json.dumps({'strings':[{'id':source_trans.id,'translations':{ 'other': trans}}]}),
            content_type='application/json' )
        self.assertEqual(resp.status_code, 403)
        source_trans.delete()

        # Delete Translations
        resp = self.client['team_member'].post(reverse(
            'resource_translations_delete',
            args=[self.project.slug, self.resource.slug,self.language.code]))
        self.assertEqual(resp.status_code, 403)

        # Check if resource gets deleted
        resp = self.client['team_member'].get(reverse('resource_delete',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 403)

        # Check if user is able to access resource details
        resp = self.client['team_member'].get(reverse('resource_detail',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 200)

        # Check if user is able to access resource edit
        resp = self.client['team_member'].get(reverse('resource_edit',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 403)
        resp = self.client['team_member'].post(reverse('resource_edit',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 403)

        # Check the popup
        resp = self.client['team_member'].post(reverse('resource_actions',
            args=[self.project.slug, self.resource.slug, self.language_ar.code]))
        self.assertEqual(resp.status_code, 200)

        # Check the ajax view which returns more resources in project detail page.
        resp = self.client['team_member'].post(reverse('project_resources',
            args=[self.project.slug, 5]))
        self.assertEqual(resp.status_code, 200)
        resp = self.client['team_member'].post(reverse('project_resources_more',
            args=[self.project.slug, 5]))
        self.assertEqual(resp.status_code, 200)

        # Check clone language perms
        resp = self.client['team_member'].get(reverse('clone_translate',
            args=[self.project.slug, self.resource.slug, self.language_en.code,
                  self.language.code]) ,follow=True)
        self.assertEqual(resp.status_code, 200)

        # Check lock and get translation file perms
        resp = self.client['team_member'].get(reverse('lock_and_download_translation',
            args=[self.project.slug, self.resource.slug, self.language.code]))
        self.assertEqual(resp.status_code, 200)

        # Check download file perms
        resp = self.client['team_member'].get(reverse('download_translation',
            args=[self.project.slug, self.resource.slug, self.language.code]))
        self.assertEqual(resp.status_code, 302)


    def test_maintainer(self):
        """
        Test maintainer permissions
        """

        # Test main lotte page
        page_url = reverse('translate_resource', args=[
            self.project.slug, self.resource.slug, self.language.code])
        resp = self.client['maintainer'].get(page_url)
        self.assertEqual(resp.status_code, 200)

        # Create source language translation. This is needed to push
        # additional translations
        source_trans = Translation(source_entity=self.source_entity,
            language = self.language_en,
            string="foobar")
        source_trans.save()
        trans_lang = self.language.code
        trans = "foo"
        # Create new translation
        resp = self.client['maintainer'].post(reverse('push_translation',
            args=[self.project.slug, trans_lang,]),
            json.dumps({'strings':[{'id':source_trans.id,'translations':{ 'other': trans}}]}),
            content_type='application/json' )
        self.assertEqual(resp.status_code, 200)
        source_trans.delete()

        # Delete Translations
        resp = self.client['maintainer'].post(reverse(
            'resource_translations_delete',
            args=[self.project.slug,
            self.resource.slug,self.language.code]),follow=True)
        self.assertEqual(resp.status_code, 200)

        # Check if resource gets deleted succesfully
        resp = self.client['maintainer'].get(reverse('resource_delete',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 200)

        # Check if user is able to access resource details
        resp = self.client['maintainer'].get(reverse('resource_detail',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 200)
        resp = self.client['maintainer'].post(reverse('resource_detail',
            args=[self.project.slug, self.resource.slug]))
        self.assertEqual(resp.status_code, 200)

        # Check the popup
        resp = self.client['maintainer'].post(reverse('resource_actions',
            args=[self.project.slug, self.resource.slug, self.language_ar.code]))
        self.assertEqual(resp.status_code, 200)

        # Check the ajax view which returns more resources in project detail page.
        resp = self.client['maintainer'].post(reverse('project_resources',
            args=[self.project.slug, 5]))
        self.assertEqual(resp.status_code, 200)
        resp = self.client['maintainer'].post(reverse('project_resources_more',
            args=[self.project.slug, 5]))
        self.assertEqual(resp.status_code, 200)

        # Check clone language perms
        resp = self.client['maintainer'].get(reverse('clone_translate',
            args=[self.project.slug, self.resource.slug, self.language_en.code,
                  self.language.code]) ,follow=True)
        self.assertEqual(resp.status_code, 200)

        # Check lock and get translation file perms
        resp = self.client['maintainer'].get(reverse('lock_and_download_translation',
            args=[self.project.slug, self.resource.slug, self.language.code]))
        self.assertEqual(resp.status_code, 200)

        # Check download file perms
        resp = self.client['maintainer'].get(reverse('download_translation',
            args=[self.project.slug, self.resource.slug, self.language.code]))
        self.assertEqual(resp.status_code, 302)
