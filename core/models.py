import logging

from django.conf import settings
from django.db import models, transaction
from django.dispatch.dispatcher import receiver


logger = logging.getLogger(__name__)


class Parent(models.Model):
    """Top-level model."""
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return u"Parent: %s" % (self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    @transaction.atomic
    def delete(self, *args, **kwargs):
        """Log the deletion."""
        logger.debug(u"Enter Parent.delete() method.")
        super(Parent, self).delete(*args, **kwargs)
        logger.debug(u"Exit Parent.delete() method.")


@receiver(models.signals.pre_delete, sender=Parent)
def _parent_pre_delete(sender, instance, **kwargs):
    """Parent model pre_delete signal receiver."""
    logger.debug(u"Deleting %s", instance)
    if instance.name == "Job":
        logger.error("Job's an unlucky name, can't delete %s.", instance)
        raise Exception(u"Job was a very unlucky man.")


@receiver(models.signals.post_delete, sender=Parent)
def _parent_post_delete(sender, instance, **kwargs):
    """Parent model post_delete signal receiver."""
    logger.debug(u"Deleted %s.", instance)


class Child(models.Model):
    """Bottom-level model - has a Parent."""
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(Parent, related_name='children')

    def __unicode__(self):
        return u"Child: %s" % (self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def delete(self, *args, **kwargs):
        """Log the deletion."""
        logger.debug(u"Enter Child.delete() method.")
        return super(Child, self).delete(*args, **kwargs)
        logger.debug(u"Exit Child.delete() method.")


@receiver(models.signals.pre_delete, sender=Child)
def _child_pre_delete(sender, instance, **kwargs):
    logger.debug(u"Deleting %s.", instance)
    if instance.name == "Job":
        logger.error("Job's an unlucky name, can't delete %s.", instance)
        raise Exception(u"Job was a very unlucky man.")


@receiver(models.signals.post_delete, sender=Child)
def _child_post_delete(sender, instance, **kwargs):
    """Child model post_delete signal receiver."""
    logger.debug(u"Deleted %s.", instance)
    if instance.name == "Baby":
        logger.warning(u"No one puts Baby in the corner - deleting everything.")
        Unrelated.objects.all().delete()


class Unrelated(models.Model):
    """Model used to verify database interactions unrelated to Parent-Child relationship."""
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return u"Unrelated: %s" % (self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')
