# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
from django.core.exceptions import ValidationError

class Drug(models.Model):
    """
    The list of illegal and recreational drugs is likely to be extensive, so provide a user expandable dictionary to
    improve on the list of drugs imported from the application fixtures list. Initial (sample) data supplied via
    http://en.wikipedia.org/wiki/Drugs_controlled_by_the_UK_Misuse_of_Drugs_Act and in Data.json
    """
    UK_CLASS_CHOICES = (
        ('A', u'Class A'),
        ('B', u'Class B'),
        ('C', u'Class C'),
        ('U', u'Unclassified')
    )
    TYPE_CHOICES = (
        (u'opioid', u'Opioid'),
        (u'stimulant', u'Stimulant'),
        (u'sedative', u'Sedative'),
        (u'erythroxylum', u'Erythroxylum'),
        (u'arylcyclohexylamine', u'Arylcyclohexylamine'),
        (u'phenethylamine', u'Phenethylamine'),
        (u'benzodiazepine', u'Benzodiazepine'),
        (u'other', u'Other'),
    )
    name = models.CharField(max_length=200, verbose_name='Name')
    uk_class = models.CharField(max_length=1, verbose_name='UK classification', choices=UK_CLASS_CHOICES, default='U')
    alternative_names = models.CharField(max_length=200, verbose_name='Alternative names', null=True, blank=True)
    type = models.CharField(max_length=20, verbose_name='Drug type', default='other', choices=TYPE_CHOICES)
    note = models.TextField(verbose_name='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'drugs'

    def __unicode__(self):
        if len(self.alternative_names) > 0:
            return smart_unicode("{0} ({1})".format(self.name, self.alternative_names))
        else:
            return smart_unicode("{0}".format(self.name))


class DrugUse(models.Model):
    """
    Linking table with extra relationship information for adding 0-n Drugs to a CapsForm record.
    Last use may be unknown, in which case there will be no datetime for last_use, and a True result in last_use_unknown
    If a date and time is supplied for last_use, then last_use_unknown should be false (and is the default)
    """
    drug = models.ForeignKey(Drug, verbose_name='Drug')
    person = models.ForeignKey('CapsForm', related_name='drug_history', verbose_name='Case')
    last_use = models.DateTimeField(blank=True, null=True, verbose_name='Last used?')
    last_use_unknown = models.BooleanField(default=False, verbose_name='Last use unknown?')
    # Quantity to be recorded in the future if known?

    class Meta:
        verbose_name = 'drug used'
        verbose_name_plural = 'drugs used'

    def __unicode__(self):
        if self.last_use_unknown:
            return smart_unicode("{0} used at an unknown time and date".format(self.drug.name))
        else:
            return smart_unicode("{0} used at {1:%Y-%m-%d %H:%M}".format(self.drug.name, self.last_use))

    def clean(self):
        if self.last_use is None and not self.last_use_unknown:
            raise ValidationError("Section 3: Please specify a date for this drug use, or tick the box to say the timing is unknown")
        if self.drug is not None:
            self.person.drug_use = True


class CapsForm(models.Model):
    """
    Main record created from the data input, this represents the core of the form data.
    Background record keeping allows us to track data entry and provide a visible reference, then the rest of the model
    is broken down into section blocks inline with sections on the sample form.

    No clear guidance is given on what questions are optional, and what are not, so there is some guessing being done
    presently over which fields to insist on data for. Also, this model doesn't presently recognise any difference
    between "Unknown" and "Unanswered", something that would need to be addressed in a more complete solution. I have
    opted to exclude "null" for the Boolean fields presently as this would perhaps add confusion, thus making them
    compulsory.

    Additionally, as this is not incorporated into any wider clinical software or setup at present, the guidance to
    the data entry person on what to do with any problems or queries on how to complete this is not addressed - for
    example, inline help within the templates, email or instant messenger links to the UKOSS support team, etc
    """
    # Ethnic codes based on the UK Census coding
    ETHNIC_ORIGIN_CHOICES = (
        (u'White', (
                (1, u'British'),
                (2, u'Irish'),
                (3, u'Any Other White Background')
            )
        ),
        (u'Mixed', (
                (4, u'White & Black Caribbean'),
                (5, u'White & Black African'),
                (6, u'White & Asian'),
                (7, u'Any Other Mixed Background'),
            )
        ),
        (u'Asian or Asian British', (
                (8, u'Indian'),
                (9, u'Pakistani'),
                (10, u'Bangladeshi'),
                (11, u'Any Other Asian Background'),
            )
        ),
        (u'Black or Black British', (
                (12, u'Caribbean'),
                (13, u'African'),
                (14, u'Any Other Black Background'),
            )
        ),
        (u'Chinese or Other Ethic Group', (
                (15, u'Chinese'),
                (16, u'Any Other Ethnic Group'),
            )
        ),
        (0, u'Unknown')
    )
    # List of valid choices defined by the form for marital status
    MARTIAL_STATUS_CHOICES = (
        (u'single', u'Single'),
        (u'married', u'Married'),
        (u'cohabiting', u'Cohabiting')
    )
    # List of valid choices defined by the form for smoking status
    SMOKING_CHOICES = (
        (u'never', u'Never'),
        (u'prior', u'Gave up prior to pregnancy'),
        (u'during', u'Gave up during pregnancy'),
        (u'current', u'Current'),
    )
    # Because we want boolean values to appear as Yes/No options rather than a single tick box, define some choices as...
    BOOLEAN_CHOICES = (
        (True,'Yes'),
        (False,'No'),
    )
    NULLBOOLEAN_CHOICES = (
        (True,'Yes'),
        (False,'No'),
        (None, 'Not Applicable')
    )
    # Background record keeping
    case_id = models.CharField(max_length=10, verbose_name='ID Number', db_index=True, help_text="")
    case_reported = models.CharField(max_length=200, blank=True, null=True, verbose_name='Case reported in', help_text="")
    created_by = models.ForeignKey(User, related_name='+', verbose_name='Name of person completing form', help_text="")
    # TODO: make this automatically default to the logged in user and not be user editable
    created_on = models.DateTimeField(auto_now_add=True, editable=False, help_text="")
    # Section 1: Woman's details
    year_of_birth = models.IntegerField(
        max_length=4,
        verbose_name='Year of birth',
        validators=[MaxValueValidator(date.today().year), MinValueValidator(1900)],
        help_text="Woman's year of birth as a four digit number (YYYY)"
    )
    # MinValue is a tad arbitrary, but domain specific knowledge required to tighten this up. MaxValue could be better, perhaps today - 12?
    ethnic_group = models.IntegerField(choices=ETHNIC_ORIGIN_CHOICES, verbose_name='Ethnic group')
    marital_status = models.CharField(max_length=10, choices=MARTIAL_STATUS_CHOICES, verbose_name='Marital status')
    employed = models.BooleanField(
        choices=BOOLEAN_CHOICES,
        verbose_name='Was the women in paid employment at booking?'
    )
    occupation = models.TextField(
        blank=True,
        null=True,
        help_text="If paid employment was yes, please enter her occupation. Otherwise record the occupation of her partner if known."
    )
    # Occupation could likely be better served from a list of common occupations such as used in the census, etc.
    height = models.PositiveIntegerField(
        verbose_name='Height at booking (cm)',
        validators=[MaxValueValidator(300), MinValueValidator(90)] # Again, needs some domain knowledge to tighten up
    )
    weight = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name='Weight at booking (kg)',
        validators=[MaxValueValidator(300), MinValueValidator(30)], # Again, needs some domain knowledge to tighten up
        help_text="Weight can be up to 300kg, and allows one decimal place of accuracy (e.g. 78.5 kg)"
    )
    smoking = models.CharField(choices=SMOKING_CHOICES, verbose_name='Smoking status', max_length=10)
    # Section 2: Previous Obstetric History
    gravidity_24plus = models.PositiveSmallIntegerField(
        verbose_name='Number of completed pregnancies beyond 24 weeks',
        default=0,
        validators=[MaxValueValidator(20)] # Again, needs some domain knowledge to tighten up
    )
    # Where are the number of incomplete pregnancies beyond 24 weeks?
    gravidity_24minus = models.PositiveSmallIntegerField(
        verbose_name='Number of pregnancies less than 24 weeks',
        default=0,
        validators=[MaxValueValidator(20)] # Again, needs some domain knowledge to tighten up
    )
    previous_pregnancy_problem = models.NullBooleanField(
        choices=NULLBOOLEAN_CHOICES,
        verbose_name='Did the women have any previous pregnancy problems?',
        help_text="Skip this question and advance to section 3 if there have been no previous pregnancies"
    )
    # previous_pregnancy_history - related name from PregnancyProblem list
    # Section 3: Previous Medical History
    heart_disease = models.BooleanField(
        choices=BOOLEAN_CHOICES,
        verbose_name='Does the women have a history of predisposing factors for heart disease?'
    )
    # heart_disease_history - related name from HeartDisease list
    cardiac_arrest = models.BooleanField(
        choices=BOOLEAN_CHOICES,
        verbose_name='Does the women have a history of previous cardiac arrest?'
    )
    cardiac_arrest_date = models.DateField(
        verbose_name='Date of last cardiac arrest',
        blank=True,
        null=True,
        validators=[MaxValueValidator(date.today())]
    )
    cardiac_arrest_cause = models.TextField(verbose_name='Cause of cardiac arrest if known', blank=True, null=True)
    drug_use = models.BooleanField(
        choices=BOOLEAN_CHOICES,
        verbose_name='Does the women have a history of recreational/illegal drug use?'
    )
    drug_use_history = models.ManyToManyField(Drug, through=DrugUse, null=True)
    previous_medical_problem = models.BooleanField(
        choices=BOOLEAN_CHOICES,
        verbose_name='Does the women have any pre-existing or previous medical problems?'
    )
    # previous_medical_history - related name from MedicalProblem list

    class Meta:
        verbose_name = "CAPS Form"
        verbose_name_plural = 'CAPS Forms'
        get_latest_by = "created_on"

    def __unicode__(self):
        return smart_unicode("Case ID {0} created on {1:%Y-%m-%d %H:%M:%S} by {2} {3}".format(
            self.case_id,
            self.created_on,
            self.created_by.first_name,
            self.created_by.last_name
        ))

    def ethnic_group_string(self):
        for k,v in self.ETHNIC_ORIGIN_CHOICES:
            if k == self.ethnic_group:
                return v
        return ''

    def marital_status_string(self):
        for k,v in self.MARTIAL_STATUS_CHOICES:
            if k == self.marital_status:
                return v
        return ''

    def smoking_string(self):
        for k,v in self.SMOKING_CHOICES:
            if k == self.smoking:
                return v
        return ''

    def clean(self):
        """
        Add model level validation for some of the multi-field validation tests required.
        E.g. Entering Occupation details when employed is marked as True/Yes. Ensuring at least one drug has been
        selected if drug use is highlighted.
        """
        # TODO: Find a better way to do field level validation rather than model level over multiple fields. This feels too inelegant.
        # Test employed status and ensure there's occupation information when expected
        if self.employed and len(self.occupation) < 1:
            raise ValidationError('Section 1: Please enter occupation details for the woman')

        # Test answers in section 2.
        # If previous pregnancy problems have been entered here, then ensure gravidity count and pregnancy_problem are set
        if self.previous_pregnancy_history.count() > 0:
            self.previous_pregnancy_problem = True
            if self.gravidity_24minus == 0 and self.gravidity_24plus == 0:
                raise ValidationError("""
                Section 2: No previous pregnancies have been entered. Please correct the number of previous pregnancies.
                """)
        elif self.previous_pregnancy_problem:
            if self.previous_pregnancy_history.count() == 0:
                raise ValidationError("Section 2: Please enter more information about previous pregnancy problems.")
            if self.gravidity_24minus == 0 and self.gravidity_24plus == 0:
                raise ValidationError("""
                Section 2: No previous pregnancies have been entered. Please correct the number of previous pregnancies.
                """)
        # If there were previous pregnancies, remind them to answer the past problems question
        if ((self.gravidity_24minus > 0 or self.gravidity_24plus > 0) and self.previous_pregnancy_problem == ""):
            raise ValidationError("Section 2: Please indicate whether there were any previous pregnancy problems")

#        TODO: Determine validation and save order for admin interface and model. At present related objects are not being
#              validated on save, and there's no clear way to resolve this in the time remaining. Look to do this in the
#              admin form validation?
#        #Section 3 Tests
        # If there are previous cardiac arrests, ensure a date has been entered
        if self.cardiac_arrest and self.cardiac_arrest_date == None:
            raise ValidationError("Section 3: Please enter the date of the most recent cardiac arrest")
        # Autocorrect the cardiac arrest history
        if not self.cardiac_arrest and self.cardiac_arrest_date != None:
            self.cardiac_arrest = True
#        # Ensure a drug has been linked if drug use is True
#        if self.drug_use and self.drug_use_history.count() == 0:
#            raise ValidationError("Section 3: Please specify at least one drug used by the woman")
#        # Similar tests for medical history
#        if self.previous_medical_problem and self.previous_medical_history.count() == 0:
#            raise ValidationError("Section 3: Please specify a pre-existing or previous medical condition")

        return None


class PregnancyProblem(models.Model):
    """
    Extended reference data for coding answer to pregnancy problems, allowing for undefined (Other) answers to be
    stored, and also additional optional information beyond the codified example problems.
    """
    TYPE_CHOICES = (
        (u'throm', u'Thrombotic event'),
        (u'afe',u'Amniotic fluid embolism'),
        (u'eclampsia',u'Eclampsia'),
        (u'miscar3plus',u'3 or more miscarriages'),
        (u'premormtril',u'Preterm birth or mid trimester loss'),
        (u'neodeath',u'Neonatal death'),
        (u'stillbirth',u'Stillbirth'),
        (u'majcongab',u'Baby with a major congenital abnormality'),
        (u'sga',u'Small for gestational age (SGA) infant'),
        (u'lga',u'Large for gestational age (LGA) infant'),
        (u'infinstcare',u'Infant requiring intensive care'),
        (u'puerpysco',u'Puerperal psychosis'),
        (u'placentpreav',u'Placenta praevia'),
        (u'gestdiab',u'Gestational diabetes'),
        (u'placentabrupt',u'Significant placental abruption'),
        (u'postparthaemor',u'Post-partum haemorrhage requiring transfusion'),
        (u'surgpreg',u'Surgical procedure in pregnancy'),
        (u'hyperemadmit',u'Hyperemesis requiring admission'),
        (u'dehydrateadmin',u'Dehydration requiring admission'),
        (u'ovhypersynd',u'Ovarian hyperstimulation syndrome'),
        (u'sevinfect',u'Severe infection e.g. pyelonephritis'),
        (u'other',u'Other')
        )
    form = models.ForeignKey(CapsForm, related_name='previous_pregnancy_history')
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)
    details = models.TextField(blank=True, null=True, verbose_name='Additional Information')

    class Meta:
        verbose_name_plural = 'pregnancy problems'

    def __unicode__(self):
        return smart_unicode("Case {} with pregnancy problem of {}".format(self.form.case_id, self.type_string()))

    def type_string(self):
        for k,v in self.TYPE_CHOICES:
            if k == self.type:
                return v
        return ''

    def clean(self):
        # Autocorrect form if pregnancy issues have been added.
        if self.type is not None:
            self.form.previous_pregnancy_problem = True
        return None


class HeartDisease(models.Model):
    """
    Extended reference data for coding answer to heart diseases, allowing for undefined (Other) answers to be
    stored, and also additional optional information beyond the codified example problems.
    """
    TYPE_CHOICES = (
        (u'knowichheartdis',u'Known ischaemic heart disease'),
        (u'congheartdis', u'Congenital heart disease'),
        (u'prevcardsurg', u'Previous cardiac surgery'),
        (u'prevmyoinfarc', u'Previous myocardial infarction'),
        (u'cardiomypathy', u'Cardiomyopathy'),
        (u'prespermpacemaker', u'Presence of Permanent Pacemaker'),
        (u'knowreductventfunc', u'Known reduction in ventricular function'),
        (u'lowlevhdlchol', u'Low levels of HDL cholesterol'),
        (u'highlevldlchol', u'High levels of LDL cholesterol'),
        (u'cocaineuse', u'Cocaine use'),
        (u'vavheartdis',u'Valvular heart disease'),
        (u'vasculitis', u'Vasculitis'),
        (u'ischheartdisfirstdegrel', u'Ischaemic heart disease in first degree relative'),
        (u'diabetes', u'Diabetes'),
        (u'bromcripcarbelinuse', u'Bromocriptine/cabergoline use'),
        (u'famhistsudcarddeath', u'Family history of sudden cardiac death'),
        (u'histarrythimia', u'History of arrhythmia'),
        (u'persfamhisthyperobstcardmyp', u'Personal or family history of hypertrophic obstructive cardiomyopathy (HOCM)'),
        (u'famhistinharry', u'Family history of inherited arrhythmia e.g. long QT syndrome Marfan syndrome'),
        (u'turnersynd', u'Turner\'s Syndrome'),
        (u'other', u'Other')
        )
    form = models.ForeignKey(CapsForm, related_name='heart_disease_history')
    type = models.CharField(choices=TYPE_CHOICES, max_length=30)
    details = models.TextField(blank=True, null=True, verbose_name='Additional Information')

    class Meta:
        verbose_name = 'heart disease'
        verbose_name_plural = 'heart diseases'

    def __unicode__(self):
        return smart_unicode("Case {} with heart disease history of {}".format(self.form.case_id, self.type_string()))

    def type_string(self):
        for k,v in self.TYPE_CHOICES:
            if k == self.type:
                return v
        return ''

    def clean(self):
#        This test is never executed because if there is no data entered at all on this inline, then there's no model to clean...
#        # Check that at least one factor has been added for heart disease history
#        if self.form.heart_disease and self.type is None:
#            raise ValidationError("Section 3: Please specify more information about pre-disposing factors for heart disease.")
        # Autocorrect form if heart diseases issues have been added.
        if self.type is not None:
            self.form.heart_disease = True
        return None


class MedicalProblem(models.Model):
    """
    Extended reference data for coding answer to pre-existing medical problems, allowing for undefined (Other) answers
    to be stored, and also additional optional information beyond the codified example problems.
    """
    TYPE_CHOICES = (
        (u'carddiscongoracq', u'Cardiac disease (congenital or acquired'),
        (u'renaldisease', u'Renal disease'),
        (u'endodisord', u'Endocrine disorders e.g. hypo or hyperthyroidism Psychiatric disorders'),
        (u'haemdisord', u'Haematological disorders e.g. sickle cell disease, diagnosed thrombophilia'),
        (u'inflamdisord', u'Inflammatory disorders e.g. inflammatory bowel disease Autoimmune diseases'),
        (u'cancer', u'Cancer'),
        (u'hiv', u'HIV'),
        (u'respdisease', u'Respiratory disease e.g. severe asthma, COPD'),
        (u'other', u'Other')
        )
    form = models.ForeignKey(CapsForm, related_name='previous_medical_history')
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)
    details = models.TextField(blank=True, null=True, verbose_name='Additional Information')

    class Meta:
        verbose_name = 'medical problem'
        verbose_name_plural = 'medical problems'

    def __unicode__(self):
        return smart_unicode("Case {} with pre-existing medical problem of {}".format(self.form.case_id, self.type_string()))

    def type_string(self):
        for k,v in self.TYPE_CHOICES:
            if k == self.type:
                return v
        return ''

    def clean(self):
        # Autocorrect the answer to previous medical problems if data entered here
        if self.type is not None:
            self.form.previous_medical_problem = True
        return None
