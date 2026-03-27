from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Site


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'list', 'guide']

    def location(self, item):
        return reverse(item)


class SiteSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Site.objects.all()

    def location(self, obj):
        return reverse('detail_site', kwargs={'slug': obj.slug})
