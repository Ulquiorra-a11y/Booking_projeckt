import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class UniqueID(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, verbose_name=_('UUID id'))

    class Meta:
        abstract = True

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    deleted_at = models.DateTimeField(null=True,blank=True, verbose_name=_('Deleted at'))

    class Meta:
        abstract = True

class Grades(models.IntegerChoices):
    ONE = 1, _("Poor")
    TWO = 2, _("Fair")
    THREE = 3, _("Average")
    FOUR = 4, _("Good")
    FIVE = 5, _("Excellent")





class Country(models.TextChoices):
    # Europe
    GERMANY = "DE", _("Germany")
    FRANCE = "FR", _("France")
    ITALY = "IT", _("Italy")
    SPAIN = "ES", _("Spain")
    PORTUGAL = "PT", _("Portugal")
    NETHERLANDS = "NL", _("Netherlands")
    BELGIUM = "BE", _("Belgium")
    AUSTRIA = "AT", _("Austria")
    SWITZERLAND = "CH", _("Switzerland")
    POLAND = "PL", _("Poland")
    CZECHIA = "CZ", _("Czechia")
    HUNGARY = "HU", _("Hungary")
    GREECE = "GR", _("Greece")
    CROATIA = "HR", _("Croatia")
    SWEDEN = "SE", _("Sweden")
    NORWAY = "NO", _("Norway")
    DENMARK = "DK", _("Denmark")
    FINLAND = "FI", _("Finland")
    IRELAND = "IE", _("Ireland")
    UNITED_KINGDOM = "GB", _("United Kingdom")
    ICELAND = "IS", _("Iceland")

    # Asia
    JAPAN = "JP", _("Japan")
    SOUTH_KOREA = "KR", _("South Korea")
    CHINA = "CN", _("China")
    THAILAND = "TH", _("Thailand")
    VIETNAM = "VN", _("Vietnam")
    INDONESIA = "ID", _("Indonesia")
    INDIA = "IN", _("India")
    SINGAPORE = "SG", _("Singapore")
    MALAYSIA = "MY", _("Malaysia")
    PHILIPPINES = "PH", _("Philippines")
    UAE = "AE", _("United Arab Emirates")
    TURKEY = "TR", _("Turkey")
    ISRAEL = "IL", _("Israel")

    # Americas
    USA = "US", _("United States")
    CANADA = "CA", _("Canada")
    MEXICO = "MX", _("Mexico")
    BRAZIL = "BR", _("Brazil")
    ARGENTINA = "AR", _("Argentina")
    CHILE = "CL", _("Chile")

    # Australia and Oceania
    AUSTRALIA = "AU", _("Australia")
    NEW_ZEALAND = "NZ", _("New Zealand")

    # Africa
    EGYPT = "EG", _("Egypt")
    MOROCCO = "MA", _("Morocco")
    SOUTH_AFRICA = "ZA", _("South Africa")
    TUNISIA = "TN", _("Tunisia")


class City(models.TextChoices):
    # Germany
    BERLIN = "BER", _("Berlin")
    MUNICH = "MUC", _("Munich")
    AUGSBURG = "AUG", _("Augsburg")
    HAMBURG = "HAM", _("Hamburg")
    FRANKFURT = "FRA", _("Frankfurt")
    COLOGNE = "CGN", _("Cologne")
    STUTTGART = "STR", _("Stuttgart")

    # France
    PARIS = "PAR", _("Paris")
    NICE = "NCE", _("Nice")
    LYON = "LYO", _("Lyon")
    MARSEILLE = "MRS", _("Marseille")
    BORDEAUX = "BOD", _("Bordeaux")

    # Italy
    ROME = "ROM", _("Rome")
    MILAN = "MIL", _("Milan")
    VENICE = "VCE", _("Venice")
    FLORENCE = "FLR", _("Florence")
    NAPLES = "NAP", _("Naples")

    # Spain
    MADRID = "MAD", _("Madrid")
    BARCELONA = "BCN", _("Barcelona")
    VALENCIA = "VLC", _("Valencia")
    SEVILLE = "SVQ", _("Seville")
    MALAGA = "AGP", _("Malaga")

    # Portugal
    LISBON = "LIS", _("Lisbon")
    PORTO = "OPO", _("Porto")

    # Netherlands
    AMSTERDAM = "AMS", _("Amsterdam")
    ROTTERDAM = "RTM", _("Rotterdam")
    THE_HAGUE = "HAG", _("The Hague")

    # Austria
    VIENNA = "VIE", _("Vienna")
    SALZBURG = "SZG", _("Salzburg")
    INNSBRUCK = "INN", _("Innsbruck")

    # Switzerland
    ZURICH = "ZRH", _("Zurich")
    GENEVA = "GVA", _("Geneva")
    BERN = "BRN", _("Bern")
    LUCERNE = "LUC", _("Lucerne")

    # United Kingdom
    LONDON = "LON", _("London")
    EDINBURGH = "EDI", _("Edinburgh")
    MANCHESTER = "MAN", _("Manchester")
    LIVERPOOL = "LIV", _("Liverpool")

    # Czechia
    PRAGUE = "PRG", _("Prague")
    BRNO = "BRQ", _("Brno")

    # Greece
    ATHENS = "ATH", _("Athens")
    THESSALONIKI = "SKG", _("Thessaloniki")

    # Turkey
    ISTANBUL = "IST", _("Istanbul")
    ANKARA = "ANK", _("Ankara")
    ANTALYA = "AYT", _("Antalya")
    IZMIR = "IZM", _("Izmir")

    # Japan
    TOKYO = "TYO", _("Tokyo")
    KYOTO = "KYO", _("Kyoto")
    OSAKA = "OSA", _("Osaka")
    HIROSHIMA = "HIJ", _("Hiroshima")
    SAPPORO = "SPK", _("Sapporo")

    # South Korea
    SEOUL = "SEL", _("Seoul")
    BUSAN = "PUS", _("Busan")
    INCHEON = "ICN", _("Incheon")

    # China
    BEIJING = "PEK", _("Beijing")
    SHANGHAI = "SHA", _("Shanghai")
    GUANGZHOU = "CAN", _("Guangzhou")
    SHENZHEN = "SZX", _("Shenzhen")

    # Thailand
    BANGKOK = "BKK", _("Bangkok")
    PHUKET = "HKT", _("Phuket")
    CHIANG_MAI = "CNX", _("Chiang Mai")

    # United Arab Emirates
    DUBAI = "DXB", _("Dubai")
    ABU_DHABI = "AUH", _("Abu Dhabi")

    # United States
    NEW_YORK = "NYC", _("New York")
    LOS_ANGELES = "LAX", _("Los Angeles")
    CHICAGO = "CHI", _("Chicago")
    MIAMI = "MIA", _("Miami")
    SAN_FRANCISCO = "SFO", _("San Francisco")
    LAS_VEGAS = "LAS", _("Las Vegas")
    BOSTON = "BOS", _("Boston")
    WASHINGTON = "WAS", _("Washington")

    # Canada
    TORONTO = "YYZ", _("Toronto")
    VANCOUVER = "YVR", _("Vancouver")
    MONTREAL = "YMQ", _("Montreal")

    # Australia
    SYDNEY = "SYD", _("Sydney")
    MELBOURNE = "MEL", _("Melbourne")
    BRISBANE = "BNE", _("Brisbane")
    PERTH = "PER", _("Perth")

    # Egypt
    CAIRO = "CAI", _("Cairo")
    HURGHADA = "HRG", _("Hurghada")
    SHARM_EL_SHEIKH = "SSH", _("Sharm El Sheikh")

class Guests(models.IntegerChoices):
    ONE = 1, _('1 quest')
    TWO = 2, _('2 quests')
    THREE = 3, _('3 quests')
    FOUR = 4, _('4 quests')
    FIVE = 5, _('5 quests')
    SIX = 6, _('6 quests')
    SEVEN = 7, _('7 quests')


class BookingStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    CONFIRMED = 'confirmed', _('Confirmed')
    CANCELLED = 'cancelled', _('Cancelled')
    COMPLETED = 'completed', _('Completed')




