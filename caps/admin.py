from django.contrib import admin
from caps.models import CapsForm, Drug, PregnancyProblem, HeartDisease, MedicalProblem, DrugUse
from django.utils.encoding import smart_unicode
from django.conf.urls import patterns

class PreviousPregnancyInline(admin.TabularInline):
    model = PregnancyProblem
    extra = 0
#    verbose_name = "If appropriate, please provide additional information about previous pregnancy problems"


class HeartDiseaseInline(admin.TabularInline):
    model = HeartDisease
    extra = 0
#    verbose_name = "If appropriate, please provide additional information about pre-disposing factors for heart disease"


class MedicalProblemInline(admin.TabularInline):
    model = MedicalProblem
    extra = 0


class DrugUseInline(admin.TabularInline):
    model = DrugUse
    extra = 0
    fields = ('drug', 'last_use_unknown', 'last_use')


class CapsFormAdmin(admin.ModelAdmin):
    # Bring back the first and last name from the User record for display
    def created_name(self, obj):
        return smart_unicode("{0} {1}".format(
            obj.created_by.first_name,
            obj.created_by.last_name
        ))
    created_name.short_description = "Created by"
    # Shorten the list display column heading for previous pregnancy
    def prev_preg(self, obj):
        return obj.previous_pregnancy_problem
    prev_preg.short_description = "Pregnancy Problems"
    prev_preg.boolean = True
    # Shorten the list display column heading for heart disease
    def heart_dis(self, obj):
        return obj.heart_disease
    heart_dis.short_description = "Heart Disease"
    heart_dis.boolean = True
    # Shorten the list display column heading for cardiac arrest
    def cardiac_arr(self, obj):
        return obj.cardiac_arrest
    cardiac_arr.short_description = "Cardiac Arrest"
    cardiac_arr.boolean = True
    # Shorten the list display column heading for drug use
    def drug_u(self, obj):
        return obj.drug_use
    drug_u.short_description = "Drug Use"
    drug_u.boolean = True
    # Shorten the list display column heading for previous medical
    def prev_med(self, obj):
        return obj.previous_medical_problem
    prev_med.short_description = "Medical Problems"
    prev_med.boolean = True
    # Set admin display options
    list_display = ('case_id', 'created_name', 'created_on', 'smoking', 'prev_preg', 'heart_dis',
                    'cardiac_arr', 'drug_u', 'prev_med')
    list_filter = ('created_by', 'created_on', 'smoking', 'previous_pregnancy_problem', 'heart_disease',
                   'cardiac_arrest', 'drug_use', 'previous_medical_problem')
    fieldsets = [
        (None, {
            'fields': [
                'case_id',
                'case_reported',
                'created_by',
                # created_on
            ],
            'description': '<p class="example">Please do not enter any personally identifiable information (e.g. name, address, or '
                           'hospital number) on this form<br/>'
                           'Fill in the form using the information available in the woman\'s case notes</p>'
        }),
        ("Section 1: Woman's details", {
            'fields': [
                'year_of_birth',
                'ethnic_group',
                'marital_status',
                'employed',
                'occupation',
                'height',
                'weight',
                'smoking'
            ]
        }),
        ("Section 2: Previous Obstetric History", {
            'fields': [
                'gravidity_24plus',
                'gravidity_24minus',
                'previous_pregnancy_problem',
                # 'previous_pregnancy_history'
            ]
        }),
        ("Section 3: Previous Medical History", {
            'fields': [
                'heart_disease',
                # heart_disease_history
                'cardiac_arrest',
                'cardiac_arrest_date',
                'cardiac_arrest_cause',
                'drug_use',
                # drug_use_history
                'previous_medical_problem'
                # previous_medical_history
            ]
        })
    ]
    inlines = [PreviousPregnancyInline, HeartDiseaseInline, MedicalProblemInline, DrugUseInline]
    save_on_top = True

#    # Add some custom admin views to export the data
#    def get_urls(self):
#        urls = (superConfigAdmin, self).get_urls()
#        my_urls = patterns('',
#            (r'^view/(?P\d+)', self.admin_site.admin_view(self.config_detail))
#        )
#        return my_urls + urls
#
#    def config_detail(self,request, id):
#        config = Config.objects.get(pk=id),exclude.('email_notification', 'loginkey'))
#        opts = Config._meta
#        app_label = opts.app_label
#
#        #create tempate page and extend admin/base.html
#        config_detail_view_template = 'admin/config/detail_view.html'
#        cxt = {
#            'data' : config,
#        }
#        return render_to_response(config_detail_view_template , cxt, context_instance=RequestContext(request))
#
#    def action(self,form):
#        return "<a href='view/%s'>view</a>" % (form.id)
#    action.allow_tags = True

admin.site.register(CapsForm, CapsFormAdmin)


class DrugAdmin(admin.ModelAdmin):
    # Set admin display options
    list_display = ('name', 'alternative_names', 'uk_class', 'type', 'note')
    list_filter = ('uk_class', 'type')
    search_fields = ('name', 'alternative_names')
    save_on_top = True

admin.site.register(Drug, DrugAdmin)
