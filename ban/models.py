from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
try:
    from ipcalc import Network
except ImportError:
    raise ImproperlyConfigured('You must install ipcalc >= 0.1')

class IP(models.Model):
    ip = models.CharField(_('IP network'), max_length=18,
            help_text=_('Either IP address or IP network specification'))
    
    def __unicode__(self):
        return self.ip

    def network(self):
        return Network(self.ip)
        
    class Meta:
        abstract = True
        
class DeniedIP(IP):
    class Meta:
        verbose_name = _('Denied IP')
        verbose_name_plural = _('Denied IPs')
        
class AllowedIP(IP):
    class Meta:
        verbose_name = _('Allowed IP')
        verbose_name_plural = _('Allowed IPs') 