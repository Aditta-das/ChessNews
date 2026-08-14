from django.contrib.sitemaps import Sitemap
from django.utils import timezone
from .models import Article  # Adjust import based on your app structure


class ArticleSitemap(Sitemap):
  changefreq = "weekly"
  priority = 0.8

  def items(self):
    # Only return articles that have a published date set in the past or present
    return Article.objects.filter(
        published_at__isnull=False, published_at__lte=timezone.now()
    )

  def lastmod(self, obj):
    # Use 'published_at' as the date field
    return obj.published_at