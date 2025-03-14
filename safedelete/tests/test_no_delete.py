from ..config import NO_DELETE, FIELD_NAME, USE_BOOLEAN_FIELD, BOOLEAN_FIELD_NAME
from ..models import SafeDeleteModel
from .testcase import SafeDeleteForceTestCase


class NoDeleteModel(SafeDeleteModel):
    _safedelete_policy = NO_DELETE


class NoDeleteTestCase(SafeDeleteForceTestCase):

    def setUp(self):
        self.instance = NoDeleteModel.objects.create()

    def test_no_delete(self):
        """Test whether the model's delete is ignored.

        Normally when deleting a model, it can no longer be refreshed from
        the database and will raise a DoesNotExist exception.
        """
        self.instance.delete()
        self.instance.refresh_from_db()
        self.assertIsNone(getattr(self.instance, FIELD_NAME))
        if USE_BOOLEAN_FIELD:
            self.assertEqual(getattr(self.instance, BOOLEAN_FIELD_NAME), False)

    def test_no_delete_manager(self):
        """Test whether models with NO_DELETE are impossible to delete via the manager."""
        NoDeleteModel.objects.all().delete()
        self.instance.refresh_from_db()
        self.assertIsNone(getattr(self.instance, FIELD_NAME))
        if USE_BOOLEAN_FIELD:
            self.assertEqual(getattr(self.instance, BOOLEAN_FIELD_NAME), False)