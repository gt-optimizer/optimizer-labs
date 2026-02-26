"""
models.py — optimizer_labs / home app
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.snippets.models import register_snippet
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.search import index


# ---------------------------------------------------------------------------
# SNIPPETS
# ---------------------------------------------------------------------------

@register_snippet
class ClientTestimonial(models.Model):
    """Témoignage client — affiché dans le carrousel de la HomePage."""

    client_name = models.CharField(max_length=100, verbose_name=_("Nom du client"))
    client_company = models.CharField(max_length=100, verbose_name=_("Entreprise"), blank=True)
    client_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo du client"),
    )
    testimonial = models.TextField(verbose_name=_("Témoignage"))
    sector = models.CharField(max_length=100, verbose_name=_("Secteur d'activité"), blank=True)

    panels = [
        MultiFieldPanel([
            FieldPanel("client_name"),
            FieldPanel("client_company"),
            FieldPanel("sector"),
        ], heading="Informations client"),
        FieldPanel("client_logo"),
        FieldPanel("testimonial"),
    ]

    class Meta:
        verbose_name = _("Témoignage client")
        verbose_name_plural = _("Témoignages clients")
        ordering = ["client_name"]

    def __str__(self):
        return f"{self.client_name} — {self.client_company}"


@register_snippet
class PressCut(models.Model):
    """Coupure de presse — PDF ou image."""

    title = models.CharField(max_length=200, verbose_name=_("Titre"))
    source = models.CharField(max_length=100, verbose_name=_("Source (journal, site...)"))
    date = models.DateField(verbose_name=_("Date de publication"))
    file = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Fichier (PDF)"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Image de couverture"),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("source"),
        FieldPanel("date"),
        FieldPanel("file"),
        FieldPanel("cover_image"),
    ]

    class Meta:
        verbose_name = _("Coupure de presse")
        verbose_name_plural = _("Coupures de presse")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} ({self.source})"


# ---------------------------------------------------------------------------
# METHODE PAGE — étape structurée
# ---------------------------------------------------------------------------

class MethodeStep(Orderable):
    """Une étape de la méthode — liée à MethodePage via InlinePanel."""

    page = ParentalKey("MethodePage", on_delete=models.CASCADE, related_name="steps")
    title = models.CharField(max_length=200, verbose_name=_("Titre de l'étape"))
    description = RichTextField(
        verbose_name=_("Description"),
        features=["bold", "italic", "ul", "ol", "link"],
    )
    schema = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Schéma / illustration"),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("schema"),
    ]


class MethodePage(Page):
    """Page décrivant la méthode de travail, avec étapes ordonnées."""

    intro = RichTextField(
        verbose_name=_("Introduction"),
        features=["bold", "italic", "link"],
    )
    global_schema = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Schéma global de la méthode"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("global_schema"),
        InlinePanel("steps", label=_("Étapes de la méthode")),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Page Méthode")

    template = "home/methode_page.html"


# ---------------------------------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------------------------------

class SocialLink(Orderable):
    """Lien réseau social — lié à AboutPage via InlinePanel."""

    page = ParentalKey("AboutPage", on_delete=models.CASCADE, related_name="social_links")
    platform = models.CharField(
        max_length=50,
        verbose_name=_("Plateforme"),
        choices=[
            ("linkedin", "LinkedIn"),
            ("github", "GitHub"),
            ("twitter", "Twitter / X"),
            ("website", "Site web"),
            ("other", "Autre"),
        ],
    )
    url = models.URLField(verbose_name=_("URL"))

    panels = [
        FieldPanel("platform"),
        FieldPanel("url"),
    ]


class AboutPage(Page):
    """Page À propos — bio, compétences, réseaux sociaux."""

    profile_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Photo de profil"),
    )
    biography = RichTextField(
        verbose_name=_("Biographie / Parcours"),
        features=["bold", "italic", "ul", "ol", "link", "h2", "h3"],
    )
    skills = RichTextField(
        verbose_name=_("Compétences"),
        features=["bold", "italic", "ul", "ol"],
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("profile_image"),
        FieldPanel("biography"),
        FieldPanel("skills"),
        InlinePanel("social_links", label=_("Liens réseaux sociaux")),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Page À propos")

    template = "home/about_page.html"


# ---------------------------------------------------------------------------
# CASE STUDY — tags + pages
# ---------------------------------------------------------------------------

class CaseStudyTag(TaggedItemBase):
    """Table de liaison tags ↔ CaseStudyPage (via django-taggit)."""

    content_object = ParentalKey(
        "CaseStudyPage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class CaseStudyGalleryImage(Orderable):
    """Image supplémentaire liée à un CaseStudyPage."""

    page = ParentalKey("CaseStudyPage", on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Image"),
    )
    caption = models.CharField(max_length=255, blank=True, verbose_name=_("Légende"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]


class CaseStudyPage(Page):
    """Page d'étude de cas — structure fixe : contexte, problème, solution, résultats."""

    # Méta-données
    project_date = models.DateField(verbose_name=_("Date du projet"))
    client_sector = models.CharField(
        max_length=100,
        verbose_name=_("Secteur du client"),
        help_text=_("Ex : Artisan boucher, Industrie agroalimentaire..."),
    )
    tags = ClusterTaggableManager(through=CaseStudyTag, blank=True)
    main_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Image principale"),
    )

    # Structure fixe
    context = RichTextField(
        verbose_name=_("Contexte client"),
        features=["bold", "italic", "ul", "ol", "image", "link"],
    )
    problem = RichTextField(
        verbose_name=_("Problème à résoudre"),
        features=["bold", "italic", "ul", "ol", "image", "link"],
    )
    solution = RichTextField(
        verbose_name=_("Solution apportée"),
        features=["bold", "italic", "ul", "ol", "image", "embed", "link"],
    )
    results = RichTextField(
        verbose_name=_("Résultats"),
        features=["bold", "italic", "ul", "ol", "image", "link"],
    )

    # Panels avec onglets pour une meilleure ergonomie dans l'admin
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("project_date"),
            FieldPanel("client_sector"),
            FieldPanel("tags"),
            FieldPanel("main_image"),
        ], heading=_("Informations générales")),
        FieldPanel("context"),
        FieldPanel("problem"),
        FieldPanel("solution"),
        FieldPanel("results"),
        InlinePanel("gallery_images", label=_("Galerie d'images")),
    ]

    parent_page_types = ["home.CaseStudyIndexPage"]
    subpage_types = []

    search_fields = Page.search_fields + [
        index.SearchField("context"),
        index.SearchField("problem"),
        index.SearchField("solution"),
        index.SearchField("results"),
        index.FilterField("client_sector"),
    ]

    class Meta:
        verbose_name = _("Étude de cas")
        verbose_name_plural = _("Études de cas")

    template = "home/case_study_page.html"


class CaseStudyIndexPage(Page):
    """Page listant toutes les études de cas, avec filtrage par tag."""

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        features=["bold", "italic"],
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["home.CaseStudyPage"]

    class Meta:
        verbose_name = _("Index des études de cas")

    template = "home/case_study_index_page.html"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        projects = CaseStudyPage.objects.live().public().child_of(self).order_by("-project_date")

        # Filtrage par tag
        tag = request.GET.get("tag")
        if tag:
            projects = projects.filter(tagged_items__tag__slug=tag)

        context["projects"] = projects
        context["current_tag"] = tag
        return context


# ---------------------------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------------------------

class HomePage(Page):
    """Page d'accueil — hero, projets en vedette, carrousel clients, presse."""

    # Hero
    hero_title = models.CharField(max_length=150, verbose_name=_("Titre principal"))
    hero_subtitle = RichTextField(
        verbose_name=_("Accroche / sous-titre"),
        features=["bold", "italic"],
    )
    hero_cta_text = models.CharField(
        max_length=50,
        default="Voir mes projets",
        verbose_name=_("Texte du bouton d'appel à l'action"),
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Image Hero"),
    )

    # Sections — titres
    projects_section_title = models.CharField(
        max_length=100,
        default="Mes projets",
        verbose_name=_("Titre de la section Projets"),
    )
    testimonials_section_title = models.CharField(
        max_length=100,
        default="Ils me font confiance",
        verbose_name=_("Titre de la section Témoignages"),
    )
    press_section_title = models.CharField(
        max_length=100,
        default="Dans la presse",
        verbose_name=_("Titre de la section Presse"),
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("hero_title"),
            FieldPanel("hero_subtitle"),
            FieldPanel("hero_cta_text"),
            FieldPanel("hero_image"),
        ], heading=_("Section Hero")),
        MultiFieldPanel([
            FieldPanel("projects_section_title"),
        ], heading=_("Section Projets")),
        MultiFieldPanel([
            FieldPanel("testimonials_section_title"),
        ], heading=_("Section Témoignages")),
        MultiFieldPanel([
            FieldPanel("press_section_title"),
        ], heading=_("Section Presse")),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = [
        "home.CaseStudyIndexPage",
        "home.AboutPage",
        "home.MethodePage",
        "home.ContactPage",
    ]

    class Meta:
        verbose_name = _("Page d'accueil")

    template = "home/home_page.html"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Récupère l'index des projets pour construire l'URL du CTA
        case_study_index = CaseStudyIndexPage.objects.live().child_of(self).first()
        context["case_study_index"] = case_study_index

        # 4 derniers projets publiés
        context["featured_projects"] = (
            CaseStudyPage.objects.live().public().order_by("-project_date")[:4]
        )

        # Tous les témoignages
        context["testimonials"] = ClientTestimonial.objects.all()

        # 3 dernières coupures de presse
        context["press_cuts"] = PressCut.objects.all()[:3]

        return context


# ---------------------------------------------------------------------------
# CONTACT PAGE
# ---------------------------------------------------------------------------

class ContactFormField(AbstractFormField, Orderable):
    """Champ de formulaire lié à ContactPage."""

    page = ParentalKey("ContactPage", on_delete=models.CASCADE, related_name="form_fields")


class ContactPage(AbstractEmailForm):
    """Page de contact avec formulaire intégré Wagtail."""

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        features=["bold", "italic", "link"],
    )
    thank_you_text = RichTextField(
        blank=True,
        verbose_name=_("Message de confirmation après envoi"),
        features=["bold", "italic"],
    )

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        InlinePanel("form_fields", label=_("Champs du formulaire")),
        FieldPanel("thank_you_text"),
        MultiFieldPanel([
            FieldPanel("from_address"),
            FieldPanel("to_address"),
            FieldPanel("subject"),
        ], heading=_("Paramètres email")),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Page Contact")

    template = "home/contact_page.html"
    landing_page_template = "home/contact_page_landing.html"