import pytest
from unittest.mock import patch

from django.test import TransactionTestCase
from django.contrib.auth.models import AnonymousUser

from codecov_auth.tests.factories import OwnerFactory
from ..trigger_sync import TriggerSyncInteractor
from codecov.commands.exceptions import Unauthenticated, ValidationError


class IsSyncingInteractorTest(TransactionTestCase):
    def setUp(self):
        self.user = OwnerFactory(username="codecov-user")

    def test_when_unauthenticated_raise(self):
        with pytest.raises(Unauthenticated):
            TriggerSyncInteractor(AnonymousUser(), "github").execute()

    @patch("services.refresh.RefreshService.trigger_refresh")
    def test_call_is_refreshing(self, mock_trigger_refresh):
        TriggerSyncInteractor(self.user, "github").execute()
        mock_trigger_refresh.assert_called_once_with(
            self.user.ownerid, self.user.username, using_integration=False
        )
